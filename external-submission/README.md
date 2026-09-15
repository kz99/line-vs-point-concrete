# External submissions

This folder contains contribution packages received without requiring a GitHub account. Each
package has a `manifest.json` and a LaTeX (`.tex`) or PDF document. The manifest must put the
absolute agreement count first:

```json
{"absolute_agreements": 7810920777, "fixed_prime": 147457, "fixed_degree": 87, "dimension": 2}
```

Place incoming packages under `external-submissions/inbox/<slug>/`, then run:

```bash
python scripts/ingest_external_submissions.py
```

Validated packages are transferred into `external-submission/<slug>/` and remain available for
the normal submission and verifier workflow. The uploader should run the repository's ChatGPT or
Codex contribution prompt on the note before sending it, and the first non-comment line of a TeX
note should state `Absolute agreements: A = ...`.
