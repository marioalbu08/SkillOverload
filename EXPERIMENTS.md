# Experimental Protocol

**Status:** proposed protocol. No runs, registered study, or statistical findings are claimed. Freeze a versioned protocol before a confirmatory evaluation.

## 1. Scope and outcomes

Primary question: does expanded relevant skill text reduce task success compared with concise relevant skill text under a specified model and harness?

Primary outcome: binary task success determined by an independent verifier of the final artifact or environment state. All conditions must have access to the same necessary task facts and equivalent executable capabilities.

Secondary questions examine metadata selection, irrelevant activation, evidence position, conflicting instructions, unsupported claims, and compaction. Predeclare which comparisons are confirmatory and which are exploratory.

## 2. Two complementary tracks

**Controlled context track:** construct model inputs with known content, lengths, and evidence offsets. This isolates interventions but does not reproduce every native skill implementation.

**Native agent track:** run an actual skill-supporting harness with metadata discovery and on-demand reading. This tests practical relevance. Capture loaded files and context transformations where observable. Do not infer an unavailable final prompt from a list of installed files.

Run them separately and label their results separately.

## 3. Tasks

The included version 0.1 pilot covers one narrow family: closed-world fact extraction from fictional API documents, using 12 hand-written cases with current and archived values. It is a public development set. It is not held out from skill authors and is not suitable for confirmatory claims.

The planned extension includes three bounded families:

| Family | Example | Independent outcome check |
| --- | --- | --- |
| Evidence retrieval | Identify the active API version and a specific exception | Exact answer against an authoritative manifest |
| Small repository change | Adapt a caller to a documented API with renamed arguments | Hidden behavioral tests and prohibited-change checks |
| Tool workflow | Update a simulated record under a current policy | Final database state and action log |

Include resolvable tasks and tasks missing a necessary fact. The latter require explicit uncertainty or a prescribed information request. Make correctness rules unambiguous; human policy and instruction priority are fixed across conditions.

Publish task-family definitions. Keep confirmatory instances, answer manifests, and tests inaccessible to prompt writers until evaluation ends. Use held-out repositories or independently authored task instances, not merely renaming development examples. Public release does not make future reuse uncontaminated; version and refresh held-out sets.

## 4. Treatment conditions

| ID | Condition | Role |
| --- | --- | --- |
| A | No optional skills | Measures whether skills help relative to baseline |
| B | Concise relevant skill | Positive reference for focused guidance |
| C | Expanded relevant skill with the same required guidance | Primary contrast with B |
| D | B plus length-matched unrelated background text | Helps interpret generic length effects |
| E | B plus irrelevant skill instructions | Tests added instruction interference |
| F | Relevant skills loaded on demand | Tests a realistic delivery policy |
| G | Stale version of B, with matched structure and approximate length | Tests content errors separately from volume |

A retains essential user requests and mandatory policy. For instruction-only experiments, all arms retain equivalent tools. Test script-backed skills in a separate capability study.

Do not call D neutral: filler can itself affect the model. Build several distractor variants and record their contents.

## 5. Isolate the mechanisms

**Length:** compare B and C at the same evidence placement and output budget. Describe how expansion was written and verify that it adds no necessary task knowledge. Test several lengths within supported input budgets.

**Position:** at fixed content and token length, place the same necessary evidence block near the beginning, middle, or end of a controlled document region. Reorder existing blocks rather than adding new text. Measure actual tokenizer offsets. Keep instruction roles fixed; moving content across system/user roles changes authority as well as position.

**Selection:** vary only the discoverable metadata catalog. Compare free selection with an externally selected correct skill using the same catalog and tools. Report irrelevant activation, missed activation, and selection time.

**Conflict:** replace an instruction with a stale equivalent while preserving total structure. The authoritative current source and correct resolution rule remain available. G is an intentionally adverse intervention, not an estimate of naturally occurring stale-skill prevalence.

**Compaction:** introduce a necessary fact early, then perform a fixed interaction sequence. Compare logged compaction with a matched policy preserving that fact. Fix the workload and distinguish pre-transformation errors from post-transformation errors. Unobservable compaction cannot support a mechanistic finding.

The included pilot holds task text constant, but the longer skill adds prompt tokens before that text and therefore shifts evidence position. Its expansion comparison tests the combined intervention. A follow-up must vary skill length while also matching or independently controlling evidence positions before attributing any loss specifically to position or token count.

Do not exhaustively cross every factor in the first pilot. Choose a small primary contrast, then run focused follow-ups.

