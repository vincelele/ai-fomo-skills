---
type: public-skill-boundaries
status: draft
version: 0.1
created: 2026-05-18
---

# Public Skill Boundaries

## Boundary Principle

Split the system by trigger and risk:

- `ai-fomo-init` handles alignment setup.
- `ai-fomo-sources` handles source intake.
- `ai-fomo` handles judgment and knowledge work.

The skills should interoperate, but each one should have a hard contract. This prevents the system from becoming a vague "summarize everything" workflow.

## Skill 1: `ai-fomo-init`

### Purpose

Create a local Personal Alignment Layer and starter workspace for AI information judgment.

### Trigger

Use when the user says they want to:

- set up AI FOMO
- initialize a personal AI alignment workspace
- create a source intelligence workspace
- configure what AI content is worth their attention
- build a personal anti-FOMO system

### Inputs

- target workspace path
- user-provided profile brief such as resume, bio, project history, portfolio notes, or free-form context
- optional long-term themes
- optional source preferences
- optional examples of valuable and low-value AI content

### Outputs

- starter directory structure
- empty or lightly guided `self-context` files
- starter `raw/`, `wiki/`, `signals/`, and `digests/` templates
- a first-pass alignment contract for the user to review

### Required Behavior

- First invite the user to provide a profile brief.
- Extract a tentative alignment map from that brief.
- Then ask targeted QA to fill gaps that matter for filtering and judgment.
- Ask for missing long-term context only when needed.
- Prefer placeholders over strong guesses.
- Mark uncertain profile claims as draft or pending confirmation.
- Keep initialization separate from source processing.
- Create a workspace that can be used by `ai-fomo` without private assumptions.

### Must Not Do

- Do not ingest external sources.
- Do not summarize articles or podcasts.
- Do not create a detailed personal profile from weak inference.
- Do not turn resume details into public examples or templates.
- Do not write credentials or private tokens into templates.
- Do not assume the user's interests match the original author's interests.

### Minimal Contract

`ai-fomo-init` ends when the workspace can answer:

- who is this agent serving?
- what themes matter?
- what content should be downranked?
- what does "high signal" mean for this user?
- where should raw input, knowledge, signals, digests, and feedback go?
- which profile-derived assumptions still need confirmation?

## Skill 2: `ai-fomo-sources`

### Purpose

Connect or configure source intake so AI-related material can enter the raw layer with traceability.

The skill should lower source onboarding friction by directly importing common sources where possible, then falling back to a manual raw snapshot only when direct import is unavailable.

### Trigger

Use when the user says they want to:

- connect sources
- add a Feishu, Notion, GitHub, X, RSS, YouTube, podcast, changelog, or web source
- collect new source material
- create raw snapshots
- configure source registry or source state

### Inputs

- target workspace path
- source URL, account, feed, list, or config
- optional authentication method
- optional collection frequency
- optional dedupe and state preferences

### Outputs

- source configuration
- raw snapshots in `raw/inbox/`
- source state when needed
- clear notes about credentials and privacy boundaries

### Required Behavior

- Use the direct import runtime for supported source types.
- Treat `raw/` as the only default write target for collected source material.
- Keep raw snapshots traceable to the original source.
- Store credentials outside the public workspace or in ignored local files.
- Prefer dry-run or preview mode before writing bulk data.
- Preserve source metadata: URL, title, source type, collected time, published time when known.

### Must Not Do

- Do not judge whether the source is worth keeping long-term.
- Do not write `wiki/sources`, `themes`, `dossiers`, `signals`, or `digests`.
- Do not put tokens, cookies, or API keys into committed files.
- Do not bypass copyright boundaries by storing full third-party content when not permitted.
- Do not overwrite existing source state without an explicit reason.
- Do not block intake just because a direct importer is unavailable.

### Minimal Contract

`ai-fomo-sources` ends when the workspace has traceable raw material that `ai-fomo` can judge later.

If direct import is unavailable, it should end with a manual raw snapshot or an explicit next step.

## Skill 3: `ai-fomo`

### Purpose

