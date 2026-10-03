# When Skills Hurt: Context Costs in Skill-Augmented AI Agents

Version: research note 0.1, October 3, 2026.

**Evidence status:** literature review and falsifiable hypotheses. Original empirical findings: none. The experimental protocol is proposed, not executed or externally preregistered.

## Abstract

Skills package procedural knowledge, instructions, and resources for AI agents. They can improve task execution, but their delivery also changes the information an agent must select, interpret, and retain. This note examines conditions under which skill augmentation could reduce reliability: irrelevant activation, unnecessary instruction volume, unfavorable placement of necessary evidence, contradictory guidance, and premature context compaction. We distinguish these hypotheses from established long-context observations and from claims about hallucination. Existing positive results for curated skills preclude a universal conclusion that skills are harmful. We propose controlled experiments that measure task outcomes and unsupported factual claims while independently varying loading policy, length, position, and content quality.

## 1. The thesis

The useful question is not whether skills are good or bad as a category. It is whether a particular configuration adds enough useful guidance to justify its context and execution costs.

**Hypothesis:** an agent can perform worse after skill augmentation when the added material or the loading policy interferes with selecting and using the evidence needed for its task.

This has observable consequences. The agent might select an irrelevant workflow, miss a current requirement, execute an obsolete procedure, or describe facts that the task environment does not support. These consequences do not necessarily share one cause.

We use *skill-induced degradation* to mean a decrease in measured reliability relative to a matched baseline under a specified skill intervention. It is an outcome definition, not a diagnosis of the underlying neural mechanism.

## 2. Skills are a delivery system, not just a pile of text