## 6. Execution and reproducibility

1. Freeze tasks, skill files, graders, conditions, and analysis rules with content hashes.
2. Verify that reference solutions pass and representative incorrect solutions fail.
3. Create a fresh isolated environment for every trial; reset filesystem, databases, memory, and conversation state.
4. Randomize condition order within tasks. Use identical task instances across matched conditions.
5. Pin model identifiers and harness revisions; record sampling, reasoning, tool, and resource settings.
6. Use equal predeclared output, time, and tool budgets for the primary controlled comparison. Treat input length as an intervention. Report timeout rates, not just completed runs.
7. Log outputs, tool calls, loaded resources, usage, errors, compaction events, and final environment state.
8. Grade without exposing answers to the evaluated agent. Review ambiguous factual claims with a condition-blinded human rubric.
9. Include failed attempts in the release. Retry transport failures only under a frozen rule, retaining all attempts and incurred usage.

Seeds control generated tasks and randomization. They do not guarantee identical provider outputs or deterministic inference.

## 7. Metrics

| Metric | Definition |
| --- | --- |
| Task success | Successful independent outcome checks / all assigned trials |
| Unsupported-claim run rate | Trials with at least one adjudicated unsupported factual claim / all assigned trials |
| Claim-level unsupported rate | Unsupported factual claims / all adjudicated factual claims; report claim counts |
| Appropriate abstention | Correct uncertainty responses / tasks defined as missing necessary information |
| Evidence accuracy | Correct required facts recovered / required facts, evaluated independently |
| Skill selection errors | Irrelevant activations and missed needed activations, reported separately |
| Token burden | Metadata, body, resource/output, and total trajectory tokens without double counting |
| Latency | Median and upper quantiles of wall time, with timeout incidence |
| Cost per successful task | Total cost of assigned trials / successful trials; undefined when none succeed |
| Transformation loss | Necessary facts absent after an observable context transformation |

Also report API/environment failure rates and quality outcomes conditional on valid execution. Do not silently drop infrastructure failures from end-to-end success. Avoid relying on claim rate alone: a terse or silent agent could improve that denominator while failing the task.

## 8. Analysis and trial budgets

For task i and condition c, estimate success probability with repeated fresh trials. The primary difference is:

```text
Delta = mean across held-out tasks of [success(C) - success(B)]
```

Negative Delta indicates average harm from expansion in this comparison. Separately report B versus A so harm from expansion is not confused with harm from all skills.

Bootstrap matched task differences at the task level, or at the repository level when tasks share a repository. Keep repeats within their task clusters. Report a 95% confidence interval, effect size, task counts, and repeated-trial counts. Model/harness results remain separate unless a pooled analysis is justified in advance.

Pass@k rewards success in at least one attempt; it is not the primary reliability metric. Report per-attempt success and repeated-run variability.

A larger feasibility pilot would use 12 tasks, three conditions A/B/C, three repeats, and one model-harness pair: **108 trajectories**. The included CLI defaults to one repeat (36 live calls), requires an explicit call cap above 36, and limits each invocation to 108 calls. This is not proof of general skill harm. Bound tokens, steps, and time per trajectory before launch. Pilot variability informs a subsequent power calculation, task sample size, and smallest practically meaningful effect. Do not reuse these public pilot tasks as the confirmatory holdout.

The included runner sends each live trial as a fresh [OpenAI Responses API](https://developers.openai.com/api/docs/guides/structured-outputs) request, disables response storage, and asks for a strict JSON schema. Its common instruction and fictional task files are held constant while the optional developer skill message varies. Exact input and output token counts come from the returned usage fields. The deterministic fixture provider returns the answer key by design to check request ordering, report writing, and grading only. Fixture scores must never be included in model-performance tables.

Publish null and positive effects. Correct for multiple confirmatory comparisons or explicitly limit inference to one primary comparison. Avoid selecting a harmful subgroup after seeing outcomes and presenting it as preregistered.

## 9. Allowed conclusions

- A positional difference supports positional sensitivity in the tested setting.
- C worse than B supports harm from the defined expansion, not a universal token threshold.
- E worse than D suggests added instruction content matters beyond these particular length controls.
- G worse than B supports harm from stale guidance, not proof of attention dilution.
- More unsupported claims supports an observed claim-rate difference; a neural mechanism needs separate evidence.
- F matching or exceeding B despite many installed skills weakens the claim that installed skill count inherently causes degradation.

All claims must name the task population, model, harness, intervention, and uncertainty.
