import { copyFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('../../how_to_contribute/RESEARCH_PROMPT.md', import.meta.url));
const destination = fileURLToPath(new URL('../public/contributor-research-prompt.md', import.meta.url));

await mkdir(dirname(destination), { recursive: true });
await copyFile(source, destination);
console.log(`Synced contributor prompt to ${destination}`);

