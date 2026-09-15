# C4-sharpened three-direction soundness at `(p,d)=(147457,87)`

## Abstract

For the affine line-versus-point test on `F_147457^2`, I prove the admissible soundness threshold

`epsilon = 7349491214/21743566849 = 0.33800761692132436...`.

Acceptance at least `epsilon` forces one bivariate polynomial of total degree at most `87` to agree with the point table on more than `epsilon/10` of the plane, hence on at least `734949122` points.

The new fixed-instance ingredient is an exact affine-incidence credit in the final two-sided peel. A `C4`-free residual with `5194` point vertices and `15129` line vertices has at most `646374` edges. Consequently an empty `(15130,5195)` core costs `156513678` fewer incidences than separate point and line charging. Spliced into a three-complete-direction pencil argument, this lowers the previous unaudited three-direction count by `924` and the stated comparison count by `461429563`.

## Test and Notation

Let `F=F_147457`, `d=87`, and

- `h=p+1=147458`;
- `M=p^2=21743566849` points;
- `Lambda=p(p+1)=21743714306` affine lines;
- `N=p^2(p+1)=3206262880419842` incident point-line pairs.

The verifier samples a uniform affine line and then a uniform point on it. Since every line has `p` points, this is uniform sampling from the `N` incidences.

For the accepted incidence graph `G`, write `rho=|E(G)|/N`. The auxiliary parameters are

| parameter | value |
|---|---:|
| selected directions | `t=3` |
| selected lines | `r=3p=442371` |
| weighted degree | `D=15129` |
| point-core degree | `D+1=15130` |
| line-core degree | `s=5195` |
| line-deletion cap | `b=s-1=5194` |
| derivative root cap | `q=D-d=15042` |
| maximum Z-degree | `nu<=173` |
| exceptional-line cap | `E_D=2615604` |
| pencil-envelope maximizer | `j=49152` |
| pencil coefficient | `K=1610629120/10871857153` |
| residual edge cap | `Z_*=646374` |
| C4 peeling credit | `kappa=156513678` |
| fixed charge after credit | `C_*=769296828797543` |

The theorem uses

`epsilon=7349491214/M`

and its acceptance premise is equivalently at least

`epsilon*N=1083741275434012`

accepted incidences.

## Prior Results

The authoritative campaign-30 soundness history contains no verified point. The comparison threshold supplied for this task is the terminating decimal `0.35922904602094702`, whose absolute count is `7810920777`.

The prior campaign-30 submission by researcher-0003 derived the three-direction tuple `(D,s)=(15129,5195)` and count `7349492138`, but did not use a `C4` credit. Researcher-0002 proved the same style of residual-corner lemma at the different tuple `(17642,5494)`. Neither campaign-30 artifact has an audit verdict. The present proof recomputes the residual corner at the new tuple and includes every other load-bearing step explicitly.

The historical campaign-10 theorem at `0.359229046020947` was independently accepted twice. Its proof is comparison material only. No theorem from that campaign is imported here.

There is no load-bearing literature dependency. The interpolation, primitive cleanup, component estimate, and simple-root reconstruction are proved directly. In particular, the analogous KTZ revision-1 Lemmas 2.5, 2.7, and 6.1 are not invoked.

## Theorem

### Theorem 1

For `p=147457`, `d=87`, every function `f:F_p^2 -> F_p`, and every assignment of a degree-at-most-87 polynomial to every affine line, if

`Pass(f,P) >= 7349491214/21743566849`,

then there is a polynomial `Q in F_p[X,Y]` of total degree at most `87` satisfying

`Pr_x[Q(x)=f(x)] >= max(174/147457, 3674745607/108717834245)`.

Moreover, `Q` agrees with `f` on at least `734949122` points.

### Lemma 2

For every accepted incidence graph of density `rho` on `F_147457^2`, there are three distinct directions whose `442371` lines form a set `R` such that

`U_R/N <= (1610629120/10871857153)(1-rho)`,

