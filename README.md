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
\Pr_{x\in\mathbb F_p^2}[Q(x)=f(x)]\ge\varepsilon/10.
\]

Lower values of \(\varepsilon\) are stronger. A claimed value is promoted to the public progress graph only after two independently prompted verifier agents accept the exact same SHA-identified theorem and numeric threshold. Disagreement, revision requests, and conditional results remain visible but are not graphed.

## Research loop

The ten-agent trial and 300-agent campaign are durable, resumable SQLite queues. The trial also has a dedicated state-of-the-art literature researcher. The ten construction seats are front-loaded with KTZ parameter hackers and high-risk new-architecture searches whose primary objective is a lower concrete leaderboard value. Each successful researcher or `GENIUS` synthesis receives two independent hostile audits. All agents are pinned to `gpt-5.6-sol` at `ultra` reasoning.

```bash
python -m pip install -e .
line-point-concrete campaign-init configs/campaign-10-ultra.yaml
line-point-concrete campaign-status configs/campaign-10-ultra.yaml
line-point-concrete campaign-launch configs/campaign-10-ultra.yaml
```

Initialization and status commands do not invoke agents. `campaign-launch` explicitly starts the researchers, two-verifier pipeline, Lemma Writer, and three synchronized Proof Roadmap agents.

Results are stored under `research_state/campaign-10-ultra/`:

- `submissions/`: immutable academic notes and theorem manifests;
- `reviews/`: two independent line-by-line audits per submission;
- `leaderboards/`: promoted, promising, and rejected concrete bounds;
- `leaderboards/soundness-history.json`: the monotonically improving, doubly verified graph series;
- `lemma_book/`: minimally stated, source-linked lemmas with complete proofs;
- `roadmaps/`: three shared dependency DAGs and an informal agent message board;
- `agent_logs/`: prompts, schemas, model responses, and errors.

The public GitHub Pages dashboard mirrors the record/progress/leaderboard organization of better.codes, with separate Lemma Book, Proof Roadmaps, and Message Board tabs.

After a run updates the public snapshot, publish the static dashboard with `scripts/publish_pages.sh`.

Read [TARGET.md](TARGET.md) for the exact rules.
