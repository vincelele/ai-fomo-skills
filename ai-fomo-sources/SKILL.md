---
name: ai-fomo-sources
description: Configure AI information sources and collect traceable raw snapshots for an AI FOMO workspace. Use when the user wants to add feeds, docs, X accounts, GitHub repos, YouTube videos, podcasts, podcast comments, audio transcripts, changelogs, RSS sources, or other source connectors. This skill handles source intake only and should not judge or file knowledge.
---

# AI FOMO Sources

## Purpose

Connect AI-related information sources and write traceable raw snapshots into `raw/`. This skill handles intake only. It must not decide long-term value.

## Use When

Use this skill when the user asks to:

- connect a source
- configure source registry
- collect new source material
- create raw snapshots
- add Feishu, Notion, GitHub, X, RSS, YouTube, podcast, podcast comments, transcript, changelog, or web sources

## Do Not Use When

Do not use this skill to:

- judge whether a source is high value
- write `wiki/sources`
- update `themes` or `dossiers`
- generate signals or digests

Use `ai-fomo` for judgment after raw material exists.

## Core Workflow

1. Confirm the target AI FOMO workspace.
2. Identify the source type and required access method.
3. If the source is supported by `scripts/import_source.py`, directly import it.
4. Use `references/source-connectors.md` when connector-specific guidance is needed.
5. Prefer preview or dry-run before bulk writes.
6. Store credentials outside committed files.
7. Write source material only to `raw/inbox/` by default.
8. Preserve source metadata: URL, title, author, source type, published time, collected time, and dedupe key when known.
9. Report what was collected and what still needs authentication or manual review.

## Direct Import Runtime

Use `scripts/import_source.py` for supported sources:

```bash
python scripts/import_source.py --workspace /path/to/workspace official-page --url https://example.com/changelog
python scripts/import_source.py --workspace /path/to/workspace rss --url https://example.com/feed.xml
python scripts/import_source.py --workspace /path/to/workspace github-repo --repo owner/name
python scripts/import_source.py --workspace /path/to/workspace github-trending --language python --since daily --limit 10
python scripts/import_source.py --workspace /path/to/workspace xiaoyuzhou-episode --url https://www.xiaoyuzhoufm.com/episode/episode_id
python scripts/import_source.py --workspace /path/to/workspace x-user --handle OpenAI
```

Use `--dry-run` first when importing a new source. `x-user` requires an X API bearer token in `X_BEARER_TOKEN` or a custom env var.

For Xiaoyuzhou bridge install/start, account login, subscribed inbox batch import, episode comments, and audio transcription, use `scripts/xiaoyuzhou_account.py` and read `references/xiaoyuzhou-account.md`.

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --dry-run
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --start
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace bridge-status
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 30 --max-pages 3 --dry-run
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-comments --episode-id episode_id --include-replies --dry-run
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace transcribe-raw --raw-file /path/to/raw.md --dry-run
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --with-transcripts --transcript-limit 3 --dry-run
```

## Fallback Strategy

Direct import is the default. If a source is unsupported:

1. create a manual raw snapshot from user-provided content, export, notes, or URL metadata
2. add a registry entry only if the user explicitly wants to track the source long term
3. hand off to `ai-fomo` for judgment

Do not turn fallback setup into a long onboarding survey.

## Raw Snapshot Requirements

Each raw snapshot should be traceable and minimally structured:

- source name and source id
- source type
- original URL or stable reference
- title
- author or publisher when known
- published date when known
- collected timestamp
- content or excerpt permitted by the source boundary
- metadata needed for later judgment

## Credential Rules

- Use environment variables or ignored local files for credentials.
- Never commit tokens, cookies, or access keys.
- Create `.env.example` with empty variable names only.
- If a credential was committed, tell the user it must be rotated before public release.

## Handoff

After collection, tell the user that `ai-fomo` should be used to judge whether the raw material deserves knowledge work.

## References

- Use `references/source-connectors.md` for source-type recipes.
- Use `references/xiaoyuzhou-account.md` for Xiaoyuzhou bridge install, login, subscribed inbox import, comments, and transcription.
