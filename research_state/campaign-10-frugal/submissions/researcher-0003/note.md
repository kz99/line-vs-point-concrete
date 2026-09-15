# Label-Sensitive Surplus Interpolation Lowers the Fixed Score by 779

## Abstract

For `p=147457`, total degree `d=87`, and uniform affine-line-then-point sampling, the verified incumbent selects three complete directions and leaves an interpolation kernel of dimension at least `9117`. I spend `9116` of these dimensions on the actual labels of the heaviest points not covered by the selected directions. This reduces the uncovered-incidence coefficient from

\[
\kappa=\frac{1610629120}{10871857153}
\]

to

\[
\kappa'=\left(1-\frac{9116}{21743566849}\right)\kappa
=\frac{35020807257170984960}{236392952779034320897}.
\]

The resulting terminating trigger is

\[
\varepsilon=\frac{3380075810946357}{10^{16}},
\]

with score `7349490435`, improving the incumbent `7349491214` by `779`.

## Test and Notation

Set

\[
h=p+1=147458,\quad M=p^2=21743566849,
\]
\[
\Lambda=p(p+1)=21743714306,\quad N=Mh=3206262880419842.
\]

Let `E` be the accepted incidence graph, `rho=|E|/N`, and `a_x` the accepted degree of point `x`.

## Prior Results

The imported record is the doubly verified campaign-30 theorem in `research_state/campaign-30-leaderboard/submissions/researcher-0003/response.json`, theorem SHA-256 `53c9e438528bd0576c18932996e7607f719d4f9e051243f15e86889aae6b4762`. Its exact audits are in `research_state/campaign-30-leaderboard/reviews/researcher-0003/verifier-a-researcher-0003/audit.json` and the verified-results ledger. Its interpolation count is

\[
6693082347-442371\cdot15130=9117.
\]

The sensitivity and partial-direction obstruction are recorded in `research_state/campaign-30-leaderboard/submissions/researcher-0001/response.json`. The present proof uses the self-contained version of the incumbent modules, so it has no load-bearing primary-paper dependency.

## Theorem

Let `p=147457`, `d=87`, and `epsilon=3380075810946357/10^16`. Every point table and every affine-line table of univariate degree at most `87` with acceptance at least `epsilon` admit a polynomial in `F_p[X,Y]` of total degree at most `87` agreeing with the point table on more than `epsilon/10` of `F_p²`.

## Proof

[P1, proved] The verified three-direction averaging lemma supplies three directions whose `3p=442371` lines leave uncovered accepted-incidence mass

\[
U\le \kappa(1-\rho)N.
\]

[P2, proved] Choose the `k=9116` largest weights `a_x` among uncovered points, or every uncovered point if there are fewer. For nonnegative weights totaling `U` on at most `M` points, their top `k` values total at least `kU/M`. After declaring these points covered, the residual mass satisfies

\[
U'\le\left(1-\frac{k}{M}\right)U
\le\kappa'(1-\rho)N.
\]

[P3, proved] Impose the original formal identities on the `442371` selected labeled lines and additionally impose `A(x,f(x))=0` at the selected points. Weighted degree `D=15129` gives `6693082347` monomials. The line identities impose at most `6693073230` equations and the point labels impose at most `9116`, leaving dimension at least one.

Every nonzero solution is Z-dependent. Choose one of minimum weighted degree. Dividing out one copy of a repeated irreducible factor preserves every formal line identity and every added point zero. The incumbent repeated-factor argument also preserves a nonzero Z-derivative. Minimality therefore gives a squarefree `A` with `A_Z` nonzero and `deg_Z A≤173<p`.

[P4, proved] Redefine a covered point to mean either a point hit by an accepted selected-direction line or one of the additional labeled points. At every covered point, `A(x,f(x))=0`. Hence any unselected line containing more than `D` covered accepted points is an A-identity line. The identity-extension inequality becomes

\[
|E|\le |E_T|+U'+D(\Lambda-|T|).
\]

