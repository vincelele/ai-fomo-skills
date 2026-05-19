---
name: ai-fomo-init
description: Initialize a personal AI FOMO workspace and Personal Alignment Layer. Use when the user wants to set up an anti-AI-FOMO system, create a source intelligence workspace, configure long-term AI interests, define information value standards, or generate starter workspace templates for AI information judgment.
---

# AI FOMO Init

## Purpose

Create a local Personal Alignment Layer and starter workspace. This skill aligns the agent before any source is summarized, collected, or filed.

## Use When

Use this skill when the user asks to:

- set up AI FOMO
- initialize a personal AI alignment workspace
- create an anti-FOMO knowledge workspace
- configure what AI information is worth attention
- generate starter folders and templates

## Do Not Use When

Do not use this skill to:

- summarize a specific source
- collect from a source
- write `wiki/sources`
- generate a digest from existing material

Use `ai-fomo-sources` for source intake and `ai-fomo` for judgment and filing.

## Core Workflow

1. Choose or confirm the target workspace path.
2. Ask the user for a profile brief: resume, bio, portfolio, LinkedIn-style summary, project history, or free-form notes.
3. Extract a first-pass alignment map from the profile brief.
4. Ask targeted QA to fill only the gaps that matter for AI information filtering.
5. Copy the starter workspace from `assets/starter-workspace/` if the user wants files created.
6. Write confirmed alignment context into `self-context/`.
7. Mark weak inferences as draft or pending confirmation.
8. End with a short alignment contract summary for the user to review.

## Two-Stage Alignment Intake

### Stage 1: Profile Brief

Invite the user to provide one or more of:

- resume or CV
- personal bio
- project list
- portfolio notes
- work history
- current goals
- examples of AI content they found valuable or useless

From this, extract only tentative alignment signals:

- role and current work
- long-term themes
- recurring decisions
- technical or product interests
- likely source preferences
- possible downrank patterns

Do not treat these as final until confirmed.

### Stage 2: Targeted QA

Ask a small number of focused questions to close gaps. Prefer 3 to 7 questions.

Question areas:

- what decisions the user wants AI information to improve
- which AI topics are high priority now
- which topics are interesting but lower priority
- what kinds of content waste the user's time
- what sources they trust or distrust
- how aggressive the agent should be about skipping material
- what output style is most useful

Do not ask a long onboarding survey. The goal is enough alignment to start, then improve through feedback.

## Personal Alignment Layer

The minimum layer should answer:

- who the agent is serving
- what the user is building, studying, or deciding
- which AI themes are high priority
- which content types should be downranked
- what counts as high-signal information
- how feedback should change future filtering

If the user provides too little information, ask concise follow-up questions instead of overfitting.

## Output Contract

When initialization finishes, report:

- workspace path
- files created or updated
- confirmed alignment facts from the profile brief and QA
- draft assumptions still requiring user review
- next recommended action: connect sources or process the first source

## Safety Rules

- Do not write credentials into the workspace.
- Do not copy private examples into templates.
- Do not infer sensitive personal context unless explicitly provided.
- Do not assume the user's interests match the author's interests.
- Do not treat one-time task goals as long-term preferences.
- Do not turn resume details into public examples or shareable templates.
