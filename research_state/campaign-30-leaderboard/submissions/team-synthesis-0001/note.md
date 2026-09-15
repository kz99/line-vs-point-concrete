# Record-equivalent synthesis of the C4-sharpened fixed-instance theorem

## Abstract

Let \(p=147457\), \(d=87\), and

\[
\varepsilon_{\mathrm{lat}}=\frac{3380076168821833}{10^{16}}.
\]

For the affine line-versus-point test on \(\mathbb F_p^2\), acceptance at least
\(\varepsilon_{\mathrm{lat}}\) forces agreement with one bivariate polynomial of total degree at
most \(87\) on more than

\[
\frac{3674745607}{108717834245}
\]

of the plane, hence on at least \(734949122\) points. The proof combines the exact
three-direction and \(C_4\)-peeling chain independently written by researchers 2 and 3 with the
incidence-lattice normalization of researcher 1. The reconstruction is given directly, so the
final proof has no load-bearing literature dependency. Its agreement-count score is
\(7349491214\), equal to the current verified record rather than smaller; this is therefore a
proved record-equivalent synthesis, not a leaderboard improvement.

The remaining completed work is also classified. Researcher 4 gives a lossless algebraic
reconstruction package at weighted degree \(17642\), but its \(17643\)-line seed does not replace
the present \(15130\)-line seed. Researcher 5 gives exact list bounds and a list-to-one conversion,
but the required below-Johnson list-cover statement is open and its natural \(3\%\)-Johnson bridge
is false. Researcher 1's adjacent parameter searches identify two concrete improvement
frontiers, neither of which closes with the currently proved component estimate.

## Test and Notation

Let \(F=\mathbb F_{147457}\). A point table is a function \(f:F^2\to F\). Each affine line
\(L\subset F^2\) is assigned a univariate polynomial \(P_L\) of degree at most \(87\), interpreted
under a fixed affine parametrization. The test samples \(L\) uniformly among all affine lines,
then samples \(x\in L\) uniformly, and accepts when \(P_L(x)=f(x)\).

Put

\[
h=p+1=147458,\qquad M=p^2=21743566849,
\]

\[
\Lambda=p(p+1)=21743714306,\qquad N=p^2(p+1)=3206262880419842.
\]

Thus the acceptance probability \(\rho\) is an integral multiple of \(1/N\). The fixed proof
parameters are

\[
D=15129,\quad s=5195,\quad b=s-1=5194,\quad q=D-d=15042,
\]

\[
\kappa=\frac{1610629120}{10871857153},\quad
E_D=2615604,\quad K_4=156513678.
\]

Write

\[
A=7349491214,\qquad \bar\varepsilon=\frac{A}{M},\qquad
\bar\tau=\frac{\bar\varepsilon}{10}
=\frac{3674745607}{108717834245}.
\]

## Prior Results

Researchers 2 and 3 supplied two complete presentations of the same \(C_4\)-sharpened theorem at
trigger \(\bar\varepsilon\). Each exact theorem received one independent accepting verifier audit.
The verifier for researcher 2 checked every load-bearing proof step, the exact fixed charge,
component conversion, reconstruction, recovery maximum, and score. The verifier for researcher 3
independently accepted the corresponding self-contained chain. These audits concern distinct
theorem hashes and are evidence for the shared mathematical chain; they are not audits of the
present synthesis hash.

Researcher 1 computed the continuous survival frontier

\[
R_*=\frac{1244293905093223}{3681259956715522}
\]

and observed that the discrete acceptance lattice permits the smaller terminating trigger
\(\varepsilon_{\mathrm{lat}}\) without changing the score or recovery count. This normalization is
the only mathematical strengthening over the two verified source submissions.

The proof below restates the common chain and uses researcher 3's direct lifting argument in place
of the analogous Kominers--Thaler--Zheng lemmas. Consequently no external theorem is imported.

## Theorem

