---
name: ai-fomo
description: Judge, summarize, create podcast learning notes, and file AI-related information through the user's Personal Alignment Layer. Use when the user sends AI articles, changelogs, docs, X threads, GitHub repos, videos, podcasts, podcast transcripts, raw notes, asks whether AI content is worth reading or listening to, asks for a learning note that can replace listening to a podcast, asks what podcast segments are worth hearing, asks whether content should be kept or should go into wiki, should become a signal, or should update long-term preferences.
---

# AI FOMO

## Purpose

Turn AI information overload into personally aligned judgment. This skill should produce a decision, not just a summary.

## Use When

Use this skill when the user:

- sends AI-related content or a link
- points to `raw/inbox/`
- asks whether something is worth reading
- asks whether a podcast or video is worth listening to
- asks for a summary plus recommendation
- asks for a podcast learning note that can replace listening to the full episode
- asks whether something should go into wiki
- asks for signals or a digest from retained material
- gives feedback on filtering or summarization behavior

## Do Not Use When

Do not use this skill for:

- initializing a new workspace; use `ai-fomo-init`
- connecting source APIs or feed collectors; use `ai-fomo-sources`
- non-AI content with no relation to the user's alignment layer
- generic summarization without value judgment

## Required Context

Before judging material, read:

1. `self-context/index.md` if it exists
2. relevant `self-context/preferences/*` files when needed
3. `wiki/index.md` when existing knowledge may already cover the topic

If the Personal Alignment Layer is missing or too vague, ask for minimal clarification or recommend running `ai-fomo-init`.

## Core Workflow

1. Read the source content directly or read the provided raw snapshot.
2. Read the Personal Alignment Layer.
3. Use `references/alignment-rubric.md` for value judgment.
4. Reply in chat with a complete but concise summary.
5. Make a three-tier recommendation:
   - write now: high quality, high relevance, durable judgment
   - ask first: useful but uncertain
   - skip: weak, generic, hype-heavy, or low relevance
6. If writing files, use `references/filing-rules.md`.
7. Always write or update `wiki/sources` before checking `themes` or `dossiers`.
8. Prefer updating existing `themes` or `dossiers` over creating new pages.
9. Only write `signals` or `digests` when the user asks or when the workflow explicitly calls for it.
10. Record feedback as long-term preference only when the user indicates it should persist.

## Podcast Learning Note Mode

Use this mode when the source is a podcast episode, video transcript, or long-form interview and the user wants to learn without listening end to end.

Before writing the note, read `references/podcast-learning-note.md`. Use `assets/podcast-learning-note.template.md` as the scaffold when creating a Markdown file.

Default output target:

`digests/podcasts/YYYY-MM-DD-short-slug.md`

The note must answer three decisions:

1. What is this episode about, and is it worth continuing?
2. If continuing, what does the full episode cover in a readable learning structure?
3. If listening to the original, which segments are worth hearing and which can be skipped?

Keep podcast learning notes separate from durable source summaries. Use `digests/podcasts/` for human-readable learning notes and `wiki/sources/` for retained long-term knowledge.

## Default Chat Output

For each source, include:

- what it is about
- main structure or claims
- durable mechanisms, constraints, or tradeoffs
- why it matters or does not matter for this user
- recommendation: write now, ask first, or skip
- proposed filing target when relevant

## Judgment Rules

- Novelty is not importance.
- Hype is not signal.
- Long content is not automatically worth filing.
- Long audio is not automatically worth listening to end to end.
- Good filing candidates change product, system, market, evaluation, or workflow judgment.
- If a source mainly reinforces an existing theme, update that theme rather than creating a new one.
- Do not create a new theme for a one-off concept.
- For podcasts, distinguish "worth reading the learning note", "worth selected listening", and "worth full listening".

## References

- Use `references/alignment-rubric.md` for judging value.
- Use `references/filing-rules.md` before writing workspace files.
- Use `references/podcast-learning-note.md` before writing podcast learning notes.
- Use `references/examples.md` for calibration or testing.
