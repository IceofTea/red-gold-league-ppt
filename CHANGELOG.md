# Changelog

所有 notable changes 记录在这里。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-10-25

### Added

- 配置驱动的 `red_gold_deck` 包：`build()`、`build_from_file()`、`validate_config()`；
- CLI：`red-gold-deck build` / `red-gold-deck validate`；
- 16 种页面类型：封面、金句、数字、目录（3/6/8）、章节、卡片、时间轴、人物、左右对照、全图、左文右图、清单、结语、致谢、来源；
- 31 页可运行示例 `examples/demo.py`，含 12 张配图；
- 4 张 CC0 抽象背景 + 12 张 CC0 示意图，均由 Pillow 脚本生成；
- 逐页 Word 讲稿生成（`docx_util.py`）；
- `SKILL.md`：OpenCode / Claude 风格的 Agent Skill 入口；
- 文档：页面手册、视觉规范、素材与隐私、排障、贡献指南；
- 脚本：生成背景、生成示例图、抓取候选图、渲染（PowerShell / Bash）、成品检查；
- pytest 测试与 GitHub Actions CI 配置样例（Python 3.10—3.13）。

### Notes

- 不包含任何第三方照片、人物肖像或商业字体；
- 示例文字为通用演示内容，不含真实姓名、单位、学号、联系方式；
- 字体需要本机安装，可用 `RED_GOLD_*_FONT` 环境变量替换。
