# Source Connectors

This reference describes connector behavior and the current direct import commands.

Version 0 includes a lightweight standard-library importer at `scripts/import_source.py`.

## General Contract

All connectors should:

- write only to `raw/inbox/` by default
- preserve source metadata
- use stable dedupe keys when possible
- keep credentials outside committed files
- avoid storing full third-party content when redistribution is not permitted
- treat raw snapshots as local evidence, not public examples
- report collection errors clearly

When a direct importer is not available, create a manual raw snapshot from user-provided content or exported material.

Do not commit generated raw snapshots to the public skills repo. Generated raw may contain copyrighted text, account-scoped data, transcripts, comments, API responses, or source state.

## Direct Import Commands

### Official Pages And Company Changelogs

```bash
python scripts/import_source.py --workspace /path/to/workspace official-page --url https://example.com/changelog
```

Use for company websites, official changelogs, launch posts, API docs pages, and engineering blogs.

### RSS Or Atom Feeds

```bash
python scripts/import_source.py --workspace /path/to/workspace rss --url https://example.com/feed.xml --limit 10
```

Use when the source exposes a public feed.

### GitHub Repo

```bash
python scripts/import_source.py --workspace /path/to/workspace github-repo --repo owner/name
```

Uses the GitHub API. A `GITHUB_TOKEN` env var is optional but useful for rate limits.

This importer can include README text in the local raw snapshot. Keep generated raw local unless the repository license and your use case permit redistribution.

### GitHub Trending

```bash
python scripts/import_source.py --workspace /path/to/workspace github-trending --language python --since daily --limit 10
```

Use for daily, weekly, or monthly discovery snapshots.

### X User Timeline

```bash
python scripts/import_source.py --workspace /path/to/workspace x-user --handle OpenAI --max-results 10
```

Uses the official X API v2. Set `X_BEARER_TOKEN` in local env only.

### Xiaoyuzhou Episode

```bash
python scripts/import_source.py --workspace /path/to/workspace xiaoyuzhou-episode --url https://www.xiaoyuzhoufm.com/episode/episode_id
```

Imports episode metadata, show notes, and audio URL when available. Transcript generation requires a separate ASR workflow.

### Xiaoyuzhou Account Inbox, Comments, And Transcripts

Use account-level import when the user wants bridge setup, login, subscribed inbox batch import, episode comments, or audio transcription.

Use only with accounts and source material the user is allowed to access. Comments and transcripts are account-scoped raw evidence and should not be published by default.

See `xiaoyuzhou-account.md`.

Prefer one-shot bundle import for early usage:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --start
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --with-transcripts --transcript-limit 3 --dry-run
```

## Source Types

### Official Changelogs And Blogs

Use for AI product, API, model, research, and engineering updates.

Recommended raw metadata:

- vendor
- source URL
- title
- published date
- collected timestamp
- changelog or article category

### GitHub Repositories

Use for repos, releases, issues, pull requests, and gists.

Recommended raw metadata:

- owner and repo
- URL
- stars, forks, language, topics when available
- release tag or commit when relevant
- collected timestamp

### Social Posts

Use for X posts, threads, or other public social updates.

Recommended raw metadata:

- platform
- handle
- post URL
- post id
- published timestamp
- whether it is a reply, repost, or original post

Do not store private timelines or non-public social data.

### Podcasts And Videos

Use for episodes, videos, show notes, and transcripts.

Recommended raw metadata:

- title
- creator or show
- episode or video URL
- published date
- transcript source
- transcript confidence when known

Treat transcripts as raw evidence, not as knowledge pages.

For Xiaoyuzhou comments, store them as separate raw evidence instead of merging them into the episode transcript. Comments are useful for judging resonance, objections, and community context, but they should not be treated as the source's primary claim.

### Docs And Internal Workspaces

Use for user-provided docs only when the user has access and wants them processed.

Recommended raw metadata:

- source workspace name
- document title
- stable document reference
- collected timestamp
- access constraints

Never publish private document content in public examples.

## Registry Example

Use `assets/source-registry.example.yaml` as a non-secret starting point. Adapter names in that file are illustrative; map them to the user's actual runtime or connector implementation.

Keep real credentials in local environment variables or ignored files.
