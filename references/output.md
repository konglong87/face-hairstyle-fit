# 输出协议

## 面向用户

用简洁卡片组织：建议方向（主/备选）→ 看见的依据与未知项 → 发型/妆容/穿搭 →
低成本先试什么 → 哪个反馈会改变判断。不要为了凑 JSON 打断正常咨询。
需要机器验收、展示页或保存时，再生成 `schemas/report.schema.json` 格式的报告。

## 本地校验与展示

在 Skill 根目录安装可选依赖后：

```sh
python3 scripts/skill_tools.py check-catalog
python3 scripts/skill_tools.py list
python3 scripts/skill_tools.py show sweet
python3 scripts/skill_tools.py check-report private/report.json
python3 scripts/skill_tools.py render private/report.json --output artifacts/report.html
```

示例 `examples/provisional-report.json` 是人工构造的结构示例，不是真人或模型效果证明。
`check-report` 校验结构、ID 引用、角色与状态边界，不保证审美或看图判断正确。
HTML 只展示合法报告，不嵌入/读取照片、不请求远端资源；默认拒绝覆盖已有文件。
本地生成文件依然可能包含敏感描述，勿上传或提交。

报告 `observations[].evidence` 必须是可见图像依据，不能是截图字幕或风格名。
`recommendations[].evidence_ids` 必须引用 observations。
三个模块每个有 status、actions、reason；skip 模块 actions 为空且解释原因，propose 不可空。
`presentation_dimensions` 要包含 catalog 中全部维度；无法观察用 null。
provisional 和 needs_input 要写 uncertainties、questions；needs_input 不给推荐或改造实验。
ready 必须有可用的 user_photo；unknown-role 的 face 观察只允许 low。
