# A C4-free peeling credit for the fixed three-direction KTZ chain

## Abstract

For the immutable instance `m=2`, `p=147457`, and total degree `d=87`, I prove soundness at

`ε = 7349491214/21743566849 ≈ 0.33800761692132436`.

The new ingredient is an exact C4-free credit in the `(15130,5195)` core peeling stage. A C4-free bipartite graph on `5194` and `15129` vertices has at most `646374` edges, yielding the universal deletion credit

`K4 = 156513678`.

Splicing this into the three-full-direction interpolation chain reduces the earlier score by `924`. Every table accepted with probability at least `ε` admits one bivariate polynomial of total degree at most `87` agreeing with the point table on more than `ε/10` of the plane, hence on at least `734949122` points. The comparison score `7810920777` is improved by `461429563`.

## Test and Notation

Let `F=F_147457`. A point table is `f:F²→F`. Each affine line `L` carries a univariate polynomial `P_L` of degree at most `87`, interpreted using a fixed affine parametrization of `L`. The verifier samples an affine line uniformly and then a point of that line uniformly, accepting when `P_L(x)=f(x)`.

Set

- `h=p+1=147458` lines through each point;
- `M=p²=21743566849` points;
- `Λ=p(p+1)=21743714306` affine lines;
- `N=p²(p+1)=3206262880419842` incidences.

Thus uniform-line-then-point sampling is uniform on the `N` incidences. Let `E` be the accepted incidence graph, `ρ=|E|/N`, and `a_x` the accepted degree of point `x`.

The auxiliary parameters are

`t_dir=3`, `r=3p=442371`, `D=15129`, `q_der=D−87=15042`, `s=5195`, `k=s−1=5194`, `ν_max=173`, and `E_D=2615604`.

The acceptance premise `ρ≥ε` is equivalently

`|E|≥εN=1083741275434012`.

## Prior Results

All active campaign-30 submissions, leaderboards, verifier material, and message-board entries were inspected, excluding every directory named `superseded`. The current campaign history and verified-results files contain no promoted point. The board's score-one discussion predates the current admissibility floor and recovery contract and is therefore not a leaderboard route.

The historical doubly audited comparison threshold is approximately `0.35922904602094702`, with score `7810920777`. The active researcher-0003 note supplied the same three-direction algebraic architecture without a C4 peeling credit, at score `7349492138`. Researcher-0001 and researcher-0002 recorded a related credit only for the old parameters `D=17642`, `k=5494`; it does not certify the present corner.

