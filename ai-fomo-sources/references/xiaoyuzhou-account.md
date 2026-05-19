# Xiaoyuzhou Account Import

Use this when the user wants account-level Xiaoyuzhou import, including bridge setup, login, subscribed inbox batch import, episode comments, and audio transcription.

## Requirement

This workflow needs a local Xiaoyuzhou account API bridge compatible with:

- `POST /sendCode`
- `POST /login`
- `POST /refresh_token`
- `POST /inbox_list`
- `POST /comment_primary`
- `POST /comment_thread`

The default bridge URL is:

```text
http://127.0.0.1:23020
```

The bridge source is not vendored in this skill. The installer clones the third-party `ultrazg/xyz` bridge into the user's workspace under `.tools/xiaoyuzhou-bridge` by default, then builds and starts it locally.

Audio transcription does not require the Xiaoyuzhou bridge after an audio URL is available. It requires `DASHSCOPE_API_KEY` or a custom env var passed with `--api-key-env`.

## Access Boundary

Use this workflow only for accounts, subscriptions, comments, and audio that the user is allowed to access and process. The skill does not grant platform rights, bypass access controls, or make collected content safe to redistribute.

Raw snapshots, comments, and transcripts are local evidence for the user's own AI FOMO workspace. Do not publish them unless the source license and platform terms permit redistribution.

The bridge is a third-party dependency. Before using `install-bridge`, the user should review its repository, license, and behavior. Pin a reviewed version with `--ref` when reproducibility matters.

## Bridge Setup

Check whether the default bridge port is already listening:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace bridge-status
```

Preview install:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --dry-run
```

Clone, build, and start the bridge:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace install-bridge --start
```

Start an already installed bridge:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace start-bridge
```

Stop a bridge started by this script:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace stop-bridge
```

Notes:

- Requires `git` and `go`.
- Default repo: `https://github.com/ultrazg/xyz.git`.
- Default install dir: `<workspace>/.tools/xiaoyuzhou-bridge`.
- Default local URL: `http://127.0.0.1:23020`.
- Use `--repo`, `--ref`, and `--bridge-dir` if the user wants a fork, pinned commit, or custom location.
- Do not commit `.tools/`, bridge logs, pid files, or session files.

## Login Flow

1. Send SMS code:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace send-code --phone-number PHONE_NUMBER
```

2. Login with code:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace login --phone-number PHONE_NUMBER --verify-code CODE
```

The session is saved by default to:

```text
<workspace>/.secrets/xiaoyuzhou_session.json
```

Do not commit this file.

3. Check session:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace session-status
```

## Batch Import Subscribed Inbox

Dry-run first:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 30 --max-pages 3 --dry-run
```

Write raw snapshots:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 30 --max-pages 3
```

This writes one raw snapshot per episode into:

```text
raw/inbox/
```

Batch import episode metadata plus comments:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --comments-max-pages 2
```

Batch import episode metadata, comments, and transcripts:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --with-transcripts --transcript-limit 3 --dry-run
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-inbox --limit 10 --with-comments --with-transcripts --transcript-limit 3
```

Use `--transcript-limit` to avoid accidentally transcribing every imported episode. Transcription can be slow and may incur ASR cost.

## Import Episode Comments

Import primary comments:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-comments --episode-id EPISODE_ID --max-pages 2 --dry-run
```

Write comments:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-comments --episode-id EPISODE_ID --max-pages 2
```

Include reply threads when needed:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace import-comments --episode-id EPISODE_ID --include-replies
```

This writes a separate `podcast_comments` raw snapshot. Do not merge comments into the transcript snapshot.

## Transcribe Audio

Recommended path after `import-inbox`: transcribe one of the generated raw snapshots that contains `metadata.episode.audio_url`.

Dry-run:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace transcribe-raw --raw-file /path/to/workspace/raw/inbox/episode.md --dry-run
```

Run transcription:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace transcribe-raw --raw-file /path/to/workspace/raw/inbox/episode.md
```

Direct audio URL path:

```bash
python scripts/xiaoyuzhou_account.py --workspace /path/to/workspace transcribe-audio --episode-id EPISODE_ID --audio-url AUDIO_URL --title "Episode title"
```

Useful options:

- `--language zh`
- `--diarization-enabled`
- `--speaker-count 2`
- `--poll-interval 10`
- `--max-poll-attempts 90`

This writes a separate `podcast_transcript` raw snapshot. The next step is `ai-fomo` judgment, not immediate wiki filing.

## Current Scope

Included:

- SMS code request
- login and local session save
- session status without printing tokens
- refresh session
- bridge status check
- automatic bridge clone/build/start/stop
- batch import subscribed inbox episodes
- one raw snapshot per episode
- primary comment import
- optional reply-thread import
- DashScope async Fun-ASR transcript generation from `audio_url`
- separate raw snapshots for episode metadata, comments, and transcript
- one-command inbox bundle import with optional comments and transcripts

Still not included:

- full podcast subscription list export
- scheduled collection

## Deferred Capabilities

### Scheduled Collection

This would run Xiaoyuzhou imports periodically, for example daily or weekly.

Recommendation: keep it outside the skill's core. Add a recipe later after a source has proven valuable. Scheduling belongs to the user's automation layer, while this skill should provide safe one-shot commands.

### Full Subscription List Export

This would export the user's complete subscribed podcast list, not just recent inbox episodes.

Recommendation: useful, but lower priority than inbox, comments, and transcripts. Add it when the bridge exposes a stable subscription-list endpoint. It helps initial source discovery, but it is not required for the current anti-FOMO judgment loop.
