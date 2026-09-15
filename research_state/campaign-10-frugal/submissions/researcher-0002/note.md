# Factor-coherent cleanup: an exact conditional score reduction and two sharp local obstructions

## Abstract

At `p=147457`, `d=87`, weighted interpolation degree `D=15129`, and line-core threshold `s=5195`, a proper irreducible factor common to every identity line has weighted degree at most `D-d=15042`. Its exceptional-line cap is `2585520`, and its regular derivative-root cap is `14955`. Substitution in the audited incumbent ledger changes the fixed charge from `769296828797543` to `767401523276597` and gives the conditional trigger

\[
\varepsilon_{\rm fac}=\frac{7338296486}{21743566849}
\approx0.3374927645018597.
\]

The corresponding absolute score is `7338296486`, improving the incumbent by `11194728`, and recovery is strictly greater than `epsilon_fac/10`, hence at least `733829649` points. The missing hypothesis is factor coherence: product vanishing assigns each identity line some factor but need not assign the same factor to all lines. Two exact examples show that neither the `15042` local derivative cap nor the `2615604` discriminant-degree cap can be reduced using only the incumbent degree, primitivity, squarefreeness, or irreducibility data.

## Test and Notation

The test samples an affine line uniformly in `F_p^2`, then a uniform point on it. Put

\[
p=147457,\quad d=87,\quad h=p+1=147458,
\]
\[
M=p^2=21743566849,\quad \Lambda=p(p+1)=21743714306,
\quad N=Mh=3206262880419842.
\]

The incumbent parameters are

\[
D=15129,\quad s=5195,\quad k=s-1=5194,
\quad \kappa=\frac{1610629120}{10871857153},
\quad K_4=156513678.
\]

Weights of `(X,Y,Z)` are `(1,1,87)`.

## Prior Results

The active scan covered the 17 top-level prior notes, all leaderboard files, 18 verifier audits, and both active message boards, excluding every `superseded` directory. The authoritative [history](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/leaderboards/soundness-history.json) records score `7349491214`. The exact incumbent chain is in [researcher-0002/note.md](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/submissions/researcher-0002/note.md), and the factor-aware target `25216` is isolated in [researcher-0001/note.md](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/submissions/researcher-0001/note.md).

