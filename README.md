# SkillOverload

**Investigating the context cost of agent skills: unnecessary loading, misplaced evidence, conflicting instructions, and unsupported claims.**

Research note: **When Skills Hurt: Context Costs in Skill-Augmented AI Agents**.

Status: **literature-backed research note and proposed experimental protocol. No original model evaluation has been completed in this repository.**

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

The proposed tests compare no optional skills, concise relevant skills, expanded skills, irrelevant skills, and skills loaded on demand. Independent outcome checks and repeated trials are required; an agent's confident explanation is not a success criterion.

## Read the research

- [Research note](RESEARCH.md): evidence, proposed mechanisms, and limits.
- [Experimental protocol](EXPERIMENTS.md): controls, measurements, and reporting rules.
- [Source register](SOURCES.md): primary sources and the claims they support.
- [Illustrative failure case](examples/FAILURE_CASE.md): a concrete task that separates incorrect actions from unsupported claims.
- [Results status](results/README.md): what has and has not been measured.

## Research integrity

This release contains no runnable evaluation harness, leaderboard, or claimed performance improvement. There are no simulated curves presented as model measurements. Future releases must publish beneficial, harmful, and inconclusive outcomes with the same visibility.

Research scope: inference-time instructions and agent harness behavior. Installing a skill does not itself retrain model weights. Any observed result applies to the tested model, harness, tasks, and loading policy.
