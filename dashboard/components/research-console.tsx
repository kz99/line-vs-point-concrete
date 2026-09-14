'use client';

import { useEffect, useMemo, useState } from 'react';
import { BookOpen, Check, FlaskConical, Map, MessageSquare, RefreshCw, Search, ShieldCheck } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

type Audit = { verifier_id: string; verdict: 'accept' | 'revise' | 'reject'; verified_soundness: number | null; summary: string; required_changes: string[] };
type SoundnessStage = { stage: string; input_bound: string; output_bound: string; loss: string; justification: string; status: string };
type Candidate = { job_id: string; role: string; title: string; result_status: string; claimed_soundness: number | null; theorem_statement: string; theorem_sha256: string; review_verdict: string; double_verified: boolean; audits: Audit[]; soundness_ledger: SoundnessStage[]; note_markdown: string };
type HistoryPoint = { job_id: string; title: string; soundness: number; previous_best: number; gain: number; verified_at: string | null; verifier_ids: string[]; theorem_sha256: string };
type Lemma = { id: string; source_job_id: string; source_step_id: string; part: number; title: string; statement_markdown: string; proof_markdown: string; status: string; dependencies: string[]; editorial_status: string };
type RoadmapNode = { id: string; label: string; statement_markdown: string; proof_state: string; dependencies: string[]; resolved_lemma_ids: string[]; notes: string };
type Roadmap = { roadmap_id: string; title: string; focus: string; target_statement: string; summary: string; round: number; progress: { percent: number; verified: number; provisional: number; open: number; blocked: number; total: number }; critical_path: string[]; nodes: RoadmapNode[] };
type BoardMessage = { id: string; author: string; channel: string; kind: string; subject: string; body_markdown: string; created_at: string; related_node_ids: string[]; references: string[] };
type Job = { id: string; role: string; status: string };

export type ResearchSnapshot = {
  schema: string;
  campaign: string;
  status: { model: string; reasoning_effort: string; fixed_prime: number; fixed_degree: number; recovery_divisor: number; researcher_count: number; planned_agent_invocations: number; counts: Record<string, number>; updated_at: string };
  candidates: { verified: Candidate[]; promising: Candidate[]; rejected: Candidate[] };
  bottlenecks: SoundnessStage[];
  soundness_history: { points: HistoryPoint[]; verification_threshold: number; lower_is_better: boolean };
  lemma_book?: { editorial_rule: string; model: string; reasoning_effort: string; lemmas: Lemma[] };
  proof_roadmaps?: { status: string; round: number; roadmaps: Roadmap[]; active_roadmaps: string[] };
  message_board?: { messages: BoardMessage[] };
  jobs: Job[];
};

type View = 'record' | 'lemmas' | 'roadmaps' | 'messages';
const hashes: Record<View, string> = { record: 'record', lemmas: 'lemma-book', roadmaps: 'proof-roadmaps', messages: 'message-board' };

function MathText({ children, className = '' }: { children: string; className?: string }) {
  const normalized = children
    .replace(/\\\[([\s\S]*?)\\\]/g, '\n\n$$$$\n$1\n$$$$\n\n')
    .replace(/\\\(([\s\S]*?)\\\)/g, '$$$1$$')
    .replace(/\\begin\{align\*?\}([\s\S]*?)\\end\{align\*?\}/g, '\n\n$$$$\n\\begin{aligned}$1\\end{aligned}\n$$$$\n\n');
  if (className.split(' ').includes('inline')) {
    return <span className={`math-text ${className}`}><ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]} components={{ p: ({ children: content }) => <>{content}</> }}>{normalized}</ReactMarkdown></span>;
  }
  return <div className={`math-text ${className}`}><ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{normalized}</ReactMarkdown></div>;
}

function formatEpsilon(value: number | null | undefined) {
  if (value == null) return '—';
  return value < 0.001 ? value.toExponential(4) : value.toFixed(6).replace(/0+$/, '').replace(/\.$/, '');
}