**Theorem 1.** Let \(f:\mathbb F_{147457}^2\to\mathbb F_{147457}\), and assign a polynomial of
degree at most \(87\) to each affine line. If

\[
\operatorname{Pass}(f,P)\ge
\frac{3380076168821833}{10^{16}},
\]

then there is \(Q\in\mathbb F_{147457}[X,Y]\) of total degree at most \(87\) such that

\[
\Pr_x[Q(x)=f(x)]>
\frac{3674745607}{108717834245}.
\]

In particular, \(Q\) agrees with \(f\) on at least \(734949122\) points,
\(\varepsilon_{\mathrm{lat}}\ge1.1d/p\), and

\[
\Pr_x[Q(x)=f(x)]
\ge \max\left\{\frac{2d}{p},\frac{\varepsilon_{\mathrm{lat}}}{10}\right\}.
\]

## Proof or Conditional Proof

Every step below is proved; there are no conditional steps.

### [P1] Fixed field and incidence counts

The factorization \(p-1=2^{14}3^2\), together with

\[
10^{p-1}\equiv1,\qquad 10^{(p-1)/2}\equiv-1,
\qquad 10^{(p-1)/3}\equiv78348\pmod p,
\]

and the associated coprimality checks gives a Pocklington certificate that \(p\) is prime.
Standard affine-plane counting gives \(M,\Lambda,N\) as displayed above. Uniform-line-then-point
sampling is therefore uniform on the \(N\) incidences.

### [P2] Three-direction coverage

For a point of accepted pencil degree \(a\), a uniformly chosen set of three complete directions
misses its accepted pencil with probability

\[
H_a=\frac{\binom{h-a}{3}}{\binom h3}.
\]

The ratio of consecutive positive values of
\(a(h-a-1)(h-a-2)\) shows that its maximum occurs at \(a=49152\). Hence, for every
\(0\le a\le h\),

\[
aH_a\le \kappa(h-a),\qquad
\kappa=\frac{1610629120}{10871857153}.
\]

Averaging over the three chosen directions gives a union \(R\) of \(3p=442371\) lines for which
the number \(U_R\) of accepted incidences based at points missed by \(R\) satisfies

\[
\frac{U_R}{N}\le\kappa(1-\rho).
\]

### [P3] Squarefree weighted interpolation

Give \(X,Y,Z\) weights \(1,1,87\). The number of monomials of weighted degree at most \(D\) is

\[
V_D=\sum_{z=0}^{173}\binom{D-87z+2}{2}=6693082347.
\]

Formal vanishing on each selected line graph imposes at most \(D+1\) homogeneous linear
conditions, and

\[
3p(D+1)=6693073230<V_D.
\]

Thus a nonzero interpolant \(A(X,Y,Z)\) exists. A \(Z\)-independent interpolant would have total
degree at most \(D\) and be divisible by more than \(D\) distinct line equations, which is
impossible. Hence \(A\) depends on \(Z\), and \(\deg_ZA\le173<p\) gives \(A_Z\ne0\).

Choose such an interpolant of minimum weighted degree. If an irreducible factor occurred with
multiplicity at least two, division by one copy would preserve every formal line identity because
\(F[t]\) is a domain. The quotient cannot be \(Z\)-independent by the preceding line-divisibility
argument. It would therefore be a smaller eligible interpolant, a contradiction. Thus \(A\) is
squarefree.

### [P4] Identity-line extension

Call an accepted point covered if its accepted pencil meets \(R\). Let \(T\) contain \(R\) and
every other affine line having more than \(D\) covered accepted points. At every such point on a
line \(L\), one has \(A(x,P_L(x))=A(x,f(x))=0\). The polynomial
\(A(L(t),P_L(t))\) has degree at most \(D\), so more than \(D\) roots make it identically zero.

If \(t=|T|\) and \(E_T\) denotes accepted incidences on \(T\), then

\[
|E|\le |E_T|+U_R+D(\Lambda-t).
\]

### [P5] Primitive and derivative cleanup

