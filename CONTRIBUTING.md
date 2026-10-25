# 参与贡献

感谢你愿意改进这个项目。它最初是为团支部主题团课做的排版工具，欢迎把它用到更多场景。

## 开发环境

```bash
git clone https://github.com/IceofTea/red-gold-league-ppt.git
cd red-gold-league-ppt
python -m pip install -e ".[dev]"
python -m pytest
python examples/demo.py
```

要求 Python 3.10+。依赖：`python-pptx`、`python-docx`、`Pillow`、`lxml`。

## 目录约定

```text
red_gold_deck/
├── builder.py      # 配置校验、页面分发、DOCX 生成
├── deck.py         # 基础版式
├── rich.py         # 丰富版式
├── helpers.py      # 颜色、字体、文本框、图片裁切
├── docx_util.py    # Word 讲稿
└── assets/bg/      # CC0 背景
```

- 通用排版函数放 `helpers.py`；
- 基础页面放 `deck.py`；
- 依赖更多元素的页面放 `rich.py`；
- 页面类型必须在 `builder.PAGE_REQUIRED` 注册，并在 `build()` 里分发。

## 新增一种页面

1. 在 `deck.py` 或 `rich.py` 里写方法，签名保持“数据在前、`script` 在后”；
2. 在 `builder.PAGE_REQUIRED` 加字段列表；
3. 在 `builder.build()` 加 `elif` 分支；
4. 在 `docs/PAGES.md` 写字段说明和示例；
5. 在 `tests/test_builder.py` 加一个最小用例；
6. 运行 `pytest` 和 `python examples/demo.py`，再渲染目检。

## 代码风格

- 4 空格缩进，行宽尽量 ≤ 100；
- 公开函数写 docstring，说明参数和副作用；
- 注释用中文，标识符用英文；
- 不引入新的重量级依赖；能用 Pillow / python-pptx 解决就不要加库；
- 不提交生成物：`out/`、`*.pptx`、`*.docx`、`render/` 已在 `.gitignore`。

## 素材与隐私

提交图片前必须确认：

- 你有权分发该图片；
- 图片里没有真实姓名、单位、学号、手机号、住址；
- 没有未授权的真人肖像；
- 没有带水印的网络图片；
- 在 `docs/ASSETS.md` 或 `sources` 页写清授权。

**不要在仓库、示例、测试、截图里写入本机绝对路径、令牌、真实支部信息。** 这是硬性要求。

## 测试

```bash
python -m pytest -q
python -m red_gold_deck.cli validate examples/demo.py
python examples/demo.py
python scripts/check_deck.py out/demo/demo_主题团课.pptx \
  --docx out/demo/demo_演讲稿.docx
```

涉及版式的改动，请附一张渲染截图（可以只截相关页面）。截图里不要出现个人信息。

## 提交信息

用简短的祈使句，例如：

```text
add map_page layout
fix timeline clipping with six events
docs: clarify font fallback
```

一个提交只做一件事。大改动请先开 issue 说明动机和方案。

## Pull Request 清单

- [ ] `pytest` 通过；
- [ ] `examples/demo.py` 能生成 31 页；
- [ ] `scripts/check_deck.py` 无 ERROR；
- [ ] 新增/修改的页面已渲染目检；
- [ ] 文档已同步；
- [ ] 没有个人信息、绝对路径、令牌、未授权图片；
- [ ] 没有提交 `out/` 或生成物。

## 许可

提交代码即表示同意以 MIT 许可发布；提交图片即表示同意以 CC0 1.0 发布（或已在文件中注明其他许可）。
