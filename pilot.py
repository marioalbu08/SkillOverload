import argparse
import hashlib
import json
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TASKS_PATH = ROOT / "data" / "tasks.json"
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "service": {"type": "string"},
        "api_version": {"type": "string"},
        "upload_endpoint": {"type": "string"},
        "multipart_field": {"type": "string"},
        "auth_scheme": {"type": "string"},
        "file_size_limit": {"type": "string"},
        "sources": {
            "type": "object",
            "properties": {
                "service": {"type": "array", "items": {"type": "string"}},
                "api_version": {"type": "array", "items": {"type": "string"}},
                "upload_endpoint": {"type": "array", "items": {"type": "string"}},
                "multipart_field": {"type": "array", "items": {"type": "string"}},
                "auth_scheme": {"type": "array", "items": {"type": "string"}},
                "file_size_limit": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "service",
                "api_version",
                "upload_endpoint",
                "multipart_field",
                "auth_scheme",
                "file_size_limit",
            ],
            "additionalProperties": False,
        },
    },
    "required": [
        "service",
        "api_version",
        "upload_endpoint",
        "multipart_field",
        "auth_scheme",
        "file_size_limit",
        "sources",
    ],
    "additionalProperties": False,
}
FIELD_NAMES = (
    "service",
    "api_version",
    "upload_endpoint",
    "multipart_field",
    "auth_scheme",
    "file_size_limit",
)
CONCISE_SKILL = (
    "Extract the requested values only from the supplied case files. Treat current_manifest.md "
    "and access_policy.md as current; archive.md is historical and must not override them. "
    "Cite the authoritative filename for each value. If a value is absent, say so rather than guess."
)
EXPANSION_NOTES = (
    "First identify exactly which values the request asks for, then match each value to a sentence in the supplied files. "
    "Read the current manifest as the source for service identifiers, API versions, upload routes, multipart names, and limits. "
    "Read the access policy as the source for authentication requirements. "
    "Check the filename and the stated version before using a value from any excerpt. "
    "Keep facts from different files associated with their own source names. "
    "An old route can describe a real previous release and still be wrong for a question about the current release. "
    "Do not merge historical and current settings into one answer. "
    "Preserve capitalization, punctuation, units, and version strings from the current source. "
    "Do not convert a file-size limit into a different unit unless the request asks for that conversion. "
    "Do not infer authentication from the endpoint name or from an archived example. "
    "Return every requested key, even when its value is not available. "
    "Use the specified unknown marker when the documents do not answer a requested field. "
    "Attach a source to each field instead of listing sources without explaining which fact they support. "
    "Prefer a direct quote-compatible value over a paraphrase when extracting configuration. "
    "Check the answer against the request once more before returning it. "
    "Leave unrelated implementation details out of the structured result. "
    "Keep the response parseable as the requested JSON object. "
    "Never invent a header, path, field, version, or size limit. "
)
EXPANDED_SKILL = CONCISE_SKILL + "\n\nDetailed extraction procedure:\n" + "\n".join(
    f"{index}. {EXPANSION_NOTES[(index - 1) % len(EXPANSION_NOTES)]}"
    for index in range(1, 49)
)


class PilotError(Exception):
    def __init__(self, message, usage=None):
        super().__init__(message)
        self.usage = usage


def load_tasks():
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    if not isinstance(tasks, list) or not tasks:
        raise PilotError("The task file must contain a non-empty JSON list.")
    seen = set()
    required_answer = set(FIELD_NAMES)
    for task in tasks:
        if not isinstance(task, dict):
            raise PilotError("Every task must be a JSON object.")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise PilotError("Task IDs must be non-empty and unique.")
        seen.add(task_id)
        if set(task.get("answer", {})) != required_answer:
            raise PilotError(f"{task_id} has an invalid answer key set.")
        if set(task.get("citations", {})) != required_answer:
            raise PilotError(f"{task_id} has an invalid citation key set.")
        if not isinstance(task.get("files"), list) or not task["files"]:
            raise PilotError(f"{task_id} has no case files.")
    return tasks


def render_case(task):
    sections = [task["question"]]
    for item in task["files"]:
        sections.append(f"\n--- {item['path']} ---\n{item['content']}")
    return "\n".join(sections)