The primary-source counterparts are KTZ revision-1 Lemma 2.6 (coprime resultant line bound), Lemma 2.7 (unique simple formal lift), and Lemma 6.1 (lifting from more than `D` root lines) in the [official report](https://eccc.weizmann.ac.il/report/2026/147/revision/1/download/). They are not load-bearing here: the discriminant calculation is proved below, while component mixing and reconstruction are imported from the self-contained [team synthesis](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/submissions/team-synthesis-0001/note.md), steps P6–P9.

## Theorem

**Lemma 1 (factor-coherent cleanup).** Let `B in F_147457[X,Y,Z]` be primitive and squarefree with `(1,1,87)`-weighted degree at most `15129`. Let `G` be a proper irreducible factor of `B`, and let `T` be a family of affine lines carrying polynomials `P_L` of degree at most `87` such that

\[
G(L(t),P_L(t))\equiv0\qquad(L\in T).
\]

Then `wdeg(G)≤15042`, `deg_Z(G)≤172`, and `gcd(G,G_Z)=1`. There is a set `E subseteq T` with `|E|≤2585520` such that, for every `L in T\E`, the polynomial `G_Z(L(t),P_L(t))` is nonzero and has degree at most `14955`.

**Conditional Corollary 2.** Suppose the incumbent three-direction interpolation and identity-extension construction produces `B,T` satisfying Lemma 1 with one proper irreducible factor `G` common to every line of `T`. If the test accepts with probability at least

\[
\varepsilon_{\rm fac}=\frac{7338296486}{21743566849},
\]

then one polynomial of total degree at most `87` agrees with the point table on more than

\[
\frac{\varepsilon_{\rm fac}}{10}
=\frac{3669148243}{108717834245}
\]

of the plane, hence on at least `733829649` points.

## Proof or Conditional Proof

### [P1] Proper-factor degree — proved

Write `B=GH`. Since `B` is primitive in `Z`, the nonconstant factor `H` cannot be `Z`-independent. Thus `wdeg(H)≥87`. Weighted leading forms multiply nontrivially, so weighted degree is additive and

\[
w:=\operatorname{wdeg}G\le15129-87=15042.
\]

Consequently `nu:=deg_Z(G)≤floor(15042/87)=172<p`. Irreducibility, Gauss's lemma, and this characteristic bound give `G_Z!=0` and `gcd(G,G_Z)=1`.

### [P2] Exceptional lines — proved

For `nu≥2`, the nominal projective `Z`-discriminant is nonzero. If `g_j(X,Y)` is the coefficient of `Z^j`, then `deg(g_j)≤w-87j`. Discriminant homogeneity therefore gives

\[
\deg_{X,Y}\Delta_G\le(\nu-1)(2w-87\nu).
\]

A line on which both specialized identities hold divides `Delta_G`; nominal homogenization makes this valid even when the specialized leading coefficient vanishes. Since

\[
(\nu-1)(2w-87\nu)\le171(30084-14964)=2585520,
\]

there are at most `2585520` exceptional lines. For `nu=1`, simultaneous vanishing of `G` and `G_Z` on a line would make that line divide both coefficients of `G`, contradicting primitivity.

### [P3] Regular derivative roots — proved

`wdeg(G_Z)≤w-87≤14955`. Hence every nonexceptional restriction is a nonzero univariate polynomial of degree at most `14955` and has at most that many roots.

### [P4] Fixed-charge propagation — proved under factor coherence

Using the unchanged identity loss, point peeling, line peeling, and `C_4` credit gives

\[
C_{\rm fac}=(14955+5195-1)\Lambda+15129M
 +(147457-14955-5195+1)2585520-K_4
\]
\[
=438114099551594+328958422858521+329157380160-156513678
=767401523276597.
\]

The old-to-new fixed saving is

\[
769296828797543-C_{\rm fac}=1895305520946.
\]

Only `25216` fixed incidences are needed for a one-score improvement, since the exact threshold is

\[
\frac{3718145613}{147457}=25215.117\ldots.
\]

The resulting continuous survival frontier is

\[
R_{\rm fac}=\frac{1242398599572277}{3681259956715522},
\]

and

\[
\varepsilon_{\rm fac}-R_{\rm fac}
=\frac{10269023767}{542827549437400727554}>0.
\]

### [P5] Component and recovery splice — proved under factor coherence

The core retains minimum degrees `(15130,5195)`. At `tau=epsilon_fac/10`, the incumbent component polynomial satisfies

\[
F(\tau)=\frac{87078601536763088}{525974319933351363995825}>0,
\quad
F'(\tau)=-\frac{14291449783}{4837976433085}<0.
\]

The side conditions are

\[
\beta-\tau=\frac{161047332}{108717834245}>0,
\qquad
\frac12-c\tau=\frac{2669203254501}{6644623283510}>0.
\]

Thus every component has point density greater than `tau`. Since a seed point has `15130>w` factor-coherent root lines and all retained roots are simple for `G`, the self-contained lifting and propagation proof yields one total-degree-at-most-87 polynomial on the component. Finally,

\[
\varepsilon_{\rm fac}-\frac{957}{10p}
=\frac{73241848511}{217435668490}>0,
\]
\[
\frac{\varepsilon_{\rm fac}}{10}-\frac{174}{p}
=\frac{3540860653}{108717834245}>0.
\]

The score is `7338296486`, and strict agreement above `733829648.6` points gives at least `733829649` points.

### [P6] Sharp local bounds — proved

Let `g(X)=prod_{a=0}^{15041}(X-a)`. The polynomial `Y+g(X)Z` is irreducible, primitive, squarefree, and has weighted degree `15129`; on `Y=0,Z=0`, its derivative has exactly `15042` roots. Thus no universal `15041` cap holds even for an irreducible relation.

Also `X^78Z^173+Y^15129` is primitive and squarefree, and its nominal discriminant has degree

\[
172(78+15129)=2615604.
\]

Thus the discriminant degree expression itself cannot be lowered.

### [P7] Unconditional splice — conditional

Product vanishing only shows that each identity line belongs to at least one factor. Different lines may choose different factors, splitting the point degree and destroying both monochromatic seeding and the component-mass inequality. No active-corpus lemma establishes the factor-coherence hypothesis.

## Soundness Ledger

| Stage | Exact loss | Output |
|---|---:|---|
| Sampling | none; `N=3206262880419842` | uniform incidences |
| Direction coverage | `kappa(1-rho)` | unchanged three-direction selector |
| Interpolation | surplus `9117` | squarefree relation, weight `15129` |
| Identity extension | `15129(Lambda-t)` | factor-coherent identities assumed |
| Exceptional factor lines | `p e`, `e≤2585520` | derivative-nondegenerate lines |
| Derivative roots | `14955(t-e)` | simple factor roots |
| Peeling | `15129M+5194(t-e)-156513678` | minimum degrees `(15130,5195)` |
| Fixed subtotal | `C_fac=767401523276597` | frontier `R_fac` |
| Component conversion | centered affine mixing | density `>epsilon_fac/10` |
| Reconstruction | no loss | one total-degree-87 polynomial |
| Required recovery | `max(174/p,epsilon_fac/10)=epsilon_fac/10` | at least `733829649` points |
| Conditional score | `ceil(epsilon_fac M)` | `7338296486` |

## Counterexample Attempts

The two polynomials in [P6] show that local degree-only sharpening cannot supply the required credit. The reducible example `Z(Z+g)` shows a large factor-aware saving but is favorable precisely because the factor `Z` is globally coherent. Branch switching in `Z^2-X^2` remains possible at product-singular intersections. Concentrated good directions do not supply factor coherence.

## Characteristic Audit

All `Z`-degrees are below `p`. Ordinary derivatives therefore detect every positive-`Z` irreducible factor. The discriminant proof uses nominal homogenization and no leading-coefficient division. Root restrictions have degree below `p`. Downstream reconstruction divides only by a certified nonzero first derivative and uses neither factorials nor Hasse derivatives. No irreducibility of a line specialization is assumed.

## Limitations

The factor-coherent corollary is not an unconditional line-versus-point theorem. The discriminant example proves sharpness of the algebraic degree bound, not existence of `2615604` distinct exceptional identity lines. The derivative example saturates one regular line, not the aggregate charge over all lines. These leave an aggregate irreducible-case incidence bound as a possible third direction, outside this scout's two-approach budget.

## Team Handoff

- **Researcher-0008 / algebraic-cleanup builder:** target a monochromatic `(15130,5195)` core; on success, import `E_fac=2585520`, `q_fac=14955`, and `C_fac=767401523276597`.
- **Researcher-0009 / red-team:** reject any argument that infers a common factor merely from product identities; test the four displayed examples.
- **Researcher-0010 / integrator:** the conditional trigger is `7338296486/21743566849`, recovery is `3669148243/108717834245`, and the proved conditional count is `733829649`; do not mark it as a leaderboard result until factor coherence is closed.
