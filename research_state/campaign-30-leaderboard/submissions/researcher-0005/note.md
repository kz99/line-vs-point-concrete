# Abstract

For p=147457 and total degree d=87, I prove exact bivariate Johnson, overwrite, list-cover, and list-to-one statements. The exact Johnson bound gives at most 94 candidates at 3% agreement and at most 50 candidates at the comparison recovery count, but it stops at agreement 0.024289967… and therefore does not reach the useful below-Johnson regime. A common-factor construction gives 1693 candidates at the mandatory 2d/p floor, 90 candidates at ceil(p²/86), and 28 candidates at the comparison recovery count.

The affine list-to-one lemma retains every loss: a line-deviation term, an exact Cantelli/affine-design term, the rd/p nonstandard-line collision term, the unexplained-good-point mass, and a separate beta loss for accepted incidences at low-good points. At an exact below-Johnson interface with list size 90, it would turn acceptance

E₁ = 7,810,920,776 / 21,743,566,849 = 0.359229046009037…

into one polynomial agreeing on at least E₁/10, hence 781,092,078 points. Its score is 7,810,920,776, one below the comparison score. The needed size-and-coverage interface remains unproved. Moreover, an exact 86-color counterexample refutes the natural attempt to derive that interface from the available 3%-agreement Johnson list. Thus this note supplies a proved foundation obstruction and exact reusable conversion, not a leaderboard theorem.

# Test and Notation

Let F=F_147457, p=147457, d=87, and N=p²=21,743,566,849. There are p(p+1)=21,743,714,306 affine lines and N(p+1)=3,206,262,880,419,842 incidences. The verifier chooses a uniform geometric affine line L and then a uniform x in L. Since the incidence graph is biregular, this is equivalently a uniform point followed by a uniform one of its p+1 incident lines.

The point table is f:F²→F. Every affine line L has an arbitrary supplied univariate label P_L of degree at most 87. Write

- rho = Pr[P_L(x)=f(x)];
- g(x)=Pr_{L containing x}[P_L(x)=f(x)];
- x is beta-good when g(x)>=beta;
- A_Q={x:f(x)=Q(x)} and a_Q=|A_Q|/N;
- c=dp=12,828,759.

The admissibility floor is 957/1474570. For the one-score candidate

E₁=7,810,920,776/N,

gamma=E₁/10=3,905,460,388/108,717,834,245=0.0359229046009037… .

Here gamma>174/p, since the difference is 3,777,172,798/108,717,834,245. Therefore the amended recovery contract is max(174/p,E₁/10)=E₁/10, and its absolute count is ceil(gamma N)=781,092,078.

# Prior Results

