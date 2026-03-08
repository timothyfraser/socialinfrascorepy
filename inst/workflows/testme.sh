#!/usr/bin/env bash
set -euo pipefail

# Local preview for socialinfrascorepy docs, matching Netlify publish folder.
# - Build quartodoc pages from socialinfrascorepy/docs/_quarto.yml
# - Render Quarto site from socialinfrascorepy/docs
# - Sync output to docs/socialinfrascorepy
# - Remove transient socialinfrascorepy/docs/_site build output
# - Serve docs/socialinfrascorepy at http://127.0.0.1:4848

if ! command -v python >/dev/null 2>&1; then
  echo "Error: python is not on PATH." >&2
  exit 1
fi

quarto_bin=""
if command -v quarto >/dev/null 2>&1; then
  quarto_bin="$(command -v quarto)"
elif [[ -x "/c/Program Files/Quarto/bin/quarto" ]]; then
  quarto_bin="/c/Program Files/Quarto/bin/quarto"
else
  echo "Error: quarto is not on PATH. Install Quarto first." >&2
  exit 1
fi

if ! command -v quartodoc >/dev/null 2>&1; then
  echo "Error: quartodoc is not on PATH. Install with: python -m pip install quartodoc" >&2
  exit 1
fi

repo_root="$(pwd)"
if [[ "$(basename "$repo_root")" == "socialinfrascorepy" ]]; then
  repo_root="$(cd .. && pwd)"
fi

source_docs="$repo_root/socialinfrascorepy/docs"
site_build="$source_docs/_site"
publish_dir="$repo_root/docs/socialinfrascorepy"

if [[ ! -d "$source_docs" ]]; then
  echo "Error: source docs directory not found: $source_docs" >&2
  exit 1
fi

cd "$repo_root"

echo "1/4 Building quartodoc reference pages..."
quartodoc build --config socialinfrascorepy/docs/_quarto.yml

echo "2/4 Rendering Quarto docs site..."
"$quarto_bin" render socialinfrascorepy/docs

if [[ ! -d "$site_build" ]]; then
  echo "Error: expected rendered site directory missing: $site_build" >&2
  exit 1
fi

echo "3/4 Syncing rendered site to docs/socialinfrascorepy..."
rm -rf "$publish_dir"
mkdir -p "$publish_dir"
cp -a "$site_build"/. "$publish_dir"/
rm -rf "$site_build" "$source_docs/.quarto" "$source_docs/reference" "$source_docs/objects.json"

if [[ ! -f "$publish_dir/index.html" ]]; then
  echo "Error: expected rendered homepage missing: $publish_dir/index.html" >&2
  exit 1
fi

echo "4/4 Serving local site at http://127.0.0.1:4848"
echo "Press Ctrl+C to stop."
python -m http.server 4848 --bind 127.0.0.1 --directory "$publish_dir"