Write \(A=CB\), where \(C\in F[X,Y]\) is the coefficient content in \(Z\) and \(B\) is primitive.
If \(c_0=\deg C\), \(W=\operatorname{wdeg}B\), and \(\nu=\deg_ZB\), then

\[
c_0+W\le D,\qquad 1\le\nu\le173<p,
\qquad \gcd(B,B_Z)=1.
\]

The nominal projective \(Z\)-discriminant has degree at most

\[
(\nu-1)(2W-87\nu).
\]

It detects derivative-degenerate identity lines even if the specialized leading coefficient
vanishes, because the homogenized specialization has a repeated finite projective root; no
leading coefficient is inverted. Including content lines, the number of exceptional identity
lines is at most

\[
c_0+(\nu-1)(2(D-c_0)-87\nu)\le E_D=2615604.
\]

On every other identity line, \(B_Z(L(t),P_L(t))\) is a nonzero polynomial of degree at most
\(D-87=15042\), so it has at most \(15042\) zeros.

### [P6] The fixed \(C_4\) corner

The point-line incidence graph of an affine plane is \(C_4\)-free. In any \(C_4\)-free bipartite
graph with part sizes \(5194\) and \(15129\), if the degrees on the second part are \(r_i\), then

\[
\sum_i\binom{r_i}{2}\le\binom{5194}{2}=13486221.
\]

Discrete convexity and

\[
646374=42\cdot15129+10956
\]

give equality in the lower convex bound at \(646374\) edges. One additional edge increases the
bound by \(42\), so the edge count is at most \(646374\). The resulting peeling credit is

\[
K_4=2\cdot15129\cdot5194-646374=156513678.
\]

Induction along any deletion order that removes point vertices at current degree at most \(15129\)
or line vertices at current degree at most \(5194\) yields

\[
|E_G|\le15129M+5194|Y|-156513678.
\]

For \(|Y|<15129\), the trivial bound \(|E_G|\le M|Y|\) suffices because the smallest remaining
margin is \(21665628003>0\).

### [P7] Survival of a simple-root core

Delete all accepted incidences on the \(e\le E_D\) exceptional lines, delete derivative-zero
incidences on the remaining identity lines, and peel at the degree thresholds above. If the graph
empties, [P2]--[P6] imply

\[
|E|\le U_R+C_*,
\]

where

\[
C_*=(15042+5195-1)\Lambda+15129M
 +(p-15042-5195+1)E_D-K_4
=769296828797543.
\]

Consequently complete deletion at density \(\rho\) would imply

\[
\rho\le\frac{C_*}{N}+\kappa(1-\rho),
\]

or \(\rho\le R_*\), where

\[
R_*=\frac{C_*/N+\kappa}{1+\kappa}
=\frac{1244293905093223}{3681259956715522}.
\]

Thus every realized acceptance density strictly above \(R_*\) leaves a nonempty core in which
point degrees are at least \(15130\), line degrees are at least \(5195\), every retained line is a
formal \(B\)-identity, and \(B_Z(x,f(x))\ne0\) on every retained edge.

### [P8] Component mass

For a point set of density \(a\) and a line set of density \(\ell\), the affine incidence matrix
satisfies \(II^\mathsf T=pI+J\). Centering the indicator vectors and applying Cauchy--Schwarz gives

\[
\frac{I(X,S)}N\le a\ell+
\sqrt{\frac{a(1-a)\ell(1-\ell)}h}.
\]

For a connected core component, set

\[
\alpha=\frac{15130}{147458},\qquad
\beta=\frac{5195}{147457},\qquad c=\frac\alpha\beta,
\qquad\gamma^2=\frac1{ch}.
\]

The two minimum-degree bounds and the mixing inequality imply

\[
\beta\le a+\gamma\sqrt{(1-a)(1-ca)}.
\]

For \(F(a)=(\beta-a)^2-\gamma^2(1-a)(1-ca)\), exact arithmetic at
\(\bar\tau=A/(10M)\) gives

