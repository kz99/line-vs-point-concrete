#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
dashboard_root="$project_root/dashboard"
runtime_bin="/Users/kaizheng/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:/Users/kaizheng/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback:/usr/bin:/bin"
publish_dir=$(mktemp -d /private/tmp/line-point-concrete-pages.XXXXXX)
trap 'rm -rf "$publish_dir"' EXIT HUP INT TERM

cd "$dashboard_root"
env PATH="$runtime_bin" pnpm run build:pages

if [ ! -f "$dashboard_root/dist/client/index.html" ]; then
  echo "Refusing to publish: GitHub Pages build is missing root index.html." >&2
  exit 1
fi

git clone --depth 1 https://github.com/kz99/line-vs-point-concrete-observatory.git "$publish_dir"
find "$publish_dir" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -R "$dashboard_root/dist/client/." "$publish_dir/"
touch "$publish_dir/.nojekyll"

cd "$publish_dir"
git add -A
if git diff --cached --quiet; then
  echo "GitHub Pages is already current."
  exit 0
fi
git commit -m "Publish concrete soundness observatory"
git push origin main