The [Agent Skills specification](https://agentskills.io/specification) distinguishes discovery metadata, activated instructions, and supporting resources. Scripts and tools may perform work without requiring all implementation details to appear in the model's prompt.

Consequently, record four different quantities: installed skills, exposed metadata tokens, activated instruction tokens, and returned resource/tool-output tokens. Actual context use depends on the harness. A directory on disk is not automatically text in the model's input.

An instruction-only comparison also cannot establish the value of script-backed skills. Giving one condition a useful executable capability and withholding it from another confounds instructions with tool access.

## 3. Evidence and boundaries

### Positional sensitivity

[Liu et al.](https://arxiv.org/abs/2307.03172v3) find that moving relevant information changes performance on multi-document question answering and key-value retrieval, with middle positions often worse in the evaluated settings. This motivates a placement experiment; it does not prove that every modern model, task, or agent exhibits the same curve.

### Length and distractors

[Chroma's Context Rot](https://www.trychroma.com/research/context-rot) reports performance changes across input lengths and distractor conditions. Its specific NIAH extension found no notable position effect. Therefore, deterioration with longer prompts is not sufficient evidence of Lost in the Middle.

[RULER](https://arxiv.org/abs/2404.06654v3) evaluates retrieval, tracing, and aggregation beyond simple needle retrieval. Its findings motivate treating usable context as task dependent rather than assuming an advertised maximum guarantees reliable use of every supplied token.

### Evidence that skills help

[SkillsBench v4](https://arxiv.org/abs/2602.12670v4) evaluates 87 tasks across eight domains and 18 model-harness configurations. Its aggregate pass rate increases from 33.9% without skills to 50.5% with curated skills. It also reports stronger performance from focused bundles than larger or exhaustive ones. Those comparisons do not, by themselves, identify context length as the causal mechanism.

### Implementation guidance

[OpenAI's September 2026 guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) describes long or contradictory descriptions, excessive activation, and overly specific workflows as concerns for Codex. This is practitioner guidance for a named product/model setting, not a controlled estimate of general skill harm.

## 4. Five proposed failure pathways

These are hypotheses to distinguish experimentally. They are not established findings of this project.

### 4.1 Selection overhead

Many similar descriptions could make the correct skill harder to select. A broad trigger might cause an agent to load migration guidance for an unrelated database question.

Prediction: irrelevant activations increase when overlapping descriptions are introduced, even if body loading is otherwise held constant. Compare actual selection with an externally chosen relevant skill to isolate selection from execution.

### 4.2 Unnecessary instruction volume

A relevant instruction may be surrounded by examples and procedures that do not apply. This could increase reading work and reduce successful use of other task information.

Prediction: an expanded skill performs worse than a concise version that contains the same necessary guidance. A separate, length-matched background-text control helps distinguish instruction interference from a generic length effect. Neither control is assumed to be cognitively neutral.

### 4.3 Placement of evidence

Loading a skill changes the assembled prompt. Necessary facts might move away from a favored position. Repeated reads could also separate facts that need to be combined.

Prediction: at fixed total length and content, moving necessary evidence changes outcomes. This supports behavioral positional sensitivity; it does not reveal internal attention weights or prove that an agent literally forgot the fact.

### 4.4 Stale or conflicting procedures

An obsolete skill might name a removed API or prescribe an old architecture. An agent could follow it despite accessible current evidence.

Prediction: a stale condition causes more obsolete actions than an updated, equally structured condition. If repairing the stale instruction fixes performance without reducing length, content quality is a stronger explanation than length alone.

Specify the correct authority ordering before testing. Failure to obey an outdated skill is sometimes correct behavior, not a skill-use failure.

### 4.5 Eviction and compaction

Additional material could bring a conversation to a harness threshold sooner. The harness may then omit, truncate, or summarize earlier information.

Prediction: failures occur after logged context transformations that remove a necessary fact, and preservation of that fact improves outcomes. If the harness hides its assembled prompt or compaction events, this pathway must remain unverified.

## 5. Context capacity is not a theorem of inevitable harm

Let C be the usable input capacity after any applicable output reservation, and let I_t be the assembled input at step t. Partition I_t into disjoint counted components:

```text
I_t = fixed instructions + task evidence + skill metadata
    + activated skill bodies + retained history and tool outputs
```

Provider accounting determines which items consume the relevant budget. Avoid double-counting a skill body that is already part of retained tool history. When I_t exceeds C, the provider may reject the input or the harness may transform it. Record what actually happens.

The inequality I_t <= C establishes budget compliance, not correct use of the content. Conversely, staying below C does not guarantee a performance decrease as I_t grows.

For one query in one attention head, softmax weights sum to one. This normalization does not imply uniform weights, a fixed share for a middle token, or a universal U-shaped accuracy curve. Attention is content dependent, and behavior also depends on layers, heads, training, and the rest of the architecture. We do not derive numerical failure rates from token count or equate an attention weight with task accuracy.

## 6. Hallucination needs its own measurement

A missed instruction, failed build, or wrong tool call is not automatically a hallucination.

For this project's bounded tasks, an *unsupported factual claim* is an asserted fact that is false or ungrounded relative to the supplied authoritative environment. Examples include inventing an endpoint, claiming an absent dependency is installed, or asserting that a test ran without an execution record.

Use tasks with checkable answers and deliberately missing information. Track correct answers, wrong factual claims, and appropriate abstentions separately. Only call a claim unsupported when the environment and adjudication rule justify that label. Silence and an explicit admission of uncertainty must not be scored as factual fabrication.

The proposed pathway is: an intervention changes evidence access or instruction following, and unsupported claims become more frequent. Observing both events is suggestive, but attributing the second to the first requires further interventions. A positional retrieval study alone does not prove this causal chain.

## 7. What would change our mind?

Evidence against the harm hypothesis includes unchanged or improved outcomes under realistic added skill load, no position effect in the tested tasks, or reliable selective loading that keeps irrelevant bodies out of context.

If only intentionally false skills cause failures, the conclusion concerns misleading guidance. If only forced eager loading causes failures, the conclusion concerns that loading policy. If curated skills help overall while one subset worsens, report both results and identify the subset without claiming a universal reversal.

The proposed contribution is a method for identifying these boundaries. Novelty remains to be assessed against existing skill benchmarks and long-context research.

## 8. Practical implications to test

Evaluate concise triggers, selective reference loading, versioned guidance, preservation of critical facts through compaction, and moving deterministic work into scripts. Treat each as a candidate mitigation with a cost and a failure mode; none is guaranteed to solve context degradation.

Before recommending a mitigation, compare task success, unsupported claims, latency, and total tokens over the complete trajectory. A shorter first prompt can lead to additional retrieval calls and higher total cost.

