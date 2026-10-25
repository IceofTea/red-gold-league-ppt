# -*- coding: utf-8 -*-
"""Fetch candidate images from Wikimedia Commons, with license metadata.

This is a convenience helper, **not** a copyright clearance tool.  Always open
``licenses.json`` and verify each file's license before using it.

Usage::

    python scripts/fetch_images.py "Chinese wheat field" -n 6 -o my_assets
    python scripts/fetch_images.py "Great Wall" --width 2000

The script writes images plus ``licenses.json``.  It uses the public MediaWiki
API and does not need an API key.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = ("red-gold-deck/0.1 (https://github.com/IceofTea/red-gold-league-ppt; "
      "educational deck helper)")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def search(query: str, limit: int, width: int) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "iiurlwidth": str(width),
    }
    url = API + "?" + urllib.parse.urlencode(params)
    data = json.loads(_get(url).decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    results = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        results.append({
            "title": page.get("title", ""),
            "descriptionurl": info.get("descriptionurl", ""),
            "thumburl": info.get("thumburl") or info.get("url", ""),
            "width": info.get("width"),
            "height": info.get("height"),
            "license": _strip_html((meta.get("LicenseShortName") or {}).get("value", "")),
            "license_url": _strip_html((meta.get("LicenseUrl") or {}).get("value", "")),
            "artist": _strip_html((meta.get("Artist") or {}).get("value", "")),
            "credit": _strip_html((meta.get("Credit") or {}).get("value", "")),
        })
    return [r for r in results if r["thumburl"]]


def safe_name(title: str, index: int) -> str:
    name = title.replace("File:", "")
    name = re.sub(r"[^\w.\-]+", "_", name, flags=re.UNICODE)
    name = name.strip("._") or "image"
    if not name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        name += ".jpg"
    return f"{index:02d}_{name}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="search keywords, e.g. 'Chinese wheat field'")
    parser.add_argument("-n", "--limit", type=int, default=6, help="number of candidates")
    parser.add_argument("-o", "--out", default="my_assets/candidates", help="output directory")
    parser.add_argument("--width", type=int, default=1600, help="thumbnail width")
    args = parser.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    try:
        results = search(args.query, args.limit, args.width)
    except Exception as exc:  # noqa: BLE001 - CLI should print a hint
        print(f"error: {exc}", file=sys.stderr)
        print("hint: check your network / DNS, or download manually.", file=sys.stderr)
        return 1

    if not results:
        print("No results. Try different keywords.")
        return 1

    manifest = []
    for i, item in enumerate(results, 1):
        name = safe_name(item["title"], i)
        path = out / name
        try:
            path.write_bytes(_get(item["thumburl"]))
        except Exception as exc:  # noqa: BLE001
            print(f"skip {item['title']}: {exc}", file=sys.stderr)
            continue
        item["file"] = name
        manifest.append(item)
        print(f"{name}  {item['license'] or 'UNKNOWN'}  {item['descriptionurl']}")

    (out / "licenses.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(manifest)} images + licenses.json to {out}")
    print("IMPORTANT: open licenses.json and verify each license before use.")
    print("CC BY / CC BY-SA require attribution; 'UNKNOWN' means do not use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