where `U_R` counts accepted incidences at points whose accepted pencil contains no line of `R`.

### Lemma 3

Every `C4`-free bipartite graph with vertex-class sizes `5194` and `15129` has at most `646374` edges.

### Lemma 4

For every integer `n>=0`, every `C4`-free bipartite graph with `21743566849` point-side vertices and `n` line-side vertices that is emptied by deletion of point vertices of current degree at most `15129` and line vertices of current degree at most `5194` has at most

`15129*21743566849 + 5194*n - 156513678`

edges.

## Proof

### [P1] Fixed field and incidence arithmetic — proved

The affine plane has `M=p^2` points, `Lambda=p(p+1)` lines, and `N=p^2(p+1)` incidences.

For primality, `p-1=2^14*3^2`. Direct modular exponentiation gives

`10^(p-1)=1`, `10^((p-1)/2)=p-1`, and `10^((p-1)/3)=78348 mod p`,

with

`gcd(p-2,p)=gcd(78347,p)=1`.

Pocklington's criterion therefore certifies that `147457` is prime.

### [P2] Three-direction pencil coverage — proved

Choose a uniform three-element subset of the `h` directions and include every line in those directions. A point having accepted degree `a` is missed with probability

`H_a=binom(h-a,3)/binom(h,3)`.

For `0<a<h-2`, the quantity relevant to the affine majorant is

`a H_a/(h-a)=a(h-a-1)(h-a-2)/(h(h-1)(h-2))`.

The ratio of consecutive positive numerators is

`((a+1)(h-a-3))/(a(h-a-1))`.

It is at least one exactly when `h-3-3a>=0`. Thus the unique maximum is attained at `j=49152`, and

`a H_a <= K(h-a)`

for every integer `0<=a<=h`, where

`K=j*binom(h-j,3)/((h-j)binom(h,3))=1610629120/10871857153`.

Since `sum_x a_x=rho*M*h`, averaging gives

`E_R[U_R]/N <= K(1-rho)`.

At least one three-direction set realizes this bound, proving Lemma 2. This is averaging only; there is no Markov or union-bound loss.

### [P3] Weighted interpolation — proved

Give `X,Y,Z` weights `(1,1,87)` and put `D=15129`. The number of monomials of weighted degree at most `D` is

`V_D=sum_{z=0}^{173} binom(D-87z+2,2)=6693082347`.

Every selected labeled-line identity imposes at most `D+1=15130` homogeneous coefficient equations, while

`442371*15130=6693073230<V_D`.

Hence there is a nonzero polynomial `A(X,Y,Z)` of weighted degree at most `D` vanishing formally on every selected line graph.

A `Z`-independent solution would be a bivariate polynomial of degree at most `D` divisible by the distinct equations of `442371>D` affine lines, which is impossible. Thus `A` depends on `Z`. Since `deg_Z(A)<=173<p`, one has `A_Z!=0`.

Choose a nonzero interpolant of minimum weighted degree. If an irreducible factor occurred twice, dividing by one copy would preserve every selected formal identity: specialization occurs in the domain `F[t]`, so either that factor or the complementary factor specializes to zero. The quotient would be a lower-weight nonzero interpolant, a contradiction. Therefore `A` is squarefree.

### [P4] Extension to identity lines — proved

Call an accepted point covered when its accepted pencil meets the selected line set `R`. Let `T` consist of `R` and every other line having more than `D` covered accepted points. At a covered accepted point of a line `L`, a selected accepted line through that point shows

`A(x,P_L(x))=A(x,f(x))=0`.

The restriction `A(L(t),P_L(t))` has degree at most `D`, so more than `D` roots force a formal identity. Consequently every line in `T` is an `A`-identity line.

Writing `t=|T|` and `E_T` for accepted edges on these lines gives

`|E| <= |E_T|+U_R+D(Lambda-t)`.

### [P5] Primitive and derivative cleanup — proved

