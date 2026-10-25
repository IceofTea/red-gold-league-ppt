# 配图、肖像、版权与隐私

## 仓库里有什么

| 目录 | 内容 | 授权 |
|---|---|---|
| `red_gold_deck/assets/bg/` | 4 张抽象背景（封面/宣纸/章节/深色） | CC0 1.0 |
| `examples/assets/` | 12 张示意图（山、海、城市、道路、田野、森林、星空、河流、草原、桥、梯田、光束） | CC0 1.0 |
| `red_gold_deck/assets/portraits/` | 空目录，放你自己的肖像 | 你负责授权 |
| `red_gold_deck/assets/scenes/` | 空目录，放你自己的场景图 | 你负责授权 |

所有内置图片都由脚本生成：

```bash
python scripts/make_backgrounds.py red_gold_deck/assets/bg
python scripts/make_demo_assets.py examples/assets
```

脚本使用固定随机种子，重复运行结果基本一致。图片不含任何真实人物、地点、标志或文字。

## 三类图片，三种处理

### 1. 自有照片

- 确认照片里没有不愿公开的第三人；
- 人脸清晰的照片，公开前取得本人同意；
- 活动照片去掉门牌、工牌、车牌、手机号；
- 在 `sources` 页写“作者拍摄”或“支部供图”。

### 2. 明确授权的素材

- 保留授权凭证（邮件、截图、订单）；
- 在 `sources` 页写清作者、来源、授权方式；
- 需要署名的，按授权要求署名；
- 不确定时不要用。

### 3. 公共领域 / CC0

- 优先使用 Wikimedia Commons、博物馆开放资源等；
- 逐张核对许可，注意“Public Domain”与“CC BY-SA”不是一回事；
- CC BY / CC BY-SA 需要署名，CC0 不需要；
- 历史照片即使进入公共领域，也要注意人物尊严与使用场景。

`scripts/fetch_images.py` 可以从 Wikimedia Commons 按关键词抓取候选图，并保存许可信息。它只负责下载，**不替你判断授权是否适用**。

```bash
python scripts/fetch_images.py "Chinese wheat field" -n 6 -o my_assets/candidates
```

下载后请打开 `licenses.json` 逐张核对。

## 人物肖像

- 历史人物：使用博物馆、档案馆、官方纪念馆发布的公共领域图片；
- 当代人物：必须取得本人或家属授权；
- 不要用 AI 生成的人像冒充真实人物；
- 没有合适图片时，保留 `person` 页的金色剪影占位；
- 肖像不要拉伸、不要过度滤镜、不要裁掉面部。

## 字体

仓库**不打包字体**。默认字体栈：

- 方正小标宋简体
- 华文中宋
- 微软雅黑
- Noto Serif SC

这些字体需要本机安装。没有安装时，PowerPoint 会回退到系统字体，版式可能变化。开源分发时，请使用 SIL OFL 等允许再分发的字体（如思源宋体、Noto Serif CJK），并通过环境变量替换：

```bash
export RED_GOLD_TITLE_FONT="Source Han Serif SC"
export RED_GOLD_SERIF_FONT="Source Han Serif SC"
export RED_GOLD_BODY_FONT="Source Han Sans SC"
export RED_GOLD_NUM_FONT="Source Han Serif SC"
```

## 隐私检查清单

公开仓库、示例课件、截图、讲稿中，逐项确认没有：

- [ ] 真实姓名（包括文件名、图片 EXIF、文档属性）；
- [ ] 学校、学院、班级、团支部全称；
- [ ] 学号、工号、身份证号；
- [ ] 手机号、微信号、邮箱、住址；
- [ ] 个人照片、合影、家庭照片；
- [ ] 内部文件编号、会议纪要、未公开数据；
- [ ] 本机绝对路径（`C:\Users\...`、`/home/...`）；
- [ ] GitHub / API 令牌、密码、密钥；
- [ ] 带水印或来源不明的网络图片。

建议在提交前跑一遍：

```bash
# 在仓库根目录
grep -rInE "C:\\\\Users|/home/|[0-9]{11}|【?[0-9]{8,12}】?" . --exclude-dir=.git --exclude-dir=out
```

Windows PowerShell：

```powershell
Get-ChildItem -Recurse -File | Select-String -Pattern 'C:\\Users|/home/|\b1[3-9]\d{9}\b'
```

## 文档属性

PowerPoint / Word 会写入作者、单位、最后修改人。公开前检查：

- PowerPoint：文件 → 信息 → 检查问题 → 检查文档；
- Word：文件 → 信息 → 检查问题 → 检查文档；
- 或直接看 `docProps/core.xml`、`docProps/app.xml`。

`python-pptx` 生成的默认作者是 `python-pptx`，一般不含个人信息；如果你用模板，务必检查模板属性。

## 免责声明

本项目只提供排版工具，不构成历史、政治或法律结论。图片授权、史实核对、宣传纪律由使用者负责。
