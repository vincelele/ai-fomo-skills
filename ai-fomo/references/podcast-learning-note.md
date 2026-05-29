# Podcast Learning Note

Use this reference when the user wants a podcast, video transcript, or long interview turned into a readable Markdown learning note, especially when they want to decide whether the original audio/video is worth their time.

This reference is intentionally generic. Do not include private transcripts, private alignment context, or real copyrighted podcast text as examples in a public skill.

## Output Goal

Produce a digest that answers three decisions:

1. What did this episode roughly cover, and is it worth continuing?
2. If it is worth continuing, what is the full episode content in a structured learning form?
3. If the user listens to the original, which segments are worth hearing?

This is a digest layer, not the durable wiki layer.

## Required Inputs

Read these before writing:

- the raw podcast snapshot or transcript in `raw/inbox/`
- show notes and timestamps if present
- an existing `wiki/sources/` summary if one already exists
- `self-context/index.md` when judging relevance to the user
- comments or listener feedback if available, especially for listenability signals

If no raw transcript exists, do not invent the episode content. Ask for a transcript, import one with the appropriate source skill, or create a manual raw snapshot first.

## Default File Target

Write learning notes to:

`digests/podcasts/YYYY-MM-DD-short-slug.md`

Use the episode publish date when available. Use a stable slug based on the episode topic or memorable case, not only the platform episode id.

## Required Structure

Use four main sections.

### 0. Quick Judgment

Answer:

- what this episode is about in 3-5 sentences
- whether it is worth continuing
- why, using a small table when useful
- the recommended reading/listening path

Use one of these conclusion labels:

- `Read the note; no need to listen fully`
- `Read the note; selectively listen to key segments`
- `Worth listening end to end`
- `Skim only`
- `Skip`

### 1. Full Learning Summary

Rewrite the episode into learning material:

- one-sentence conclusion
- content map in original episode order
- core concepts
- main claims with reasons, examples, and limitations
- important cases, people, products, companies, or events
- reusable judgments worth remembering

Do not produce a transcript recap. Remove greetings, repeated explanations, filler, ads, and conversational drift unless they change the user's judgment.

### 2. Personal Learning Value

Connect the episode to the user's long-term themes from the Personal Alignment Layer.

Include:

- why this matters or does not matter for the user
- what the user should take away
- which existing themes this reinforces or challenges
- follow-up questions worth tracking

### 3. Original Listening Recommendation

Always include this section. It is the main difference from a generic summary.

Make a clear recommendation:

- not worth listening to fully
- read the note plus listen to selected segments
- worth listening to end to end

Judge with this rubric:

| Dimension | Question |
| --- | --- |
| Information density | Does the audio contain dense claims or mostly background? |
| Audio-only increment | Does tone, interaction, story detail, or live reasoning add value beyond the note? |
| Listenability | Is the original easy to follow? Consider language switching, audio quality, filler, and whether subtitles are needed. |
| Summary replacement rate | How much of the useful content is already captured by the note? |
| Time cost | Is 10, 20, or full-episode listening worthwhile? |

Then include:

- recommended segments table with `time range`, `priority`, `why listen`, `what to listen for`, `whether the note covers it`
- skippable segments
- minimum listening path for 10 minutes, 20 minutes, and deeper study

### 4. Reliability And Limitations

Explain constraints:

- source bias, e.g. founder interview, vendor position, marketing incentives
- product or market claims not externally validated
- transcript noise, ASR mistakes, language switching
- comments reflect listenability or audience reaction, not necessarily content truth
- which claims need external fact-checking

Also state how the note was processed:

- based on raw transcript/show notes/source-summary
- conceptually rewritten
- not a verbatim transcript
- not a replacement for fact-checking

## Writing Rules

- Lead with judgment, then explain.
- Prefer structured tables for decision points, but do not turn every paragraph into a table.
- Preserve source traceability through links, not long quotes.
- Keep the output readable enough that the user can learn without opening the raw transcript.
- Separate long-term wiki conclusions from human-readable digest conclusions.

## Filing Rules

- If the user asked only for a learning note, write only to `digests/podcasts/`.
- If the episode is also worth retaining as knowledge, write or update `wiki/sources/` separately.
- If a `source-summary` already exists, use it to calibrate the learning note, but do not copy it wholesale.
- Do not update `wiki/index.md` or `wiki/log.md` for a digest-only learning note.

## Synthetic Calibration Example

Input: a fictional 70-minute podcast where a founder explains why their agent product moved from one-off chat sessions to persistent project threads. Show notes include timestamps for product problem definition, memory architecture, customer deployment, and fundraising background.

Expected behavior:

- Quick judgment says the note is worth reading and selected listening is enough.
- Full summary extracts the durable product claims rather than replaying the conversation.
- Original listening recommendation points to the problem-definition and architecture timestamps, while skipping fundraising background unless the user cares about startup process.
- Reliability section notes that founder claims need external validation.
