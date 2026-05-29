# Synthetic Examples

These examples are fictional. They exist to calibrate judgment behavior, not to document real AI news.

## Example 1: High-Signal Changelog

### Input

`ModelHost` announces cache-aware tool-call traces. The release explains how each tool call now records cache hit rate, replay cost, failed argument repair, and downstream latency impact. The changelog includes migration notes and a before/after evaluation showing that teams can replay failed agent runs without re-querying the model.

### Expected Judgment

Write now.

### Why

This changes how agent systems can be evaluated and debugged. It exposes a reusable mechanism: replayable tool-call traces with cache and latency attribution.

### Filing

- Write `wiki/sources/modelhost-cache-aware-tool-call-traces.md`.
- Check existing themes related to agent evaluation, observability, or cost control.
- Do not create a dossier unless `ModelHost` is already a tracked entity or the user wants to track it.

## Example 2: Low-Signal Hype Article

### Input

An article titled "12 AI Tools That Will 100x Your Productivity This Week" lists popular tools with short descriptions, affiliate links, and broad claims. It does not explain workflows, constraints, evaluation methods, or why the tools work.

### Expected Judgment

Skip.

### Why

The content is novelty and social proof without durable judgment. Filing it would add noise.

### Filing

No wiki page. Optionally explain in chat that the user can paste a specific tool or workflow if they want deeper evaluation.

## Example 3: Theme Update

### Input

`LoopAgent Lab` publishes a technical note on agent memory failures. It shows that long-term memory quality improved only after the team separated user preferences, task state, source evidence, and failed attempts into different stores. A single vector index caused retrieval collisions and repeated stale instructions.

### Expected Judgment

Write now.

### Why

This provides a reusable architecture constraint: memory systems should separate durable preferences from task state and source evidence.

### Filing

- Write a source summary.
- Update an existing memory architecture theme if present.
- Propose a new theme only if no broad memory theme exists and the user's workspace repeatedly discusses this pattern.

## Example 4: Useful But Uncertain

### Input

`PromptBench Studio` publishes a short case note claiming that a new prompt review checklist reduced evaluation failures for customer support agents. The note includes three checklist items and one chart, but does not describe the dataset, baseline, or failure definitions.

### Expected Judgment

Ask first.

### Why

The topic may be relevant if the user tracks agent evaluation or customer support workflows, but the evidence is too thin for automatic filing. It may be useful as a lightweight lead, not a durable source summary.

### Filing

- Do not write to `wiki/sources` without confirmation.
- Ask whether the user wants to track prompt review workflows.
- If confirmed, file as a cautious source summary and mark evidence limitations clearly.

## Example 5: Podcast Learning Note

### Input

A fictional 65-minute podcast episode features the founder of `ThreadAgent`, a startup building agents for team workspaces. Show notes include timestamps for:

- 00:00 founder background
- 08:00 why session-based chat agents fail in team work
- 18:00 how persistent project threads changed user behavior
- 31:00 memory architecture and permission boundaries
- 46:00 fundraising and hiring stories
- 58:00 predictions about model companies

The user asks: "Can you make this a learning note so I do not need to listen to the full episode? Also tell me which parts are worth listening to."

### Expected Judgment

Write a podcast learning note.

### Why

The user is not only asking for a source judgment or wiki filing. They need a human-readable digest that supports three decisions: whether to continue, what the episode teaches, and which original segments are worth hearing.

### Filing

- Write `digests/podcasts/<date>-threadagent-persistent-project-threads.md`.
- Use `references/podcast-learning-note.md`.
- Recommend selected listening for 08:00-18:00 and 31:00-46:00.
- Skip or downrank founder background and fundraising unless the user's alignment layer says startup hiring/fundraising is important.
- Do not write `wiki/sources` unless the user also asks to retain it as long-term knowledge or the episode contains durable, high-relevance claims.
