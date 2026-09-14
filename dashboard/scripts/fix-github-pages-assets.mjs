import { access, cp } from 'node:fs/promises';
import { resolve } from 'node:path';

const basePath = process.env.GITHUB_PAGES_BASE_PATH ?? '/line-vs-point-concrete-observatory';
const projectPath = basePath.replace(/^\/+|\/+$/g, '');
const outputRoot = resolve('dist/client');
const nestedAssets = resolve(outputRoot, projectPath, '_next');
const pagesAssets = resolve(outputRoot, '_next');

await access(nestedAssets);
await cp(nestedAssets, pagesAssets, { recursive: true, force: true });

process.stdout.write(`Copied GitHub Pages assets to ${pagesAssets}\n`);
