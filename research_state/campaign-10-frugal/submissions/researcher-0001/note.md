# Component-Potential Peeling at Score 7,249,456,451

## Abstract

For `m=2`, `p=147457`, and total degree `d=87`, a component-aware peeling potential lowers the verified score from `7349491214` to

\[
A=7249456451,
\qquad \varepsilon=\frac{A}{p^2}=0.3334069567033068\ldots .
\]

The proof retains the incumbent three-direction interpolation and primitive cleanup, but peels lines at degree at most `k=4415`. Exact affine mixing shows that every surviving component below density `ε/10` contributes at least `66772609` incidences of negative potential. Acceptance above the resulting frontier therefore forces a sufficiently large component. Simple-root reconstruction then gives one total-degree-at-most-87 polynomial on at least `724945646` points.

## Test and Notation

Let `F=F_147457`, `h=p+1=147458`,

\[
M=p^2=21743566849,\quad \Lambda=p(p+1)=21743714306,
\quad N=Mh=3206262880419842.
\]

The test samples a uniform affine line and then a uniform point on it, hence is uniform on the `N` incidences. Let `E` be the accepted-incidence graph and `ρ=|E|/N`.

Set

\[
D=15129,\quad q=D-87=15042,\quad k=4415,
\quad E_D=2615604,
\]

and

\[
\kappa=\frac{1610629120}{10871857153}.
\]

## Prior Results

The active submissions, leaderboards, message board, and verifier audits were inspected with every `superseded` directory excluded. The verified incumbent and its exact chain are in [researcher-0003/note.md](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/submissions/researcher-0003/note.md:1), with the accepting [audit](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/reviews/researcher-0003/verifier-a-researcher-0003/audit.json:1). The authoritative imported record is in [soundness-history.json](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/leaderboards/soundness-history.json:1).

The present proof reproduces the needed interpolation, cleanup, mixing, and reconstruction arguments; no primary-source theorem is imported. KTZ revision-1 Lemmas 2.5, 2.7, and 6.1 are analogous interfaces but are not load-bearing dependencies here.

## Theorem

For every `f:F^2→F` and every assignment of a degree-at-most-87 polynomial to each affine line, if

\[
\operatorname{Pass}(f,P)\ge \frac{7249456451}{21743566849},
\]

then some `Q∈F[X,Y]` of total degree at most `87` satisfies

\[
\Pr_x[Q(x)=f(x)]\ge
\max\left\{\frac{174}{147457},
\frac{7249456451}{217435668490}\right\}
=\frac{7249456451}{217435668490}.
\]

Consequently `Q` agrees with `f` on at least `724945646` points.

## Proof

### [P1] Field and incidence arithmetic — proved

The factorization `p−1=2^14·3^2`, together with

\[
10^{p-1}=1,\quad 10^{(p-1)/2}=p-1,\quad
10^{(p-1)/3}=78348\pmod p
\]

and the two corresponding Pocklington gcds equal to one proves primality. Standard affine-plane counting gives `M,Λ,N` above.

### [P2] Three-direction coverage — proved

For a point of accepted degree `a`, a uniform three-direction set misses its accepted pencil with probability

\[
H_a=\binom{h-a}{3}/\binom h3.
\]

The integer maximum of `aH_a/(h−a)` occurs at `a=49152`, giving

\[
aH_a\le \kappa(h-a).
\]

Averaging therefore selects three complete directions whose uncovered accepted incidences satisfy

\[
U\le \kappa(1-\rho)N.
\]

### [P3] Interpolation — proved

The number of `(1,1,87)`-weighted monomials of weight at most `D` is

\[
\sum_{z=0}^{173}\binom{D-87z+2}{2}=6693082347,
\]

whereas the `3p=442371` selected line graphs impose at most

\[
442371(D+1)=6693073230
\]