\[
F(\bar\tau)=
\frac{498727149435244}{30939665878432433176225}>0,
\qquad
F'(\bar\tau)=\frac{-13793284387}{4837976433085}<0.
\]

Since \(F''=2(1-1/h)>0\), one has \(F(a)>0\) for every \(0\le a\le\bar\tau\), contradicting the
necessary component inequality. Every retained component therefore contains more than
\(\bar\tau M\) point vertices.

### [P9] Self-contained reconstruction

Choose a point \(x_0\) of a retained component and translate it to the origin. Put
\(a_0=f(x_0)\). Since \(B_Z(0,0,a_0)\ne0\), homogeneous terms
\(Q_1,\ldots,Q_{87}\) are determined recursively so that

\[
Q=a_0+Q_1+\cdots+Q_{87}
\]

solves \(B(X,Y,Q(X,Y))=0\) to successively higher total degree. Each of the at least \(D+1\)
retained line labels through \(x_0\) is a degree-at-most-\(87\) formal root with the same simple
constant value. The identical one-variable recursion shows that each label equals \(Q\) restricted
to its line.

The polynomial \(B(X,Y,Q(X,Y))\) has total degree at most \(D\) and vanishes formally on \(D+1\)
distinct seed lines, hence is identically zero. At any accepted simple intersection of a recovered
line and an adjacent retained line, the one-variable recursion again identifies the adjacent label
with the restriction of the same \(Q\). Connectivity propagates \(Q\) throughout the component,
and \(Q(x)=f(x)\) at every component point.

### [P10] Incidence-lattice normalization and target conversion

Let \(k_*=1083741275308516\). Exact cross multiplication gives

\[
\frac{k_*-1}{N}<\varepsilon_{\mathrm{lat}}<R_*<\frac{k_*}{N}.
\]

Because every realized acceptance probability lies in \(N^{-1}\mathbb Z\), the premise
\(\rho\ge\varepsilon_{\mathrm{lat}}\) forces \(\rho\ge k_*/N>R_*\). Steps [P7]--[P9] yield a
polynomial agreeing on more than \(\bar\tau M=734949121.4\) points, hence on at least
\(734949122\) points.

Finally,

\[
\varepsilon_{\mathrm{lat}}\ge\frac{957}{10p},\qquad
\bar\tau>\frac{\varepsilon_{\mathrm{lat}}}{10}>\frac{174}{p},
\qquad \left\lceil M\varepsilon_{\mathrm{lat}}\right\rceil=A.
\]

This proves Theorem 1.

## Soundness Ledger

| Stage | Exact loss or threshold | Result |
|---|---:|---|
| Direction coverage | \(\kappa(1-\rho)\) | Three complete directions |
| Interpolation | \(6693082347-6693073230=9117\) surplus | Squarefree relation of weight at most \(15129\) |
| Identity transfer | \(D(\Lambda-t)\) | All retained lines are identities |
| Exceptional lines | \(e\le2615604\) | Primitive nondegenerate identities |
| Derivative zeros | At most \(15042\) per regular identity line | Simple retained incidences |
| Two-sided peeling | \(15129M+5194(t-e)-156513678\) | \(C_4\) credit counted once |
| Fixed charge | \(C_*=769296828797543\) | Survival frontier \(R_*\) |
| Component conversion | Exact centered affine mixing | Density greater than \(\bar\tau\) |
| Reconstruction | No agreement loss | One total-degree-\(87\) polynomial |
| Lattice conversion | \(\lceil N\varepsilon_{\mathrm{lat}}\rceil=k_*\) | Realized acceptance exceeds \(R_*\) |
| Required recovery | \(\max\{174/p,\varepsilon_{\mathrm{lat}}/10\}\) | At least \(734949122\) points |
| Score | \(\lceil M\varepsilon_{\mathrm{lat}}\rceil\) | \(7349491214\), equal to current record |

