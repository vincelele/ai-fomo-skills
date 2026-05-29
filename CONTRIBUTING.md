# Contributing

AI FOMO Skills is a local-first skill pack. Contributions are welcome, but public safety matters more than completeness.

## What To Contribute

Useful contributions:

- new source importers with clear access boundaries
- safer dry-run and validation flows
- better starter workspace templates
- public documentation for setup and troubleshooting
- synthetic examples or examples based on redistributable public content
- fixes to `SKILL.md`, references, scripts, and README instructions

## Do Not Contribute

Do not include:

- real `raw/` captures
- real `self-context/`, `wiki/`, `signals/`, or `digests/`
- podcast transcripts or comments collected from user accounts
- account exports
- cookies, tokens, API keys, session files, or `.env*`
- private source material that cannot be redistributed
- local tool checkouts such as `.tools/`

If you are unsure whether something is safe to publish, do not include it.

## Branch And PR Flow

Use a topic branch:

```text
codex/<short-topic>
```

Examples:

- `codex/readme-install-flow`
- `codex/rss-importer`
- `codex/xiaoyuzhou-docs`

Open a pull request into `main`. PRs should explain:

- what changed
- why it changed
- how it was checked
- whether README or public boundaries need updates

## README Update Rule

Update `README.md` when a change affects user-facing behavior:

- a skill is added, removed, renamed, or re-scoped
- installation instructions change
- source import coverage changes
- Xiaoyuzhou behavior changes
- account, privacy, copyright, or cost risks change
- current gaps become supported, or new important gaps appear

Small internal refactors usually do not need README changes.

## Validation

For script-related changes, run:

```bash
python3 -m py_compile ai-fomo-sources/scripts/import_source.py ai-fomo-sources/scripts/xiaoyuzhou_account.py
```

For README changes, check local links:

```bash
python3 - <<'PY'
from pathlib import Path
import re
import sys

root = Path('.')
text = Path('README.md').read_text()
missing = []
for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
    if target.startswith(('http://', 'https://', '#')):
        continue
    path = target.split('#', 1)[0]
    if path and not (root / path).exists():
        missing.append(target)
if missing:
    print('missing links:')
    print('\n'.join(missing))
    sys.exit(1)
print('all local README links exist')
PY
```

Before opening a PR, inspect staged files explicitly:

```bash
git diff --cached --name-only
```

Do not use `git add .` for public releases unless you have reviewed every file.