Write `A=CB`, where `C in F[X,Y]` is the coefficient content in `Z` and `B` is primitive. Let `c_0=deg C`, `W=wdeg(B)`, and `nu=deg_Z(B)`. Weighted leading forms do not cancel, so

`c_0+W=wdeg(A)<=D`.

The polynomial `B` is squarefree and `1<=nu<=173<p`. Primitivity excludes `Z`-independent irreducible factors. Every irreducible factor therefore has nonzero `Z`-derivative, and squarefreeness gives `gcd(B,B_Z)=1`.

For `nu>=2`, the nominal-degree discriminant is nonzero. Its monomials have coefficient degree `2nu-2` and coefficient-index weight `nu(nu-1)`, hence its `(X,Y)`-degree is at most

`(nu-1)(2W-87nu)`.

If a noncontent identity line also makes `B_Z(L(t),P_L(t))` vanish formally, the homogenized nominal-degree binary form has a singular finite root. Euler's identity is valid because `nu<p`; therefore the specialized nominal discriminant vanishes. No leading coefficient is inverted.

The number of content or derivative-degenerate identity lines is at most

`c_0+(nu-1)(2W-87nu) <= (nu-1)(2D-87nu)`.

The last expression increases through `nu=173`, because its consecutive difference is `2(D-87nu)>0` for `nu<=172`. Its maximum is

`172*(2*15129-87*173)=2615604`.

For `nu=1`, a derivative-degenerate noncontent identity line would divide both coefficients of the primitive linear polynomial, which is impossible; its content count is at most `D-87<2615604`.

On every remaining identity line, `B_Z(L(t),P_L(t))` is a nonzero polynomial of degree at most

`q=D-87=15042`,

and therefore has at most `15042` roots.

### [P6] The residual affine-incidence corner — proved

Consider a `C4`-free bipartite graph with `b=5194` point vertices and `D=15129` line vertices. If the line degrees are `r_1,...,r_D`, every pair of point vertices has at most one common line, so

`sum_i binom(r_i,2) <= binom(5194,2)=13486221`.

For a fixed edge total, discrete convexity minimizes the left side when the degrees differ by at most one. The exact division is

`646374=42*15129+10956`,

and

`15129*binom(42,2)+10956*42=13486221`.

One more edge would make the convex lower bound `13486221+42`. Thus there are at most `646374` edges, proving Lemma 3.

### [P7] C4-free empty-core credit — proved

Let `H` satisfy Lemma 4. For `n>=D`, follow an emptying order until either only `b` point vertices or only `D` line vertices remain. If the point side reaches `b` first, all remaining line vertices have degree at most `b`, so delete down to `D` line vertices. The symmetric argument applies if the line side reaches `D` first. Pad the residual with isolated vertices when necessary.

Edges deleted before the residual cost at most

`D(M-b)+b(n-D)`.

Lemma 3 bounds the residual by `646374`. Therefore

`|E(H)| <= DM+bn-kappa`,

where

`kappa=2Db-646374=156513678`.

For `n<D`, the trivial estimate `|E(H)|<=Mn` suffices because the minimum difference occurs at `n=D-1` and equals

`M+b(D-1)-kappa=21665628003>0`.

This proves Lemma 4 for every `n>=0`.

### [P8] Cleanup, peeling, and survival — proved

Delete all accepted edges on the `e` exceptional identity lines and at most `q` derivative-zero edges on each remaining identity line. Apply Lemma 4 to the resulting graph with `n=t-e`.

If the `(15130,5195)` core were empty, P4-P7 would give

`|E| <= U_R+D(Lambda-t)+pe+q(t-e)+DM+b(t-e)-kappa`.

The coefficients of `t` and `e` after collection are

`q+b-D=s-88=5107>0`

and

`p-q-b=p-q-s+1=127221>0`.

Using `t<=Lambda` and `e<=E_D` yields

`|E| <= U_R+C_*`,

where

`C_*=(q+s-1)Lambda+DM+(p-q-s+1)E_D-kappa`