constraints. A nonzero interpolant `A(X,Y,Z)` exists. It depends on `Z`, since a `Z`-independent polynomial of degree at most `D` cannot contain more than `D` distinct line factors. Choosing minimum weighted degree makes `A` squarefree. Moreover `deg_Z(A)<=173<p`, so `A_Z` is nonzero.

### [P4] Identity extension and cleanup — proved

Let `t` be the number of formal identity lines. Every omitted line has at most `D` covered accepted points, so

\[
|E|\le U+D(\Lambda-t)+|E_T|.
\]

Write `A=HB`, with `H` the coefficient content and `B` primitive in `Z`. Squarefreeness, primitivity, and `deg_Z(B)<p` give `gcd(B,B_Z)=1`. The nominal projective discriminant bounds content or derivative-degenerate identity lines by

\[
E_D=172(2D-87\cdot173)=2615604.
\]

If `z<=E_D` is their number, each remaining identity line has at most `q=D−87=15042` derivative-zero accepted points. Thus, for the cleaned graph `G` on `n=t−z` regular lines,

\[
|E_T|\le pz+q(t-z)+|E(G)|.
\]

### [P5] Exact affine mixing — proved

For `X⊆F^2`, `S` a line set, put `a=|X|/M` and `ℓ=|S|/Λ`. Ordered-pair counting gives

\[
\sum_L(|X\cap L|-ap)^2=p^3a(1-a).
\]

Centering the indicator of `S` and applying Cauchy–Schwarz yields

\[
\frac{I(X,S)}N\le a\ell+
\sqrt{\frac{a(1-a)\ell(1-\ell)}h}. \tag{1}
\]

### [P6] Component-potential inequality — proved

Put `δ=D/h` and `θ=k/p`. For `η>=0`, set `δ'=δ−η`,

\[
Q_\eta=4\delta'(\delta'-1)+1/h,
\quad L_\eta(a)=4\delta'\theta-1/h+Q_\eta a,
\]