The strongest located Reed–Muller list-radius statement relevant here is Bhowmick–Lovett Theorem 1.6: over a prime field with |F|>d, agreement at least d/|F|+1/|F|^s has list size at most |F|^{c(d,s)}. At s=1 this already reaches 88/p, below the campaign floor, but c(87,1) is unnamed and gives no numerical list bound usable in an rd/p ledger. See [Bhowmick–Lovett, Theorem 1.6](https://eccc.weizmann.ac.il/report/2015/096/download).

HKSS define the appropriate good-point list-cover property in Definition B.2. Their v1 Appendix B contains two numerical proof defects discussed in [P8]: the printed hypotheses of Lemma B.4 do not imply the inequalities used in its proof, and Lemma B.6 neither accounts for low-good unexplained incidences nor adds its displayed case losses correctly. Consequently those lemmas are navigation aids, not load-bearing numerical imports here. See [HKSS v1, Appendix B](https://arxiv.org/pdf/2311.12752v1).

KTZ Lemmas 6.1 and 6.3 give the stronger list-free alternative: a simple seed with more than D root lines determines one global polynomial, which then propagates with no loss through connected simple-root transitions. See [KTZ revision 1](https://eccc.weizmann.ac.il/report/2026/147/revision/1/download). The active [campaign-30 researcher-0004 extraction](/Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/submissions/researcher-0004/response.json) specializes this to D=17642 and 17643 seed lines. Downstream modules possessing those hypotheses should use that no-loss route.

The active campaign-30 history still has no verified point. The supplied comparison epsilon 0.35922904602094702 has agreement-count score 7,810,920,777. The score-one roadmaps on the message board predate the amended max(174/p,epsilon/10) contract and are not used.

# Theorem

**Lemma 1 (exact bivariate Johnson bound).** Let 1<=K<=N satisfy K²>cN. For every f:F²→F, the number R_K(f) of distinct total-degree-at-most-87 polynomials Q satisfying |A_Q|>=K obeys

R_K(f) <= floor( N(K-c)/(K²-cN) ).

**Lemma 2 (common-factor lower lists).** Let c<K<=N and let 1<=r<p satisfy r(K-c)<=N-c. There are f:F²→F and r distinct total-degree-at-most-87 polynomials Q_1,…,Q_r such that |A_{Q_i}|=K for every i and |A_{Q_i} intersect A_{Q_j}|=c for every i≠j.

**Lemma 3 (fixed overwrite lemma).** For every f:F²→F and T subset F², there is g:F²→F equal to f outside T such that every total-degree-at-most-87 polynomial Q agrees with g at fewer than s=493,416 points of T.

**Lemma 4 (weak recovery to list coverage).** Let sigma,beta,u be nonnegative reals with beta·u>=sigma, and let H,K be integers with H>=K+493,415. Suppose every point/line table of acceptance at least sigma has a total-degree-at-most-87 polynomial agreeing with its point table on at least H points. Then, for every f and line table, the set L_K(f)={Q:|A_Q|>=K} leaves at most uN beta-good points x with f(x) not in {Q(x):Q in L_K(f)}.

**Lemma 5 (exact affine list-to-one conversion).** Let 0<gamma<1/2, beta,u>=0, t>0, and let Q_1,…,Q_r be distinct total-degree-at-most-87 polynomials. Suppose at most uN beta-good points are unexplained by this list. If

rho >= gamma+t + r·gamma(1-gamma)/(gamma(1-gamma)+(p+1)t²) + 87r/p + beta+u,

then some Q_i satisfies a_{Q_i}>=gamma.

**Conditional fixed-instance theorem.** Define

K_86=ceil(N/86)=252,832,173,

t=7/200,

lambda=280,765,415,738,023/2,664,116,737,257,800,

b=85,607,619,234,595,001,849/785,685,323,451,646,829,200.

For every f and line table, suppose L_{K_86}(f) has at most 90 members and leaves at most bN b-good points unexplained. If rho>=E₁, then one total-degree-at-most-87 polynomial agrees with f on at least gamma N and hence on at least 781,092,078 points.

# Proof or Conditional Proof

[P1] **Proved.** For distinct Q_i,Q_j, the nonzero polynomial Q_i-Q_j has total degree at most 87, so it has at most dp=c zeros in F². Let n_x be the number of list members agreeing with f at x and I=sum_x n_x. Then

sum_x binom(n_x,2) <= binom(r,2)c,

while Cauchy–Schwarz gives

sum_x binom(n_x,2) >= (I²/N-I)/2.

Put alpha=K/N and delta=c/N. The proposed bound B=(alpha-delta)/(alpha²-delta) satisfies B>=1/(2alpha). If r>B, then I>=r alpha N>N/2, so z²/N-z is increasing throughout the relevant interval. Substitution of I>=r alpha N gives

r alpha²-alpha <= (r-1)delta,

hence r<=B, a contradiction. This proves Lemma 1.

At K_3=ceil(3N/100)=652,307,006, the bound is 94. At K=781,092,078, it is 50. The smallest integer K for which the denominator is positive is 528,150,527, corresponding to agreement 0.0242899672656… . At K_86, K_86²-cN=-215,018,871,202,308,462, so Johnson supplies no bound.

[P2] **Proved.** Choose 87 distinct a-values and put H(X)=product_a(X-a). Its zero set Z consists of 87 parallel affine lines and has |Z|=c. Choose distinct constants zeta_1,…,zeta_r and disjoint sets T_i subset F²\Z of size K-c. Define Q_i=zeta_i H. Set f=0 on Z, f=Q_i on T_i, and at each remaining point choose a field value outside {Q_1(x),…,Q_r(x)}. This last choice is possible because r<p and H(x)≠0 makes those r values distinct. Thus A_{Q_i}=Z union T_i, proving Lemma 2.

The construction gives:

- r=1693 at K=2c, with unused complement 11,649,103 points;
- r=90 at K=K_86, with unused complement 130,430,830 points;
- r=28 at K=781,092,078, with unused complement 219,365,158 points.

[P3] **Proved.** There are exactly p^3916 formal bivariate polynomials of total degree at most 87. Randomly and independently replace f(x) by a uniform field value for x in T. For a fixed Q, the probability of at least s matches on T is at most binom(N,s)p^{-s}. Hence the probability that some Q has s matches is at most

p^3916 binom(N,s)p^{-s} < p^3916(3p/s)^s.

Here e<3 was used in the standard bound binom(N,s)<=(eN/s)^s. The remaining comparison is an integer certificate:

- 9s-30p=17,034>0, so s/(3p)>10/9;
- s=493,416=7·18·3916;
- 10^7-2·9^7=434,062>0, so (10/9)^7>2;
- p<2^18.

Therefore (10/9)^s>2^{18·3916}>p^3916, and the union probability is strictly below one. A deterministic g with the asserted property exists.

[P4] **Proved.** Let T be the union of A_Q over Q in L_K(f), and choose g from Lemma 3. If Q is outside the list, it has at most K-1 agreements with f outside T and at most s-1 agreements with g inside T. If Q is in the list, it has zero agreements with g=f outside T and at most s-1 inside T. Thus every Q agrees with g on at most K+s-2<=H-1 points.

If more than uN beta-good points of f were outside T, those points retain their values under the overwrite and contribute more than beta u>=sigma to the acceptance of (g,P). The hypothesized weak recovery theorem would then produce H agreements, a contradiction. This proves Lemma 4.

[P5] **Proved.** For a fixed set S of density a, let Y=|S intersect L| for a uniform affine line. Every point is on p+1 lines and every ordered pair of distinct points determines one line, so

E[Y]=a p,

E[Y(Y-1)]=|S|(|S|-1)/(p(p+1)),

Var(Y/p)=a(1-a)/(p+1).

Assume every candidate has a_i<gamma. Call L abnormal if |A_{Q_i} intersect L|/p>=gamma+t for some i. Cantelli's inequality and a_i(1-a_i)<gamma(1-gamma) give

Pr[L abnormal] < r gamma(1-gamma)/(gamma(1-gamma)+(p+1)t²).

A standard normal line contributes less than gamma+t acceptance. On a nonstandard line, P_L-Q_i restricted to L is a nonzero univariate polynomial of degree at most 87, so the fraction of points coinciding with at least one candidate is at most 87r/p. Good unexplained points contribute at most u. Points that are not beta-good contribute less than beta, including all low-good unexplained incidences. These four cases cover every accepted incidence and yield the strict upper bound contradicting the displayed premise of Lemma 5.

[P6] **Conditional.** Assume the two L_{K_86} hypotheses in the conditional theorem. Under the contrary assumption that no candidate reaches gamma, use gamma<9/250 and hence gamma(1-gamma)<2169/62500. With r=90 and t=7/200, the abnormal-line loss is at most

B=1,561,680/90,335,377=0.0172875793721…,

and the nonstandard coincidence loss is

7830/147457=0.0531002258285… .

Thus

lambda=7/200+B+7830/147457
      =280,765,415,738,023/2,664,116,737,257,800
      =0.105387805200690… .

The definition of b gives the exact closing identity

E₁ = gamma + lambda + 2b.

Lemma 5 therefore gives rho<E₁, contradicting rho>=E₁. Hence one candidate reaches gamma. Since gamma N=781,092,077.6, it agrees on at least 781,092,078 points. The score of E₁ is 7,810,920,776, exactly one below the comparison score.

Lemma 3 shows how the coverage hypothesis could be obtained: it would suffice to prove the sharp size bound |L_{K_86}(f)|<=90 and the weak theorem

acceptance >= b² = 7,328,664,471,015,400,130,221,789,954,532,313,418,801 / 617,301,427,487,318,898,967,840,521,526,413,972,640,000

implies at least

K_86+493,415=253,325,588

agreements. This output fraction is 0.0116505994513…, below b²=0.0118721003139…, so the interface is not ruled out by the basic color construction.

[P7] **Proved obstruction.** The natural explicit-Johnson splice instead takes K_3=652,307,006 and r=94. Its exact list-to-one balance has

lambda_94=516,242,693,665,555/4,757,315,129,572,852,

b_94=753,377,354,251,711,533,937/7,014,994,170,614,240,373,640,

sigma_94=b_94²<29/2500.

Lemma 4 would require the weak conclusion H_3=K_3+493,415=652,800,421.

Choose 86 distinct field values and sample f(x) independently and uniformly from them. Every line has a majority value occurring at least ceil(p/86)=1715 times; labeling that line by the corresponding constant gives acceptance at least 1715/p>29/2500>sigma_94.

For any fixed Q, its agreement indicators are independent Bernoulli variables with mean at most 1/86. Since H_3/N>3/100 and 3/100-1/86=79/4300, Hoeffding's inequality gives failure probability below exp(-2N(79/4300)²). Union bounding over p^3916 polynomials is still below one because

2N·79²-18·3916·4300²=270,099,878,289,218>0,

p<2^18, and ln 2<1. Thus some such table has no degree-87 polynomial with H_3 agreements. The required weak theorem is false, so the explicit 3%-Johnson splice cannot close.

[P8] **Refuted imported inferences.** HKSS v1 Lemma B.4 prints the hypothesis

h(beta_0'^2) >= max(e/(2 sqrt(q)), 2(d+1)/q, sqrt(d/q)),

but its proof sets eta=h/2 and invokes eta>=e/sqrt(q), eta>=4(d+1)/q, and eta>=2sqrt(d/q). The printed inequalities do not imply those uses. The same proof would be safe under the stronger sufficient condition

h(beta_0'^2) >= max(2e/sqrt(q), 8(d+1)/q, 4sqrt(d/q)).

In Lemma B.6, Definition B.2 controls unexplained beta-good points only. Accepted incidences at points below the goodness threshold cost an additional beta term. Independently, the four displayed case bounds in the source are eta_1+beta, beta, beta, and beta, which do not sum to eta_1+3beta. These observations refute those proof inferences, not the possibility that the source theorem has another repair. Lemma 5 is the independently proved replacement used here.

[P9] **Proved finite certificate.** The following exact checker verifies every large integer and rational used above.

```python
from fractions import Fraction as F
p,d=147457,87
N=p*p; c=d*p; dim=(d+1)*(d+2)//2
ceilf=lambda x:(x.numerator+x.denominator-1)//x.denominator
assert (N,p*(p+1),N*(p+1),c,2*c)==(
  21743566849,21743714306,3206262880419842,12828759,25657518)
K3=ceilf(F(3,100)*N)
num=N*(K3-c); den=K3*K3-c*N
assert (K3,num-94*den,num-95*den)==(
  652307006,127761602101311073,-18799849069162572)
s=493416
assert dim==3916 and 9*s-30*p==17034
assert s==7*18*dim and 10**7-2*9**7==434062
E=F(7810920776,N); gamma=E/10
assert ceilf(E*N)==7810920776 and ceilf(gamma*N)==781092078
assert gamma>F(174,p)
K86=ceilf(F(1,86)*N)
assert K86==252832173 and divmod(N-c,K86-c)==(90,130430830)
cp=F(2169,62500); t=F(7,200); r=90
B=r*cp/(cp+F(p+1)*t*t)
lam=t+B+F(r*d,p)
assert B==F(1561680,90335377)
assert lam==F(280765415738023,2664116737257800)
S=E-gamma-lam; b=S/2; sigma=b*b
assert b==F(85607619234595001849,785685323451646829200)
assert sigma>F(K86+s-1,N)
T=F(35922904602094702,10**17)
assert ceilf(T*N)==7810920777
Krec=ceilf(T*N/10)
assert Krec==781092078
assert divmod(N-c,Krec-c)==(28,219365158)
assert divmod(N-c,c)==(1693,11649103)
r=94; t=F(1,28)
B94=r*cp/(cp+F(p+1)*t*t)
lam94=t+B94+F(r*d,p)
b94=(E-gamma-lam94)/2; sig94=b94*b94
assert B94==F(19980828,1152228187)
assert sig94<F(29,2500)<F(1715,p)
assert 100*(K3+s-1)-3*N==49341553
assert 2*N*79**2-18*dim*4300**2==270099878289218
```

# Soundness Ledger

| Stage | Exact loss or threshold | Status |
|---|---:|---|
| Candidate acceptance | E₁=7,810,920,776/N | conditional target |
| Admissibility | E₁-957/(10p)=77,968,091,411/(10p²)>0 | proved |
| Recovery contract | max(174/p,E₁/10)=E₁/10 | proved |
| Recovery count | ceil(E₁N/10)=781,092,078 | proved |
| Below-Johnson candidate threshold | K_86=252,832,173 | proved definition |
| Candidate-list size | at most 90 | conditional; sharp lower construction has 90 |
| Goodness threshold | beta=b=0.108959168103722… | conditional interface |
| Unexplained-good density | u=b | conditional interface |
| Standard-line deviation | t=7/200 | proved loss |
| Abnormal lines | 1,561,680/90,335,377 | proved by exact variance and Cantelli |
| Nonstandard coincidences | 7830/147457 | proved by univariate root counting |
| Low-good plus unexplained-good | beta+u=2b | proved once coverage holds |
| Total structural loss | lambda=280,765,415,738,023/2,664,116,737,257,800 | proved |
| Closing identity | gamma+lambda+2b=E₁ | proved |
| Overwrite cap | s=493,416 points | proved |
| Weak bridge output | H=253,325,588 points | conditional |
| Weak bridge trigger | b²=0.0118721003138551… | conditional |
| Comparison score | 7,810,920,777 | proved |
| Candidate score | 7,810,920,776 | conditional one-count improvement |
| Derivative/discriminant/interpolation loss | zero; not used | proved |

# Counterexample Attempts

The common-factor construction succeeds against small universal lists. At the mandatory recovery floor it gives 1693 candidates. At the proposed K_86 interface it gives exactly 90 exhibited candidates, making 90 the smallest possible universal upper bound. At the comparison recovery count it gives 28 candidates, leaving a genuine gap to the exact Johnson upper bound 50.

The 86-color construction succeeds against the natural weak theorem needed by the 3%-Johnson splice. Its line labels are constants, so it respects total degree 87 without interpolation or separability assumptions. It does not refute the line-versus-point theorem at the campaign recovery floor; it only proves that this particular weak-to-list parameter choice is impossible.

A one-direction table also shows why unexplained low-good incidences cannot be discarded. This attacks the inference used in HKSS v1 B.6, not the repaired list-to-one lemma.

# Characteristic Audit

The field remains F_147457 throughout. The upstream exact certificate has p-1=2^14·3² and verifies Pocklington's modular and gcd conditions. The list arguments need only p>87 and at least 86 distinct field values.

Schwartz–Zippel and univariate root counting are characteristic-free. No ordinary or Hasse derivative is taken. No discriminant, resultant, leading coefficient, irreducible factor, or interpolation multiplicity is divided by. Inseparability examples such as Z^p-X therefore do not affect these lemmas. The polynomial code dimension is exactly binom(89,2)=3916 because the convention is total degree, not individual degree.

The affine variance identity averages all p(p+1) lines and follows from the exact two-design property: every ordered pair of distinct points lies on one affine line. Concentration in a few directions is fully charged to the abnormal-line term.

# Limitations

The sharp below-Johnson statement |L_{K_86}(f)|<=90 is not proved. Bhowmick–Lovett gives only p^{c(87,s)} with an unnamed exponent and cannot discharge it. The associated good-point coverage statement is also unproved. Consequently E₁ is not a claimed soundness value, and this note is not a leaderboard submission.

The color-table obstruction refutes only the stated 3%-Johnson weak bridge. It does not rule out a stronger bivariate structural list theorem near 1/86, a direct list-cover proof, or the existing list-free simple-root route.

The HKSS audit identifies failures in the printed v1 derivations. It does not claim that their high-agreement theorem is false after suitable repairs.

# Team Handoff

- **Below-Johnson list-decoding module:** attack the exact statement |L_{252,832,173}(f)|<=90. Return a counterexample if 91 candidates are possible; 90 is already attained.
- **List-cover module:** target beta=u=85,607,619,234,595,001,849 / 785,685,323,451,646,829,200. This single coverage interface plus the size bound activates [P6].
- **Weak-recovery module:** an alternative sufficient interface is acceptance at least b² implying 253,325,588 agreements. Lemma 3 then supplies coverage.
- **End-to-end soundness module:** import [P5] with r=90 and t=7/200. The exact closing identity yields score 7,810,920,776 and 781,092,078 recovered points.
- **Simple-root reconstruction modules (ea-r1-08/ea-r1-09 successors):** if the active D=17642 simple-component hypotheses are available, use the researcher-0004 lossless recovery instead of this list conversion.
- **Auditors:** reject verbatim numerical uses of HKSS v1 B.4/B.6 unless the constant mismatch and low-good loss are repaired explicitly.