`=440005802696216+328958422858521+332759756484-156513678`

`=769296828797543`.

Combining this with P2 gives, under complete deletion,

`rho <= R_0 := (C_*/N+K)/(1+K)`

with

`R_0=1244293905093223/3681259956715522`.

Exact cross multiplication gives

`7349491213/M <= R_0 < 7349491214/M`.

At `epsilon=7349491214/M`, the survival margin in the original inequality is

`epsilon-C_*/N-K(1-epsilon)`

`=1249813349/27810935621062861282>0`.

Thus acceptance at least `epsilon` leaves a nonempty core with point degree at least `15130`, line degree at least `5195`, formal `B`-identities, and `B_Z(x,f(x))!=0` on every retained edge.

### [P9] Exact component mass — proved

For point set `X`, put `a=|X|/M` and let `m_L=|X intersection L|`. Ordered-pair counting gives

`sum_L m_L=h|X|`

and

`sum_L m_L^2=|X|^2+p|X|`.

Therefore

`sum_L (m_L-ap)^2=p^3a(1-a)`.

For a line set of density `ell`, centering its indicator and applying Cauchy-Schwarz yields

`I(X,S)/N <= a ell + sqrt(a(1-a)ell(1-ell)/h)`.

Consider a connected core component. Define

`alpha=15130/147458=445/4337`,

`beta=5195/147457`,

`c=alpha/beta=13123673/4506143`,

`gamma^2=1/(ch)=1039/446204882`.

Minimum degrees imply retained-edge density at least `alpha*a` and at least `beta*ell`. Splitting at `ell=ca` and using that `ca<1/2` gives the necessary condition

`beta <= a+gamma*sqrt((1-a)(1-ca))`.

Let

`tau=epsilon/10=3674745607/108717834245`

and

`F(a)=(beta-a)^2-gamma^2(1-a)(1-ca)`.

The exact endpoint values are

`beta-tau=155449968/108717834245>0`,

`1/2-c*tau=2668206923709/6644623283510>0`,

`F(tau)=498727149435244/30939665878432433176225>0`,

`F'(tau)=-13793284387/4837976433085<0`.

Moreover `F''=2(1-1/h)>0`, so `F'` is negative throughout `[0,tau]` and `F(a)>=F(tau)>0` there. This contradicts the necessary component condition. Every component therefore has point density greater than `tau`.

Since `tau*M=734949121.4`, every component contains at least `734949122` point vertices.

### [P10] One-polynomial reconstruction — proved

Choose a point `x_0` in a retained component and translate it to the origin. Put `a_0=f(x_0)` and `c_1=B_Z(0,0,a_0)!=0`.

Recursively construct homogeneous polynomials `Q_1,...,Q_87`. If `a_0+Q_1+...+Q_{n-1}` solves `B=0` modulo `(X,Y)^n`, adding a homogeneous polynomial `Q_n` changes the degree-`n` residual by `c_1 Q_n`. Division by `c_1` uniquely cancels that residual. Let

`Q=a_0+Q_1+...+Q_87`.

Each of the at least `D+1` retained line labels through `x_0` is a formal root with the same simple constant value. The one-variable version of the recursion shows that its coefficients through degree `87` equal those of `Q` restricted to the line. Both polynomials have degree at most `87`, so they are identical.

The polynomial `B(X,Y,Q(X,Y))` has total degree at most the weighted degree `D`. It vanishes formally on `D+1` distinct seed lines, whose distinct linear equations divide it. Hence it is zero identically.

At an accepted simple intersection of a recovered line with a new retained line, `Q` and the new line label are two formal roots with the same constant value. The same recursion makes them identical. Connectivity propagates the fixed polynomial `Q` throughout the component. It agrees with `f` at every component point.

### [P11] Soundness contract and score — proved

The admissibility-floor difference is

`epsilon-957/1474570=73353795791/217435668490>0`.

The two recovery fractions satisfy

`epsilon/10-174/147457=3546458017/108717834245>0`.

