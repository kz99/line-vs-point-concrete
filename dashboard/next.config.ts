import type { NextConfig } from 'next';

const githubPages = process.env.GITHUB_PAGES === 'true';
const githubPagesBasePath =
  process.env.GITHUB_PAGES_BASE_PATH ?? '/line-vs-point-concrete-observatory';

const nextConfig: NextConfig = {
  output: githubPages ? 'export' : undefined,
  basePath: '',
  assetPrefix: githubPages ? githubPagesBasePath : '',
  trailingSlash: githubPages,
};

export default nextConfig;
