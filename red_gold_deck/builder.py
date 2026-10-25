# -*- coding: utf-8 -*-
"""Turn a plain-Python ``CFG`` dict into a PPTX deck and a matching DOCX script.

A config is intentionally data-only: it can live in its own file, be generated
by another program, or be loaded from JSON/YAML by the caller.  See
``examples/demo.py`` for a complete, runnable example.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from .docx_util import build_docx
from .rich import RichDeck

PAGE_REQUIRED: dict[str, tuple[str, ...]] = {
    "cover": ("kicker", "years", "title", "subtitle", "lead", "big", "script"),
    "quote": ("chapter", "small", "big", "sub", "script"),
    "stats": ("chapter", "title", "sub", "numbers", "script"),
    "toc": ("title", "sub", "items", "script"),
    "toc6": ("title", "sub", "items", "script"),
    "toc8": ("title", "sub", "items", "script"),
    "chapter": ("num", "cn", "title", "quote", "script"),
    "content": ("chapter", "title", "sub", "cards", "script"),
    "timeline": ("chapter", "title", "sub", "events", "script"),
    "person": ("chapter", "title", "sub", "name", "dates", "deeds", "script"),
    "fullpic": ("chapter", "title", "sub", "points", "script"),
    "map_page": ("chapter", "title", "sub", "points", "script"),
    "two_col": ("chapter", "title", "sub", "left_title", "left_items",
                "right_title", "right_items", "script"),
    "listpage": ("chapter", "title", "sub", "items", "script"),
    "closing": ("kicker", "title", "lines", "slogan", "script"),
    "thanks": ("title", "sub", "script"),
    "sources": ("items", "script"),
}


def validate_config(cfg: dict[str, Any]) -> None:
    """Fail fast with a readable message instead of a KeyError deep in layout."""
    for key in ("footer", "header", "topic", "pages"):
        if not cfg.get(key):
            raise ValueError(f"config is missing required key: {key!r}")
    pages = cfg["pages"]
    if not isinstance(pages, list) or not pages:
        raise ValueError("config['pages'] must be a non-empty list")

    for i, page in enumerate(pages, 1):
        t = page.get("t")
        if not t:
            raise ValueError(f"page {i}: missing 't' (page type)")
        if t not in PAGE_REQUIRED:
            raise ValueError(
                f"page {i}: unknown page type {t!r}; "
                f"expected one of {sorted(PAGE_REQUIRED)}")
        missing = [k for k in PAGE_REQUIRED[t] if k not in page]
        if missing:
            raise ValueError(f"page {i} ({t}): missing keys {missing}")

    _check_counts(pages)


def _check_counts(pages: list[dict[str, Any]]) -> None:
    for i, p in enumerate(pages, 1):
        t = p["t"]
        if t == "toc6" and len(p["items"]) != 6:
            raise ValueError(f"page {i}: toc6 needs exactly 6 items")
        if t == "toc8" and len(p["items"]) != 8:
            raise ValueError(f"page {i}: toc8 needs exactly 8 items")
        if t == "stats" and not 2 <= len(p["numbers"]) <= 5:
            raise ValueError(f"page {i}: stats needs 2-5 numbers")
        if t == "timeline" and not 3 <= len(p["events"]) <= 6:
            raise ValueError(f"page {i}: timeline needs 3-6 events")
        if t == "content" and not 2 <= len(p["cards"]) <= 4:
            raise ValueError(f"page {i}: content needs 2-4 cards")
        if t == "person" and len(p["deeds"]) != 3:
            raise ValueError(f"page {i}: person needs exactly 3 deeds")
        if t == "two_col":
            for side in ("left_items", "right_items"):
                if not 2 <= len(p[side]) <= 4:
                    raise ValueError(
                        f"page {i}: two_col {side} needs 2-4 items")
        if t == "listpage" and not 3 <= len(p["items"]) <= 6:
            raise ValueError(f"page {i}: listpage needs 3-6 items")


def build(cfg: dict[str, Any], out_dir: str | Path | None = None) -> RichDeck:
    """Build the PPTX and the DOCX, returning the :class:`RichDeck` instance."""
    validate_config(cfg)

    base = Path(out_dir if out_dir is not None else cfg.get("out_dir", "out"))
    folder = base / cfg.get("folder", "")
    ppt_path = folder / cfg.get("ppt", "deck.pptx")
    doc_path = folder / cfg.get("doc", "deck_script.docx")

    deck = RichDeck(
        str(ppt_path),
        cfg["footer"],
        cfg["header"],
        cfg["topic"],
        cfg.get("date", ""),
        key=cfg.get("key", ""),
        portraits=cfg.get("portraits"),
        scenes=cfg.get("scenes"),
        portrait_dir=cfg.get("portrait_dir"),
        scene_dir=cfg.get("scene_dir"),
    )

    for p in cfg["pages"]:
        t = p["t"]
        if t == "cover":
            deck.cover(p["kicker"], p["years"], p["title"], p["subtitle"],
                       p["lead"], p["big"], p["script"])
        elif t == "toc":
            deck.toc(p["title"], p["sub"], p["items"], p["script"],
                     p.get("note", "一条主线，几个问题，一次真正的思考。"))
        elif t == "toc6":
            deck.toc6(p["title"], p["sub"], p["items"], p["script"],
                      p.get("note", "六章，一条主线；每一章都回答一个问题。"))
        elif t == "toc8":
            deck.toc8(p["title"], p["sub"], p["items"], p["script"],
                      p.get("note"))
        elif t == "chapter":
            deck.chapter(p["num"], p["cn"], p["title"], p["quote"],
                         p["script"], p.get("img"), p.get("caption", ""))
        elif t == "content":
            deck.content(p["chapter"], p["title"], p["sub"], p["cards"],
                         p["script"], p.get("lead"), p.get("cols", 3),
                         p.get("note"))
        elif t == "timeline":
            deck.timeline(p["chapter"], p["title"], p["sub"], p["events"],
                          p["script"], p.get("note"))
        elif t == "stats":
            deck.stats(p["chapter"], p["title"], p["sub"], p["numbers"],
                       p["script"], p.get("note"))
        elif t == "quote":
            deck.quote(p["chapter"], p["small"], p["big"], p["sub"],
                       p["script"], p.get("note"))
        elif t == "two_col":
            deck.two_col(p["chapter"], p["title"], p["sub"],
                         p["left_title"], p["left_items"],
                         p["right_title"], p["right_items"],
                         p["script"], p.get("note"))
        elif t == "person":
            deck.person(p["chapter"], p["title"], p["sub"], p["name"],
                        p["dates"], p.get("img"), p["deeds"],
                        p.get("quote", ""), p["script"],
                        p.get("photo_note"))
        elif t == "fullpic":
            deck.fullpic(p["chapter"], p["title"], p["sub"], p.get("img"),
                         p["points"], p["script"], p.get("caption", ""))
        elif t == "map_page":
            deck.map_page(p["chapter"], p["title"], p["sub"], p.get("img"),
                          p["points"], p["script"], p.get("caption", ""),
                          p.get("footnote"))
        elif t == "listpage":
            deck.listpage(p["chapter"], p["title"], p["sub"], p["items"],
                          p["script"], p.get("note"))
        elif t == "closing":
            deck.closing(p["kicker"], p["title"], p["lines"], p["slogan"],
                         p["script"], p.get("note"))
        elif t == "thanks":
            deck.thanks(p["title"], p["sub"], p["script"])
        elif t == "sources":
            items = list(p["items"])
            credit = p.get("credit") or cfg.get("image_credit")
            if credit:
                items.append(("图片版权", credit))
            deck.sources(
                items, p["script"],
                p.get("title", "图片与资料说明"),
                p.get("sub", "感谢所有记录、保存和传播历史的人"),
                p.get("footer_note", "主题团课学习资料"),
            )

    deck.save()
    build_docx(
        deck, str(doc_path),
        cfg.get("doc_title", cfg["topic"]),
        cfg.get("doc_sub", ""),
        cfg["footer"],
        cfg.get("doc_note",
                "本稿与 PPT 逐页对应，可直接照读。方括号【】内为提示，不读。"),
    )

    pages = len(deck.prs.slides)
    expected = cfg.get("expect_pages")
    if expected is not None and pages != expected:
        raise ValueError(
            f"page count mismatch: generated {pages}, expected {expected}. "
            "Check for a missing quote/content page in one of the chapters.")
    print(f"saved {ppt_path} | {pages} pages | {len(deck.script)} script sections")
    return deck


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Import a ``.py`` file and return its top-level ``CFG`` dict."""
    path = Path(config_path).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    # Let the config import sibling modules or reference relative assets.
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location("_red_gold_config", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot import {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    cfg = getattr(module, "CFG", None)
    if not isinstance(cfg, dict):
        raise ValueError(f"{path} must define a top-level dict named CFG")
    return cfg


def build_from_file(config_path: str | Path,
                    out_dir: str | Path | None = None) -> RichDeck:
    """Load ``CFG`` from a Python file and build the deck."""
    return build(load_config(config_path), out_dir)