[P5, proved] The verified primitive cleanup, nominal-discriminant estimate, and C4-free peeling apply unchanged. Their parameters are

\[
q=D-d=15042,\quad E_D=2615604,
\]

line threshold `s=5195`, and peeling credit `156513678`. Complete deletion would imply

\[
\rho\le \frac{C_*}{N}+\kappa'(1-\rho),
\qquad C_*=769296828797543.
\]

[P6, proved] The strict frontier is

\[
R'=\frac{C_*/N+\kappa'}{1+\kappa'}
=\frac{61159938999447089357}{180942506690803537238}.
\]

At the claimed terminating epsilon,

\[
\varepsilon-\frac{C_*}{N}-\kappa'(1-\varepsilon)
=\frac{64670249872480163804912949}
{2363929527790343208970000000000000000}>0.
\]

Thus a nonempty `(15130,5195)` simple-root core survives.

[P7, proved] The incumbent affine-incidence component argument applies with `tau=epsilon/10`. Its endpoint polynomial satisfies `F(tau)>0`, `F'(tau)<0`, and `F''=2(1-1/h)>0`; hence every connected core component contains more than `tau M` points. The incumbent formal implicit-lifting and propagation argument then produces one total-degree-at-most-87 polynomial agreeing throughout that component.

Finally,

\[
\frac{\varepsilon}{10}-\frac{174}{147457}
=\frac{481015838854716964149}{14745700000000000000000}>0.
\]

Therefore the required maximum is `epsilon/10=3380075810946357/10^17`, and

\[
\left\lceil\varepsilon M\right\rceil=7349490435,
\qquad
\left\lceil\frac{\varepsilon M}{10}\right\rceil=734949044.
\]

This proves the theorem.

## Soundness Ledger

| Stage | Exact loss or gain |
|---|---:|
| Three-direction coverage | `kappa(1-rho)N` |
| Label-sensitive point constraints | gain factor `1-9116/M` |
| Interpolation | `442371·15130+9116` equations; surplus `1` |
| Identity extension | `15129(Λ-t)` |
| Exceptional lines | at most `p·2615604` incidences |
| Derivative roots | at most `15042(t-e)` |
| C4 peeling | `15129M+5194(t-e)-156513678` |
| Fixed subtotal | `C*=769296828797543` |
| Component conversion | no deletion; exact incidence mixing |
| Reconstruction | zero agreement loss |
| Final agreement | `epsilon/10`, at least `734949044` points |

## Counterexample Attempts

Three noncollinear point pencils use the same `3p` line budget but give coefficient approximately `0.148148148093641`, worse than the incumbent. A two-direction/one-pencil/one-line hybrid gives approximately `0.148147310890715`, also worse. These exact negative results rule out the most economical pencil replacements.

## Characteristic Audit

All Z-degrees are at most `173<p`. Added point constraints introduce no derivative, discriminant, irreducibility, or interpolation-multiplicity issue. Repeated-factor removal preserves both line identities and point zeros. The inherited cleanup never divides by a specialized leading coefficient, and reconstruction divides only by a certified nonzero simple-root derivative.

## Limitations

The improvement uses only the guaranteed rank-nullity surplus. It does not prove an additional rank deficit, optimize multiplicity constraints, or improve the C4 corner. The campaign-10-frugal history file is presently empty; comparison is against the imported doubly verified campaign-30 record specified by the task.

## Team Handoff

- `researcher-0008`: import [P2]–[P4] as the label-sensitive coverage module.
- `researcher-0009`: audit squarefree reduction with the added point-zero invariant.
- `researcher-0010`: integrate `kappa'`, `R'`, the terminating epsilon, score `7349490435`, and recovery count `734949044`.
- Interpolation/rank module: seek a certified rank deficit beyond the current guaranteed surplus `9117`.
- Verifier: replay the incumbent checker after replacing `kappa` by `kappa'` and adding the single identity `6693082347−6693073230−9116=1`.
