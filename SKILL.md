---
name: red-gold-league-ppt
description: 生成红金党政风团支部主题团课 PPT（30—50 页）及逐页可照读的 Word 讲稿。当用户要求制作团课、党课、纪念周年、主题团日 PPT，或提到红金风格、宣纸、深红封面、丰富版、把某个主题做成团课时使用。内置六章结构、页面类型、生成脚本、渲染检查和质量红线。
---

# 红金党政风团课 PPT 生成

## 这个 Skill 解决什么问题

把“团课 PPT”从一次性手工排版，变成可复用的生产线：

- **统一视觉**：深红封面、宣纸内容页、金色线条、宋体标题；
- **统一结构**：封面 → 序章 → 六章 → 结语 → 来源，30—50 页；
- **统一讲稿**：每页 150—250 字，与 PPT 页码一一对应，可照读；
- **统一质检**：生成后渲染成图，逐页检查压字、溢出、裁切；
- **配置驱动**：页面是数据，不是手工排版；改文字、换图片即可复用。

## 环境准备

```bash
python -m pip install -e .
# 或
python -m pip install -r requirements.txt
```

字体不随仓库分发。Windows 默认字体栈为：方正小标宋简体、华文中宋、微软雅黑、Noto Serif SC。macOS/Linux 请先安装思源宋体 / Noto Serif CJK，再用环境变量替换：

```bash
export RED_GOLD_TITLE_FONT="Source Han Serif SC"
export RED_GOLD_SERIF_FONT="Source Han Serif SC"
export RED_GOLD_BODY_FONT="Source Han Sans SC"
export RED_GOLD_NUM_FONT="Source Han Serif SC"
```

渲染检查需要 PowerPoint（Windows）或 LibreOffice（macOS/Linux），以及 `pdftoppm`（poppler）。

## 工作流

### 1. 明确主题与结构

先和用户确认四件事：

1. 主题与副标题；
2. 页数区间（建议 30—50 页）与章节数（建议 6 章）；
3. 是否有真实人物、历史事件、支部信息需要呈现；
4. 配图来源（自有 / CC0 / 已授权），以及是否需要人物肖像。

把答案写成一句话，例如：

> 《把青春写在祖国大地上》，6 章 31 页，无真人照片，配图全部脚本生成。

### 2. 复制示例配置

```bash
cp examples/demo.py my_deck.py
```

打开 `my_deck.py`，先改顶部的 `CFG`（footer / header / topic / date / expect_pages），再逐页改 `PAGES`。

**先定页数，再填内容。** 推荐骨架（以 6 章、31 页为例）：

| 区块 | 页数 | 页面类型 |
|---|---|---|
| 封面 + 序章 | 4 | `cover` `quote` `stats` `toc6` |
| 每章 | 4 | `chapter` + 3 个内容页 |
| 结语 + 致谢 + 来源 | 3 | `closing` `thanks` `sources` |

内容页在 `content` / `timeline` / `person` / `two_col` / `listpage` / `fullpic` / `map_page` 之间轮换，避免连续三页同一种版式。

### 3. 处理配图

- 优先使用**自有照片**或明确授权的素材；
- 不确定版权时，用 `scripts/make_demo_assets.py` 生成示意图，或留空让章节页使用内置红底；
- **不要**把网络搜索到的历史照片、人物肖像直接放进公开仓库；
- 人物页没有照片时保留占位，不要用 AI 生成的人像冒充真实人物；
- 每张图在 `sources` 页写清来源与授权。

详见 [docs/ASSETS.md](docs/ASSETS.md)。

### 4. 生成

```bash
red-gold-deck validate my_deck.py
red-gold-deck build my_deck.py
```

输出：

```text
out/<folder>/
├── <ppt>.pptx
└── <doc>.docx
```

`validate` 只检查配置，不写文件；`build` 会同时生成 PPTX 和逐页讲稿。页数不符时会在最后报 `page count mismatch`，这是有意的保护。

### 5. 渲染与目检

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File scripts/render.ps1 `
  -Pptx out/demo/demo_主题团课.pptx -OutDir out/demo/render
```

