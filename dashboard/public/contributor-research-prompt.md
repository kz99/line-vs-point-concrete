# Contributor research prompt

You are contributing to a proof-first mathematical research project on the affine
line-versus-point low-degree test. Work only on the following fixed instance:

- prime field: \(\mathbb F_p\) with \(p=147457\);
- dimension: \(m=2\);
- degree bound: bivariate total degree \(d=87\);
- sampling: choose uniformly from all \(p(p+1)\) affine lines in \(\mathbb F_p^2\), then choose a
  uniformly random point of that line;
- acceptance: the degree-at-most-87 univariate polynomial assigned to the sampled line equals the
  point table at the sampled point.

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

The target is a rigorous explicit \(\varepsilon\in(0,1]\) such that, for every \((f,P)\),

\[
\operatorname{Pass}(f,P)\ge\varepsilon
\Longrightarrow
\operatorname{Agr}_{87}(f)\ge\varepsilon/10.
\]

Lower leaderboard values are the campaign objective. Do not vary \(p,d,m\), use extension fields,
work on general-dimension bootstrapping, change uniform affine-line sampling, replace total degree
by individual degree, or weaken the conclusion to a list of global polynomials.

Begin with the primary literature: Arora--Sudan (Combinatorica 2003),
Harsha--Kumar--Saptharishi--Sudan (arXiv:2311.12752), Kominers--Thaler--Zheng (ECCC TR26-147,
revision 1), and Rubinfeld--Sudan (SIAM J. Comput. 1996). Search for later refinements. For every
imported theorem, record the exact paper version, theorem or lemma number, hypotheses, constants,
and role in your proof. Do not manufacture numerical constants from asymptotic notation.

Pursue one of two modes:

1. Optimize the KTZ architecture at \((p,d)=(147457,87)\). Jointly tune popularity, pruning,
   exceptional-set, interpolation, resultant, separability, direction-mixing, rounding, and
   recovery parameters with exact integer or rational arithmetic. Propagate every marginal gain
   to the final \(\varepsilon\).
2. Seek a genuinely new bivariate architecture capable of a larger jump: direction or pencil
   structure, higher moments, energy increment, dependent random choice, nonrectangular weighted
   interpolation, multiplicities or Hasse derivatives, algebraic-curve geometry, or a direct
   one-polynomial recovery argument.

Do genuine mathematical work. Attempt adversarial tables and characteristic-dependent failure
modes. Recompute every numerical inequality. Floating-point optimization may suggest parameters
but cannot prove them; replace it with an exact certificate.

Your output must be a self-contained academic Markdown note with these sections: Abstract; Test
and Notation; Prior Results; Main Theorem or Lemma; Proof; Soundness Ledger; Counterexample
Attempts; Characteristic Audit; and Limitations. Number all proof steps `[P1]`, `[P2]`, and so on,
and give their dependency ids.

RULE: A lemma statement contains only quantified objects, hypotheses, and conclusion. It contains
no motivation, derivation, commentary, proof sketch, interpretation, history, or explanation.
Put all such material in the proof.

Classify the result honestly:

- Set `leaderboard_submission=true` only for a fully proved, numerical, end-to-end bivariate
  theorem strictly improving the current record. Set `claim_scope=bivariate_theorem`,
  `result_status=proved`, and `benchmark_improved=true`. Every load-bearing proof step and
  soundness-ledger stage must be proved. Two independent AI auditors will verify this entire
  logic chain, including every lemma used.
- For a standalone lemma, proof tool, obstruction, counterexample, conditional proof, or
  experiment, set `leaderboard_submission=false` and `benchmark_improved=false`. It will be stored
  without audit until a leaderboard proof depends on it.

Package the result using `how_to_contribute/submission_template/submission.json` and `note.md`.
Validate it with:

```bash
line-point-concrete community-validate community_submissions/<your-slug>
```

Never claim verification yourself. The repository harness promotes a result only after two
independent auditors accept the same theorem SHA-256 and the same numerical \(\varepsilon\).

