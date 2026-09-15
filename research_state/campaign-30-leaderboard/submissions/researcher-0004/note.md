# Fixed-field interpolation and simple-transition reconstruction at p=147457

## Abstract

For `F=F_147457`, line-label degree `d=87`, weighted degree `D=17642`, and `r=600782` selected affine lines, I prove a self-contained algebraic package. Exact coefficient counting yields a nonzero squarefree interpolant with `A_Z≠0` and surplus `1281`. Removing its coefficient content produces a primitive polynomial `B` with `gcd(B,B_Z)=1` and derivative weighted degree at most `17555`.

I then independently prove the `D+1=17643` simple-root seed-lifting interface and a stronger propagation statement. Lines are connected only through accepted intersections at which the common root is simple. One seed star recovers a single total-degree-at-most-87 global root on its entire connected line component. Every accepted point on a recovered line is an agreement point, even when that point is singular and is not used for propagation.

The package introduces no probabilistic or agreement loss. It supplies the algebraic interfaces needed by the unproved candidate `epsilon_*=7810919590/21743566849`, whose score is `7810919590`, or `1187` below the configured comparison count. It is not an end-to-end soundness proof.

## Test and Notation

The verifier chooses a uniformly random affine line in `F^2` and then a uniformly random point on it. Thus there are

- `p^2=21743566849` points;
- `p(p+1)=21743714306` affine lines;
- `p^2(p+1)=3206262880419842` incident pairs.

For a monomial `X^i Y^j Z^k`, set

`wdeg(X^i Y^j Z^k)=i+j+87k`.

The proved algebraic parameters are

| parameter | value |
|---|---:|
| field size `p` | `147457` |
| line and recovered degree `d` | `87` |
| weighted degree `D` | `17642` |
| selected lines `r` | `600782` |
| maximum `Z`-degree | `202` |
| seed size `D+1` | `17643` |
| derivative weighted-degree cap `D-d` | `17555` |

The surrounding candidate additionally uses `j=51837`, final line degree `s=5495`, exceptional-line cap `3559710`, and C4 credit `193111783`; none of those four quantities is used to prove the lemmas below.

The configured comparison is `epsilon_0=0.35922904602094702`, with score `7810920777`. The candidate integration target is

`epsilon_*=7810919590/21743566849`,

with required agreement

`epsilon_*/10=781091959/21743566849`.

A strict component-density conclusion above this value would contain at least `781091960` points.

## Prior Results

The active campaign-30 corpus index and Lemma Book are empty, and its soundness history contains no promoted point. The older campaign-10 chain at `359229046020947/10^15` was double-audited and was consulted to avoid repeating its certified arithmetic. In particular, its values `D=17642`, `r=600782`, monomial count `10599598107`, and surplus `1281` are reused rather than presented as a new optimization.