```bash
# macOS / Linux
bash scripts/render.sh out/demo/demo_主题团课.pptx out/demo/render
```

渲染后**必须逐页看**，重点检查：

- 封面标题是否换行、是否压到年份或导语；
- 目录卡片文字是否溢出卡片；
- 内容页第 3/4 张卡片是否超出右边界；
- 时间轴第一个和最后一个节点是否被裁切；
- 人物页肖像是否变形、占位提示是否清楚；
- 章节页 / 全图页图片是否裁掉了主体；
- 来源页版权与隐私说明是否完整；
- 每一页 PPT 是否都有对应的讲稿段落。

完整清单见 [docs/DESIGN.md](docs/DESIGN.md)。

## 页面类型速查

| 类型 | 用途 | 关键字段 |
|---|---|---|
| `cover` | 封面 | `kicker` `years` `title` `subtitle` `lead` `big` |
| `quote` | 序章 / 金句 / 小结 | `chapter` `small` `big` `sub` `note` |
| `stats` | 一组数字 | `numbers`（2—5 组） |
| `toc` / `toc6` / `toc8` | 目录（3—8 章） | `items` |
| `chapter` | 章节页 | `num` `cn` `title` `quote` `img` |
| `content` | 2—4 卡内容页 | `cards` `lead` `note` |
| `timeline` | 3—6 节点时间轴 | `events` |
| `person` | 人物页（3 件事 + 原话） | `name` `dates` `deeds` `quote` `img` |
| `two_col` | 左右对照 | `left_items` `right_items` |
| `fullpic` | 整版图片页 | `img` `points` `caption` |
| `map_page` | 左文右图（地图/竖图） | `img` `points` `footnote` |
| `listpage` | 3—6 条清单 | `items` |
| `closing` | 结语 | `lines` `slogan` |
| `thanks` | 致谢 | `title` `sub` |
| `sources` | 来源 / 版权说明 | `items` `credit` |

字段、数量限制和完整示例见 [docs/PAGES.md](docs/PAGES.md)。

## 质量红线

1. **不压字**：标题、副标题、页脚互不重叠；长标题靠 `title_size()` 自动缩字号，不要硬压。
2. **不溢出**：卡片正文控制在 60 字以内；超过就拆页，不要缩到 8pt。
3. **不裁切**：时间轴两端留 1 个字符宽度；全图页主体放在画面中间 60% 区域。
4. **不拉伸**：所有图片用 `add_pic_cover()` 裁切填充，不要直接改宽高比。
5. **不空讲**：每页 `script` 150—250 字，和页面标题对得上，能直接照读。
6. **不泄私**：公开仓库和示例中不出现真实姓名、学校/学院/支部、学号、手机号、住址、个人照片、令牌。
7. **不侵版权**：不使用来源不明的网络图片；字体不打包；来源页写清楚。

## 目录结构

```text
red-gold-league-ppt/
├── SKILL.md                 # 本文件：Agent Skill 入口
├── red_gold_deck/
│   ├── builder.py           # 配置校验 + 页面分发 + DOCX
│   ├── deck.py              # 基础版式
│   ├── rich.py              # 丰富版式
│   ├── helpers.py           # 颜色、字体、文本框、图片裁切
│   ├── docx_util.py         # Word 讲稿
│   └── assets/bg/           # 4 张 CC0 背景
├── examples/demo.py         # 31 页可运行示例
├── scripts/                 # 生成背景/图片、渲染、检查
├── docs/                    # 页面、设计、素材、排障
└── tests/                   # pytest
```

## 常见问题

- 中文变成方框：字体没装，或环境变量指向了不存在的字体。
- PPT 打不开 / 图片丢失：检查 `img` 路径是否为绝对路径或相对当前工作目录。
- 页数对不上：`expect_pages` 是硬校验；改完页面记得同步修改。
- 渲染失败：确认 PowerPoint / LibreOffice 与 `pdftoppm` 可用，详见 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)。

## 许可与免责声明

- 代码 MIT；内置背景与示例图片 CC0 1.0。
- 本 Skill 只提供排版工具，不构成历史、政治或法律结论。
- 使用者应自行核对史实、引文、数据与官方提法，并遵守所在单位的宣传纪律。
