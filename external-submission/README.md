# External submissions

This folder contains contribution packages returned without requiring a GitHub account. The
observatory creates a single `.lvp-submission.json` handoff bundle containing both metadata and a
Markdown, TeX, or PDF document. GitHub Pages does not upload the bundle: the contributor returns
it to the person who assigned the research.

A **leaderboard** manifest must give the absolute soundness score:

```json
{"contribution_type": "leaderboard", "absolute_agreements": 7000000000, "fixed_prime": 147457, "fixed_degree": 87, "dimension": 2}
```

A **research** contribution, including a standalone lemma or partial proof, uses
`"contribution_type": "research"` and `"absolute_agreements": null`.

Place a returned `.lvp-submission.json` bundle directly in `external-submissions/inbox/`, or place
a legacy expanded package under `external-submissions/inbox/<slug>/`, then run:

```bash
python scripts/ingest_external_submissions.py
```

Validated bundles are unpacked and transferred into `external-submission/<slug>/`. Research
contributions enter the shared corpus without an audit. Leaderboard submissions enter the single
`xhigh` verifier workflow after their full community package is ingested. The first content line
of a leaderboard Markdown or TeX note must state `Absolute soundness score: A = ...`.
