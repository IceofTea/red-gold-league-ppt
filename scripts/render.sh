#!/usr/bin/env bash
# Render a PPTX to JPEG images with LibreOffice + poppler.
# Usage: bash scripts/render.sh deck.pptx out/render [dpi]
set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "usage: $0 <deck.pptx> <out_dir> [dpi]" >&2
    exit 2
fi

pptx="$1"
out="$2"
dpi="${3:-150}"

if [[ ! -f "$pptx" ]]; then
    echo "PPTX not found: $pptx" >&2
    exit 1
fi

if command -v libreoffice >/dev/null 2>&1; then
    soffice="libreoffice"
elif command -v soffice >/dev/null 2>&1; then
    soffice="soffice"
else
    echo "LibreOffice not found. Install it or use scripts/render.ps1 on Windows." >&2
    exit 1
fi

if ! command -v pdftoppm >/dev/null 2>&1; then
    echo "pdftoppm not found. Install poppler-utils." >&2
    exit 1
fi

mkdir -p "$out"
out="$(cd "$out" && pwd)"

"$soffice" --headless --convert-to pdf --outdir "$out" "$pptx" >/dev/null

pdf="$out/$(basename "${pptx%.*}").pdf"
if [[ ! -f "$pdf" ]]; then
    echo "PDF export failed: $pdf" >&2
    exit 1
fi

rm -f "$out"/slide-*.jpg
pdftoppm -jpeg -r "$dpi" "$pdf" "$out/slide"

count="$(find "$out" -maxdepth 1 -name 'slide-*.jpg' | wc -l | tr -d ' ')"
echo "Done: $count images in $out"
