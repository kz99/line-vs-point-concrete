# Contributor research prompt

You are contributing to the public Line--Point Concrete research project. This prompt is
self-contained: **do not stop merely because your workspace is empty, the repository is absent,
or `line-point-concrete` is not installed.**

## Bootstrap and durable output

First inspect the workspace. If the repository is absent and shell/network access is available,
run:

```bash
git clone https://github.com/kz99/line-vs-point-concrete.git
cd line-vs-point-concrete
python -m pip install -e .
```

If cloning, installation, or shell access is unavailable, continue the mathematical work. Create
and return two downloadable artifacts named `note.md` and `submission.json` using the contract
below. Say that local validation is **deferred**, not that the mathematics or submission is
blocked. Never claim that an artifact was uploaded unless an upload actually succeeded.

Save useful results as soon as they become concrete. A proved standalone lemma, obstruction,
counterexample, corrected constant, or partial proof is a valid research contribution even when
it gives no leaderboard improvement. Do not discard it and do not force it into the leaderboard
track.

## Fixed mathematical instance

Work only with:

- prime field \(\mathbb F_p\), \(p=147457\);
- dimension \(m=2\);
- bivariate total-degree bound \(d=87\);
- a uniformly random affine line among all \(p(p+1)\) lines, followed by a uniformly random point
  on that line;
- acceptance when the degree-at-most-87 polynomial assigned to the line equals the point table at
  the sampled point.

For a point table \(f:\mathbb F_p^2\to\mathbb F_p\) and line table \(P=(P_L)_L\), define

\[
\operatorname{Pass}(f,P)=\Pr_{L,\,x\in L}[P_L(x)=f(x)]
\]

and

\[
\operatorname{Agr}_{87}(f)=
\max_{Q\in\mathbb F_p[X,Y],\,\deg Q\le87}
\Pr_{x\in\mathbb F_p^2}[Q(x)=f(x)].
\]

An admissible soundness candidate is a fixed \(\varepsilon\) satisfying

\[
\varepsilon\ge \frac{1.1d}{p}=\frac{957}{1474570}
\]

for which the following holds for every pair \((f,P)\):

\[
\operatorname{Pass}(f,P)\ge\varepsilon
\quad\Longrightarrow\quad
\operatorname{Agr}_{87}(f)\ge
\max\!\left\{\frac{2d}{p},\frac{\varepsilon}{10}\right\}.
\]

The leaderboard score is the absolute integer

\[
A=\lceil \varepsilon p^2\rceil.
\]

Lower scores are stronger. The current verified record is **7,349,491,214**. A leaderboard
submission must rigorously certify a score at most **7,349,491,213**. This record may change; if
the repository is available, inspect `dashboard/public/research-data.json` before claiming an
improvement.

Do not vary \(p,d,m\), use extension fields, work on general-dimension bootstrapping, change the
sampling distribution, replace total degree by individual degree, or weaken the conclusion to a
list of global polynomials.

## Research directions

Begin with the primary literature: Arora--Sudan (Combinatorica 2003),
Harsha--Kumar--Saptharishi--Sudan (arXiv:2311.12752), Kominers--Thaler--Zheng (ECCC TR26-147,
revision 1), and Rubinfeld--Sudan (SIAM J. Comput. 1996). Search for later refinements. For every
imported theorem, record the exact paper version, result number, hypotheses, constants, and role.
Never manufacture numerical constants from asymptotic notation.

Either optimize the KTZ architecture at \((p,d)=(147457,87)\) with exact arithmetic, jointly
tuning all pruning, exceptional-set, interpolation, resultant, separability, direction-mixing,
rounding, and recovery losses; or seek a genuinely new bivariate architecture. Attempt
adversarial tables and characteristic-dependent failure modes. Floating-point optimization may
suggest parameters but cannot prove them; replace it with an exact certificate.

## Writing contract

Write a self-contained academic Markdown note with: Abstract; Test and Notation; Prior Results;
Main Theorem or Lemma; Proof; Soundness Ledger; Counterexample Attempts; Characteristic Audit;
and Limitations. Number proof steps `[P1]`, `[P2]`, and so on, and list their dependency ids.

**Lemma rule.** A lemma statement contains only quantified objects, hypotheses, and conclusion.
It contains no motivation, derivation, commentary, proof sketch, interpretation, history, or
explanation. Put all such material in the proof. Split a lemma when this makes its logical content
clearer.

Classify the result honestly:

- **Leaderboard submission:** only a fully proved numerical end-to-end bivariate theorem that
  strictly improves the current record. Set `leaderboard_submission=true`,
  `claim_scope=bivariate_theorem`, `result_status=proved`, and `benchmark_improved=true`. Put the
  absolute score \(A\) at the top of the note. Every load-bearing step and ledger stage must be
  proved. One independent `xhigh` verifier audits the complete logic chain; only its acceptance
  promotes the result.
- **Research contribution:** any standalone lemma, proof tool, obstruction, counterexample,
  corrected calculation, conditional architecture, or experiment. Set
  `leaderboard_submission=false` and `benchmark_improved=false`. Use the honest `claim_scope` and
  `result_status`. No agreement score is required. The contribution is stored without audit; a
  verifier checks it later only if a leaderboard proof uses it.

## Package, validate, and hand off

When the repository is available, copy `how_to_contribute/submission_template/` to
`community_submissions/<your-slug>/`, fill in `submission.json`, and replace `note.md`. Validate
with either:

```bash
line-point-concrete community-validate community_submissions/<your-slug>
```

or, without an installed console script:

```bash
PYTHONPATH=src python -m line_point_research community-validate community_submissions/<your-slug>
```

A GitHub user may open a pull request. Without GitHub, return `submission.json` and `note.md` (or
the one-file handoff bundle produced by the observatory's **Submit a contribution** tab) directly
to the person who assigned this task. The website packages files locally; it does not silently
upload them. The project operator places the returned bundle in `external-submissions/inbox/` and
runs the repository ingestion script.

If the repository is unavailable, make `submission.json` conform to
`line-point-community-submission-v1`. It must include a lowercase hyphenated `slug`, contributor
name (a pseudonym is allowed), `github` set to `none` when applicable, AI-assistance disclosure,
fixed parameters, honest status and scope, both leaderboard booleans, theorem statement,
literature dependencies, a nonempty `proof_steps` array, a nonempty `soundness_ledger` array,
counterexample attempts, characteristic audit, finite sanity checks, obstructions, and next
tasks. Use `null` for soundness and recovery fields in a research contribution.

Never claim verification yourself. Never say that a standalone result is unsubmittable merely
because it does not improve the leaderboard.
