# AI FOMO Skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#status)

Personal superalignment skills for turning AI information overload into traceable knowledge, signals, and digests.

AI FOMO Skills is a local-first Codex skill pack. It helps an agent answer:

```text
Is this worth my attention, why does it matter to me, and where should it be filed?
```

The goal is not to summarize more AI news. The goal is to make the agent judge information through the user's long-term goals, standards, source preferences, and feedback.

## Status

Alpha / developer preview.

The skills are usable, but the repository should be treated as an early public release. Validate outputs in your own workspace before relying on them for recurring workflows.

## What This Is

- A three-skill system for personal AI information alignment.
- A local workspace pattern for raw captures, reusable wiki pages, signals, and digests.
- A source intake layer for official pages, feeds, GitHub, X API, Xiaoyuzhou episodes, Xiaoyuzhou account imports, comments, and audio transcripts.
- A privacy-conscious public template. Your real personal context and collected source data should stay outside this repository.

## What This Is Not

- Not a generic AI news summarizer.
- Not a hosted SaaS product.
- Not a redistribution channel for podcast transcripts, comments, private feeds, or account data.
- Not legal permission to scrape, store, or republish content you are not allowed to access or process.

## Skill Catalog

| Skill | Use When | Primary Output | Writes By Default |
| --- | --- | --- | --- |
| [`ai-fomo-init`](ai-fomo-init/SKILL.md) | You are setting up a new personal AI FOMO workspace. | Profile brief, targeted QA, starter workspace, draft self-context. | Only after user confirmation. |
| [`ai-fomo-sources`](ai-fomo-sources/SKILL.md) | You need to import source material into traceable raw snapshots. | Files under `raw/inbox/`, optional source registry entries, local session state. | CLI supports `--dry-run`; write only after review. |
| [`ai-fomo`](ai-fomo/SKILL.md) | You need judgment, filing, signal extraction, or digest generation. | `write now`, `ask first`, `skip`, wiki updates, signals, digests, feedback candidates. | Depends on task; should preserve raw -> wiki -> signal order. |

## Safety Model

- **Local first:** run skills against your own workspace and accounts.
- **Dry-run first:** source import commands support preview paths before writing raw snapshots.
- **Traceable evidence:** imported material lands in `raw/inbox/` before it is promoted into wiki, signals, or digests.
- **No private data in public git:** do not commit raw captures, transcripts, comments, cookies, tokens, account sessions, or real personal context.
- **User-aligned judgment:** the core skill should optimize for relevance and reusable signal, not novelty or volume.

See also [`docs/public-sharing-policy.md`](docs/public-sharing-policy.md) and [`docs/public-skill-boundaries.md`](docs/public-skill-boundaries.md).

## First 10 Minutes

### 1. Install the skills

Recommended, using Codex's skill installer:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo vincelele/ai-fomo-skills \
  --path ai-fomo-init ai-fomo-sources ai-fomo
```

Manual install:

```bash
git clone https://github.com/vincelele/ai-fomo-skills.git
cd ai-fomo-skills
cp -R ai-fomo-init ai-fomo-sources ai-fomo ~/.codex/skills/
```

Restart Codex after installing new skills so the metadata is picked up.

### 2. Initialize a local workspace

Ask Codex:

```text
Use $ai-fomo-init to initialize a local AI FOMO workspace at /path/to/workspace.
```

The init flow is intentionally two-step:

1. Provide a profile brief, such as a resume, bio, project list, portfolio, or current goals.
2. Answer targeted QA so the agent can fill gaps without over-inferring your preferences.

### 3. Import one public source

Preview first:

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/import_source.py \
  --workspace /path/to/workspace \
  --dry-run \
  official-page \
  --url https://example.com/changelog
```

If the preview looks right, write the raw snapshot:

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/import_source.py \
  --workspace /path/to/workspace \
  official-page \
  --url https://example.com/changelog
