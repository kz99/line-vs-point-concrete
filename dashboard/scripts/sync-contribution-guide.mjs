import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('../../how_to_contribute/RESEARCH_PROMPT.md', import.meta.url));
const destination = fileURLToPath(new URL('../public/contributor-research-prompt.md', import.meta.url));
const dataPath = fileURLToPath(new URL('../public/research-data.json', import.meta.url));

await mkdir(dirname(destination), { recursive: true });
const sourceText = await readFile(source, 'utf8');
const data = JSON.parse(await readFile(dataPath, 'utf8'));
const scores = (data.soundness_history?.points ?? [])
  .map((point) => point.agreement_count)
  .filter((score) => Number.isSafeInteger(score) && score > 0);
const record = scores.length ? Math.min(...scores) : null;
const recordLine = record == null
  ? '**Live build snapshot.** No verified record was available when this prompt was built.'
  : `**Live build snapshot.** The current verified record is **${record.toLocaleString('en-US')}**. A leaderboard submission must prove a score at most **${(record - 1).toLocaleString('en-US')}**.`;
const output = sourceText.replace('<!-- CURRENT_RECORD_FROM_DASHBOARD -->', recordLine);
await writeFile(destination, output);
console.log(`Synced contributor prompt to ${destination}`);
