# SkillOverload

**Do the instructions we give AI agents make them better at the work, or can they get in the way?**

Skills are meant to help an agent do a job well. They can explain a workflow, provide domain knowledge, or remind an agent about a tool it would not otherwise use. But every instruction also competes for the agent’s attention. A skill can be irrelevant to the current task, repeat what the agent already knows, conflict with another instruction, or push useful evidence farther away in a long prompt.

SkillOverload is an independent research project about that tradeoff. We want to understand **when added context earns its place, when it becomes overhead, and how to tell the difference with evidence**.

## Why look at this?

As agent ecosystems grow, it becomes easier to add more context than a task needs: skills, tool descriptions, project rules, examples, memory, and retrieved documents. It is tempting to assume that more guidance must produce better work. It is also tempting to jump to the opposite conclusion and say that skills make agents worse.

Neither assumption is a useful starting point. Some research finds that carefully designed skills improve task performance. Other work shows that models can be sensitive to where information appears in a long context, and that adding irrelevant material can make some tasks harder. Those findings can both be true. The effect depends on the task, the instructions, the model, and how the agent loads and uses them.

The question we are investigating is narrower than “Are skills good or bad?” It is: **under what conditions does a skill help, and what costs or failure modes appear when it does not?**

## What we mean by “context cost”

Context cost is more than token count. Extra instructions may consume space, distract from task evidence, duplicate or contradict other guidance, or cause the wrong skill to be selected. A long instruction may still be valuable if it prevents expensive mistakes. A short instruction may still be harmful if it sends the agent down the wrong path.

So we are treating skill count and prompt length as things to measure, not as explanations by themselves. We want to separate several possible causes:

- A relevant skill gives the agent useful knowledge or a better procedure.
- An irrelevant skill adds distraction without helping the task.
- Longer instructions change where important evidence appears in the prompt.
- Conflicting or outdated instructions lead to the wrong action.
- A task fails for reasons unrelated to unsupported claims, so “accuracy” alone can hide what went wrong.

That distinction matters. If an agent gets a task wrong, we should be able to tell whether it missed a fact, cited the wrong source, followed a bad instruction, or simply failed for another reason.

## What we have so far

This repository contains a literature-backed research note, an experimental protocol, and a small exploratory pilot. The pilot compares three conditions on fictional API documentation tasks: no optional skill, a concise relevant skill, and a longer version of that skill. Each task has a hand-written answer key, including the expected citations.

The fixture mode checks that the runner and grader work as intended. It uses prewritten answers, so its perfect scores say nothing about how a model behaves. A live provider mode can run the same task-condition trials with a model and records the provider’s token counts and response data. **We have not published results from a live model evaluation yet.**

This is an early instrument for asking a research question, not a benchmark that can settle it today. The task set is small and synthetic. The expanded skill also changes the position of later evidence, so the pilot cannot yet tell whether an effect comes from instruction length, evidence placement, or both. We call the findings exploratory and will keep those limits visible as the work develops.

## What the research does not claim

We are not arguing that skills are inherently harmful, that a larger prompt always performs worse, or that the current pilot proves a general effect. Nor does this project treat every wrong answer as a hallucination. A failed answer can have many causes, and those causes need separate measurements.

There is already meaningful counterevidence to a blanket “skills hurt” story. For example, SkillsBench reports aggregate improvements from curated skills across its evaluated tasks. That makes the more careful question even more interesting: **what makes a skill useful in one setting and costly in another?**

## How we plan to test it

The pilot is a first step toward controlled comparisons. The broader protocol calls for testing relevant, irrelevant, expanded, contradictory, and on-demand skills while holding the task and model conditions steady. It also calls for repeated trials, independent grading, and reporting results that are beneficial, harmful, or inconclusive.

We want to measure task success and unsupported claims alongside the resources spent to get there: input and output tokens, latency, and repeatability across runs. Where possible, the task set should include examples the people designing the skill conditions did not use to tune them. That helps reduce the risk of building a skill that merely looks good on the examples we already know.

The goal is not to produce one score that ranks every skill. It is to build a clearer picture of the conditions under which skills improve an agent, have no measurable effect, or make the work worse.

## Explore the work

- [Research note](RESEARCH.md) reviews the evidence, possible mechanisms, and open questions.
- [Experimental protocol](EXPERIMENTS.md) describes the comparisons, controls, and measurements we propose.
- [Source register](SOURCES.md) lists the sources and the claims they support.
- [Illustrative failure case](examples/FAILURE_CASE.md) shows why an incorrect action and an unsupported factual claim should not be treated as the same outcome.
- [Results status](results/README.md) records what has and has not been measured.

## Try the pilot

To check the evaluation pipeline without making model requests, run:

```bash
python pilot.py --provider fixture
```

The fixture creates known-answer records to exercise the runner and grader. It is a pipeline check, not an AI evaluation.

For a live exploratory run, configure an OpenAI API key in your environment and choose a model available to your account:

```bash
python pilot.py --provider openai --model YOUR_MODEL --repeats 1
```

The default live run makes 36 requests and may incur API charges. It writes the run record under `results/runs/`. Read the [experimental protocol](EXPERIMENTS.md) before interpreting the output: the current tasks are synthetic, the set is public, and the results cannot yet support broad conclusions about agent skills.

## Sources that shaped the question

- [Lost in the Middle](https://arxiv.org/abs/2307.03172v3) studies how the position of relevant information can affect performance on specific long-context tasks.
- [Context Rot](https://www.trychroma.com/research/context-rot) examines how context length and distractors affect different tasks; length and position should not be conflated.
- [SkillsBench v4](https://arxiv.org/abs/2602.12670v4) reports that curated skills improved aggregate task success in its evaluation, an important counterpoint to claims that skills are generally harmful.
- [The Agent Skills specification](https://agentskills.io/specification) describes progressive disclosure, where skill metadata, instructions, and supporting resources can be loaded in stages.
- [OpenAI’s skill-writing guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) discusses practical issues such as bloated descriptions, irrelevant activation, and overprescriptive workflows.

SkillOverload studies inference-time instructions and agent behavior. Installing a skill does not retrain a model’s weights, and any result we report should be read in the context of the specific model, tasks, harness, and loading policy we tested.