Apply the Personal Alignment Layer to AI-related material and decide what should be summarized, skipped, filed, promoted, or turned into signals and digests.

### Trigger

Use when the user:

- sends AI-related content
- asks whether something is worth reading
- asks to summarize and judge a source
- asks whether content should go into wiki
- asks whether a podcast or video is worth listening to
- asks for a podcast learning note that can replace listening to the full episode
- asks for signals from a batch of raw material
- asks for a digest based on retained knowledge
- gives feedback on filtering or summarization behavior

### Inputs

- pasted content, URL, or `raw/inbox` path
- existing workspace context
- `self-context` alignment files
- existing `wiki/index.md` and relevant wiki pages when needed
- optional user instruction about whether to write files

### Outputs

- chat summary and judgment
- recommendation: write now, ask first, or skip
- optional `wiki/sources` page
- optional updates to existing `themes` or `dossiers`
- optional signal or digest when requested
- optional podcast learning note in `digests/podcasts`
- optional feedback-log entry or preference update

### Required Behavior

- Read the Personal Alignment Layer before making relevance judgments.
- Provide a useful chat summary before filing.
- Use a three-tier judgment:
  - high quality and high relevance: write to `wiki/sources`
  - useful but uncertain: ask before filing
  - weak, generic, or low relevance: skip
- Always write or update `wiki/sources` before second-layer promotion.
- Prefer updating existing `themes` or `dossiers` over creating new ones.
- For podcast learning notes, distinguish the human-readable digest from durable wiki filing.
- Always include an original listening recommendation when the user asks whether a podcast is worth hearing.
- Treat user feedback as persistent only when the user indicates it should persist.

### Must Not Do

- Do not summarize everything by default.
- Do not treat novelty as importance.
- Do not file weak material just because it is AI-related.
- Do not create narrow one-off theme pages.
- Do not convert raw transcripts into wiki pages without judgment.
- Do not treat podcast learning notes as source-of-truth knowledge pages.
- Do not update long-term preferences from one-off instructions.
- Do not perform complex source collection; hand that to `ai-fomo-sources`.

### Minimal Contract

`ai-fomo` ends with a judgment, not just a summary.

For every source, it should answer:

- what is this about?
- what are the durable claims or mechanisms?
- why might this matter to this user?
- should it be filed, skipped, or reviewed first?
- does it update an existing theme or dossier?

For podcast learning requests, it should also answer:

- can the learning note replace listening to the full episode?
- which original segments, if any, are worth hearing?
- which sections can be skipped?

## Inter-Skill Handoff

### Init To Sources

`ai-fomo-init` creates the workspace and alignment files. `ai-fomo-sources` then uses the workspace path and writes only to `raw/` unless the user explicitly asks otherwise.

### Sources To Main Skill

`ai-fomo-sources` creates raw snapshots. `ai-fomo` reads those snapshots and decides whether they deserve knowledge work.

### Main Skill To Init

If `ai-fomo` finds the Personal Alignment Layer missing or too vague, it should recommend running `ai-fomo-init` or ask for a minimal clarification.

### Main Skill To Sources

If the user provides a source link that requires authentication, transcript generation, feed setup, or repeated collection, `ai-fomo` should hand off to `ai-fomo-sources`.

## Common Boundary Failures

### Failure: Source Intake Becomes Judgment

Bad behavior:

- a connector writes directly into `wiki/`
- a crawler labels sources as high-value without reading user context

Correct behavior:

- connectors write raw snapshots only
- `ai-fomo` performs judgment later

### Failure: Main Skill Becomes A Generic Summarizer

Bad behavior:

- every article gets a summary
- every summary gets filed

Correct behavior:

- each source receives a value judgment
- weak material is skipped explicitly

### Failure: Initialization Overfits The User

Bad behavior:

- `ai-fomo-init` invents a strong profile from a short prompt

Correct behavior:

- use placeholders and ask for confirmation
- keep uncertain claims in draft status

### Failure: Public Skill Leaks Private Assumptions

Bad behavior:

- templates include the original author's preferences, topics, or private source paths

Correct behavior:

- templates are empty or generic
- examples are synthetic or explicitly licensed
