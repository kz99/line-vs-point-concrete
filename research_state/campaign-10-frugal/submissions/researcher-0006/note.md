# Spectral Component Floor Lowers the Fixed Score to 7,249,403,428

## Abstract

For `p=147457`, total degree `d=87`, and uniform affine-line-then-point sampling, I strengthen the component-potential module of researcher-0004. Combining both residual minimum degrees with the exact centered affine-incidence inequality forces every nonempty residual component to contain at least `622400212` points. This raises the nonempty-component peeling credit from `28291` to `5933551`.

Spliced into the independently audited partial-fourth-direction proof, this gives

\[
\varepsilon=\frac{3334045181429561}{10^{16}},\qquad
\left\lceil\varepsilon p^2\right\rceil=7249403428.
\]

The recovered polynomial agrees on at least `724940343` points. The score improves the verified `7349490435` record by `100087007` and researcher-0004’s pending score by `35`.

## Test and Notation

Let

\[
h=p+1=147458,\quad M=p^2=21743566849,
\]
\[
\Lambda=p(p+1)=21743714306,\quad N=Mh=3206262880419842.
\]

The accepted-edge density is the prescribed test acceptance. Retain researcher-0004’s parameters

\[
D=15136,\quad k=4414,\quad q=D-d=15049,
\]

and selector coefficient

\[
\kappa'_4=
\frac{1246437422331006215441194309538667}
{8421304329489870366247361127538688}.
\]

## Prior Results

I scanned the 21 active submission notes, all active leaderboard files, 20 verifier audits, and both message boards, excluding every `superseded` directory. The authoritative history remains `research_state/campaign-10-frugal/leaderboards/soundness-history.json`.

The unchanged modules are researcher-0004 `[P2]`–`[P5]` and `[P9]` in `research_state/campaign-10-frugal/submissions/researcher-0004/response.json`. Its audit at `research_state/campaign-10-frugal/reviews/researcher-0004/verifier-a-researcher-0004/audit.json` independently marks every load-bearing module valid; its aggregate `revise` verdict is caused by stale, non-load-bearing comparison metadata. The present theorem corrects that metadata and replaces its component step.

## Theorem

For every point table \(f:\mathbb F_{147457}^2\to\mathbb F_{147457}\) and every assignment of a degree-at-most-87 polynomial to every affine line, if

\[
\operatorname{Pass}(f,P)\ge
\frac{3334045181429561}{10^{16}},
\]

then some \(Q\in\mathbb F_{147457}[X,Y]\) of total degree at most `87` satisfies

\[
\Pr_x[Q(x)=f(x)]\ge
\max\left\{\frac{174}{147457},
\frac{3334045181429561}{10^{17}}\right\}
=rac{3334045181429561}{10^{17}}.
\]

## Proof

### [P1] Centered affine incidence bound — proved

For point and line sets of densities \(a,b\), ordered-pair counting gives

\[
\frac{I(X,S)}N\le ab+
\sqrt{\frac{a(1-a)b(1-b)}h}. \tag{1}
\]

### [P2] Spectral component floor — proved

Let a nonempty residual component have normalized edge mass \(J\), point density \(a\), and line density \(b\). Minimum degrees `(15137,4415)` give

\[
J\ge\alpha a,\quad J\ge\beta b,
\quad \alpha=\frac{15137}{147458},\quad
\beta=\frac{4415}{147457}.
\]

Put \(c=\alpha/\beta=2232056609/651027070\) and
\(\gamma^2=1/(ch)=4415/2232056609\). Applying (1) separately when \(b\le ca\) and \(b\ge ca\) yields, whenever \(ca<1/2\),

\[
\beta\le a+\gamma\sqrt{(1-a)(1-ca)}. \tag{2}
\]

Let \(a_*=622400211/M\) and

\[
F(a)=(\beta-a)^2-\gamma^2(1-a)(1-ca).
\]

Exact checks give

\[
F(a_*)=rac{84092949843}{3578280126216242515417889}>0,
\]

\[
F'(a_*)=-\frac{863766445687}{329134603449922}<0,
\]

\[
\beta-a_*=\frac{28622444}{21743566849}>0,
\quad
\frac12-ca_*=rac{19288988668294}{47999249330495}>0.
\]

Since \(F''=147457/73729>0\), `F` is decreasing throughout `[0,a*]`. Squaring (2) would require `F(a)≤0`, a contradiction. Thus every component has at least `622400212` points.

### [P3] Improved component potential — proved

Set

\[
\eta=\frac{40407}{625000000000},\quad
\delta=\frac D h,\quad \theta=\frac k p,
\]

