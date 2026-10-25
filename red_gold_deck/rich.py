# -*- coding: utf-8 -*-
"""Rich red-gold deck: chapter covers, person pages, full-bleed photos, etc.

The class is configuration-driven; see ``docs/PAGES.md`` for every page type.
No third-party images are bundled. Put your own files in ``assets/portraits``
and ``assets/scenes`` (or pass absolute paths per page) and map them via the
``portraits`` / ``scenes`` keys of the deck config.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from .deck import Deck
from .helpers import (
    ASSETS_DIR, BG_CHAPTER, BG_COVER, BG_DARK, BG_PAPER, BODY_FONT, DEEP, GOLD,
    GRAY, INK, LGOLD, NUM_FONT, PALE, RED, SERIF_FONT, SH, SW, TITLE_FONT,
    WHITE, add_line, add_pic_cover, add_rect, add_text, frame, title_size,
)

PORTRAIT_DIR = Path(os.environ.get(
    "RED_GOLD_PORTRAIT_DIR", ASSETS_DIR / "portraits"))
SCENE_DIR = Path(os.environ.get(
    "RED_GOLD_SCENE_DIR", ASSETS_DIR / "scenes"))


def _cjk_lines(text, limit):
    """按标点优先把中文切成不超过 limit 字的行，避免标点落到行首。"""
    parts = re.findall(r"[^，。；：、！？]*[，。；：、！？]?", text)
    parts = [p for p in parts if p]
    lines, cur = [], ""
    for part in parts:
        if len(cur) + len(part) <= limit:
            cur += part
            continue
        if cur:
            lines.append(cur)
            cur = ""
        while len(part) > limit:
            cut = limit
            while cut > 1 and part[cut] in "，。；：、！？":
                cut -= 1
            lines.append(part[:cut])
            part = part[cut:]
        cur = part
    if cur:
        lines.append(cur)
    return lines


def _body_runs(text, size, limit, color, line_spacing, align=None):
    runs = []
    for line in _cjk_lines(text, limit):
        item = {"text": line, "size": size, "color": color, "line_spacing": line_spacing}
        if align is not None:
            item["align"] = align
        runs.append(item)
    return runs


class RichDeck(Deck):
    def __init__(self, *args, portraits=None, scenes=None,
                 portrait_dir=None, scene_dir=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.portraits = portraits or {}
        self.scenes = scenes or {}
        self.portrait_dir = str(portrait_dir or PORTRAIT_DIR)
        self.scene_dir = str(scene_dir or SCENE_DIR)

    # ---------- 自动场景图 ----------
    def _auto_scene(self, img, page_no):
        if img:
            return img
        fn = self.scenes.get(getattr(self, "key", ""), {}).get(page_no)
        return os.path.join(self.scene_dir, fn) if fn else None

    def chapter(self, num, cn, title, quote, script, img=None, img_caption=""):
        img = self._auto_scene(img, self.n + 1)
        if img and not img_caption:
            img_caption = "资料图片"
        super().chapter(num, cn, title, quote, script, img, img_caption)

    # ---------- 内容页（按语义分行，避免标点行首） ----------
    def content(self, chapter, title, sub, cards, script, lead=None, cols=3, note=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        y = 2.62
        if lead:
            add_text(s, 0.85, 1.97, 11.7, 0.55,
                     [{"text": lead, "size": 12, "color": INK, "line_spacing": 1.55}])
            y = 2.72
        n = len(cards)
        if n <= 3:
            w, gap, x0 = 3.75, 0.30, 0.85
        else:
            w, gap, x0 = 2.85, 0.20, 0.85
        h = 2.90 if lead else 3.10
        hsize = 16.5 if n <= 3 else 15
        for i, (head, body) in enumerate(cards):
            x = x0 + i * (w + gap)
            add_rect(s, x, y, w, h, PALE, alpha=60)
            add_rect(s, x, y, w, 0.055, RED)
            add_text(s, x + 0.22, y + 0.18, 0.8, 0.35,
                     [{"text": f"{i+1:02d}", "font": NUM_FONT, "size": 17, "color": GOLD, "bold": True}])
            add_text(s, x + 0.22, y + 0.60, w - 0.44, 0.52,
                     [{"text": head, "font": SERIF_FONT, "size": hsize, "color": RED, "line_spacing": 1.2}])
            add_text(s, x + 0.22, y + 1.15, w - 0.42, h - 1.28,
                     _body_runs(body, 11, 20, GRAY, 1.7))
        if note:
            add_text(s, 0.85, min(y + h + 0.18, 6.42), 11.7, 0.32,
                     [{"text": note, "size": 10.8, "color": RGBColor(0x8A, 0x4A, 0x2A), "italic": True}])
        self.footer(s)
        self.say(title, script)

    # ---------- 左右对照（按语义分行） ----------
    def two_col(self, chapter, title, sub, left_title, left_items,
                right_title, right_items, script, note=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        for side, (x, head, items, color) in enumerate([
            (0.85, left_title, left_items, RED),
            (6.90, right_title, right_items, DEEP),
        ]):
            add_rect(s, x, 2.12, 5.55, 0.46, color)
            add_text(s, x + 0.20, 2.18, 5.15, 0.30,
                     [{"text": head, "size": 12, "color": WHITE, "bold": True}])
            yy = 2.78
            for h, b in items:
                add_text(s, x + 0.12, yy, 0.16, 0.28,
                         [{"text": "◆", "size": 8, "color": GOLD}])
                add_text(s, x + 0.38, yy - 0.02, 5.0, 0.30,
                         [{"text": h, "size": 12, "color": color, "bold": True}])
                add_text(s, x + 0.38, yy + 0.31, 4.95, 0.62,
                         _body_runs(b, 9.6, 34, GRAY, 1.45))
                yy += 0.92
        if note:
            add_text(s, 0.85, 6.48, 11.7, 0.30,
                     [{"text": note, "size": 10.5, "color": RGBColor(0x8A, 0x4A, 0x2A), "italic": True}])
        self.footer(s)
        self.say(title, script)

    # ---------- 时间轴（按语义分行） ----------
    def timeline(self, chapter, title, sub, events, script, note=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        yline = 3.62
        x_start, x_end = 1.55, 11.78
        add_line(s, x_start, yline, x_end, yline, RGBColor(0xC8, 0xA4, 0x5D), 1.1)
        n = len(events)
        step = (x_end - x_start) / max(n - 1, 1)
        for i, (year, head, desc) in enumerate(events):
            x = x_start + i * step
            add_rect(s, x - 0.07, yline - 0.07, 0.14, 0.14, RED, line=GOLD, lw=0.8)
            add_text(s, x - 1.00, yline - 0.75, 2.0, 0.40,
                     [{"text": year, "font": NUM_FONT, "size": 17, "color": RED, "bold": True,
                       "align": PP_ALIGN.CENTER}])
            add_text(s, x - 1.05, yline + 0.18, 2.1, 0.42,
                     [{"text": head, "size": 12.5, "color": INK, "bold": True,
                       "align": PP_ALIGN.CENTER}])
            add_text(s, x - 1.08, yline + 0.66, 2.16, 1.25,
                     _body_runs(desc, 9.2, 16, GRAY, 1.45, align=PP_ALIGN.CENTER))
        if note:
            add_text(s, 0.85, 6.22, 11.7, 0.55,
                     [{"text": note, "size": 11.2, "color": RGBColor(0x8A, 0x4A, 0x2A),
                       "italic": True, "line_spacing": 1.4}])
        self.footer(s)
        self.say(title, script)

    # ---------- 数据页（按语义分行） ----------
    def stats(self, chapter, title, sub, numbers, script, note=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        n = len(numbers)
        w = 11.55 / n
        for i, (num, label, desc) in enumerate(numbers):
            x = 0.85 + i * w
            add_text(s, x, 2.55, w - 0.2, 0.95,
                     [{"text": num, "font": NUM_FONT, "size": 50, "color": RED, "bold": True}])
            add_text(s, x, 3.55, w - 0.2, 0.38,
                     [{"text": label, "font": SERIF_FONT, "size": 15, "color": INK}])
            add_text(s, x, 4.05, w - 0.28, 1.35,
                     _body_runs(desc, 10.3, 17, GRAY, 1.55))
            if i < n - 1:
                add_line(s, x + w - 0.12, 2.65, x + w - 0.12, 5.55,
                         RGBColor(0xD8, 0xC8, 0xAE), 0.7, alpha=60)
        if note:
            add_line(s, 0.85, 6.05, 12.45, 6.05, RGBColor(0xD8, 0xC8, 0xAE), 0.7, alpha=60)
            add_text(s, 0.85, 6.20, 11.7, 0.55,
                     [{"text": note, "size": 11.5, "color": RGBColor(0x8A, 0x4A, 0x2A),
                       "italic": True, "line_spacing": 1.4}])
        self.footer(s)
        self.say(title, script)

    # ---------- 六章目录 ----------
    def toc6(self, title, sub, items, script,
             note="六章，一条主线；每一章都回答一个问题。"):
        s = self._slide(BG_PAPER)
        self.header(s, "目录  ·  CONTENTS")
        add_text(s, 0.78, 0.78, 11.7, 0.62,
                 [{"text": title, "font": TITLE_FONT, "size": 34, "color": RED}])
        add_text(s, 0.80, 1.44, 11.7, 0.28,
                 [{"text": sub, "size": 11, "color": RGBColor(0x8A, 0x7A, 0x66)}])
        add_line(s, 0.80, 1.86, 12.5, 1.86, RGBColor(0xD8, 0xC8, 0xAE), 0.7, alpha=70)

        x0, y0, cw, ch = 0.85, 2.08, 3.78, 1.62
        gx, gy = 0.30, 0.18
        for i, (head, desc) in enumerate(items):
            x = x0 + (i % 3) * (cw + gx)
            y = y0 + (i // 3) * (ch + gy)
            add_rect(s, x, y, cw, ch, PALE, alpha=55)
            add_rect(s, x, y, cw, 0.05, RED)
            add_text(s, x + 0.18, y + 0.12, 0.62, 0.34,
                     [{"text": f"{i+1:02d}", "font": NUM_FONT, "size": 17,
                       "color": GOLD, "bold": True}])
            add_text(s, x + 0.70, y + 0.12, cw - 0.88, 0.38,
                     [{"text": head, "font": SERIF_FONT, "size": 16, "color": RED}])
            add_text(s, x + 0.18, y + 0.62, cw - 0.36, ch - 0.72,
                     [{"text": desc, "size": 9.5, "color": GRAY, "line_spacing": 1.5}])
        if note:
            add_text(s, 0.85, 6.02, 11.7, 0.30,
                     [{"text": note, "size": 12,
                       "color": RGBColor(0x8A, 0x4A, 0x2A), "italic": True}])
        self.footer(s)
        self.say(title, script)

    # ---------- 人物页 ----------
    def toc8(self, title, sub, items, script, note=None):
        s = self._slide(BG_PAPER)
        self.header(s, "目录  ·  CONTENTS")
        add_text(s, 0.78, 0.78, 11.7, 0.62,
                 [{"text": title, "font": TITLE_FONT, "size": 34, "color": RED}])
        add_text(s, 0.80, 1.44, 11.7, 0.28,
                 [{"text": sub, "size": 11, "color": RGBColor(0x8A, 0x7A, 0x66)}])
        add_line(s, 0.80, 1.86, 12.5, 1.86, RGBColor(0xD8, 0xC8, 0xAE), 0.7, alpha=70)

        x0, y0, cw, ch = 0.85, 2.02, 2.70, 1.95
        gx, gy = 0.24, 0.16
        for i, (head, desc) in enumerate(items):
            x = x0 + (i % 4) * (cw + gx)
            y = y0 + (i // 4) * (ch + gy)
            add_rect(s, x, y, cw, ch, PALE, alpha=55)
            add_rect(s, x, y, cw, 0.05, RED)
            add_text(s, x + 0.14, y + 0.10, 0.55, 0.30,
                     [{"text": f"{i+1:02d}", "font": NUM_FONT, "size": 15,
                       "color": GOLD, "bold": True}])
            add_text(s, x + 0.14, y + 0.44, cw - 0.28, 0.62,
                     [{"text": head, "font": SERIF_FONT, "size": 14,
                       "color": RED, "line_spacing": 1.15}])
            add_text(s, x + 0.14, y + 1.06, cw - 0.28, ch - 1.16,
                     [{"text": desc, "size": 8.8, "color": GRAY, "line_spacing": 1.45}])
        if note:
            add_text(s, 0.85, 6.25, 11.7, 0.30,
                     [{"text": note, "size": 12,
                       "color": RGBColor(0x8A, 0x4A, 0x2A), "italic": True}])
        self.footer(s)
        self.say(title, script)

    # ---------- 人物页 ----------
    def person(self, chapter, title, sub, name, dates, img, deeds, quote, script, photo_note=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        # 自动匹配人物肖像（配置文件里的 portraits 映射）
        if not img:
            key = (name or "").strip()
            fn = self.portraits.get(key)
            if not fn and "·" in key:
                fn = self.portraits.get(key.split("·")[0].strip())
            if fn:
                img = os.path.join(self.portrait_dir, fn)
        has_img = bool(img and os.path.exists(img))
        if not photo_note:
            if (name or "").startswith("【"):
                photo_note = "人物照片占位"
            elif has_img:
                photo_note = "资料照片"
            else:
                photo_note = "暂未找到合适照片"

        # 左侧肖像 / 占位
        if has_img:
            add_pic_cover(s, img, 0.85, 2.02, 3.05, 4.35, crop_bias_y=0.30)
            frame(s, 0.85, 2.02, 3.05, 4.35, GOLD, 1.0)
            add_rect(s, 0.85, 2.02, 3.05, 4.35, DEEP, alpha=18)
            add_text(s, 0.85, 6.42, 3.05, 0.22,
                     [{"text": photo_note, "size": 7.5, "color": GRAY,
                       "spacing": 1.5, "align": PP_ALIGN.CENTER}])
        else:
            add_rect(s, 0.85, 2.02, 3.05, 4.35, PALE, alpha=85)
            add_rect(s, 0.85, 2.02, 3.05, 0.05, RED)
            # 简洁人物剪影图标
            head = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(2.02), Inches(2.90), Inches(0.72), Inches(0.72))
            shoulders = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.72), Inches(3.78), Inches(1.32), Inches(0.52))
            for shp in (head, shoulders):
                shp.fill.background()
                shp.line.color.rgb = RGBColor(0xD8, 0xBE, 0x92)
                shp.line.width = Pt(1.4)
                shp.shadow.inherit = False
            add_text(s, 0.95, 4.55, 2.85, 0.34,
                     [{"text": photo_note, "size": 11.5, "color": RED,
                       "align": PP_ALIGN.CENTER, "spacing": 1.5}])
            hint = "请替换为人物照片" if (name or "").startswith("【") else "暂未找到合适照片"
            add_text(s, 0.95, 4.98, 2.85, 0.48,
                     [{"text": hint, "size": 8.8, "color": GRAY,
                       "align": PP_ALIGN.CENTER, "line_spacing": 1.4}])
        # 右侧
        add_text(s, 4.22, 2.02, 8.3, 0.52,
                 [{"text": name, "font": TITLE_FONT, "size": 27, "color": RED}])
        add_text(s, 4.24, 2.58, 8.2, 0.28,
                 [{"text": dates, "size": 10.5, "color": GOLD, "spacing": 1.5}])
        yy = 2.98
        for i, (h, b) in enumerate(deeds):
            add_text(s, 4.22, yy, 0.42, 0.30,
                     [{"text": f"{i+1:02d}", "font": NUM_FONT, "size": 13,
                       "color": GOLD, "bold": True}])
            add_text(s, 4.66, yy - 0.03, 7.65, 0.32,
                     [{"text": h, "size": 12.5, "color": RED, "bold": True}])
            add_text(s, 4.66, yy + 0.30, 7.55, 0.62,
                     _body_runs(b, 9.8, 48, GRAY, 1.45))
            yy += 0.95
        if quote:
            add_line(s, 4.24, 5.95, 5.2, 5.95, GOLD, 0.9)
            add_text(s, 4.24, 6.08, 8.15, 0.50,
                     [{"text": quote, "size": 10.5, "color": RGBColor(0x8A, 0x4A, 0x2A),
                       "italic": True, "line_spacing": 1.4}])
        self.footer(s)
        self.say(title, script)

    # ---------- 全图页 ----------
    def fullpic(self, chapter, title, sub, img, points, script, caption=""):
        s = self._slide(BG_CHAPTER)
        img = self._auto_scene(img, self.n + 1)
        if img and not caption:
            caption = "资料图片"
        if img and os.path.exists(img):
            add_pic_cover(s, img, 0, 0, SW, SH, crop_bias_y=0.40)
            add_rect(s, 0, 0, SW, SH, DEEP, alpha=72)
        self.header(s, chapter, dark=True)
        if caption:
            add_text(s, 9.7, 0.72, 3.0, 0.26,
                     [{"text": caption, "size": 8, "color": GOLD, "spacing": 1.5,
                       "align": PP_ALIGN.RIGHT}])
        add_text(s, 0.88, 1.55, 11.2, 0.34,
                 [{"text": "历史的现场", "size": 10.5, "color": GOLD, "spacing": 3}])
        add_text(s, 0.86, 1.98, 11.3, 1.10,
                 [{"text": title, "font": TITLE_FONT, "size": title_size(title, 44),
                   "color": WHITE}])
        add_text(s, 0.90, 3.12, 11.0, 0.55,
                 [{"text": sub, "size": 15, "color": LGOLD, "line_spacing": 1.5}])
        add_line(s, 0.92, 3.92, 5.2, 3.92, GOLD, 1.0)
        n = len(points)
        w = 11.5 / max(n, 1)
        for i, (h, b) in enumerate(points):
            x = 0.88 + i * w
            add_text(s, x, 4.35, 0.55, 0.30,
                     [{"text": f"0{i+1}", "font": NUM_FONT, "size": 12, "color": GOLD, "bold": True}])
            add_text(s, x + 0.50, 4.32, w - 0.65, 0.32,
                     [{"text": h, "size": 11.5, "color": LGOLD, "bold": True}])
            add_text(s, x + 0.50, 4.70, w - 0.68, 0.80,
                     _body_runs(b, 9.2, 26, RGBColor(0xE6, 0xCF, 0xB0), 1.45))
        self.footer(s, dark=True)
        self.say(title, script)

    # ---------- 地图页（左文右图，整幅地图不裁切） ----------
    def map_page(self, chapter, title, sub, img, points, script, caption="",
                 footnote=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        add_line(s, 0.85, 2.02, 7.55, 2.02, RGBColor(0xD8, 0xC8, 0xAE), 0.7, alpha=70)

        y = 2.24
        for i, (h, b) in enumerate(points):
            add_text(s, 0.88, y, 0.55, 0.32,
                     [{"text": f"0{i+1}", "font": NUM_FONT, "size": 13,
                       "color": GOLD, "bold": True}])
            add_text(s, 1.46, y - 0.04, 6.1, 0.34,
                     [{"text": h, "font": SERIF_FONT, "size": 14.5, "color": RED}])
            add_text(s, 1.46, y + 0.36, 6.05, 0.78,
                     _body_runs(b, 10.5, 22, GRAY, 1.6))
            if i < len(points) - 1:
                add_line(s, 1.46, y + 1.18, 7.45, y + 1.18,
                         RGBColor(0xDD, 0xCF, 0xB8), 0.5, alpha=90)
            y += 1.36

        if footnote:
            add_text(s, 0.88, 6.34, 6.7, 0.30,
                     [{"text": footnote, "size": 12,
                       "color": RGBColor(0x8A, 0x4A, 0x2A), "italic": True}])

        if img and os.path.exists(img):
            add_rect(s, 8.56, 1.92, 3.86, 4.58, PALE, alpha=45)
            add_pic_cover(s, img, 8.72, 2.06, 3.54, 4.30, crop_bias_y=0.5)
            frame(s, 8.72, 2.06, 3.54, 4.30, GOLD, 1.0)
            if caption:
                add_text(s, 8.60, 6.42, 3.78, 0.26,
                         [{"text": caption, "size": 8.2, "color": GRAY,
                           "spacing": 1.2, "align": PP_ALIGN.CENTER}])
        self.footer(s)
        self.say(title, script)

    # ---------- 清单页 ----------
    def listpage(self, chapter, title, sub, items, script, note=None):
        s = self._slide(BG_PAPER)
        self.header(s, chapter)
        self.title(s, title, sub)
        y = 2.02
        for i, (h, b) in enumerate(items):
            add_text(s, 0.88, y, 0.55, 0.32,
                     [{"text": f"{i+1:02d}", "font": NUM_FONT, "size": 15,
                       "color": GOLD, "bold": True}])
            add_text(s, 1.48, y - 0.02, 2.65, 0.34,
                     [{"text": h, "size": 12.5, "color": RED, "bold": True}])
            add_text(s, 4.18, y - 0.02, 8.15, 0.42,
                     _body_runs(b, 10.2, 50, GRAY, 1.4))
            add_line(s, 0.90, y + 0.58, 12.35, y + 0.58,
                     RGBColor(0xD8, 0xC8, 0xAE), 0.5, alpha=55)
            y += 0.72
        if note:
            add_text(s, 0.88, 6.35, 11.7, 0.32,
                     [{"text": note, "size": 10.8, "color": RGBColor(0x8A, 0x4A, 0x2A),
                       "italic": True}])
        self.footer(s)
        self.say(title, script)

    # ---------- 卷尾 ----------
    def thanks(self, title, sub, script):
        s = self._slide(BG_COVER)
        add_text(s, 0.95, 2.15, 11.2, 0.95,
                 [{"text": title, "font": TITLE_FONT, "size": 46, "color": WHITE}])
        add_text(s, 0.98, 3.20, 10.5, 0.45,
                 [{"text": sub, "size": 17, "color": LGOLD}])
        add_line(s, 1.0, 4.05, 5.2, 4.05, GOLD, 1.0)
        add_text(s, 0.98, 4.28, 11.0, 0.55,
                 [{"text": "感谢聆听  ·  欢迎批评指正", "size": 16, "color": RGBColor(0xE6, 0xCF, 0xB0)}])
        add_text(s, 0.95, 6.42, 9.5, 0.24,
                 [{"text": self.footer_label + "  ·  " + self.date_label,
                   "size": 8.8, "color": RGBColor(0xB9, 0x93, 0x62)}])
        add_text(s, 11.65, 7.10, 0.90, 0.26,
                 [{"text": f"{self.n:02d}", "size": 10, "color": LGOLD,
                   "bold": True, "align": PP_ALIGN.RIGHT}])
        self.say(title, script)

