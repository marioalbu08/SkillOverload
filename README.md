# SkillOverload

**Investigating the context cost of agent skills: unnecessary loading, misplaced evidence, conflicting instructions, and unsupported claims.**

Research note: **When Skills Hurt: Context Costs in Skill-Augmented AI Agents**.

Status: **literature-backed research note and runnable exploratory pilot. No original live model evaluation has been completed in this repository.**

## The question

Can adding skills make an AI agent less reliable, even when its prompt remains within the advertised context window?

Our hypothesis is conditional: **skills can become harmful when their added guidance is less useful than the context, routing, and instruction costs they introduce.** A skill count alone does not measure that burden.

The [Agent Skills specification](https://agentskills.io/specification) describes progressive disclosure: metadata first, instructions on activation, supporting resources as needed. Installing twenty skills does not necessarily load twenty complete instruction sets.

## What the evidence says

- [Lost in the Middle](https://arxiv.org/abs/2307.03172v3) demonstrates positional sensitivity on particular long-context retrieval tasks. It does not establish that all skills cause this effect.
- [Context Rot](https://www.trychroma.com/research/context-rot) examines degradation as input length and distractors change. Length effects and position effects must be measured separately.
- [SkillsBench v4](https://arxiv.org/abs/2602.12670v4) reports that curated skills improve aggregate task success. This is important contrary evidence to a blanket anti-skills claim.
- [OpenAI's skill-writing guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) identifies description bloat, irrelevant activation, and overprescriptive workflows as practical concerns.

## What this project contributes

A protocol for testing **why a particular skill configuration helps or harms**. We separate:

1. Metadata and selection errors.
2. Added instruction length.
3. Placement of necessary task evidence.
4. Outdated or contradictory guidance.
5. Context eviction and compaction.
6. Unsupported factual claims, distinct from ordinary task failures.

The first runner is narrower: it compares no skill, a concise relevant skill, and an expanded version on 12 small fictional API extraction tasks. A deterministic fixture mode checks the execution and grading pipeline; only the OpenAI provider measures model behavior.

## Run the pilot

Fixture mode needs only Python 3.9 or newer and makes no API requests:

```bash
python pilot.py --provider fixture
```

It produces 36 known-answer fixture records and labels the report as a simulated pipeline check. **Those all-correct fixture records are not model results.**

For a live run, set `OPENAI_API_KEY` in the shell, choose a model available to your account, and explicitly provide its model name:

```bash
python pilot.py --provider openai --model YOUR_MODEL --repeats 1
```

This makes 36 API requests, may incur provider charges, and writes a trajectory report under `results/runs/`. Each request is one independently graded task-condition trial. The program never displays or stores your API key. Repeated runs are capped at three per task; the default request cap is 36 and the hard cap is 108. Raising `--max-calls` is required for runs above the default.

Each live API report records exact provider-reported input and output token counts. Estimated prompt tokens are recorded for readability and labeled as estimates. Fixture-mode token counts remain null. A task passes only when all six extracted values and all six citations match the hand-written answer key.

This pilot tests closed-world fact extraction with a public synthetic task suite. Wrong answers are a proxy for unsupported factual claims, not a direct measure of hidden reasoning or all forms of hallucination. Expanded instructions also move later evidence further into the prompt, so the first pilot cannot separate added length from changed evidence position. Results are exploratory and do not generalize beyond the tested tasks, model, and harness.

The proposed tests compare no optional skills, concise relevant skills, expanded skills, irrelevant skills, and skills loaded on demand. Independent outcome checks and repeated trials are required; an agent's confident explanation is not a success criterion.

## Read the research

- [Research note](RESEARCH.md): evidence, proposed mechanisms, and limits.
- [Experimental protocol](EXPERIMENTS.md): controls, measurements, and reporting rules.
- [Source register](SOURCES.md): primary sources and the claims they support.
- [Illustrative failure case](examples/FAILURE_CASE.md): a concrete task that separates incorrect actions from unsupported claims.
- [Results status](results/README.md): what has and has not been measured.

## Research integrity

This release contains a runnable pilot, but no measured live model results, leaderboard, or claimed performance improvement. Fixture output exists only to check the code path and is labeled as simulated. Future releases must publish beneficial, harmful, and inconclusive outcomes with the same visibility.

Research scope: inference-time instructions and agent harness behavior. Installing a skill does not itself retrain model weights. Any observed result applies to the tested model, harness, tasks, and loading policy.
