# 常见问题

## 安装与导入

### `ModuleNotFoundError: No module named 'red_gold_deck'`

在仓库根目录安装：

```bash
python -m pip install -e .
```

或者临时把仓库根目录加入 `PYTHONPATH`：

```bash
# Windows PowerShell
$env:PYTHONPATH = (Get-Location).Path

# macOS / Linux
export PYTHONPATH="$PWD"
```

直接运行 `python examples/demo.py` 时，示例脚本会自己把仓库根目录加入 `sys.path`，所以通常不需要额外设置。

### `pytest: command not found`

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## 配置与生成

### `config is missing required key: 'pages'`

`CFG` 必须包含 `footer`、`header`、`topic`、`pages` 四个键。最小配置见 README。

### `page N (content): missing keys ['cards']`

页面缺少必填字段。对照 [PAGES.md](PAGES.md) 补齐。注意 `person` 页的 `dates` 也是必填。

### `unknown page type 'contents'`

页面类型拼写错误。运行：

```bash
red-gold-deck validate my_deck.py
```

它会打印所有用到的类型，方便对照。

### `toc6 needs exactly 6 items`

`toc6` / `toc8` 是硬校验。要么补齐条目，要么改用 `toc`（3—8 条自动排版）。

### `page count mismatch: generated 30, expected 31`

你增删了页面，但没改 `expect_pages`。这是有意的保护，避免“少了一页没发现”。

处理方式：

1. 确认页数正确后，把 `expect_pages` 改成实际页数；
2. 或者删掉 `expect_pages`，关闭校验（不推荐）。

### 图片找不到 / 生成后图片空白

- `img` 路径是相对**当前工作目录**解析的，不是相对配置文件；
- 最稳妥的写法：

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
img = str(ROOT / "examples" / "assets" / "mountain_dawn.jpg")
```

- 路径里有中文或空格时，用 `Path` 拼接，不要手写字符串；
- 生成前先 `os.path.exists(img)` 检查，`fullpic` / `map_page` 在图片缺失时会退化为纯色底，不会报错，但会少一张图。

### 保存时报 `PermissionError`

PPTX 正在 PowerPoint 里打开。先关闭文件，或输出到新目录：

```bash
red-gold-deck build my_deck.py -o out/v2
```

## 字体

### 中文变成方框 / 字体不对

1. 确认本机安装了字体：

```powershell
# Windows
Get-ChildItem C:\Windows\Fonts | Where-Object Name -match '小标宋|中宋|雅黑'
```

```bash
# macOS / Linux
fc-list :lang=zh | head
```

2. 用环境变量替换成已安装的字体：

```bash
export RED_GOLD_TITLE_FONT="Source Han Serif SC"
export RED_GOLD_SERIF_FONT="Source Han Serif SC"
export RED_GOLD_BODY_FONT="Source Han Sans SC"
export RED_GOLD_NUM_FONT="Source Han Serif SC"
```

3. 重新生成。字体只在打开 PPT 时解析，已生成的 PPTX 不会自动换字体。

### 换字体后版式变了

不同字体的字宽不同，标题可能换行。换字体后必须重新渲染检查，必要时缩短标题或调整字号。

## 渲染

### Windows：PowerPoint COM 报错

常见错误：

- `0x800A03EC`：文件路径不存在，或 PowerPoint 正在弹窗；
- `0x80010105`：PowerPoint 进程卡住；
- `Call was rejected by callee`：PowerPoint 忙。

处理：

```powershell
Stop-Process -Name POWERPNT -Force -ErrorAction SilentlyContinue
```

然后重新运行 `scripts/render.ps1`。如果经常失败，改用 LibreOffice：

```bash
libreoffice --headless --convert-to pdf --outdir out/render out/demo/demo.pptx
```

### `pdftoppm: command not found`

安装 poppler：

- Windows：`scoop install poppler` 或下载 poppler for Windows，把 `bin` 加入 PATH；
- macOS：`brew install poppler`；
- Ubuntu/Debian：`sudo apt install poppler-utils`。

检查：

```bash
pdftoppm -v
```

### 渲染出来是空白 / 只有第一页

- 确认 PDF 生成成功：`out/render/render.pdf`；
- 确认 PDF 页数等于 PPT 页数；
- 检查 `pdftoppm` 的参数：`-jpeg -r 150`；
- 文件名有中文时，先 `cd` 到输出目录再执行，避免编码问题。

### 渲染颜色和 PowerPoint 里不一样

- PDF 导出会做色彩管理，投影时以 PowerPoint 为准；
- 半透明遮罩在 LibreOffice 与 PowerPoint 中可能有细微差异；
- 关键页（封面、全图页）建议在目标电脑上再看一遍。

## 文档与讲稿

### Word 讲稿页码和 PPT 对不上

讲稿按 `deck.script` 顺序生成，一页一段。如果某页调用了两次 `say()`，或手动插入页面，页码会错位。检查自定义页面方法，确保每页只调用一次 `self.say()`。

### 讲稿里出现 `【】`

这是占位提示，不是错误。正式使用前替换掉。讲稿说明里已写明“方括号【】内为提示，不读”。

## Git 与 GitHub

### 中文文件名在 Git Bash 里显示乱码

```bash
git config --global core.quotepath false
```

### 提交里混进了 `out/`、`*.pptx`

检查 `.gitignore` 是否生效：

```bash
git check-ignore -v out/demo/demo_主题团课.pptx
```

如果文件已经被跟踪：

```bash
git rm --cached "out/demo/demo_主题团课.pptx"
```

### 推送很慢 / 超时

- 本机 DNS 对 GitHub 不稳定时，`curl` 和 `git` 可能间歇失败；
- 重试通常有效；
- 大文件（> 50 MB）不要提交，PPTX 输出目录已在 `.gitignore` 中。

## CI

### GitHub Actions 里 `python examples/demo.py` 失败

- 确认 `examples/assets/` 已提交（示例图片是 CC0，应该进仓库）；
- 确认 `pyproject.toml` 的 `package-data` 包含 `assets/bg/*.jpg`；
- CI 不需要中文字体也能生成 PPTX，但渲染检查需要额外安装字体和 LibreOffice，默认 CI 只跑生成与测试。

### CI badge 一直显示 failing

打开 Actions 页面看具体步骤。常见原因是 `pytest` 收集到了本地临时文件，或 `out/` 目录被误提交。清理后重新推送。