def estimate_tokens(text):
    return max(1, (len(text.encode("utf-8")) + 3) // 4)


def build_instructions(condition):
    if condition == "no_skill":
        return None
    if condition == "concise_skill":
        return CONCISE_SKILL
    return EXPANDED_SKILL


def call_openai(instructions, user_input, model, max_output_tokens, timeout):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise PilotError("Set OPENAI_API_KEY in your shell before using --provider openai.")
    input_items = []
    if instructions:
        input_items.append({"role": "developer", "content": instructions})
    input_items.append({"role": "user", "content": user_input})
    request_body = {
        "model": model,
        "input": input_items,
        "instructions": (
            "Extract facts from the supplied fictional case files. Use current_manifest.md and "
            "access_policy.md for the current configuration. archive.md is historical. Return "
            "only the required structured answer and source filenames. Do not invent values."
        ),
        "max_output_tokens": max_output_tokens,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "skill_overload_pilot_answer",
                "strict": True,
                "schema": OUTPUT_SCHEMA,
            }
        },
        "store": False,
    }
    encoded = json.dumps(request_body).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=encoded,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:1000]
        raise PilotError(f"OpenAI returned HTTP {error.code}: {detail}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise PilotError(f"OpenAI request failed: {error}") from error
    elapsed = time.perf_counter() - started
    text_parts = [
        item.get("text", "")
        for output in response_data.get("output", [])
        if output.get("type") == "message"
        for item in output.get("content", [])
        if item.get("type") == "output_text"
    ]
    raw_text = "".join(text_parts)
    usage = response_data.get("usage")
    token_usage = None
    if isinstance(usage, dict) and isinstance(usage.get("input_tokens"), int) and isinstance(usage.get("output_tokens"), int):
        token_usage = {
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["input_tokens"] + usage["output_tokens"],
            "latency_seconds": round(elapsed, 4),
            "response_id": response_data.get("id"),
        }
    if not raw_text:
        raise PilotError("The model returned no structured text; the response was not scored.", token_usage)
    if not isinstance(usage, dict) or not isinstance(usage.get("input_tokens"), int):
        raise PilotError("The response did not include input token usage; the response was not scored.", token_usage)
    if not isinstance(usage.get("output_tokens"), int):
        raise PilotError("The response did not include output token usage; the response was not scored.", token_usage)
    try:
        answer = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise PilotError(f"The model response was not valid JSON: {error}", token_usage) from error
    return answer, token_usage


def fixture_answer(task):
    return {
        **task["answer"],
        "sources": {key: [value] for key, value in task["citations"].items()},
    }


def score_answer(answer, task):
    if not isinstance(answer, dict):
        answer = {}
    values_correct = {}
    citations_correct = {}
    source_object = answer.get("sources", {})
    if not isinstance(source_object, dict):
        source_object = {}
    for field in FIELD_NAMES:
        values_correct[field] = answer.get(field) == task["answer"][field]
        supplied_sources = source_object.get(field, [])
        if isinstance(supplied_sources, str):
            supplied_sources = [supplied_sources]
        citations_correct[field] = (
            isinstance(supplied_sources, list)
            and set(supplied_sources) == {task["citations"][field]}
        )
    correct_values = sum(values_correct.values())
    correct_citations = sum(citations_correct.values())
    return {
        "task_success": correct_values == len(FIELD_NAMES) and correct_citations == len(FIELD_NAMES),
        "correct_fields": correct_values,
        "total_fields": len(FIELD_NAMES),
        "correct_citations": correct_citations,
        "unsupported_answer_fields": [
            field for field, correct in values_correct.items() if not correct
        ],
        "incorrect_citations": [
            field for field, correct in citations_correct.items() if not correct
        ],
    }


def summarize(records, seed):
    actual_records = [record for record in records if not record["simulated"]]
    if not actual_records:
        return {
            "report_kind": "synthetic_pipeline_check",
            "empirical_metrics": None,
            "note": "Fixture responses validate the runner and verifier; they are not model results.",
        }
    task_ids = sorted({record["task_id"] for record in actual_records})
    conditions = ("no_skill", "concise_skill", "expanded_skill")
    task_success = {
        task_id: {
            condition: sum(
                record["scores"]["task_success"]
                for record in actual_records
                if record["task_id"] == task_id and record["condition"] == condition
            )
            / max(
                1,
                sum(
                    record["task_id"] == task_id and record["condition"] == condition
                    for record in actual_records
                ),
            )
            for condition in conditions
        }
        for task_id in task_ids
    }
    means = {
        condition: sum(task_success[task_id][condition] for task_id in task_ids) / len(task_ids)
        for condition in conditions
    }
    bootstrap = random.Random(seed + 1)
    comparisons = {}
    for first, second in (
        ("concise_skill", "no_skill"),
        ("expanded_skill", "concise_skill"),
        ("expanded_skill", "no_skill"),
    ):
        differences = [task_success[task_id][first] - task_success[task_id][second] for task_id in task_ids]
        estimates = []
        for _ in range(4000):
            sample = [bootstrap.choice(differences) for _ in differences]
            estimates.append(sum(sample) / len(sample))
        estimates.sort()
        comparisons[f"{first}_minus_{second}"] = {
            "task_mean_difference": sum(differences) / len(differences),
            "task_cluster_bootstrap_95_interval": [
                estimates[int(0.025 * len(estimates))],
                estimates[min(len(estimates) - 1, int(0.975 * len(estimates)))],
            ],
            "tasks": len(differences),
        }
    by_condition = {}
    for condition in conditions:
        selected = [record for record in actual_records if record["condition"] == condition]
        scored = [record for record in selected if record.get("provider_error") is None]
        scored_count = max(1, len(scored))
        by_condition[condition] = {
            "task_mean_success_rate": means[condition],
            "trajectory_success_rate": sum(record["scores"]["task_success"] for record in selected)
            / max(1, len(selected)),
            "trajectory_count": len(selected),
            "mean_input_tokens": sum(record["usage"]["input_tokens"] for record in selected)
            / max(1, len(selected)),
            "mean_output_tokens": sum(record["usage"]["output_tokens"] for record in selected)
            / max(1, len(selected)),
            "total_input_tokens": sum(record["usage"]["input_tokens"] for record in selected),
            "total_output_tokens": sum(record["usage"]["output_tokens"] for record in selected),
            "median_latency_seconds": statistics.median(
                record["usage"]["latency_seconds"]
                for record in selected
                if record["usage"]["latency_seconds"] is not None
            )
            if any(record["usage"]["latency_seconds"] is not None for record in selected)
            else None,
            "unsupported_answer_fields": sum(
                len(record["scores"]["unsupported_answer_fields"]) for record in scored
            ),
            "unsupported_answer_field_rate": sum(
                len(record["scores"]["unsupported_answer_fields"]) for record in scored
            )
            / (scored_count * len(FIELD_NAMES)),
            "citation_accuracy": sum(record["scores"]["correct_citations"] for record in scored)
            / (scored_count * len(FIELD_NAMES)),
            "provider_errors": sum(record.get("provider_error") is not None for record in selected),
        }
    return {
        "report_kind": "pilot_model_observations",
        "by_condition": by_condition,
        "paired_comparisons": comparisons,
        "limitations": [
            "This public synthetic task suite is exploratory, not a held-out confirmatory benchmark.",
            "Incorrect closed-world answers are proxies for unsupported claims, not proof of internal hallucination.",
            "Skill expansion also shifts subsequent evidence later in the prompt; this pilot cannot isolate length from position.",
            "Results describe the recorded model, harness, task suite, and sampling settings only.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Run the SkillOverload three-condition pilot.")
    parser.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    parser.add_argument("--model", help="Required with --provider openai; model charges may apply.")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument("--max-output-tokens", type=int, default=250)
    parser.add_argument("--max-calls", type=int, default=36)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.repeats < 1 or arguments.repeats > 3:
        parser.error("--repeats must be between 1 and 3.")
    if arguments.max_output_tokens < 64 or arguments.max_output_tokens > 500:
        parser.error("--max-output-tokens must be between 64 and 500.")
    if arguments.max_calls < 1 or arguments.max_calls > 108:
        parser.error("--max-calls must be between 1 and 108.")
    if arguments.timeout < 1 or arguments.timeout > 300:
        parser.error("--timeout must be between 1 and 300 seconds.")
    if arguments.provider == "openai" and not arguments.model:
        parser.error("--model is required with --provider openai; model choice and billing are yours.")
    if arguments.provider == "fixture" and arguments.model:
        parser.error("--model is only used with --provider openai.")
    if arguments.provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is not set; fixture mode runs without credentials or API charges.")
    try:
        tasks = load_tasks()
    except (OSError, json.JSONDecodeError, PilotError) as error:
        parser.error(str(error))
    conditions = ("no_skill", "concise_skill", "expanded_skill")
    planned_calls = len(tasks) * len(conditions) * arguments.repeats
    if planned_calls > arguments.max_calls:
        parser.error(
            f"This run requires {planned_calls} calls, above --max-calls {arguments.max_calls}. "
            "Raise the cap explicitly after checking your model budget."
        )
    if arguments.provider == "openai" and planned_calls > 36:
        parser.error("Live API runs are capped at 36 calls per invocation.")
    rng = random.Random(arguments.seed)
    task_order = list(tasks)
    rng.shuffle(task_order)
    output_path = arguments.output or (
        ROOT / "results" / "runs" / f"pilot_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    )
    output_path = output_path.resolve()
    if output_path.exists():
        parser.error(f"Output already exists; choose another path: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = output_path.with_name(output_path.name + ".partial")
    if partial_path.exists():
        parser.error(f"Partial output already exists; preserve it and choose another path: {partial_path}")
    metadata = {
        "record_type": "run_metadata",
        "protocol_version": "0.1",
        "provider": arguments.provider,
        "simulated": arguments.provider == "fixture",
        "model": arguments.model if arguments.provider == "openai" else None,
        "python_version": sys.version.split()[0],
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "task_set_sha256": hashlib.sha256(TASKS_PATH.read_bytes()).hexdigest(),
        "concise_skill_sha256": hashlib.sha256(CONCISE_SKILL.encode("utf-8")).hexdigest(),
        "expanded_skill_sha256": hashlib.sha256(EXPANDED_SKILL.encode("utf-8")).hexdigest(),
        "sampling_settings": "provider defaults; no sampling override set",
        "seed": arguments.seed,
        "repeats": arguments.repeats,
        "task_count": len(tasks),
        "planned_calls": planned_calls,
        "conditions": list(conditions),
        "output_token_cap_per_call": arguments.max_output_tokens,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    records = []
    completed = 0
    try:
        with partial_path.open("x", encoding="utf-8", newline="\n") as report_file:
            report_file.write(json.dumps(metadata, ensure_ascii=False) + "\n")
            report_file.flush()
            for repeat in range(arguments.repeats):
                for task in task_order:
                    trial_conditions = list(conditions)
                    rng.shuffle(trial_conditions)
                    user_input = render_case(task)
                    for condition in trial_conditions:
                        skill_text = build_instructions(condition)
                        prompt_size = estimate_tokens(user_input)
                        skill_size = estimate_tokens(skill_text) if skill_text else 0
                        if arguments.provider == "fixture":
                            answer = fixture_answer(task)
                            usage = {
                                "input_tokens": None,
                                "output_tokens": None,
                                "total_tokens": None,
                                "latency_seconds": 0,
                                "prompt_estimated_tokens": prompt_size + skill_size,
                            }
                        else:
                            try:
                                answer, usage = call_openai(
                                    skill_text,
                                    user_input,
                                    arguments.model,
                                    arguments.max_output_tokens,
                                    arguments.timeout,
                                )
                                usage["prompt_estimated_tokens"] = prompt_size + skill_size
                                provider_error = None
                            except PilotError as error:
                                answer = {}
                                usage = error.usage or {
                                    "input_tokens": None,
                                    "output_tokens": None,
                                    "total_tokens": None,
                                    "latency_seconds": None,
                                    "response_id": None,
                                    "prompt_estimated_tokens": prompt_size + skill_size,
                                }
                                provider_error = str(error)
                        record = {
                            "record_type": "trial",
                            "task_id": task["id"],
                            "repeat": repeat + 1,
                            "condition": condition,
                            "simulated": arguments.provider == "fixture",
                            "prompt_estimated_tokens": prompt_size + skill_size,
                            "skill_estimated_tokens": skill_size,
                            "usage": usage,
                            "answer": answer,
                            "provider_error": provider_error if arguments.provider == "openai" else None,
                            "scores": score_answer(answer, task),
                        }
                        records.append(record)
                        report_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                        report_file.flush()
                        completed += 1
                        print(
                            f"{completed}/{planned_calls} {task['id']} {condition}: "
                            f"{'ERROR' if record['provider_error'] else ('PASS' if record['scores']['task_success'] else 'FAIL')}"
                        )
            report_file.write(
                json.dumps(
                    {"record_type": "summary", **summarize(records, arguments.seed)},
                    ensure_ascii=False,
                )
                + "\n"
            )
    except (PilotError, OSError, json.JSONDecodeError) as error:
        print(f"Run stopped after {completed}/{planned_calls} calls: {error}", file=sys.stderr)
        print(f"Partial evidence preserved at {partial_path}", file=sys.stderr)
        return 1
    if output_path.exists():
        print(f"Refusing to replace existing report: {output_path}", file=sys.stderr)
        return 1
    partial_path.replace(output_path)
    print(f"Saved {completed} trial records to {output_path}")
    if arguments.provider == "fixture":
        print("Fixture results are a pipeline check, not evidence of model performance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
