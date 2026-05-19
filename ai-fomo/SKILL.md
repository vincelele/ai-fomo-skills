---
name: ai-fomo
description: Judge, summarize, and file AI-related information through the user's Personal Alignment Layer. Use when the user sends AI articles, changelogs, docs, X threads, GitHub repos, videos, podcasts, raw notes, or asks whether AI content is worth reading, should be kept, should go into wiki, should become a signal, or should update long-term preferences.
---

# AI FOMO

## Purpose

Turn AI information overload into personally aligned judgment. This skill should produce a decision, not just a summary.

## Use When

Use this skill when the user:

- sends AI-related content or a link
- points to `raw/inbox/`
- asks whether something is worth reading
- asks for a summary plus recommendation
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
- Good filing candidates change product, system, market, evaluation, or workflow judgment.
- If a source mainly reinforces an existing theme, update that theme rather than creating a new one.
- Do not create a new theme for a one-off concept.

## References

- Use `references/alignment-rubric.md` for judging value.
- Use `references/filing-rules.md` before writing workspace files.
- Use `references/examples.md` for calibration or testing.