\[
R_\eta(a)=\theta+(2\delta'-1)a.
\]

The maximum over `0<=ℓ<=1` of the right side of (1) minus `δa+θℓ` equals

\[
\frac{a-\theta+
\sqrt{(a-\theta)^2+a(1-a)/h}}2-\delta a.
\]

If `R_η(a)>=0` and `L_η(a)>=0`, squaring proves

\[
I(X,S)\le D|X|+k|S|-\eta h|X|. \tag{2}
\]

Take

\[
\eta_1=512709/5000000,
\quad a_0=1/6800,
\quad \eta_2=1/7000,
\quad \tau=A/(10M).
\]

Both `Q_η` are negative. Exact endpoint checks are

\[
L_{\eta_1}(a_0)=
\frac{41436535638699821004697}
{34066774131425322500000000000000}>0,
\]

\[
R_{\eta_1}(a_0)=
\frac{5506553545490942523}{184821571601000000000}>0,
\]

\[
L_{\eta_2}(\tau)=
\frac{1125384432788401834891}
{14479166549516565012602500000}>0,
\]

\[
R_{\eta_2}(\tau)=
\frac{192575713292549221}{56109600407347235000}>0.
\]

Thus (2) holds with `η1` for `a<=a0` and with `η2` for `a0<=a<=τ`.

### [P7] Component-aware peeling — proved

Peel points of current degree at most `D` and lines of current degree at most `k`. A nonempty residual component has at least `k+1=4416` points. If its point density is below `τ`, its potential is at most

\[
-\left\lceil\eta_1h(4416)\right\rceil=-66772609
\]

in the small range, or at most

\[
-\left\lceil\eta_2a_0N\right\rceil=-67358464
\]

in the large range.

If the peel empties, the C4-free residual-corner calculation gives `Z<=550550` and empty-core credit

\[
2Dk-Z=133038520>66772609.
\]

(The `n<D` boundary equals `M+k(D−1)−133038520=21677318449>0`.) Therefore, if no residual component reaches density `τ`, uniformly

\[
|E(G)|\le DM+k(t-z)-66772609. \tag{3}
\]

### [P8] Survival — proved

Combining [P2], [P4], and (3), and using the positive coefficients

\[
q+k-D=4328,
\qquad p-q-k=128000,
\]

gives

\[
|E|\le U+C,
\]

where

\[
C=(q+k)\Lambda+DM+(p-q-k)E_D-66772609
\]

\[
=423067449251842+328958422858521
+334797312000-66772609
=752360602649754.
\]

Thus absence of a large component implies

\[
\rho\le \frac CN+\kappa(1-\rho),
\]

whose frontier is

\[
R=\frac{613678839472717}{1840629978357761}.
\]

At `ε=A/M`,

\[
\varepsilon-\frac CN-\kappa(1-\varepsilon)
=\frac{4190366454}{236392952779034320897}>0.
\]

Hence a component of point density at least `τ` survives.

### [P9] Polynomial reconstruction — proved

Every residual point has at least `D+1` accepted simple-root identity lines. At one point, homogeneous implicit recursion through degree `87`, dividing only by its nonzero `B_Z`, constructs `Q` of total degree at most `87`. Its restrictions equal the labels on `D+1` seed lines. Since `B(X,Y,Q)` has degree at most `D` and vanishes on more than `D` lines, it is identically zero. Simple-root uniqueness propagates the same `Q` through the connected component. Thus `Q=f` on every component point.

### [P10] Contract and score — proved

Exact subtraction gives

\[
\varepsilon-\frac{957}{1474570}
=\frac{72353448161}{217435668490}>0,
\]

\[
\frac\varepsilon{10}-\frac{174}{147457}
=\frac{6992881271}{217435668490}>0.
\]

Thus the required maximum is `ε/10`, and its integer count is

\[
\left\lceil A/10\right\rceil=724945646.
\]

Finally `ceil(εp²)=A=7249456451`, improving `7349491214` by `100034763`.

## Soundness Ledger

| Stage | Exact loss or credit |
|---|---:|
| three-direction coverage | `κ(1−ρ)N` |
| identity extension | `D(Λ−t)` |
| exceptional identities | `pz`, `z<=2615604` |
| derivative roots | `15042(t−z)` |
| point/line peeling | `DM+4415(t−z)` |
| no-good-component credit | `−66772609` |
| fixed subtotal | `C=752360602649754` |
| component conversion | one centered Cauchy–Schwarz bound |
| reconstruction | zero agreement loss |
| final contract | factor `1/10`; `724945646` points |

There is no Markov, union-bound, randomized-computation, or hidden reconstruction loss.

## Counterexample Attempts

The direct `s=5194` endpoint remains negative, so minimum degrees alone do not certify the target. Exact `k=4414` potential arithmetic also fails: its component-compatible score ceiling is `7249018675`, versus survival score `7249328431`. These failures motivated the component-potential charge rather than an unsupported endpoint repair.

## Characteristic Audit

All derivative degrees are below `p`; nominal discriminants avoid leading-coefficient division; root counts apply only to nonzero polynomials; reconstruction uses formal identities and nonzero first derivatives. Total degree `87` is preserved throughout.

## Limitations

The result is only for the fixed bivariate prime-field instance and uniform affine-line-then-point sampling. No global optimality is claimed. Score `7249456451` is the smallest certified by the displayed `k=4415` two-range potential package; `k=4414` is an obstruction only for this package.

## Team Handoff

- **researcher-0007 / builder:** import [P5]–[P8] with `(D,k,K)=(15129,4415,66772609)`.
- **researcher-0009 / red-team:** audit the Rayleigh maximum, both endpoint fractions, and the empty/nonempty peel split.
- **researcher-0010 / integrator:** retain the incumbent interpolation and reconstruction verbatim; replace only its component and survival modules.
- **certification:** bind the exact theorem fraction and all displayed integers to one checker and theorem hash.
