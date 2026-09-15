# Exact Current-Record Ledger and the D=15128 Partial-Direction Obstruction

## Abstract

For `p=147457`, total degree `d=87`, and uniform affine-line-then-point sampling, the live campaign harness records score

`A=7349491214`

at the canonical trigger `bar ε=A/p²=7349491214/21743566849`. The underlying exact chain has continuous survival frontier

`R*=1244293905093223/3681259956715522`.

Acceptance lies on the `1/N` incidence lattice. Consequently the same proof already gives soundness at the smaller terminating trigger

`ε*=3380076168821833/10^16`,

without changing either the score or the recovery count. It guarantees agreement greater than `bar ε/10=3674745607/108717834245`, hence at least `734949122` points. The required fraction at `ε*` is `max(174/p,ε*/10)=ε*/10`; the proved guarantee is slightly stronger.

The three dominant grouped losses by objective-relevant, one-at-a-time score sensitivity are regular-line cleanup, direction energy, and point peeling, with hypothetical score reductions `2598918767`, `2132433958`, and `1943011236`. A new exact attempt at `D′=15128` selects two complete directions and `p−58` lines of a third. Its interpolation surplus is positive, but the worsened direction envelope raises its score to `7349599431`, which is `108217` worse than the current score.

This is not a leaderboard submission: the score is not lowered, and the local harness has only one audit on each exact theorem hash.

## Test and Notation

Let `F=F_147457`. A point table is `f:F²→F`; every affine line `L` carries a univariate polynomial `P_L` of degree at most `87`. The test samples an affine line uniformly and then a point uniformly on that line, accepting when `P_L(x)=f(x)`.

Set

- `h=p+1=147458`;
- `M=p²=21743566849`;
- `Λ=p(p+1)=21743714306`;
- `N=p²(p+1)=3206262880419842`.

Thus the acceptance probability `ρ` is an integer multiple of `1/N`. The admissibility floor is `957/(10p)`, and the recovery contract is `max(174/p,ε/10)`.

For the current ledger,

`D=15129`, `q=D−87=15042`, `s=5195`, `k=s−1=5194`, `ν_max=173`, `E_D=2615604`,

`κ=1610629120/10871857153`.

The canonical trigger is `bar ε=A/M`; its incidence premise is `|E|≥A·h=1083741275434012`. Put

`bar τ=bar ε/10=3674745607/108717834245`.

The lattice-normalized claimed trigger is

`ε*=3380076168821833/10^16`,

and its required recovery fraction is

`ε*/10=3380076168821833/10^17`.

## Prior Results

The active scan excluded every directory named `superseded` and covered all 16 top-level researcher submissions, the leaderboard files, 18 verifier audits, and the active message board. The configured comparison value `0.35922904602094702` has score `7810920777`; the historical two-auditor theorem used the score-equivalent exact value `359229046020947/10^15` and recovery count `781092078`.

At the final snapshot, [soundness-history.json](</Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/leaderboards/soundness-history.json:1>) promotes researcher-0002 with theorem SHA `0deb37bf169eaa842a2de0ca23041121bf46964ea643bdd6c7df36164be0370f`, score `7349491214`, and only `verifier-a-researcher-0002`. The [audit](</Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/reviews/researcher-0002/verifier-a-researcher-0002/audit.json:1>) accepts the chain without repair. Researcher-0003 has the same score and one accept under the distinct SHA `53c9e438528bd0576c18932996e7607f719d4f9e051243f15e86889aae6b4762`. Two different one-audit theorem hashes do not constitute two audits of one theorem.

The harness currently has `verification_threshold=1` and labels these artifacts `double_verified`; the task contract requires two independent auditors. Accordingly, `7349491214` is the operational local record, whereas `7810920777` remains the last record satisfying the stated two-auditor policy.

The current proof is in [researcher-0002/note.md](</Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/campaign-30-leaderboard/submissions/researcher-0002/note.md:1>). Its deterministic exact checker is included there. The root [DATA_MANIFEST.json](</Users/kaizheng/.codex/worktrees/1f44/SSE-auto/Line-vs-Point-concrete/research_state/DATA_MANIFEST.json:1>) is stale and omits campaign-30.