Thus the required maximum is exactly

`max(2d/p,epsilon/10)=epsilon/10=3674745607/108717834245`.

P9-P10 give at least `734949122` agreements, whose density is

`734949122/21743566849 > epsilon/10`.

Finally,

`ceil(epsilon*p^2)=7349491214`.

The comparison decimal has score `7810920777`, so the exact improvement is `461429563`. This proves Theorem 1.

## Soundness Ledger

| stage | input | exact loss | output |
|---|---|---:|---|
| sampling | uniform line then point | `0` | denominator `N=3206262880419842` |
| three-direction coverage | accepted density `rho` | at most `K(1-rho)N` uncovered incidences | `K=1610629120/10871857153` |
| interpolation | `442371` selected lines | no incidence deletion; surplus `9117` | squarefree relation of weight at most `15129` |
| identity extension | nonidentity lines | at most `D(Lambda-t)` covered incidences | all retained lines are identities |
| content lines | `e` exceptional lines | at most `pe` incidences | primitive identities remain |
| derivative roots | `t-e` regular identity lines | at most `q(t-e)`, `q=15042` | every retained edge is simple |
| point/line peel | caps `(15129,5194)` | `DM+b(t-e)-156513678` | new C4 credit `156513678` |
| regular-line consolidated charge | preceding identity and peel terms | `440005802696216` | included once in `C_*` |
| point consolidated charge | point peel | `328958422858521` | included once in `C_*` |
| exceptional correction | at most `2615604` lines | `332759756484` | included once in `C_*` |
| fixed subtotal | all non-pencil charges | `C_*=769296828797543`, or `C_*/N` | no double counting |
| survival | `rho>=epsilon` | pencil loss plus `C_*/N` | positive margin `1249813349/27810935621062861282` |
| component conversion | `(15130,5195)` core | one Cauchy-Schwarz inequality, no edge deletion | component density greater than `epsilon/10` |
| reconstruction | connected simple-root component | `0` agreement loss | one total-degree-at-most-87 polynomial |
| recovery maximum | `174/p` and `epsilon/10` | none | target `epsilon/10`; count `734949122` |

## Exact Arithmetic Replay

The following deterministic checker only replays displayed identities; the analytic arguments above prove the inequalities and no exhaustive search is a proof dependency.

```python
from fractions import Fraction as F
from math import comb, gcd

p=147457; d=87; h=p+1
M=p*p; La=p*h; N=M*h
D=15129; r=3*p; s=5195; b=s-1
q=D-d; nu=D//d; j=49152

assert (M,La,N)==(21743566849,21743714306,3206262880419842)
assert p-1==2**14*3**2
assert pow(10,p-1,p)==1
assert pow(10,(p-1)//2,p)==p-1
assert pow(10,(p-1)//3,p)==78348
assert gcd(pow(10,(p-1)//2,p)-1,p)==1
assert gcd(pow(10,(p-1)//3,p)-1,p)==1

V=sum(comb(D-d*z+2,2) for z in range(nu+1))
assert (V,r*(D+1),V-r*(D+1))==(6693082347,6693073230,9117)

K=F(j*comb(h-j,3),(h-j)*comb(h,3))
assert K==F(1610629120,10871857153)

ED=max([D]+[(v-1)*(2*D-d*v) for v in range(2,nu+1)])
assert (q,nu,ED)==(15042,173,2615604)

pair=comb(b,2); qq=42; rr=10956
Z=qq*D+rr
assert D*comb(qq,2)+rr*qq==pair==13486221
assert D*comb(qq,2)+(rr+1)*qq>pair
assert Z==646374

kappa=2*D*b-Z
assert kappa==156513678
assert M+b*(D-1)-kappa==21665628003

terms=((q+s-1)*La,D*M,(p-q-s+1)*ED)
assert terms==(440005802696216,328958422858521,332759756484)
C=sum(terms)-kappa
assert C==769296828797543

R0=(F(C,N)+K)/(1+K)
assert R0==F(1244293905093223,3681259956715522)
A=7349491214; eps=F(A,M)
assert F(A-1,M)<=R0<eps
margin=eps-F(C,N)-K*(1-eps)
assert margin==F(1249813349,27810935621062861282)>0

alpha=F(D+1,h); beta=F(s,p); c=alpha/beta
gam2=F(1,c*h); tau=eps/10
fun=lambda x:(beta-x)**2-gam2*(1-x)*(1-c*x)
der=lambda x:2*(x-beta)+gam2*(1+c-2*c*x)
assert (alpha,c,gam2)==(F(445,4337),F(13123673,4506143),F(1039,446204882))
assert beta-tau==F(155449968,108717834245)>0
assert F(1,2)-c*tau==F(2668206923709,6644623283510)>0
assert fun(tau)==F(498727149435244,30939665878432433176225)>0
assert der(tau)==F(-13793284387,4837976433085)<0

assert eps>=F(957,1474570)
assert tau>F(174,p)
assert (A+9)//10==734949122

old=F(35922904602094702,10**17)
z=old*M
old_score=(z.numerator+z.denominator-1)//z.denominator
assert old_score==7810920777
assert old_score-A==461429563
```