and conservatively use \(\bar\tau=7249403428/(10M)\), which exceeds the theorem’s recovery density. Maximizing (1) minus \(D|X|+k|S|\) over the line density reduces the desired inequality to one squaring. With \(\delta'=\delta-\eta\), its guards are

\[
Q=4\delta'(\delta'-1)+1/h
=-\frac{195584747102179735885422401703791}
{530856000097656250000000000000000}<0,
\]

\[
L(\bar\tau)=
\frac{97794057801029066737011121001113}
{28856757313290348000244140625000000000000000}>0,
\]

\[
R(\bar\tau)=
\frac{4306203950438485321228529}
{1252446437664000781250000000}>0.
\]

Because `Q<0` and `2δ'−1<0`, these endpoint checks prove throughout the relevant interval

\[
I(X,S)\le D|X|+k|S|-\eta h|X|. \tag{3}
\]

By [P2], every nonempty component therefore contributes integer credit at least

\[
\left\lceil\eta h\cdot622400212\right\rceil=5933551.
\]

### [P4] Peeling dichotomy — proved

Sequentially peel points of degree at most `D` and lines of degree at most `k`. If a residual component remains and none reaches the recovery density, (3) supplies credit `5933551`. If the core empties, the audited `C4`-free corner supplies the larger credit `133070051`. Hence

\[
|E(G)|\le15136M+4414(t-z)-5933551. \tag{4}
\]

### [P5] Survival — proved

The audited selector, interpolation, identity-extension, and cleanup inequalities combine with (4). Since the coefficients of `t` and `z` are `4327` and `127994`, respectively,

\[
C'=423197911537678+329110627826464
+335089827928-5933551
=752643623258519.
\]

Absence of a large component would imply

\[
\rho\le C'/N+\kappa'_4(1-\rho).
\]

Its frontier is

\[
R'=rac{3223268780051728141186708743365483}
{9667741751820876581688555437077355},
\quad \lfloor MR'\rfloor=7249403427.
\]

At the claimed terminating \(\varepsilon\), the exact survival margin is

\[
\frac{69899855576037749414028334973789734033}
{2406086951282820104642103179296768000000000000000}>0.
\]

Thus a sufficiently large simple-root component survives.

### [P6] Reconstruction and contract — proved

KTZ revision-1 Lemmas 2.5, 2.7, and 6.1 reconstruct one total-degree-at-most-87 polynomial at a seed and propagate it through the connected component without agreement loss.

Finally,

\[
\frac\varepsilon{10}-\frac{174}{p}
=rac{474228300318058776377}
{14745700000000000000000}>0,
\]

and

\[
\varepsilon-\frac{957}{10p}
=rac{490671300318058776377}
{1474570000000000000000}>0.
\]

Also `ceil(εM)=7249403428` and `ceil(εM/10)=724940343`.

## Soundness Ledger

| Stage | Exact loss/output |
|---|---:|
| selector and labeled points | `κ′₄(1−ρ)N` |
| interpolation | `442779·15137+3776` constraints; surplus `1` |
| identity extension | `15136(Λ−t)` |
| exceptional lines | `pz`, `z≤2618012` |
| derivative roots | `15049(t−z)` |
| point/line peeling | `15136M+4414(t−z)−5933551` |
| fixed subtotal | `C′=752643623258519` |
| reconstruction | zero loss |
| recovery | `ε/10`; `724940343` points |

## Counterexample Attempts

The Moore-only floor gives merely `66814719` points. The spectral quadratic changes sign at the next integer: `F(622400212/M)<0`, so this scalar method alone cannot certify a larger floor. The audited `k=4413` endpoint is negative. Concentrated directions, branch switching, and inseparability are covered by the selector, simple-root deletion, and `deg_Z<p`.

## Characteristic Audit

All derivative degrees are below `p`; the discriminant is nominally homogenized; no specialized leading coefficient is inverted; reconstruction divides only by retained nonzero first derivatives. Total degree `87` and uniform affine-line sampling are unchanged.

## Limitations

This is only the fixed bivariate prime-field instance. The spectral floor is sharp only for the displayed scalar inequality, not necessarily for realizable labeled components. The assigned checkpoint outbox was mounted read-only: `apply_patch` rejected both attempted checkpoint files.

## Team Handoff

- **researcher-0007 / builder:** replace only the component and fixed-charge modules by [P2]–[P5].
- **researcher-0009 / red-team:** audit the two-case elimination and three potential guards.
- **researcher-0010 / integrator:** bind exact score `7249403428`, terminating epsilon, and recovery count `724940343` into the certificate.