The exact primary counterparts are [KTZ revision 1](https://eccc.weizmann.ac.il/report/2026/147/revision/1/download): Lemmas 2.3 and 4.2 for minimum-weight squarefree interpolation, Lemma 2.5 for formal line vanishing, Lemma 2.7 for Newton lifting, Lemma 6.1 for seed reconstruction, and Lemma 6.3 for component propagation. The Newton statement originates in [HKSS v1](https://arxiv.org/html/2311.12752v1), Lemma 2.10. HKSS Lemma 3.1 has materially different large-set hypotheses and is not quoted as the present seed lemma.

All results below are proved directly. No numerical constant from KTZ Theorem 1.1 is imported; that theorem has unspecified absolute constants and its displayed bivariate recovery is `epsilon/8000`, not the required `epsilon/10`.

The message board also identifies a specification-level obstruction: every point table agrees with a constant on at least `1/p` of the plane. Consequently every positive `epsilon≤10/p` is formally sound and score `1` is attainable. The present package concerns the nontrivial analytic route, not that leaderboard shortcut.

## Theorem

**Lemma 1 (fixed interpolation).** Let `R` be any set of `600782` distinct affine lines in `F^2`, with an affine parametrization `L(t)` and a polynomial `P_L∈F[t]` of degree at most `87` for every `L∈R`. There exists a nonzero squarefree `A∈F[X,Y,Z]` such that `wdeg(A)≤17642`, `deg_Z(A)≤202`, `A_Z≠0`, and `A(L(t),P_L(t))=0` in `F[t]` for every `L∈R`.

**Lemma 2 (primitive separability).** Let `A∈F[X,Y,Z]` be nonzero and squarefree, with `A_Z≠0`, `wdeg(A)≤17642`, and `deg_Z(A)≤202`. Write `A=CB`, where `C∈F[X,Y]` is the coefficient content in `Z` and `B∈F[X,Y,Z]` is primitive in `Z`. Then `1≤deg_Z(B)≤202`, `B` is squarefree, `gcd(B,B_Z)=1`, `deg(C)+wdeg(B)=wdeg(A)`, and `wdeg(B_Z)≤wdeg(B)-87≤17555`.

**Lemma 3 (seeded simple-transition reconstruction).** Let `B∈F[X,Y,Z]` have `(1,1,87)`-weighted degree at most `17642`. Let `T` be a set of affine lines, each carrying a polynomial `P_L` of degree at most `87` satisfying `B(L(t),P_L(t))=0` in `F[t]`. Let `f:F^2→F`, and let `E` consist of incidences `(x,L)` satisfying `P_L(x)=f(x)`. Define a graph on `T` by joining distinct lines `L,M` when their intersection `x` satisfies `(x,L),(x,M)∈E` and `B_Z(x,f(x))≠0`. If a point `b` is incident in `E` to `17643` distinct lines and `B_Z(b,f(b))≠0`, then there is a polynomial `Q∈F[X,Y]` of total degree at most `87` satisfying `B(X,Y,Q(X,Y))=0`. Moreover, on the connected line component containing those seed lines, `Q|_L=P_L` for every line `L`, and `Q(x)=f(x)` at every accepted point incident to any such line.

**Corollary 4 (fixed core).** Let `K` be a nonempty connected point-line incidence subgraph whose point degrees are at least `17643`. Suppose every edge is accepted, every line label is a formal root of one polynomial `B` of weighted degree at most `17642`, and `B_Z(x,f(x))≠0` at every point vertex. Then one polynomial `Q∈F[X,Y]` of total degree at most `87` agrees with every line label and with `f` at every point vertex of `K`.

## Proof

### [P1] Exact interpolation dimension — proved

Since `17642=87·202+68`, the number of monomials of weighted degree at most `17642` is

`V=sum_{z=0}^{202} binom(17642-87z+2,2)`.

Putting `j=202-z`, using `sum j=20503` and `sum j^2=2767905`, gives

`V=(7569·2767905+12093·20503+4830·203)/2=10599598107`.

On any labeled line, substitution has degree at most `D`, so a formal identity imposes at most `D+1=17643` homogeneous linear equations. The total is

`600782·17643=10599596826`,

leaving surplus `1281`.

### [P2] Squarefree formal interpolant — proved

Rank-nullity supplies a nonzero kernel element `A`. If it were independent of `Z`, its restriction would vanish formally on all `600782>D` distinct lines. The defining affine-linear form of every line would then divide `A`, contradicting `deg(A)≤D`. Thus every nonzero kernel element depends on `Z`.

Weighted degree gives `deg_Z(A)≤202<p`. Differentiation in `Z` is therefore injective on the positive-`Z` part, so `A_Z≠0`.

Choose a nonzero kernel element of minimum weighted degree. If `A=F^eG` with `e≥2` and `F` irreducible, then on each selected line graph the product specializes to zero in the domain `F[t]`. Hence either the specialization of `F` or that of `G` is zero, and `A/F=F^(e-1)G` still vanishes identically on every graph. Its weighted degree is smaller, a contradiction. Thus `A` is squarefree. This proves Lemma 1 using coefficient identities directly; no pointwise-to-formal conversion is needed.

### [P3] Primitive `Z`-separability — proved

Write `A=CB` as in Lemma 2. Weighted leading forms do not cancel in the domain `F[X,Y,Z]`, so

`deg(C)+wdeg(B)=wdeg(A)≤17642`.

Because `A` is squarefree, so is `B`. Primitivity implies that no irreducible factor of `B` lies in `F[X,Y]`; such a factor would divide every `Z`-coefficient. Every irreducible factor therefore has positive `Z`-degree at most `202<p`, and consequently has nonzero ordinary `Z`-derivative.

Reducing the product rule for `B_Z` modulo any irreducible factor of the squarefree `B` shows that factor does not divide `B_Z`. Hence `gcd(B,B_Z)=1`. Finally, differentiation lowers weighted degree by exactly `87` on each surviving monomial, giving

`wdeg(B_Z)≤wdeg(B)-87≤17642-87=17555`.

No discriminant or specialized leading coefficient is used.

### [P4] Formal lifting and seed globalization — proved

Translate a seed point `b` to the origin and put `a=f(b)`. Translation does not increase weighted degree. Let `m=(X,Y)` and `c=B_Z(0,0,a)≠0`.

Construct homogeneous polynomials `h_n` recursively. Suppose `a+h_1+...+h_(n-1)` solves `B=0` modulo `m^n`. If `R_n` is the homogeneous degree-`n` part of the residual, adding a homogeneous `h_n` changes that part by exactly `c h_n`. Taking `h_n=-c^(-1)R_n` gives the unique solution modulo `m^(n+1)`. This uses only division by `c`, never by `n!`.

Let `Q=a+h_1+...+h_87`. Reparametrize each seed line as `b+tv`; the submitted polynomial changes by an affine substitution in `t`, preserving degree at most `87`. The univariate version of the same recursion shows that `Q(b+tv)` and the seed label have identical coefficients through degree `87`. Both have degree at most `87`, so they are equal.

Now set `R(X,Y)=B(X,Y,Q(X,Y))`. Every monomial of `B` gives total degree at most its `(1,1,87)` weight after substitution, hence `deg(R)≤17642`. The polynomial `R` vanishes formally on `17643>D` distinct seed lines. Their distinct affine-linear equations divide `R`, so `R=0`. This proves the seed portion of Lemma 3.

### [P5] Propagation through simple transitions — proved

Suppose `Q|_L=P_L` and `L` is joined to `M` at `x`. Then

`Q(x)=P_L(x)=f(x)=P_M(x)`.

Both `Q|_M` and `P_M` are exact roots of `B(M(t),Z)` through this common value. Since `B_Z(x,f(x))≠0`, the one-variable recursion from [P4] has a unique formal root with that constant term. Therefore `Q|_M=P_M`.

Induction along paths proves equality on the whole connected line component. Once a line is recovered, every accepted point `x` on it satisfies `Q(x)=P_L(x)=f(x)`, irrespective of whether `B_Z(x,f(x))` vanishes there. Thus singular points may be retained as agreement leaves; simplicity is needed only where the proof crosses from one line to another.

For Corollary 4, choose any point as the seed. Its degree supplies `17643` lines. Connectedness of the bipartite core and simplicity at its point vertices make the corresponding line-transition graph connected. Lemma 3 applies.

### [P6] Exact score relevance — proved

For the configured decimal,

`epsilon_0 p^2=7810920776+25895898365733998/10^17`,

so its score is `7810920777`. For

`epsilon_*=7810919590/21743566849`,

one has `epsilon_*p^2=7810919590` and

`epsilon_*/10=781091959/21743566849`.

Thus the candidate score is smaller by exactly `1187`. Lemmas 1–3 lose no acceptance or agreement and discharge the interpolation and reconstruction interfaces of that candidate. The remaining energy, identity-transfer, discriminant, C4-peeling, survival, and component-mass statements are not proved here, so `epsilon_*` is not claimed as soundness.

### [P7] Sharpness of `D+1` — proved

Choose `D=17642` distinct homogeneous linear forms `ell_1,...,ell_D`, possible because the pencil has `p+1=147458` directions. Put

`H=product_i ell_i` and `B=Z-H`.

Then `wdeg(B)=D`, `B_Z=1`, and the zero polynomial is an exact line root on every chosen line. Any global polynomial root of `B` must equal `H`, whose total degree is `D>87`. Hence `D` seed lines do not imply the global degree-87 root conclusion; `D+1` is sharp for this interface.

### [P8] Singular, inseparable, and content obstructions — proved

At the origin, `B=Z^2-XY` has `B_Z=0`. For every nonzero square slope `s=r^2`, the line `(t,st)` carries the root `rt`; both coordinate axes carry root zero. This gives `(p-1)/2+2=73730` root lines through one common value, yet `Q^2=XY` has no polynomial solution because the prime-factor exponents of `XY` are odd.

The polynomial `Z^p-X` is squarefree because its `X`-derivative is `-1`, but its `Z`-derivative is zero. This is excluded by `deg_Z≤202<p`.

Finally, `A=X(Z-Y)` is squarefree and has `A_Z=X`, yet on `X=0` its identity is independent of the line label. Its coefficient content is exactly `X`; dividing it out produces the informative primitive factor `Z-Y`.

## Soundness Ledger

| stage | input | exact loss | output | status |
|---|---|---:|---|---|
| sampling context | uniform affine line then point | `0` | incident-pair denominator `3206262880419842` | proved |
| interpolation | `r=600782`, `D=17642` | `0`; surplus `1281` | squarefree `A`, `A_Z≠0` | proved |
| content removal | squarefree `A`, `deg_Z≤202<p` | no degree slack beyond `deg C+wdeg B=wdeg A` | primitive `B`, `gcd(B,B_Z)=1` | proved |
| derivative degree | `wdeg(B)≤17642` | weight decrement exactly `87` | `wdeg(B_Z)≤17555` | proved |
| seed reconstruction | `17643=D+1` simple identity lines | `0` agreement loss | one global total-degree-87 root | proved |
| transition propagation | accepted simple crossings | `0` agreement loss | same polynomial on a connected line component | proved |
| leaf recovery | every accepted point on a recovered line | `0`; no simplicity required at leaves | all such points agree with `Q` | proved |
| candidate integration | `epsilon_*=7810919590/p^2` | algebraic stages add `0` | target `781091959/p^2`, or `781091960` points after a strict component bound | conditional |

No union bound, Markov inequality, Cauchy–Schwarz inequality, randomized selection, multiplicity interpolation, resultant, or discriminant loss occurs in this package.

## Counterexample Attempts

The `Z-product ell_i` construction proves that the seed threshold cannot be lowered from `D+1` to `D` for an arbitrary weighted-degree-`D` relation, even with everywhere nonzero `B_Z` on the seed.

The `Z^2-XY` construction survives squarefreeness and many more than `D` root directions. It shows that a singular common value permits incompatible branches and blocks globalization.

The `Z^p-X` construction shows that squarefreeness alone is not a separability certificate in characteristic `p`. The strict `Z`-degree bound is load-bearing.

The content example shows why an interpolating identity must be made primitive before it is interpreted as constraining a line label.

Acceptance concentrated in a set of directions does not contradict the result: the seed lemma is explicitly a pencil statement and assumes no direction spreading.

## Characteristic Audit

The immutable field is the prime field `F_147457`. The historical Pocklington certificate factors `p-1=2^14·3^2` and verifies the necessary base-10 modular residues.

All positive `Z`-exponents in the interpolant lie in `{1,...,202}`, so none is zero modulo `p`. Ordinary differentiation is therefore sufficient. After primitive cleanup every irreducible factor has positive `Z`-degree, making `gcd(B,B_Z)=1` valid.

Formal lifting divides only by the explicitly retained scalar `B_Z(b,a)`. It does not divide by derivatives of higher order, factorials, discriminants, resultants, or leading coefficients. No Hasse derivative is required.

Interpolation has multiplicity one and is imposed coefficientwise. Reparametrizing a fixed affine line at a seed or transition point uses an invertible affine change of its parameter and preserves degree `87` and formal identities.

## Limitations

This is an algebraic lemma package, not a soundness theorem. It does not prove the candidate whole-pencil energy inequality, identity-transfer ledger, nominal-discriminant cap `3559710`, C4 credit, core survival, or component-mass inequality.

The primitive-separability lemma establishes `gcd(B,B_Z)=1` but does not itself count derivative-degenerate lines. That downstream count must use nominal-degree homogenization and must not divide by a specialized leading coefficient.

The `D+1` threshold is sharp for arbitrary relations, so an improvement must exploit additional structure in the interpolant or replace the seed-root architecture. The transition formulation can reduce where simplicity is required, but it yields a numerical gain only if a downstream combinatorial argument certifies substantial singular leaf mass or a cheaper connected simple-transition skeleton.

The literal leaderboard is degenerate: unconditional constant recovery gives every `0<epsilon≤10/p` formal soundness and permits score `1`. Accordingly this submission is not marked as a leaderboard improvement.

The active campaign manifest is stale and contains no campaign-30 evidence hashes. Promotion policy is also inconsistent between the target/configuration and older README text; this must be resolved before any endpoint submission.

## Team Handoff

- `researcher-0008` and `exact-analytic/ea-r1-02`: use [P1]–[P2] verbatim for the `1281`-surplus squarefree interpolant.
- `researcher-0009`, `researcher-0017`, and `ea-r1-04`: use [P3] for primitive `Z`-separability and the exact `17555` derivative degree; still prove the nominal-discriminant line cap separately.
- `researcher-0014`, `researcher-0020`, and `researcher-0024`: use [P5]'s simple-transition graph to test two-layer cleanup in which singular leaves remain countable agreement points.
- `ea-r1-08`, `ea-r1-09`, `researcher-0025`, and `researcher-0029`: use [P4]–[P5] as the self-contained one-polynomial recovery module, with no KTZ black-box dependency and no agreement loss.
