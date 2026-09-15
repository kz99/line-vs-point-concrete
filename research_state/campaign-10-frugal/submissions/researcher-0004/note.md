# Abstract

For `p=147457`, total degree `d=87`, and uniform affine-line-then-point sampling, acceptance at least

\[
\varepsilon=\frac{7249403463}{21743566849}
\]

forces one total-degree-at-most-87 polynomial to agree with the point table on at least `epsilon/10`, hence on at least `724940347` points. The score is `7249403463`, improving the verified incumbent by `100087751`.

# Test and Notation

Let `h=p+1`, `M=p²=21743566849`, `Lambda=p(p+1)=21743714306`, and `N=Mh=3206262880419842`. The accepted-incidence density equals the test acceptance `rho`.

Use weighted degree `D=15136`, derivative cap `q=15049`, point peel cap `D`, and line peel cap `k=4414`. Select three complete directions and 408 lines of a fourth direction, then add the 3776 heaviest uncovered point labels.

# Prior Results

The verified incumbent and its accepted audit are `research_state/campaign-30-leaderboard/submissions/researcher-0002/response.json` and `research_state/campaign-30-leaderboard/reviews/researcher-0002/verifier-a-researcher-0002/audit.json`. Component-potential peeling and labeled-point interpolation were independently retuned from the current frugal submissions of researchers 0001 and 0003.

# Theorem

Every point table and degree-at-most-87 affine-line table over `F_147457` with acceptance at least `7249403463/21743566849` admit one polynomial of total degree at most 87 agreeing on at least

\[
\max\left\{\frac{174}{147457},\frac{7249403463}{217435668490}\right\}
=\frac{7249403463}{217435668490}.
\]

# Proof or Conditional Proof

All steps are proved. The partial-fourth-direction miss probability at pencil degree `a` is

\[
\frac{\binom{h-a}{3}}{\binom h3}\left(1-\frac{408a}{p(h-3)}\right).
\]

Strict log-concavity and the neighboring differences certify its maximum at `a=49122`. Top-weight selection multiplies the resulting coefficient by `1−3776/M`.

There are `6702349500` eligible weighted monomials and only `442779·15137+3776=6702349499` equations. Minimum weighted degree gives a squarefree, Z-dependent relation with nonzero Z-derivative. Identity extension, coefficient-content removal, the nominal discriminant, and derivative root counting give exceptional cap `2618012` and regular-line cap `15049`.

For component densities `a,l`, centered affine mixing gives

\[
I/N\le a l+\sqrt{a(1-a)l(1-l)/h}.
\]

Writing `delta=D/h`, `theta=k/p`, maximizing over `l`, and squaring against `delta−eta` proves the potential inequality whenever the exact `L_eta` and `R_eta` quantities are nonnegative. With `a0=1/6800`, `eta1=25647317/250000000`, and `eta2=3/50000000`, the endpoint certificates are strictly positive. They give credits `66788391` and `28291`. The C4 empty-core corner gives the larger credit `133070051`; hence every no-large-component peel receives credit `28291`.

Collecting all losses gives `C=752643629163779`. With the augmented selector coefficient, absence of a component of density `epsilon/10` implies

\[
rho\le\frac{C/N+\kappa'_4}{1+\kappa'_4}
=\frac{3223268795561994597645042125366123}{9667741751820876581688555437077355}.
\]

Its product with `M` has floor `7249403462`, contradicting `rho≥epsilon`. A surviving simple-root component has point degree at least `D+1`. KTZ Lemmas 2.5, 2.7, and 6.1 give a single total-degree-at-most-87 polynomial throughout it.

# Soundness Ledger

Every numerical loss is listed in `soundness_ledger`. The final recovery is `epsilon/10`, not merely the obsolete `epsilon/10`-only contract: exact subtraction shows it exceeds `174/p`.

# Counterexample Attempts

The lower cap `k=4413` fails the component-potential endpoint exactly. Concentrated accepted directions are already covered by the pointwise selector envelope. Inseparability is excluded by `deg_Z<p`.

# Characteristic Audit

The fixed prime is Pocklington-certified. All derivative degrees are below `p`; no specialized leading coefficient is inverted; reconstruction divides only by a retained nonzero derivative.

# Limitations

Local optimality is only for the stated selector/potential neighborhood, not all architectures. The assigned checkpoint outbox was unexpectedly read-only: `apply_patch` rejected both the Markdown checkpoint and deterministic checker. The theorem itself does not depend on the exhaustive-search claim; all load-bearing rational identities are displayed here.

# Team Handoff

Builder 0007 should import `(D,r,c,k)=(15136,442779,3776,4414)`. Red-team 0009 should audit the selector and potential endpoints. Integrator 0010 should store the exact checker and bind the theorem hash before verification.