```

### 4. Ask for judgment

```text
Use $ai-fomo to review /path/to/workspace/raw/inbox and tell me what should be written, skipped, or reviewed first.
```

## Supported Source Inputs

| Source | Path | Requirement | Notes |
| --- | --- | --- | --- |
| Official pages and changelogs | `import_source.py official-page` | Public URL | Good for OpenAI, Anthropic, Google, Meta, product docs, release notes. |
| RSS / Atom feeds | `import_source.py rss` | Public feed URL | Good for blogs, changelogs, newsletters with feeds. |
| GitHub repositories | `import_source.py github-repo` | Public GitHub repo | Imports repo metadata and README context. |
| GitHub Trending | `import_source.py github-trending` | Public GitHub page | Captures a trending snapshot for later judgment. |
| X user timelines | `import_source.py x-user` | `X_BEARER_TOKEN` | Uses X API v2. Keep tokens out of git. |
| Xiaoyuzhou public episode | `import_source.py xiaoyuzhou-episode` | Public episode URL | Imports metadata and show notes when available. |
| Xiaoyuzhou subscribed inbox | `xiaoyuzhou_account.py import-inbox` | Local bridge, account login | Batch imports subscribed episodes into `raw/inbox/`. |
| Xiaoyuzhou comments | `xiaoyuzhou_account.py import-comments` | Local bridge, account login | Can include primary comments and optional reply threads. |
| Audio transcription | `xiaoyuzhou_account.py transcribe-audio` or `transcribe-raw` | `DASHSCOPE_API_KEY` | Uses DashScope Fun-ASR. Transcription may be slow or paid. |
| Manual snapshot | Template in `ai-fomo-sources/assets/` | Pasted text or exported file | Use this when no connector exists yet. Do not block ingestion. |

## Xiaoyuzhou Account Workflow

The Xiaoyuzhou account workflow is optional and more sensitive because it uses account access, a local third-party bridge, comments, and audio transcription.

Use it only with accounts and data you are allowed to access and process.

Preview bridge install:

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py \
  --workspace /path/to/workspace \
  install-bridge \
  --dry-run
```

Clone, build, and start the bridge:

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py \
  --workspace /path/to/workspace \
  install-bridge \
  --start
```

Login and import a small batch:

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace send-code --phone-number PHONE_NUMBER
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace login --phone-number PHONE_NUMBER --verify-code CODE
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --with-transcripts --transcript-limit 3 --dry-run
```

Run without `--dry-run` only after checking access, cost, and output boundaries.

More details: [`ai-fomo-sources/references/xiaoyuzhou-account.md`](ai-fomo-sources/references/xiaoyuzhou-account.md).

## Repository Layout

```text
.
|-- ai-fomo-init/       # onboarding and Personal Alignment Layer setup
|-- ai-fomo-sources/    # source importers, connector references, templates
|-- ai-fomo/            # core judgment, filing, signal, and digest workflow
|-- docs/               # public sharing policy and boundaries
|-- LICENSE
`-- README.md
```

## Public Release Boundary

Publish:

- skill folders
- templates
- synthetic examples
- connector scripts
- public docs about workflow and boundaries

Do not publish:

- `raw/inbox/` outputs
- `raw/state/` files
- podcast transcripts or comments collected from user accounts
- `.env*`, `.secrets/`, cookies, tokens, API keys, or session files
- real `self-context/`, `wiki/`, `signals/`, or `digests/`
- local bridge checkout under `.tools/`

## Current Gaps

- Scheduled collection is not included yet. Add it only after a source proves valuable enough to monitor.
- Full Xiaoyuzhou subscription list export is not included yet.
- Connectors are intentionally lightweight. Some sources may require site-specific handling.
- The core judgment quality depends on the quality of your `self-context` and feedback loop.

## Contributing

Useful contributions:

- new source importers with clear access boundaries
- safer dry-run and validation paths
- better starter workspace templates
- examples that use synthetic or public-domain content
- documentation for platform-specific setup

Please do not contribute real private workspace data, account exports, transcripts, comments, credentials, or personal context.

## License

MIT. See [`LICENSE`](LICENSE).
