---
type: public-skill-blueprint
status: draft
version: 0.1
created: 2026-05-18
---

# AI FOMO Skills Blueprint

## Core Thesis

`AI FOMO` is not an AI news summarizer.

It is a three-skill system for personal AI superalignment:

- first align the agent with the user
- then connect sources without mixing raw input with judgment
- finally turn AI information overload into reusable knowledge, signals, and digests

The public project should share the mechanism, not the private workspace.

## Problem

AI builders and product-oriented operators face a recurring problem:

- too many AI updates, demos, papers, posts, podcasts, repos, and changelogs
- too little continuity between what they read today and how they judge tomorrow
- generic summaries that ignore the user's actual goals and decision standards
- archives that store content but do not improve future judgment

The failure mode is not lack of information. It is lack of personal alignment.

## Primary Goal

Create a reusable Codex skill system that lets an agent:

1. understand what the user cares about
2. ingest AI-related sources into a traceable raw layer
3. judge whether a source is worth the user's attention
4. file high-value sources into durable knowledge
5. promote repeated patterns into themes or dossiers
6. extract short-cycle signals and digests only when useful
7. convert feedback into improved future filtering

## Non-Goals

The first public version should not try to be:

- a full SaaS product
- a universal knowledge management system
- an automatic web crawler for every source
- a generic summarization prompt pack
- a public dump of any private raw data, wiki pages, preferences, or credentials
- a guarantee of real-time AI news coverage

## Three-Skill System

```text
ai-fomo-init
  -> collects a profile brief, runs targeted QA, then creates the Personal Alignment Layer and starter workspace

ai-fomo-sources
  -> connects sources and writes traceable raw snapshots

ai-fomo
  -> judges, summarizes, files, promotes, extracts signals, and updates feedback
```

The split matters because each skill has a different trigger, risk profile, and context requirement.

## Personal Alignment Layer

The central public concept is the `Personal Alignment Layer`.

It is a local, user-owned context layer that tells the agent:

- who the user is
- what the user is trying to build or understand
- which themes are long-term important
- which sources or content types deserve higher or lower trust
- what counts as high-signal information
- what should usually be skipped
- how user feedback should change future behavior

This layer is created by `ai-fomo-init`, read by `ai-fomo`, and updated only when feedback is intended to persist.

## Workspace Model

The public starter workspace should use this minimal model:

```text
self-context/
  index.md
  profile.md
  preferences/
    topics.md
    filters.md
    sources.md
  feedback-log.md

raw/
  inbox/
  templates/

config/
  source-registry.yaml

wiki/
  index.md
  log.md
  sources/
  themes/
  dossiers/
  templates/

signals/
  daily/
  weekly/
  templates/

digests/
  daily/
  weekly/
  templates/
```

The structure is intentionally simple. The value comes from consistent judgment, not elaborate taxonomy.

## Default Information Flow

```text
source -> raw snapshot -> source-summary -> theme/dossier check -> signal/digest -> feedback
```

Rules:

- `raw/` keeps traceable source material and minimum metadata.
- `wiki/sources/` keeps grounded summaries of retained sources.
- `wiki/themes/` keeps durable concepts and judgment patterns.
- `wiki/dossiers/` keeps important recurring entities.
- `signals/` keeps short-cycle high-signal observations.
- `digests/` keeps periodic reading outputs.
- `self-context/` keeps alignment and preference information.

Do not skip `wiki/sources/` and jump straight to second-layer knowledge.

## Public Artifact Strategy

The public repo should contain:

- three skill folders
- a starter workspace with empty templates
- mock examples with no private data
- a concise public README outside skill folders
- license and security notes

The public repo should not contain:

- real personal context
- real raw snapshots
- real source summaries copied from private notes
- credentials or source-state files
- unlicensed transcripts or article copies

## Version 0 Success Criteria

Version 0 is successful if a new user can:

1. install the three skills
2. initialize a local alignment workspace
3. add or paste one AI-related source
4. receive a judgment, not just a summary
5. see high-value material filed into `wiki/sources`
6. see low-value material explicitly skipped
7. give feedback that updates future filtering

It does not need to automate every source type in the first version.
