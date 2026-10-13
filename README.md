# face-hairstyle-fit

> 根据照片探索适合自己的风格，并协调发型、可选妆容与穿搭。

`face-hairstyle-fit` 是一个面向图像理解 Agent 的 Skill。它不把用户固定成一个标签，而是
从用户声明的照片与偏好中，提出可解释、可逆、可执行的风格试验：先给主方向与备选方向，
再分别给发型、妆容（可选）、近脸穿搭和低成本验证步骤。

## v0.1 的风格模型

案例中出现的风格词并不处在同一层，因此内部拆成三类：

- **基础风格 family**：甜美系、柔和系、端庄大气系、清冷系、轻熟系。
- **表达方向 expression**：韩系、日系；描述造型语言，不推断国籍或族裔。
- **组合配方 recipe**：当前包含甜酷、柔和法式、典雅新中式；后续可只增 catalog 配置。

七维造型模型：线条、结构、明暗对比、色彩深浅、鲜艳度、装饰量、修饰精度。1–5 是有
文字锚点的设计序数，不是颜值分数、概率或训练得到的脸型分类器。详细定义见
[`references/catalog.json`](references/catalog.json) 和 [`references/dimensions.md`](references/dimensions.md)。

## 使用

把 `SKILL.md` 作为 Skill 入口加载到图像能力可用的 Agent 中。咨询时提供：

- 一张清晰、单人的正面或接近正面照片；
- 想保留/尝试的发长、发质和日常打理时间（知道多少说多少）；
- 是否化妆、职业/学校限制、喜欢或避开的方向；
- 如果要评价当前穿搭，再提供当前穿搭或全身照。

照片角色需要明确：`user_photo`、`reference`、`expected_effect` 或 `unknown`。预期效果图
只描述目标配方，不作为用户原生脸部的证据；截图字幕也不是分类真值。

## 本地质量门禁

Python 3.9+：

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/skill_tools.py check-catalog
.venv/bin/python scripts/skill_tools.py check-report examples/provisional-report.json
.venv/bin/python scripts/skill_tools.py render examples/provisional-report.json --output artifacts/example.html
```

CLI 只做 catalog/report 契约校验和静态 HTML 展示，**不执行图像分析、不联网、不读取照片**。
渲染器会转义报告文字、拒绝覆盖已有文件，并设置不加载远程资源的 CSP。示例报告是人工
构造的结构示例，不是真人案例或效果证明。

## 隐私与边界

- 默认仓库为 private；真人案例、裁剪图、OCR 文本、面部 embedding 和个体报告不进 Git。
- 不做人脸识别，不推断年龄、性别、族裔、健康、性格或社会身份，不做颜值评分与医疗诊断。
- “轻熟”“清冷”“甜美”等是可尝试的造型配方，不是人的真实年龄、性格或身份。
- 仅有脸部照片时，穿搭建议限于领口、近脸颜色、材质和整体方向，不推测体型。
- 生成本地图片 QA 产物后，验收完成应删除带真人内容的临时文件。

案例提炼边界见 [`references/case-protocol.md`](references/case-protocol.md)，方案与方案 review
见 [`docs/architecture.md`](docs/architecture.md) 和 [`docs/plan-review.md`](docs/plan-review.md)。

## 状态

v0.1 是基于本地案例的探索性规则包，不代表科学分类、泛化准确率或唯一“最适合”。新增
风格应添加 catalog 条目、补充行为测试，并经过新的真实回放与人工审核。
