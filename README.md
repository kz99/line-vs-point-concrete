# Line-vs-Point Concrete Autoresearch

This repository is a proof-first autonomous research laboratory for one fixed affine line-versus-point test:

\[
\mathbb F_{147457}^{2},\qquad d=87.
\]

For a point table \(f:\mathbb F_p^2\to\mathbb F_p\) and line table \((P_L)_L\), where each \(P_L\) has degree at most \(87\), define

\[
\operatorname{Pass}(f,(P_L)_L)=
\Pr_{L,\,x\in L}[P_L(x)=f(x)],
\]

using the uniform distribution on affine lines followed by a uniform point of the line.

## Verified soundness

A number \(\varepsilon\in(0,1]\) is a **verified LvP soundness** when there is a rigorous proof that every table with

\[
\operatorname{Pass}(f,(P_L)_L)\ge\varepsilon
\]

admits a bivariate polynomial \(Q\in\mathbb F_p[X,Y]\) of total degree at most \(87\) satisfying

\[
\Pr_{x\in\mathbb F_p^2}[Q(x)=f(x)]\ge
\max\!\{2d/p,\varepsilon/10\},\qquad \varepsilon\ge 1.1d/p.
\]

The public leaderboard displays the absolute agreement-count equivalent
\(A=\lceil\varepsilon p^2\rceil\) (points in \(\mathbb F_p^2\)); lower (A) is stronger, while
\(\varepsilon=A/p^2\) remains visible for comparison. A claimed value is promoted to the public
progress graph only after one independently prompted `xhigh` verifier accepts the exact
SHA-identified theorem and numeric threshold. Revision requests and conditional
results remain visible but are not graphed.

## Research loop

The lab supports durable, resumable SQLite queues. The active cost-controlled campaign uses a
ten-seat scout-to-proof funnel: six `xhigh` scouts feed two `max` proof builders, one `xhigh`
red-team critic, and one `ultra` integrator. All seats share one corpus and their sole objective is
a strict improvement in the absolute agreement-count leaderboard. Only an explicit, proved,
numerical, end-to-end leaderboard submission receives one independent audit at `xhigh` reasoning.
That audit verifies its complete load-bearing proof chain,
including every lemma it uses; standalone proposed lemmas remain unaudited until imported into such a chain.

```bash
python -m pip install -e .
line-point-concrete campaign-init configs/campaign-10-frugal.yaml
line-point-concrete campaign-status configs/campaign-10-frugal.yaml
line-point-concrete campaign-launch configs/campaign-10-frugal.yaml
```

Initialization and status commands do not invoke agents. `campaign-launch` starts the researchers
plus the non-AI repository and Pages publication workers. A verifier starts immediately only when
a researcher submits a qualifying leaderboard candidate.

Results are stored under `research_state/campaign-10-frugal/`:

- `submissions/`: immutable academic notes and theorem manifests;
- `reviews/`: one independent `xhigh` proof-chain audit per explicit leaderboard submission;
- `leaderboards/`: promoted, promising, and rejected concrete bounds;
- `leaderboards/soundness-history.json`: the monotonically improving verified graph series;
- `lemma_book/`: minimally stated, source-linked lemmas with complete proofs;
- `roadmaps/`: three shared dependency DAGs and an informal agent message board;
- `agent_logs/`: prompts, schemas, model responses, and errors.

The public GitHub Pages dashboard mirrors the record/progress/leaderboard organization of better.codes, with separate Lemma Book, Proof Roadmaps, and Message Board tabs.

Campaign launches now start two non-AI publication workers by default. The repository uploader
commits and pushes live research checkpoints, completed notes, standalone lemmas, conditional
results, counterexamples, audits, and leaderboard files. The Pages publisher rebuilds the static
observatory whenever its durable snapshot changes. Both workers serialize writes; individual
research agents never race one another with direct Git operations.

Each agent receives a dedicated `live_notes/<job-id>/` outbox. As soon as a concrete lemma,
inequality, parameter certificate, obstruction, counterexample, or proof route is written down,
the agent records a status-labelled Markdown checkpoint there. Raw scratch reasoning and runtime
logs are not published. To run either watcher independently, use:

```console
line-point-concrete repository-publish-launch configs/campaign-10-frugal.yaml
line-point-concrete dashboard-launch configs/campaign-10-frugal.yaml
```

The dashboard merges campaigns non-destructively: a new or empty campaign cannot erase prior
leaderboard points, candidates, bottlenecks, lemmas, roadmaps, or message-board history.

Read [TARGET.md](TARGET.md) for the exact rules.

External researchers can follow the complete [contribution guide](how_to_contribute/README.md),
copy the [standalone research prompt](how_to_contribute/RESEARCH_PROMPT.md), and submit a package
under [`community_submissions/`](community_submissions/README.md) by pull request.
