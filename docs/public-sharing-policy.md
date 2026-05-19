---
type: public-sharing-policy
status: draft
version: 0.1
created: 2026-05-18
---

# Public Sharing Policy

## Policy Goal

Open source the AI FOMO mechanism without exposing private workspace data, credentials, copyrighted source material, or personal alignment context.

The public artifact should teach others how to build their own Personal Alignment Layer. It should not publish the original private one.

## Safe To Share

These are safe by default:

- skill instructions that describe workflows and decision rules
- empty starter workspace directories
- templates for `self-context`, `raw`, `wiki`, `signals`, and `digests`
- synthetic examples written specifically for the public repo
- rubrics for judging AI information value
- promotion rules for `source-summary -> theme/dossier`
- generic connector patterns and `.env.example`
- tests that use mock data
- diagrams and documentation explaining the mechanism

Generated raw outputs are not safe by default. Treat them as local evidence, not public examples.

## Share Only After Review

These require manual review:

- excerpts from public articles
- screenshots or transcripts
- source summaries based on third-party material
- examples derived from real private notes
- source registry examples that mention real accounts or workspaces
- personal anecdotes that could reveal private work, clients, collaborators, or business strategy

Review questions:

- does this reveal a private preference, source, credential, workspace path, or business context?
- does this copy third-party content beyond fair use or license limits?
- could this let someone reconstruct a private document or source list?
- is this necessary to explain the mechanism, or can a synthetic example work?

## Never Share

These must not be included in the public repo:

- `.env`, `.env.local`, `.secrets/`, cookies, tokens, credentials, API keys
- real `self-context` files
- real feedback logs
- real raw snapshots from private ingestion
- real podcast transcripts unless explicitly licensed for redistribution
- real Feishu, Notion, or internal workspace content
- real source state files containing account IDs, cursors, or collection history
- private wiki source summaries
- private signals or digests
- local cache files, binaries, virtual environments, or tool state

## Public Example Rules

Use three classes of public examples:

1. synthetic high-signal source
2. synthetic low-signal hype source
3. synthetic source that updates an existing theme

Each example should test whether the skill makes a judgment, not whether it can produce a polished summary.

Examples should include:

- input source text or metadata
- expected judgment
- whether it should be filed
- expected target layer, if any
- explanation of why

Examples should not include:

- copied article bodies
- real private names
- real private source URLs
- raw transcript blocks
- generated connector outputs from real websites or accounts unless fully reviewed and redistribution is permitted

## Credential Policy

Public connector docs may reference environment variables, but never real values.

Allowed:

```text
X_BEARER_TOKEN=
DASHSCOPE_API_KEY=
FEISHU_USER_ACCESS_TOKEN=
```

Not allowed:

- any non-empty token, key, cookie, or credential value in a committed file
- any screenshot or log output that reveals a token, key, cookie, or credential value

Credential files should be ignored by default:

```text
.env
.env.*
.secrets/
*.token
*.cookie
```

If any credential has ever been committed to a repo that may become public, rotate it before publication.

## Git History Policy

Do not make the current private workspace public by flipping repository visibility.

Recommended path:

1. create a fresh public repository
2. copy only reviewed public files
3. start with a clean Git history
4. rotate credentials that were ever committed privately
5. run secret scanning before first public push

This avoids leaking deleted files through Git history.

## Naming Policy

Recommended public project name:

```text
AI FOMO Skills
```

Recommended tagline:

```text
Personal superalignment skills for turning AI information overload into reusable knowledge, signals, and digests.
```

Use "personal superalignment" carefully:

- it means aligning an agent to an individual user's goals, preferences, and judgment standards
- it does not claim to solve model-level alignment or AI safety superalignment

## License Policy

Default recommendation:

- MIT if the goal is adoption and remixing
- Apache-2.0 if patent language matters

Do not include third-party examples unless their license permits redistribution.

## Release Checklist

Before creating the public repo:

- no real `self-context`
- no real `raw/inbox`
- no real `raw/state`
- no real `wiki/sources`
- no real `signals` or `digests`
- no `.env*` or `.secrets`
- no private source registry entries
- no copied third-party transcripts
- no generated raw snapshots from real sources
- no local cache or binary files
- synthetic examples only
- fresh Git history
- license included
- skill metadata reviewed