## Counterexample Attempts

1. A table supported on `49152` complete accepted directions attains the pointwise pencil envelope. It does not refute soundness because the constant polynomial already explains the table, but it shows that a better pencil loss must exploit correlations or polynomial labels rather than only point degrees.

2. Without `C4`-freeness, the complete residual bipartite graph invalidates Lemma 3 and the credit in Lemma 4.

3. A table supported on exactly `15129` accepted directions has accepted degree exactly `15129` everywhere, attaining the generic point-peeling charge.

4. The primitive relation `Z(Z+g(X))` with `deg g=15042` attains `15042` derivative roots on every nonvertical line under the zero branch. Factor-aware recovery is needed to improve this interface.

5. `Z^p-X` and `Z^2-X^2` respectively test inseparability and branch switching. They are excluded by `deg_Z(B)<p` and pointwise nonvanishing of `B_Z`.

## Characteristic Audit

- `147457` is prime by the Pocklington certificate in P1.
- `87<15129<147457` and `deg_Z(B)<=173<147457`.
- Ordinary derivatives detect all positive Z-degrees occurring in `B`.
- Nominal homogenization prevents specialized leading-coefficient division.
- Euler's identity divides only by `nu`, which is nonzero in the field.
- Root counting is applied only to explicitly nonzero univariate polynomials.
- Formal reconstruction divides only by a retained nonzero scalar `B_Z(x,f(x))`.
- No discriminant value, irreducibility claim, floating-point comparison, or randomized experiment is assumed.

## Limitations

The `646374` residual corner is an exact certified upper bound, not a construction or a claimed extremal value. A stronger affine-geometric rich-line estimate could increase the credit further.

The three-direction pointwise envelope is sharp only for the degree-only averaging method. A selector exploiting direction correlations or the line labels may improve it.

The proof is specific to the bivariate prime-field instance and total degree `87`. It makes no claim about dimension lifting, extension fields, or individual degree.

The campaign-30 history still contains no verified point. Leaderboard promotion therefore requires two independent auditors to accept this exact theorem chain and theorem digest.

## Team Handoff

- **Combinatorial core:** import Lemmas 3-4 with `(b,D,Z_*,kappa)=(5194,15129,646374,156513678)`. Preserve the `n<D` case.
- **Integration and optimization:** use `A=7349491214`, `C_*=769296828797543`, and the exact survival margin.
- **Energy and direction selection:** any improvement to `K` must use more than the point-degree envelope.
- **Interpolation and algebra:** retain `(t,r,D,q,nu,E_D)=(3,442371,15129,15042,173,2615604)`.
- **Reconstruction:** P10 is self-contained and imports no external lifting lemma.
- **Certification:** replay the exact checker and request two hash-matched audits.
