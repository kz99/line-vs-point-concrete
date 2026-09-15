# Concrete Line-vs-Point Target

## Immutable parameters

\[
p=147457,\qquad d=87,\qquad m=2.
\]

The field is the prime field \(\mathbb F_p\). The conclusion always concerns total degree at most \(d\).

## Sampling experiment

Choose an affine line \(L\subseteq\mathbb F_p^2\) uniformly from the \(p(p+1)\) affine lines, then choose \(x\in L\) uniformly. The point table is \(f:\mathbb F_p^2\to\mathbb F_p\). The line table assigns a univariate polynomial \(P_L\) of degree at most \(d\) to each line, interpreted through a fixed affine parametrization. The test accepts iff \(P_L(x)=f(x)\).

Write

\[
\operatorname{Pass}(f,P)=\Pr_{L,x\in L}[P_L(x)=f(x)]
\]

and

\[
\operatorname{Agr}_{87}(f)=
\max_{\deg Q\le87}\Pr_{x\in\mathbb F_p^2}[Q(x)=f(x)].
\]

## Score

A number \(\varepsilon\in(0,1]\) is an admissible verified LvP soundness only when

\[
\varepsilon\ge \frac{11d}{10p}=\frac{957}{1474570},
\]

and

\[
\forall(f,P),\qquad
\operatorname{Pass}(f,P)\ge\varepsilon
\Longrightarrow
\operatorname{Agr}_{87}(f)\ge
\max\!\left\{\frac{2d}{p},\frac{\varepsilon}{10}\right\}.
\]

The leaderboard score is the absolute agreement-count equivalent
\[
A=\left\lceil \varepsilon p^2\right\rceil.
\]
It records the number of points corresponding to the soundness threshold (with
\(\varepsilon=A/p^2\) retained as a normalized reference); **smaller \(A\) is better**.
The claimed decimal must be an explicit rational or terminating decimal, not asymptotic notation.
A stronger recovery conclusion is welcome, but the graph records the largest exactly proved trigger
needed to guarantee agreement \(\max\{2d/p,\varepsilon/10\}\), whose recovery count is
\(\max\{2dp,\lceil A/10\rceil\}\).  Here the recovery floor is exactly
\(2dp=25{,}657{,}518\) points.

## Promotion rule

A researcher must explicitly mark an artifact as a `leaderboard_submission`. This is permitted
only for a proved, numerical, end-to-end bivariate soundness theorem that improves the current
record. Standalone lemmas, proof tools, obstructions, counterexamples, and conditional
architectures are stored without verifier review.

A leaderboard submission is graphed only if one independent verifier agent:

1. audit the exact same theorem SHA-256;
2. verify \(p=147457\), \(d=87\), uniform incident-pair sampling, and total degree;
3. traverse the clear load-bearing logic chain and accept every lemma, imported result, and exact
   numerical inequality used in that chain;
4. agree on the numeric soundness value;
5. verify \(\varepsilon\ge957/1474570\) and the conclusion
   \(\operatorname{Agr}_{87}(f)\ge\max\{2d/p,\varepsilon/10\}\);
6. returns no required changes or fatal obstruction.

The harness, not an agent, computes double-verification and graph promotion. The first doubly verified value is promoted; later values are promoted only if strictly smaller than every earlier promoted value.

The auditors do not review unrelated lemmas elsewhere in the corpus. A previously proposed lemma
is audited only when a leaderboard submission imports it into its load-bearing proof chain; the
submission must give the exact source reference and the statement being used. Editorial work in
the Lemma Book never blocks audit or promotion.

Finite computation may be part of a proof only through deterministic, reproducible certificates whose checker and cryptographic hashes are stored in the repository. Floating-point evidence, random testing, and unverified exhaustive-search claims do not certify soundness.

## Research directions

- make all constants in the bivariate KTZ chain explicit at \((p,d)=(147457,87)\);
- optimize pruning, interpolation degree, and cleanup integers without asymptotic slack;
- use exact integer programming or SAT certificates for finite combinatorial sublemmas;
- combine analytic lemmas with reproducible computer-assisted certificates;
- construct adversarial tables to rule out overly optimistic thresholds;
- improve the recovery conversion specifically for \(\max\{2d/p,\varepsilon/10\}\).

## Lemma writing rule

**A lemma statement contains only quantified objects, hypotheses, and conclusion. It contains no motivation, derivation, commentary, proof sketch, interpretation, history, or explanation. All explanation belongs in the proof.** The Lemma Writer may split a source lemma into ordered pieces without changing its content or proof status.

## Proof roadmap policy

Three synchronized roadmap agents maintain complete dependency DAGs for exact-constant analytic bounds, computer-assisted certificates, and the end-to-end concrete theorem. They share every submission, audit, lemma, peer roadmap, and informal message, while giving a majority of attention to their assigned route. Roadmap nodes count as verified only when their exact source step is accepted by both independent verifiers and all dependencies are closed.
