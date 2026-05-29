# Filing Rules

Use these rules before writing to the workspace.

## Read Order

Before writing:

1. read `self-context/index.md`
2. read `wiki/index.md`
3. inspect relevant existing `wiki/themes/` or `wiki/dossiers/` pages when they exist

## Write Order

For retained sources, write in this order:

1. `wiki/sources/`
2. affected `wiki/themes/`
3. affected `wiki/dossiers/`
4. `signals/` only when requested or explicitly useful
5. `digests/` only for periodic reading output or user-requested learning notes
6. `self-context/` only for persistent feedback or confirmed preference changes

Never skip `wiki/sources` and write directly to `themes` or `dossiers`.

## `wiki/sources`

Use for the first durable summary layer of a retained source.

Include:

- source identity and link
- source type
- why it was retained
- main claims and structure
- durable mechanisms or tradeoffs
- relevance to the user
- links to raw snapshot when available
- promotion candidates, if any

Avoid:

- long quotes
- copied article bodies
- transcript dumps
- unsupported conclusions

## `digests/podcasts`

Use for human-readable podcast learning notes when the user wants to decide whether an episode is worth continuing, understand the full episode without listening end to end, or choose which original segments to hear.

These notes should include:

- quick judgment
- full learning summary
- personal learning value
- original listening recommendation
- reliability and limitations

Do not treat a podcast learning note as a durable source summary. If the episode is worth retaining as knowledge, write `wiki/sources` separately.

## `wiki/themes`

Use for stable topics, methods, constraints, or long-term judgment patterns.

Update an existing theme when the source adds:

- stronger evidence
- a better mechanism
- a counterexample
- a clearer constraint
- a new practical implication

Propose a new theme only when at least two are true:

- the pattern appears across multiple sources or is obviously long-term
- it is reusable beyond the current source
- it has a stable name and clear boundary

## `wiki/dossiers`

Use for concrete recurring entities:

- products
- companies
- projects
- protocols
- people
- platforms
- systems

Propose a dossier only when at least two are true:

- the object is clearly identifiable
- it is likely to recur
- current material supports a stable "what it is and why it matters now" page

## Feedback

Write feedback to `self-context/feedback-log.md` when the user comments on summary quality, filtering, relevance, or formatting.

Update persistent preferences only when the user clearly indicates the rule should apply in the future.