The only proof-theoretic literature imports are KTZ Lemmas 2.5, 2.7, and 6.1 from the [official ECCC revision](https://eccc.weizmann.ac.il/report/2026/147/revision/1/download). Their statements above are paraphrases, not quotations. KTZ Theorem 1.1 is not instantiated numerically because its constants are unnamed and its printed recovery is too weak here. HKSS Appendix B is not used.

## Theorem

**Theorem 1.** Let `p=147457`, `d=87`, and `ε*=3380076168821833/10^16`. For every `f:F_p²→F_p` and every affine-line table of degree at most `87`, acceptance probability at least `ε*` implies the existence of `Q∈F_p[X,Y]` of total degree at most `87` such that

`Pr_x[Q(x)=f(x)]>3674745607/108717834245`.

Consequently, `Q` agrees with `f` on at least `734949122` points and `ceil(ε*p²)=7349491214`.

**Proposition 2.** Let `D′=15128` and `s=5195`. Select two complete directions and `p−58` uniformly chosen lines in a third distinct direction. The corresponding three-direction interpolation, primitive cleanup, C4 peeling, component-mass, and reconstruction chain has first integer score `7349599431` and recovery count `734959944`.

## Proof or Conditional Proof

### [P1] Field and normalization — proved

The complete factorization is `p−1=2^14·3²`. Modulo `p`, base 10 satisfies `10^(p−1)=1`, `10^((p−1)/2)=p−1`, `10^((p−1)/3)=78348`, and the two associated Pocklington gcds equal one. Hence `p` is prime. Standard affine-plane counting gives `M`, `Λ`, and `N` above.

### [P2] Current core-survival ledger — proved

The three-direction averaging lemma gives uncovered-incidence loss at most `κ(1−ρ)`. The interpolation space has dimension `6693082347`, while the `3p` selected lines impose at most `442371·15130=6693073230` constraints, leaving surplus `9117`.

Let `t` be the number of identity lines and `e≤E_D` the number of exceptional lines. Identity extension, derivative cleanup, and C4 peeling give

`|E|≤U_R+D(Λ−t)+pe+q(t−e)+DM+k(t−e)−K4`,

where `K4=156513678`. Since `q+k−D=5107>0` and `p−q−k=127221>0`, maximizing at `t=Λ` and `e=E_D` yields

`|E|≤U_R+C*`,

with

`C*=(q+s−1)Λ+DM+(p−q−s+1)E_D−K4`

`=440005802696216+328958422858521+332759756484−156513678`

`=769296828797543`.

Thus complete deletion implies

`ρ≤C*/N+κ(1−ρ)`.

Its continuous frontier is

`R*=(C*/N+κ)/(1+κ)=1244293905093223/3681259956715522`.

Exact division gives

`R*M=7349491213+548266597656141/3681259956715522`.

At `bar ε=A/M`, the normalized total loss is

`9400308072378016503/27810935621062861282`,

leaving margin

`1249813349/27810935621062861282>0`.

The component constants are

`α=15130/147458`, `β=5195/147457`, `c=13123673/4506143`, `γ²=1039/446204882`.

For `F(a)=(β−a)²−γ²(1−a)(1−ca)`, exact arithmetic gives

`F(bar τ)=498727149435244/30939665878432433176225>0`,

`F′(bar τ)=−13793284387/4837976433085<0`, and `F″=2(1−1/h)>0`.

Hence every retained component has point density greater than `bar τ`. KTZ Lemmas 2.7 and 6.1 then recover one total-degree-at-most-87 polynomial throughout that component.

### [P3] Incidence-lattice normalization — proved

Put `k*=1083741275308516`. Direct cross multiplication gives

`(k*−1)/N<ε*<R*<k*/N`,

`R*−ε*=809056458204087/18406299783577610000000000000000>0`,

and

`ceil(Nε*)=ceil(NR*)=k*`.

Because every realized acceptance probability is an integer multiple of `1/N`, `ρ≥ε*` implies `ρ≥k*/N>R*`. Step [P2] therefore gives a nonempty core and agreement greater than `bar τ`.

Moreover,

`ceil(Mε*)=7349491214`,

`ceil(Mε*/10)=734949122`,

`ε*−957/(10p)=497458891625961028681/1474570000000000000000>0`,

and

`ε*/10−174/p=481015891625961028681/14745700000000000000000>0`.

This proves Theorem 1. The normalization lowers numerical epsilon but not the campaign score.

### [P4] Dominant-loss ranking — proved

For fixed charge `C` and direction coefficient `λ`, define the strict-frontier score

`S(C,λ)=floor(M·(C/N+λ)/(1+λ))+1`.

Removing one grouped term while retaining every other interface gives:

| Removed term | New score | Score reduction | New recovery count |
|---|---:|---:|---:|
| regular-line joint charge `440005802696216` | `4750572447` | `2598918767` | `475057245` |
| direction energy `κ(1−ρ)` | `5217057256` | `2132433958` | `521705726` |
| point peeling `DM=328958422858521` | `5406479978` | `1943011236` | `540647998` |

Thus the objective-relevant grouped ranking is regular-line cleanup, direction energy, point peeling.

By raw normalized magnitude the ordering is

`20236/147457 > 15129/147458 > 23183517373213491200/236392952779034320897`.

At atomic resolution, score sensitivity ranks direction energy first, point peeling second, and derivative cleanup third; deleting the derivative charge `qΛ` gives score `5417640251`, a reduction of `1931850963`. Removing the exceptional correction saves only `1965464`; deleting the C4 credit worsens the score by `924`.

### [P5] Partial-third-direction coverage at D′=15128 — proved

Three complete directions would impose `6692630859` interpolation constraints, exceeding

`V_D′=6691759164`

by `871695`. The largest feasible selected-line count is

`r=floor((V_D′−1)/(D′+1))=442313=3p−58`,

and the resulting surplus is `5787`.

Choose two complete directions and `p−58` uniformly selected lines of a third. At a point of accepted degree `a`, the probability of receiving no selected accepted line is

`H′_a=((h−a)(h−a−1)/(h(h−1)))·(1−a(p−58)/(p(h−2)))`.

Writing

`G(a)=a(p−a)[p(p−1)−(p−58)a]`,

one has `aH′_a/(h−a)=G(a)/(p²(p²−1))`. The consecutive difference has the sign of

`442197a²−86956425273a+3206175914999808`.

Its values at `49161`, `49162`, and `p−1` are respectively positive, negative, and negative. Since it is an upward quadratic, `G` has its unique maximum at `a=49162`. Therefore

`aH′_a≤κ′(h−a)`,

where

`κ′=1945970716835469935/13132852758199672832`.

In particular,

`κ′−κ=22511313433215/772520750482333696>0`.

Distributing the 58 omissions among several selected directions only adds nonnegative degree-two and degree-three elementary-symmetric terms to the miss probability. Concentrating all omissions in one direction is therefore pointwise optimal within this symmetric three-direction selector family.

### [P6] D′ downstream obstruction — proved

For `D′=15128`, put `q′=15041`. Primitive cleanup gives `E_D′=2615260`. The C4 calculation gives

`Z′=646352`, `K4′=156503312`.

At `s=5195`, the fixed charge is

`C′=439984058981910+328936679291672+332718607720−156503312`

`=769253300377990`.

The resulting continuous frontier is

`R′=5096832235183716975/15078823475035142767`,

whose first strict integer score is

`A′=7349599431`.

The component constants are

`α′=15129/147458`, `β=5195/147457`, `c′=2230876953/766044310`, `γ′²=5195/2230876953`.

At `τ′=A′/(10M)`, the component endpoint equals

`10408671413351925899/715277796518802048170142600>0`.

Thus the full component and KTZ reconstruction interfaces remain valid, but `A′−A=108217`. Proposition 2 follows.

For a one-point improvement at these fixed `D′,s`, a replacement selector must satisfy

`κ_new<78621993727141/530630401283322`.

The present envelope exceeds this target by

`407947926583302485388851/47258818979494327483565580288`.

### [P7] Adjacent s barrier — proved

At the current `D=15129` but `s=5194`, survival alone would give score `7349362799`, yet the component endpoint is

`−4708014974534477/4207794559466810911966600<0`.

The largest canonical score passing the same endpoint certificate is `7349277107`; reconciling it with survival requires at least `14507831994` additional incidence credits.

At `D′=15128,s=5194`, survival gives the genuinely improved nominal score `7349471019`, but the endpoint is

`−1917047659123556921/715277796518802048170142600<0`.

These are failures of the present component certificate, not counterexamples to low-degree recovery.

### [P8] Factor-sensitive derivative obstruction — proved

Let

`g(X)=∏_{a=0}^{15041}(X−a)`, `B(X,Y,Z)=Z(Z+g(X))`.

Then `B` is squarefree, `deg_Z B=2<p`, and its `(1,1,87)`-weighted degree is `15129`. On the root branch `Z=0`, one has `B_Z=g(X)`. The derivative vanishes at exactly `15042p` points, each incident with `h` affine lines, hence at exactly

`15042ph=15042Λ=327068950590852`

incidences. The factor `Z` itself has derivative one and supplies the global root `Q=0`. Thus the whole-relation derivative charge is sharp, while a factor-aware charge can be much smaller.

### [P9] Certification state — proved

At `2026-09-15T09:14:37Z`, the active history contains exactly one point and lists exactly one verifier ID for its theorem hash. The review tree contains one audit for researcher-0002 and one for the distinct researcher-0003 hash. Therefore neither score-`7349491214` theorem has two independent audits on one exact digest. This metadata fact does not weaken the mathematical derivations above, but it blocks a two-auditor leaderboard claim.

## Soundness Ledger

| Stage | Exact loss | Output |
|---|---:|---|
| sampling normalization | none; `N=3206262880419842` | uniform accepted-incidence density `ρ` |
| three-direction coverage | `κ(1−ρ)`, `κ=1610629120/10871857153` | one union of three complete directions |
| interpolation | no incidence loss; surplus `9117` | weighted degree `D=15129` relation |
| missing identity lines | `D(Λ−t)` | every retained line is a formal identity |
| exceptional identity lines | `pe`, `e≤2615604`; raw maximum `385689119028` | primitive nondegenerate identity lines |
| derivative-zero incidences | `15042(t−e)`; atomic maximum `15042Λ` | simple roots on regular lines |
| point/line peeling | `15129M+5194(t−e)−156513678` | minimum degrees `15130,5195` |
| consolidated regular charge | `(15042+5195−1)Λ=440005802696216` | includes identity, derivative, and line-peel terms; not additive with the preceding rows |
| point charge | `15129M=328958422858521` | point-degree threshold |
| exceptional correction | `127221·2615604=332759756484` | worst-case exceptional-line adjustment |
| C4 credit | `−156513678` | saves `924` score points |
| fixed subtotal | `C*=769296828797543` | normalized charge `C*/N` |
| energy at `bar ε` | `23183517373213491200/236392952779034320897` | uncovered-incidence charge |
| total survival loss at `bar ε` | `9400308072378016503/27810935621062861282` | below `bar ε` by `1249813349/27810935621062861282` |
| centered affine mixing | `sqrt(a(1−a)b(1−b)/147458)` | sole Cauchy–Schwarz loss |
| component endpoint | `F(bar τ)>0` | every component has density `>bar τ` |
| polynomial reconstruction | no agreement loss | one total-degree-at-most-87 polynomial |
| incidence-lattice normalization | no score loss; `ceil(Nε*)=ceil(NR*)` | valid trigger `ε*<R*` |
| required recovery | `max(174/p,ε*/10)=ε*/10` | actual guarantee `>bar τ`, at least `734949122` points |

There is no Markov, union-bound, randomized-computation, or unrecorded reconstruction loss.

## Counterexample Attempts

- The 49842-direction table is accepted above the trigger but is globally explained by `Q=0`.
- The 49152-direction configuration saturates the averaged κ envelope but not the best adaptive selector.
- `B=Z(Z+g)` saturates the whole-B derivative count but is explained by the factor `Z`.
- `Z^p−X` is inseparable but lies far outside the weighted-degree budget.
- Branch switching for `Z²−X²` occurs only where `B_Z=0`, confirming the need for simple-root cleanup.

## Characteristic Audit

The prime-field certificate is explicit. Both interpolation budgets and all Z-degrees are strictly below `p`. Ordinary derivatives and root counts are therefore valid. No leading coefficient is inverted in the discriminant step. Newton lifting uses only a nonzero first derivative, not factorial division. Neither irreducibility nor extension fields are assumed. The line identities use distinct roots and total degree throughout.

## Limitations

The D′ obstruction applies only to the symmetric three-direction selector family with 58 omitted lines and the existing primitive-cleanup, peeling, and component interfaces. It does not rule out adaptive direction selection, different interpolation constraints, factor-aware reconstruction, or a stronger component theorem.

The counterfactual loss removals diagnose score leverage; they are not asserted constructions. The lattice normalization improves numerical epsilon but not `ceil(εp²)`. Finally, the operational score-`7349491214` artifact has one audit rather than the two required by this task, and campaign-30 is absent from the durable data manifest. No `benchmark.json` is present, so no Yukon benchmark operation was applicable.

## Team Handoff

- **exact-analytic / direction selection:** use the exact D′ target `κ_new<78621993727141/530630401283322`.
- **certified-computation / algebraic cleanup:** use the one-score fixed-credit target `ceil(3718145613/147457)=25216` incidences.
- **end-to-end-soundness / component mass:** attack the exact negative endpoint for `D′=15128,s=5194`; this route already has nominal score `7349471019`.
- **factor-aware reconstruction:** use `B=Z(Z+g)` as the regression example for component-factor derivative accounting.
- **verification/provenance:** obtain two matching audits for one theorem SHA and regenerate the campaign manifest.