The only external theorem dependencies are Lemmas 2.5, 2.7, and 6.1 of Kominers–Thaler–Zheng, [official ECCC revision 1](https://eccc.weizmann.ac.il/report/2026/147/revision/1/download). The direction estimate, interpolation count, squarefree reduction, discriminant bound, C4 credit, affine mixing calculation, and component inequality are proved here.

## Theorem

**Theorem 1.** For `p=147457`, `d=87`, and `ε=7349491214/21743566849`, every point table `f:F_p²→F_p` and every degree-at-most-87 affine-line table with acceptance probability at least `ε` admit a polynomial `Q∈F_p[X,Y]` of total degree at most `87` satisfying

`Pr_x[Q(x)=f(x)] > ε/10 = 3674745607/108717834245`.

Consequently, `Q` agrees with `f` on at least `734949122` points.

**Lemma 2.** For every accepted incidence graph of density `ρ` in `F_147457²`, there are three distinct directions whose union `R` satisfies

`U_R/N ≤ (1610629120/10871857153)(1−ρ)`,

where `U_R` is the number of accepted incidences at points whose accepted pencil contains no line of `R`.

**Lemma 3.** For every integer `n≥0` and every C4-free bipartite graph `G=(X,Y,E_G)` with `|X|=21743566849` and `|Y|=n` that admits an emptying order deleting an `X`-vertex only at current degree at most `15129` and a `Y`-vertex only at current degree at most `5194`,

`|E_G| ≤ 15129|X|+5194|Y|−156513678`.

## Proof or Conditional Proof

### [P1] Field and incidence counts — proved

The factorization `p−1=2^14·3²` is complete. Modulo `p`,

`10^(p−1)=1`, `10^((p−1)/2)=p−1`, and `10^((p−1)/3)=78348`,

while both `gcd(10^((p−1)/2)−1,p)` and `gcd(10^((p−1)/3)−1,p)` equal `1`. Pocklington's criterion proves that `p` is prime. Standard affine-plane counting gives `M`, `Λ`, and `N` as above.

### [P2] Three-direction pencil coverage — proved

Choose a uniformly random three-element subset of the `h` directions and include all `p` lines in those directions. A point of accepted degree `a` is uncovered with probability

`H_a=C(h−a,3)/C(h,3)`.

For `1≤a≤h−3`, the quantity controlling `aH_a/(h−a)` is

`(a/3)C(h−a−1,2)`.

The ratio of consecutive terms is

`((a+1)(h−a−3))/(a(h−a−1))`,

which is at least one exactly when `h−3−3a≥0`. Its maximum is therefore at `j=49152`. Hence

`aH_a ≤ κ(h−a)` for every `0≤a≤h`,

where

`κ = 1610629120/10871857153`.

Averaging gives

`E_R[U_R/N] = (1/(Mh))Σ_x a_xH_(a_x) ≤ κ(1−ρ)`.

Some three-direction family satisfies the asserted inequality. There is no Markov or union-bound loss.

### [P3] Weighted interpolation and squarefree reduction — proved

The number of monomials `X^iY^jZ^z` with `i+j+87z≤D` is

`V_D=Σ_(z=0)^173 C(D−87z+2,2)=6693082347`.

Every selected line graph imposes at most `D+1=15130` homogeneous coefficient constraints. Since

`442371·15130=6693073230<V_D`,

there is a nonzero `(1,1,87)`-weighted-degree-at-most-`D` polynomial `A` satisfying

`A(L(t),P_L(t))≡0`

on all selected lines. A nonzero Z-independent interpolant would have total degree at most `D` and vanish formally on `442371>D` distinct lines, contradicting KTZ Lemma 2.5. Thus `A` depends on `Z`. Since `deg_Z(A)≤173<p`, ordinary differentiation gives `A_Z≠0`.

Choose an eligible `A` of minimum weighted degree. Suppose an irreducible factor `F` occurs with multiplicity `e≥2`, and write `A=F^eG`. Removing one copy preserves all selected formal line identities because `F[t]` is an integral domain. If `deg_Z(F)=0`, nonvanishing of `A_Z=F^eG_Z` implies nonvanishing of `(F^(e−1)G)_Z`. If `deg_Z(F)>0`, then `e≤173<p`, `F_Z≠0`, and `F` does not divide `F_Z`; modulo `F`, the derivative after removal contains the nonzero term `(e−1)F_ZG`. Thus the reduced interpolant still has nonzero Z-derivative, contradicting minimality. Therefore `A` is squarefree.

### [P4] Extension to identity lines — proved

Call a point covered when its accepted pencil meets `R`. Let `T` consist of `R` and every unselected line having more than `D` covered accepted points. At such a point `x` on an added line `L`, a selected accepted line gives `A(x,f(x))=0`, while acceptance on `L` gives `P_L(x)=f(x)`. Thus `A(L(t),P_L(t))` has more than `D` roots and degree at most `D`, so it is identically zero.

Writing `t=|T|` and `E_T` for accepted incidences on `T`, every accepted incidence outside `T` is either at an uncovered point or among at most `D` covered incidences of its line. Therefore

`|E|≤|E_T|+U_R+D(Λ−t)`.

### [P5] Primitive relation and exceptional lines — proved

Write `A=HB`, where `H∈F[X,Y]` is the coefficient content in `Z` and `B` is primitive. Put `h0=deg(H)`, `W=wdeg(B)`, and `ν=deg_Z(B)`. Then `h0+W≤D`, `1≤ν≤173<p`, and `B` is squarefree. Primitivity excludes Z-independent irreducible factors. Every positive-Z-degree irreducible factor has nonzero Z-derivative because its Z-degree is below `p`; hence `gcd(B,B_Z)=1`.

For `ν≥2`, the nominal projective Z-discriminant `Δ_B(X,Y)` is nonzero and has degree at most

`(ν−1)(2W−87ν)`.

If a noncontent identity line also has `B_Z(L(t),P_L(t))≡0`, the homogenized specialization has the repeated finite projective root `[P_L(t):1]`; hence `Δ_B` vanishes formally on that line. This remains valid when the leading Z-coefficient collapses. No leading coefficient is divided by.

The number of content and derivative-degenerate identity lines is at most

`h0+(ν−1)(2W−87ν) ≤ h0+(ν−1)(2(D−h0)−87ν)`.

For `ν≥2` this is maximized at `h0=0`, `ν=173`, giving

`E_D=172(30258−15051)=2615604`.

For `ν=1`, a noncontent derivative-degenerate identity line would divide both coefficients of `B`, contradicting primitivity; the content count is smaller than `E_D`.

On every other identity line, `B_Z(L(t),P_L(t))` is a nonzero polynomial of degree at most

`q_der=D−87=15042`,

so it has at most `15042` roots.

### [P6] Fixed C4 corner — proved

Let a C4-free bipartite graph have `k=5194` left vertices and `D=15129` right vertices. If the right degrees are `r_i`, C4-freeness gives

`Σ_i C(r_i,2)≤C(k,2)=13486221`.

At `Z=646374=42D+10956` edges, convexity minimizes the left side at

`D·C(42,2)+10956·42=13486221`.

One additional edge forces at least

`D·C(42,2)+10957·42=13486263`,

which is impossible. Thus `Z≤646374`, and

`K4=2Dk−Z=156513678`.

### [P7] C4-free peeling credit — proved

First suppose a C4-free graph has part sizes `m≥k` and `n≥D` and admits the stipulated emptying order. Induct on `m+n`. At the boundary `m=k`, apply [P6] to any `D` right vertices and charge at most `k` edges for every remaining right vertex:

`|E_G|≤646374+k(n−D)=Dm+kn−K4`.

The boundary `n=D` is symmetric. In the interior, delete the first vertex of the emptying order and apply induction; the deleted vertex contributes at most `D` or `k`, respectively.

For `n<D`, use `|E_G|≤Mn`. The difference between the claimed bound and `Mn` is

`(D−n)M+kn−K4`,

which is minimized at `n=D−1` and equals

`M+k(D−1)−K4=21665628003>0`.

This proves Lemma 3 for every `n≥0`.

### [P8] Nonempty simple-root core — proved

Let `e≤E_D` be the number of exceptional lines in `T`. Delete all their accepted incidences, delete derivative-zero incidences on the remaining `t−e` lines, and peel points of current degree at most `D` and lines of current degree at most `k`.

If peeling empties the residual graph, [P7] gives

`|E_T|≤pe+q_der(t−e)+DM+k(t−e)−K4`.

Combining this with [P4] yields

`|E|≤U_R+DΛ+DM+(s−88)t+(p−q_der−s+1)e−K4`.

Both variable coefficients are positive:

`s−88=5107`, and `p−q_der−s+1=127221`.

Using `t≤Λ` and `e≤E_D` gives

`|E|≤U_R+C*`,

where

`C*=(q_der+s−1)Λ+DM+(p−q_der−s+1)E_D−K4`

`=440005802696216+328958422858521+332759756484−156513678`

`=769296828797543`.

By [P2], complete deletion at acceptance `ε` would imply

`ε≤C*/N+κ(1−ε)`.

But exactly

`C*/N+κ(1−ε)=9400308072378016503/27810935621062861282`,

and

`ε−C*/N−κ(1−ε)=1249813349/27810935621062861282>0`.

Therefore a nonempty core remains, with point degree at least `15130`, line degree at least `5195`, formal `B`-identities, and `B_Z(x,f(x))≠0` on every retained edge.

For reference, the continuous threshold of this fixed ledger is

`R*=(C*/N+κ)/(1+κ)=1244293905093223/3681259956715522`.

Exact division gives

`R*·M=7349491213+548266597656141/3681259956715522`,

so `7349491214` is the smallest integer score strictly above this fixed survival threshold.

### [P9] Exact affine incidence mixing — proved

For point set `X` of density `a` and line set `S` of density `b`, the affine incidence matrix satisfies `II^T=pI+J`. Centering the two indicator vectors and applying Cauchy–Schwarz therefore gives

`I(X,S)/N ≤ ab+sqrt(a(1−a)b(1−b)/h)`.

This is the sole Cauchy–Schwarz loss.

### [P10] Component mass — proved

For a connected core component with point density `a` and line density `b`, put

`α=15130/147458=445/4337`,

`β=5195/147457`,

`c=α/β=13123673/4506143`, and

`γ²=1/(ch)=1039/446204882`.

Minimum degrees give component edge density at least `αa` and at least `βb`. If `b≤ca`, the mixing upper bound is maximized at `b=ca` whenever `ca<1/2`; if `b≥ca`, divide by `b` and use monotonicity of `(1−b)/b`. Both cases imply

`β≤a+γ sqrt((1−a)(1−ca))`.

Let

`τ=ε/10=3674745607/108717834245`

and `F(a)=(β−a)²−γ²(1−a)(1−ca)`. Exact arithmetic gives

`β−τ=155449968/108717834245>0`,

`1/2−cτ=2668206923709/6644623283510>0`,

`F(τ)=498727149435244/30939665878432433176225>0`,

and

`F'(τ)=−13793284387/4837976433085<0`.

Since `F''=2(1−1/h)>0`, `F'` is negative throughout `[0,τ]`; hence `F(a)≥F(τ)>0` for every `a≤τ`, contradicting the necessary component inequality. Every component has point density strictly greater than `τ`.

### [P11] One-polynomial recovery — proved

Choose a point `b` in a retained component. It lies on at least `D+1` retained lines. Their degree-at-most-87 labels are formal roots of `B`, all take the common value `f(b)`, and `B_Z(b,f(b))≠0`. KTZ Lemma 6.1 produces one polynomial `Q∈F[X,Y]` of total degree at most `87` satisfying `B(X,Y,Q)≡0` and agreeing with every retained seed-pencil label.

At a reached accepted point, `Q` and every adjacent line label have the same simple initial value and are degree-at-most-87 roots of the same restricted equation. The one-variable specialization of KTZ Lemma 2.7 makes them identical. Connectivity propagates this same `Q` through the component, so `Q(x)=f(x)` at every component point.

### [P12] Recovery contract and score — proved

Because every component has density greater than `τ`, the recovered polynomial agrees at more than `τM=A/10=734949121.4` points and therefore at least `734949122` points.

The acceptance parameter is admissible because

`ε−957/(10p)=73353795791/217435668490>0`.

Moreover,

`τ−174/p=3546458017/108717834245>0`.

Thus the required recovery fraction is

`max(174/147457,ε/10)=ε/10`,

and the guaranteed count `734949122` exceeds the absolute floor

`174p=25657518`.

Finally, `ceil(εp²)=7349491214`. The comparison threshold has score `7810920777`, so the improvement is `461429563`. This proves Theorem 1.

## Soundness Ledger

| Stage | Exact charge or loss | Output |
|---|---:|---|
| Three-direction coverage | `κ(1−ρ)`, `κ=1610629120/10871857153` | one union of three complete directions |
| Interpolation | no incidence loss; `6693073230` constraints in dimension `6693082347` | weighted degree `15129`, surplus `9117` |
| Missing identity lines | `D(Λ−t)` | all retained lines are formal identities |
| Exceptional lines | `pe`, with `e≤2615604` | primitive nondegenerate identity lines |
| Derivative-zero incidences | `15042(t−e)` | simple accepted roots |
| Empty point/line peeling | `15129M+5194(t−e)−156513678` | C4 credit included once |
| Consolidated regular charge | `(15042+5195−1)Λ=440005802696216` | includes identity, derivative, and line-peel terms; do not add again |
| Point charge | `15129M=328958422858521` | point degree at least `15130` |
| Exceptional correction | `127221·2615604=332759756484` | worst-case exceptional-line maximization |
| C4 correction | `−156513678` | new fixed credit |
| Fixed subtotal | `C*=769296828797543` | normalized loss `C*/N` |
| Energy at `ε` | `23183517373213491200/236392952779034320897` | normalized uncovered-incidence loss |
| Total survival loss | `9400308072378016503/27810935621062861282` | below `ε` by `1249813349/27810935621062861282` |
| Component conversion | exact centered mixing term `sqrt(a(1−a)b(1−b)/147458)` | every component has point density `>ε/10` |
| Polynomial recovery | no further agreement loss | one total-degree-at-most-87 polynomial |
| Recovery contract | `max(174/p,ε/10)=ε/10` | at least `734949122` agreements |

## Exact Arithmetic Certificate

The following deterministic integer/rational checker replays the finite inequalities used above. It uses neither floating point nor randomness.

```python
from fractions import Fraction as F
from math import comb, gcd

p=147457; h=p+1; M=p*p; La=p*h; N=M*h; d=87
D=15129; s=5195; k=s-1; q=D-d; A=7349491214
ceil=lambda x:(x.numerator+x.denominator-1)//x.denominator

assert (M,La,N)==(21743566849,21743714306,3206262880419842)
assert p-1==2**14*3**2
assert pow(10,p-1,p)==1
assert pow(10,(p-1)//2,p)==p-1
assert pow(10,(p-1)//3,p)==78348
assert gcd(pow(10,(p-1)//2,p)-1,p)==1
assert gcd(pow(10,(p-1)//3,p)-1,p)==1

V=sum(comb(D-d*z+2,2) for z in range(D//d+1))
assert V==6693082347
assert 3*p*(D+1)==6693073230
assert V-3*p*(D+1)==9117

j=49152
kap=F(1610629120,10871857153)
for a in range(h+1):
    assert F(a*comb(h-a,3),comb(h,3))<=kap*(h-a)

nu=D//d
ED=max([D]+[(v-1)*(2*D-d*v) for v in range(2,nu+1)])
assert (nu,ED)==(173,2615604)

assert comb(k,2)==13486221
assert D*comb(42,2)+10956*42==comb(k,2)
assert D*comb(42,2)+10957*42>comb(k,2)
Z=42*D+10956
K4=2*D*k-Z
assert (Z,K4)==(646374,156513678)
assert M+k*(D-1)-K4==21665628003

C=(q+s-1)*La+D*M+(p-q-s+1)*ED-K4
assert C==769296828797543
eps=F(A,M)
loss=F(C,N)+kap*(1-eps)
assert loss==F(9400308072378016503,27810935621062861282)
assert eps-loss==F(1249813349,27810935621062861282)

R=(F(C,N)+kap)/(1+kap)
assert R==F(1244293905093223,3681259956715522)
assert divmod(R.numerator*M,R.denominator)==(7349491213,548266597656141)

tau=eps/10
alpha=F(D+1,h); beta=F(s,p); c=alpha/beta
gam2=F(s,p*(D+1))
FF=(beta-tau)**2-gam2*(1-tau)*(1-c*tau)
Fp=2*(tau-beta)+gam2*(1+c-2*c*tau)
assert FF==F(498727149435244,30939665878432433176225)
assert Fp==F(-13793284387,4837976433085)
assert tau-F(174,p)==F(3546458017,108717834245)
assert eps-F(957,10*p)==F(73353795791,217435668490)
assert ceil(tau*M)==734949122
assert 2*d*p==25657518

old=F(35922904602094702,10**17)
assert ceil(old*M)==7810920777
assert 7810920777-A==461429563
```

## Counterexample Attempts

1. For `f=0`, labeling exactly `49152` complete directions by zero and all other lines by one attains equality in the pointwise pencil-energy envelope. It does not refute the theorem because choosing one accepted direction covers all points.

2. Labeling `49842` complete directions by zero gives acceptance above `ε`, with exact cross-product margin `1583453846`. The accepted directions are maximally concentrated, but `Q=0` explains every point.

3. Let `g(X)=∏_(a=0)^15041(X−a)` and `B=Z(Z+g(X))`. At the zero root, derivative cleanup encounters exactly `15042Λ=327068950590852` degenerate incidences. This shows the whole-B derivative interface is sharp, although the factor `Z` itself already identifies `Q=0`.

4. The inseparable squarefree polynomial `Z^p−X` has `B_Z=0`, but weighted degree `87p=12828759>D`; the interpolation cutoff excludes it.

5. Relations such as `Z²−X²` permit branch changes only at derivative-zero points, confirming that simple-root deletion is load-bearing.

6. With the new credit but `s=5194`, the candidate score would be `7349362799`; however, the exact component endpoint is `−4708014974534477/4207794559466810911966600`. This refutes only that parameter within the present centered-mixing certificate.

## Characteristic Audit

- The Pocklington certificate in [P1] proves primality.
- `87<15129<147457`, `173<147457`, and `15042<147457`.
- The squarefree reduction explicitly handles derivative coefficients and repeated Z-independent factors.
- Primitivity, squarefreeness, and the Z-degree cutoff jointly prove `gcd(B,B_Z)=1`.
- The discriminant is nominal and projective; leading-coefficient collapse causes no division.
- Formal root identities, not equality merely as functions on `F_p`, are used throughout.
- Lifting divides only by certified nonzero simple-root derivatives.
- Every finite comparison is an integer or rational identity replayed by the checker.

## Limitations

The theorem is only for the fixed bivariate prime-field instance and total degree `87`. It makes no claim about higher dimensions, extension fields, individual-degree testing, or alternate sampling.

The value `646374` is a proved convex C4 upper bound, not a proved affine-geometric extremal value. A smaller true corner maximum would increase the credit. The direction-energy coefficient is sharp for the point-degree envelope, while label-sensitive selection may improve it.

No global optimality is claimed for `(t_dir,D,s)=(3,15129,5195)`. The neighboring `s=5194` remains blocked by the component inequality, and the derivative construction shows that a better cleanup must exploit factor structure. The current campaign history has no audit yet; this submission still requires two independent matching verifications.

## Team Handoff

- **Combinatorial-core and peeling modules:** import Lemma 3 with `(D,k,Z,K4)=(15129,5194,646374,156513678)` and retain the `n<D` endpoint check.
- **Interpolation and identity-extension modules:** import `(t_dir,r,D,V_D−r(D+1))=(3,442371,15129,9117)` together with [P3]–[P5].
- **Survival optimizer:** replace the no-credit fixed charge by `C*=769296828797543`; the continuous threshold is `1244293905093223/3681259956715522`.
- **Component and recovery modules:** use `s=5195`, `F(τ)=498727149435244/30939665878432433176225`, and KTZ Lemmas 2.7 and 6.1.
- **Certification modules and both auditors:** replay the exact certificate and audit [P6]–[P8] first; those are the only new load-bearing interfaces relative to the three-direction chain.