The accompanying certificate.py replays every large integer and rational comparison in this
ledger using exact arithmetic.

## Corpus Synthesis and Improvement Frontier

The completed artifacts imply the following division of labor.

1. Researchers 2 and 3 establish the current record chain. Researcher 3's direct lifting proof
   removes the need to cite KTZ for reconstruction.
2. Researcher 1 shows that the same score admits the smaller terminating trigger used here. It
   also proves that \(D'=15128,s=5195\) with two complete directions and \(p-58\) lines of a third
   has score \(7349599431\), which is worse by \(108217\).
3. At \(D'=15128,s=5194\), survival gives the nominal improved score \(7349471019\), but the current
   component endpoint is negative. A stronger component theorem is the shortest identified route
   to a genuine lower score.
4. At the present \(D=15129,s=5195\), a one-score improvement requires at least \(25216\) additional
   fixed-incidence credits. The whole-relation derivative charge is locally sharp, while the
   example \(B=Z(Z+g(X))\) indicates that factor-aware cleanup may avoid charging irrelevant
   factors.
5. Researcher 4 proves a clean lossless interpolation and simple-transition package at
   \(D=17642\). It is reusable in that parameter regime but is not compatible with the sharper
   \(D=15129\) score without restatement.
6. Researcher 5 proves exact Johnson, overwrite, weak-to-list, and list-to-one lemmas. The route
   cannot presently compete: the needed size-\(90\) list-cover statement at
   \(K=252832173\) is unproved, and an explicit \(86\)-color table refutes the natural bridge from
   the available \(3\%\) Johnson list.
7. Earlier message-board score-one arguments are invalid under the amended conditions
   \(\varepsilon\ge1.1d/p\) and recovery at least \(2d/p\).

## Counterexample Attempts

- A \(49152\)-direction construction saturates the point-degree-only direction envelope, showing
  that improvement requires label information or correlations beyond the present envelope.
- The relation \(B=Z(Z+g(X))\), with \(g\) having \(15042\) roots, saturates the whole-relation
  derivative-zero charge on one branch even though the factor \(Z\) already gives the desired
  global polynomial.
- The choice \(s=5194\) lowers the survival score but fails the displayed component certificate;
  this is an obstruction to the proof architecture, not a counterexample to soundness.
- The \(86\)-color construction refutes the weak recovery statement needed by the natural
  \(3\%\)-Johnson splice.
- Inseparable relations such as \(Z^p-X\) lie outside the weighted-degree budget because
  \(87p>D\).

## Characteristic Audit

All work is over the prime field \(\mathbb F_{147457}\). The bounds
\(87<15129<147457\), \(\deg_ZB\le173<p\), and \(15042<p\) justify ordinary derivatives and
univariate root counts. The discriminant argument uses projective homogenization and does not
divide by a specialized leading coefficient. Reconstruction divides only by the nonzero first
derivative at a simple root. No extension field, irreducibility assumption, higher-dimensional
bootstrap, floating-point estimate, or randomized certificate occurs in the proof.

## Limitations

This synthesis does not lower the absolute agreement-count record. The smaller trigger
\(\varepsilon_{\mathrm{lat}}\) lies in the same score cell as the verified source theorem, so marking
it as a leaderboard improvement would contradict the campaign's absolute-count objective. The
present theorem hash has not itself been independently audited, although its principal source
chains have two separate accepting audits. The algebraic and list-decoding modules summarized
above do not close either identified improvement frontier. No assertion is made that the current
score is optimal.

## Team Handoff

The most economical next proof attempt should target exactly one of the following:

- strengthen the component inequality enough to validate \(D'=15128,s=5194\) at score
  \(7349471019\);
- save at least \(25216\) fixed incidences at \(D=15129,s=5195\), preferably through factor-aware
  derivative cleanup;
- replace the point-degree-only three-direction envelope with a label-sensitive selector.

Each target has a deterministic numerical success condition and can be investigated without
rerunning the full thirty-seat campaign.
