# AI FOMO Skills

Personal superalignment skills for turning AI information overload into reusable knowledge, signals, and digests.

Status: alpha / developer preview.

This is a local-first skill system. It is intended for users to run against their own workspace, their own source accounts, and source material they are allowed to access. Do not commit collected raw outputs, transcripts, credentials, cookies, or personal context to a public repository.

This repository stages three Codex skills:

- `ai-fomo-init`: initialize the Personal Alignment Layer and starter workspace
- `ai-fomo-sources`: directly import common AI sources and write traceable raw snapshots
- `ai-fomo`: judge, summarize, file, promote, extract signals, and update feedback

This is not an AI news summarizer. The goal is to make the agent judge information through the user's long-term goals, standards, and feedback.

Do not publish private workspace data, credentials, raw source material, or real personal context in this repository.

## Quickstart

1. Copy or install the three skill folders into your Codex skills directory:

```bash
cp -R ai-fomo-init ai-fomo-sources ai-fomo ~/.codex/skills/
```

2. Create a local AI FOMO workspace with `ai-fomo-init`.

Ask Codex:

```text
Use $ai-fomo-init to initialize a local AI FOMO workspace at /path/to/workspace.
```

The init flow should first ask for a profile brief, then ask targeted QA, then create the starter workspace if you want files created.

3. Import a first source with `ai-fomo-sources`.

Example:

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/import_source.py --workspace /path/to/workspace --dry-run official-page --url https://example.com/changelog
```

4. If the dry-run looks right, write the raw snapshot.

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/import_source.py --workspace /path/to/workspace official-page --url https://example.com/changelog
```

5. Ask `ai-fomo` to judge the raw material.

```text
Use $ai-fomo to review /path/to/workspace/raw/inbox and tell me what should be written, skipped, or reviewed first.
```

## Xiaoyuzhou Quickstart

The Xiaoyuzhou account workflow uses a local third-party bridge and should only be used with accounts and data you are allowed to access.

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --dry-run
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --start
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace send-code --phone-number PHONE_NUMBER
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace login --phone-number PHONE_NUMBER --verify-code CODE
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --with-transcripts --transcript-limit 3 --dry-run
```

Run without `--dry-run` only after checking cost, access, and output boundaries.

## Source Import Coverage

`ai-fomo-sources` includes a lightweight importer for:

- official company pages and changelogs
- RSS and Atom feeds
- GitHub repos
- GitHub Trending snapshots
- X user timelines through X API v2
- Xiaoyuzhou episode metadata and show notes
- Xiaoyuzhou bridge install/start, account login, subscribed inbox batch import, episode comments, and DashScope Fun-ASR transcription

## Public Release Boundary

Publish the skills, templates, synthetic examples, and connector scripts. Do not publish:

- `raw/inbox/` outputs
- `raw/state/` files
- podcast transcripts or comments collected from user accounts
- `.env*`, `.secrets/`, cookies, tokens, or API keys
- real `self-context/`, `wiki/`, `signals/`, or `digests/`
- local bridge checkout under `.tools/`
