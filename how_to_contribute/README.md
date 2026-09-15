# How to contribute

This repository studies one concrete line-versus-point low-degree test. Contributions may be
human-written, AI-assisted, or produced by an independent autoresearch loop. Mathematical claims
are judged by their proofs, not their source.

## The fixed problem

Throughout,

\[
p=147457,\qquad d=87,\qquad m=2,
\]

and the field is the prime field \(\mathbb F_p\). A point table is a function
\(f:\mathbb F_p^2\to\mathbb F_p\). A line table assigns to each affine line \(L\) a univariate
polynomial \(P_L\) of degree at most \(87\), interpreted on an affine parametrization of \(L\).
The test samples an affine line uniformly from all \(p(p+1)\) affine lines, then samples a point
uniformly on that line, and accepts when \(P_L(x)=f(x)\).

Write

\[
\operatorname{Pass}(f,P)=\Pr_{L,\,x\in L}[P_L(x)=f(x)]
\]

and

\[
\operatorname{Agr}_{87}(f)=
\max_{\deg Q\le 87}\Pr_{x\in\mathbb F_p^2}[Q(x)=f(x)],
\]

where \(Q\) has total degree at most \(87\). The campaign seeks explicit values
\(\varepsilon\in(0,1]\) for which

\[
\operatorname{Pass}(f,P)\ge\varepsilon
\quad\Longrightarrow\quad
\operatorname{Agr}_{87}(f)\ge\varepsilon/10
\]

for every pair \((f,P)\). The public leaderboard records decreasing values of \(\varepsilon\).
Do not change the prime, degree, dimension, sampling distribution, total-degree convention, or
single-polynomial conclusion.

## What is useful

The main target is a complete proof with a smaller explicit numerical \(\varepsilon\). Useful
supporting contributions include:

- exact optimization of KTZ pruning, interpolation, exceptional-set, or recovery parameters;
- a new bivariate proof architecture giving a larger improvement;
- a sharp algebraic or combinatorial lemma with all hypotheses stated;
- an explicit obstruction, counterexample, or correction to a published intermediate claim;
- exact integer, rational, SAT, or computer-algebra certificates with a deterministic checker;
- a careful fixed-parameter extraction of a literature theorem.

General-dimension bootstrapping, extension-field descent, numerical experiments without a proof,
and unquantified asymptotic claims are outside the active target.

## Literature starting points

Read the primary sources before relying on any theorem.

1. Arora and Sudan, *Improved Low-Degree Testing and Its Applications*, Combinatorica 23 (2003),
   [DOI](https://doi.org/10.1007/s00493-003-0025-0).
2. Harsha, Kumar, Saptharishi, and Sudan, *An Improved Line-Point Low-Degree Test*,
   [arXiv:2311.12752](https://arxiv.org/abs/2311.12752).
3. Kominers, Thaler, and Zheng, *Improved Soundness for the Line--versus--Point Test*, ECCC
   TR26-147, revision 1 (2026), [primary report](https://eccc.weizmann.ac.il/report/2026/147/).
4. Rubinfeld and Sudan, *Robust Characterizations of Polynomials with Applications to Program
   Testing*, SIAM J. Comput. 25 (1996),
   [DOI](https://doi.org/10.1137/S0097539793255151).

The repository's [literature map](../references/LITERATURE.md) is a navigation aid. Every imported
result in a submission must name its paper version, result number, exact hypotheses, and role in
the proof. Never turn hidden \(O(\cdot)\) constants into a numerical bound without deriving them.

## Two contribution tracks

### Leaderboard submission

Use this only for a proved, numerical, end-to-end bivariate soundness theorem that improves the
current record. Set `leaderboard_submission` and `benchmark_improved` to `true`, set
`claim_scope` to `bivariate_theorem`, and give the complete load-bearing proof chain. Every proof
step and every soundness-ledger stage must be marked `proved`.

After ingestion, the lab launches exactly two independent AI audits. Each auditor checks the same
theorem hash and numerical value, traverses the complete logic chain, and verifies every lemma or
literature result actually used. A graph point appears only after two complete matching accepts.

### Research contribution

Use this for a lemma, proof tool, obstruction, counterexample, or conditional architecture. Set
`leaderboard_submission` and `benchmark_improved` to `false`. The artifact is stored and its
lemmas may appear in the Lemma Book, but it is not audited yet. If a later leaderboard submission
uses it, both auditors verify the imported statement as part of that submission's logic chain.

## Prepare a pull request

1. Fork `https://github.com/kz99/line-vs-point-concrete` and create a branch.
2. Copy `how_to_contribute/submission_template/` to
   `community_submissions/<github-handle>-<short-slug>/`.
3. Rename neither `submission.json` nor `note.md`.
4. Fill out `submission.json`. The directory name and `slug` must match and may contain lowercase
   letters, digits, and hyphens only.
5. Replace `note.md` with a self-contained academic note. Use dollar-delimited LaTeX supported by
   KaTeX. Put no TeX command outside math delimiters.
6. Run:

   ```bash
   python -m pip install -e .
   line-point-concrete community-validate community_submissions/<your-slug>
   python -m unittest discover -s tests -v
   ```

7. Commit only durable source material. Do not commit downloaded PDFs, credentials, agent logs,
   SQLite files, or generated caches.
8. Open a pull request. In its description, state the claimed \(\varepsilon\), whether the claim
   is intended for the leaderboard, the main new idea, and any AI assistance used.

The repository checks package structure and fixed parameters in CI. After an accepted pull
request is merged and synced to the research host, the operator runs

```bash
line-point-concrete community-ingest \
  configs/campaign-10-ultra.yaml \
  community_submissions/<your-slug>
```

This registers the immutable submission. A valid leaderboard submission then enters the two-agent
audit queue automatically. Verification results are published under `research_state/` and on the
public observatory.

## Mathematical writing rules

- State the theorem with every quantifier and exact numerical parameter.
- A lemma statement contains only quantified objects, hypotheses, and conclusion. Put all
  motivation and explanation in the proof.
- Number proof steps `[P1]`, `[P2]`, and so on. Declare their dependencies explicitly.
- Record every Markov, union-bound, Cauchy--Schwarz, pruning, rounding, interpolation, and recovery
  loss in the soundness ledger.
- Audit characteristic-dependent division, derivatives, factorials, multiplicities,
  discriminants, separability, and degree aliasing.
- Distinguish a theorem quoted from a source from a fixed-parameter derivation you reconstructed.
- Computer assistance is acceptable only with exact reproducible certificates and a checker.
- Do not describe conditional or experimental evidence as proved.

## Copy-paste research prompt

The standalone [research prompt](RESEARCH_PROMPT.md) can be copied directly into another capable
AI system. The public observatory also provides a one-click copy button.