function formatDate(value: string | null) {
  if (!value) return 'pending';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function RecordChart({ points }: { points: HistoryPoint[] }) {
  const width = 940, height = 330, left = 68, right = 24, top = 28, bottom = 48;
  const reference = 0.0838721841647049;
  const maximum = points.length ? Math.min(1, Math.max(reference, ...points.map((point) => point.soundness)) * 1.2) : 0.1;
  const x = (index: number) => left + (points.length <= 1 ? (width - left - right) / 2 : index * (width - left - right) / (points.length - 1));
  const y = (value: number) => top + (value / maximum) * (height - top - bottom);
  const line = points.map((point, index) => `${index ? 'L' : 'M'} ${x(index)} ${y(point.soundness)}`).join(' ');
  const ticks = [0, .25, .5, .75, 1].map((fraction) => ({ value: maximum * fraction, y: y(maximum * fraction) }));
  return <div className="chart-wrap">
    <svg className="record-chart" viewBox={`0 0 ${width} ${height}`} aria-label="Doubly verified soundness record, lower is better">
      {ticks.map((tick) => <g key={tick.value}><line x1={left} x2={width - right} y1={tick.y} y2={tick.y} className="grid-line" /><text x={left - 12} y={tick.y + 4} textAnchor="end">{formatEpsilon(tick.value)}</text></g>)}
      <line x1={left} x2={width - right} y1={y(reference)} y2={y(reference)} className="reference-line" />
      <text x={width - right} y={y(reference) - 8} textAnchor="end" className="reference-label">scale (d/p)^(1/3) ≈ 0.083872 · not a promoted result</text>
      {points.length > 0 && <path d={line} className="record-line" />}
      {points.map((point, index) => <g key={`${point.job_id}-${index}`} className="chart-point"><circle cx={x(index)} cy={y(point.soundness)} r="6" /><text x={x(index)} y={height - 16} textAnchor="middle">{index + 1}</text><title>{`${point.title}: ε=${point.soundness}`}</title></g>)}
    </svg>
    {!points.length && <div className="chart-empty"><ShieldCheck /><strong>No promoted result yet</strong><span>The chart accepts only exact claims approved independently by two verifiers.</span></div>}
  </div>;
}

function CandidateCard({ candidate, rank }: { candidate: Candidate; rank: number }) {
  return <article className="candidate-card"><div className="candidate-rank">#{rank}</div><div className="candidate-copy">
    <div className="candidate-title"><div><span>{candidate.job_id}</span><h3>{candidate.title}</h3></div><div className="epsilon"><small>soundness ↓</small><strong>{formatEpsilon(candidate.claimed_soundness)}</strong></div></div>
    <div className={`review-chip ${candidate.double_verified ? 'accepted' : ''}`}><ShieldCheck /> {candidate.double_verified ? '2/2 independent accepts' : candidate.review_verdict}</div>
    <MathText className="theorem">{candidate.theorem_statement || 'No theorem statement.'}</MathText>
    <details><summary>Proof record and audits</summary>
      {candidate.audits.map((audit) => <div className="audit" key={audit.verifier_id}><strong>{audit.verifier_id} · {audit.verdict}</strong><MathText>{audit.summary}</MathText></div>)}
      {candidate.soundness_ledger?.length > 0 && <div className="ledger"><h4>Soundness ledger</h4>{candidate.soundness_ledger.map((stage, index) => <div key={`${stage.stage}-${index}`}><strong>{stage.stage}</strong><MathText>{`${stage.input_bound} \\longrightarrow ${stage.output_bound}`}</MathText><span>{stage.loss}</span></div>)}</div>}
      <MathText className="paper">{candidate.note_markdown || 'No full note supplied.'}</MathText>
    </details>
  </div></article>;
}

export function ResearchConsole({ initialData }: { initialData: ResearchSnapshot }) {
  const [data, setData] = useState(initialData), [view, setView] = useState<View>('record'), [query, setQuery] = useState(''), [refreshing, setRefreshing] = useState(false);
  async function refresh() { setRefreshing(true); try { const response = await fetch(`./research-data.json?t=${Date.now()}`, { cache: 'no-store' }); if (response.ok) setData(await response.json() as ResearchSnapshot); } finally { setRefreshing(false); } }
  useEffect(() => { const sync = () => { const found = (Object.entries(hashes) as [View, string][]).find(([, hash]) => `#${hash}` === window.location.hash); setView(found?.[0] ?? 'record'); }; sync(); window.addEventListener('hashchange', sync); return () => window.removeEventListener('hashchange', sync); }, []);
  function choose(next: View) { setView(next); window.history.replaceState(null, '', `#${hashes[next]}`); window.scrollTo({ top: 0, behavior: 'smooth' }); }

  const points = data.soundness_history?.points ?? [], best = points.length ? points[points.length - 1].soundness : null, lemmas = data.lemma_book?.lemmas;
  const visibleLemmas = useMemo(() => (lemmas ?? []).filter((lemma) => `${lemma.title} ${lemma.statement_markdown} ${lemma.source_job_id}`.toLowerCase().includes(query.toLowerCase())), [lemmas, query]);
  const pending = [...data.candidates.promising, ...data.candidates.rejected], running = data.jobs.filter((job) => job.status === 'running').length;

  return <main><header className="site-header"><button className="wordmark" onClick={() => choose('record')}><span>LP</span><strong>Line–Point Concrete</strong></button><nav>
    <button className={view === 'record' ? 'active' : ''} onClick={() => choose('record')}>Record</button><button className={view === 'lemmas' ? 'active' : ''} onClick={() => choose('lemmas')}>Lemma Book</button><button className={view === 'roadmaps' ? 'active' : ''} onClick={() => choose('roadmaps')}>Proof Roadmaps</button><button className={view === 'messages' ? 'active' : ''} onClick={() => choose('messages')}>Message Board</button>
  </nav><button className="sync" onClick={refresh} disabled={refreshing}><RefreshCw className={refreshing ? 'spin' : ''} /> Sync</button></header>

  <div className="parameter-strip"><span><i className={running ? 'live' : ''} />{running ? `${running} agents active` : 'ready to run'}</span><span>prime <strong>147457</strong></span><span>degree <strong>87</strong></span><span>dimension <strong>2</strong></span><span>reasoning <strong>{data.status.reasoning_effort}</strong></span></div>

  {view === 'record' && <div className="page"><section className="hero"><div><p className="kicker">Concrete line-vs-point test</p><h1>How low can verified soundness go?</h1><p className="lede">For every line and point table on <MathText className="inline">{'$\\mathbb F_{147457}^2$'}</MathText>, acceptance at least <MathText className="inline">{'$\\varepsilon$'}</MathText> must force a total-degree-87 polynomial agreeing on at least <MathText className="inline">{'$\\varepsilon/10$'}</MathText> of the points.</p></div><div className="record-number"><small>best doubly verified ε</small><strong>{formatEpsilon(best)}</strong><span>lower is better ↓</span></div></section>
    <section className="chart-panel"><div className="panel-heading"><div><p className="kicker">Verified progress</p><h2>Soundness record</h2></div><div className="chart-controls"><button className="active">Record</button><button disabled>By agent</button><span>ε</span><span>All time</span></div></div><RecordChart points={points} /><div className="chart-foot"><span><ShieldCheck /> Every plotted point has 2/2 matching independent accepts.</span><span>{points.length} promoted improvement{points.length === 1 ? '' : 's'}</span></div></section>
    <section className="leaderboard"><div className="panel-heading"><div><p className="kicker">Proof leaderboard</p><h2>Doubly verified results</h2></div><span>{data.candidates.verified.length} accepted</span></div>{data.candidates.verified.length ? data.candidates.verified.map((candidate, index) => <CandidateCard candidate={candidate} rank={index + 1} key={candidate.job_id} />) : <div className="empty"><FlaskConical /><h3>The record is open.</h3><p>Researchers are configured but have not been started. A candidate appears here only after two exact, independent audits.</p></div>}</section>
    {pending.length > 0 && <section className="leaderboard secondary"><div className="panel-heading"><div><p className="kicker">Review queue</p><h2>Promising and rejected submissions</h2></div></div>{pending.map((candidate, index) => <CandidateCard candidate={candidate} rank={index + 1} key={candidate.job_id} />)}</section>}
  </div>}

  {view === 'lemmas' && <div className="page narrow"><section className="section-intro"><BookOpen /><div><p className="kicker">Polished statements</p><h1>Lemma Book</h1><p>Statements contain only quantified objects, hypotheses, and conclusions. All explanation belongs in the proof.</p></div></section><label className="search" htmlFor="lemma-search"><Search /><input id="lemma-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search lemmas, statements, or source ids" /></label><section className="book">{visibleLemmas.length ? visibleLemmas.map((lemma, index) => <article className="lemma" key={lemma.id}><span>L{String(index + 1).padStart(3, '0')}</span><div><p className="kicker">{lemma.source_job_id} · {lemma.source_step_id}{lemma.part > 1 ? ` · part ${lemma.part}` : ''}</p><h2>{lemma.title}</h2><MathText className="lemma-statement">{lemma.statement_markdown}</MathText><details><summary>Proof</summary><MathText className="paper">{lemma.proof_markdown}</MathText></details></div></article>) : <div className="empty"><BookOpen /><h3>No edited lemmas yet.</h3><p>The Lemma Writer is configured to post-edit every submitted proof step and validate its math rendering.</p></div>}</section></div>}

  {view === 'roadmaps' && <div className="page"><section className="section-intro"><Map /><div><p className="kicker">Lean-like dependency plans</p><h1>Proof Roadmaps</h1><p>Three parallel routes share every lemma and both audits, while retaining a slight preference for their own technical focus.</p></div></section><div className="roadmap-grid">{(data.proof_roadmaps?.roadmaps ?? []).map((roadmap) => <article className="roadmap" key={roadmap.roadmap_id}><header><div><p className="kicker">Round {roadmap.round}</p><h2>{roadmap.title}</h2><p>{roadmap.focus}</p></div><strong>{roadmap.progress.percent}%</strong></header><div className="progress"><i style={{ width: `${roadmap.progress.percent}%` }} /></div><div className="roadmap-counts"><span>{roadmap.progress.verified} verified</span><span>{roadmap.progress.provisional} provisional</span><span>{roadmap.progress.open + roadmap.progress.blocked} open</span></div><MathText className="roadmap-target">{roadmap.target_statement}</MathText>{roadmap.nodes.map((node, index) => <div className="roadmap-node" key={node.id}><span>{index + 1}</span><div><p><code>{node.id}</code><em className={`state-${node.proof_state}`}>{node.proof_state}</em></p><h3>{node.label}</h3><MathText>{node.statement_markdown}</MathText>{node.dependencies.length > 0 && <small>depends on {node.dependencies.join(', ')}</small>}</div></div>)}</article>)}</div></div>}

  {view === 'messages' && <div className="page narrow"><section className="section-intro"><MessageSquare /><div><p className="kicker">Informal shared channel</p><h1>Agent Message Board</h1><p>Questions, objections, and proposed lemma imports live here. Discussion never counts as proof.</p></div></section><section className="messages">{(data.message_board?.messages ?? []).length ? [...(data.message_board?.messages ?? [])].reverse().map((message) => <article key={message.id}><header><strong>{message.author}</strong><span>#{message.channel} · {message.kind}</span><time>{formatDate(message.created_at)}</time></header><h2>{message.subject}</h2><MathText>{message.body_markdown}</MathText></article>) : <div className="empty"><MessageSquare /><h3>The board is quiet.</h3><p>The three roadmap agents will use it once the research run starts.</p></div>}</section></div>}

  <footer><span>Fixed instance: <MathText className="inline">{'$p=147457,\\ d=87,\\ m=2$'}</MathText></span><span><Check /> promotion policy: two independent accepts</span></footer></main>;
}
