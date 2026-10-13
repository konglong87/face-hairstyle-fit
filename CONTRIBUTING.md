# 参与贡献

感谢你帮助完善 `face-hairstyle-fit`。欢迎中文或英文提交：文档改进、规则边界修正、
风格配方与契约测试。当前是探索版，请不要把审美偏好包装成已验证的科学分类。

## 先选择合适的入口

| 事项 | 入口 | 需要提供 |
|---|---|---|
| 使用疑问、风格模型讨论 | Discussions | 脱敏的问题描述和想要解决的场景 |
| 可复现的代码或契约问题 | Issues → Bug report | 版本、命令、合成输入、实际与预期结果 |
| 新风格或表达方向 | Issues → Feature / style proposal | 层级、定义、维度锚点、三模块配方及边界 |
| 漏洞、密钥或真人资料泄露 | [安全策略](SECURITY.md) | 不要在公开 Issue 中附敏感内容 |

## 隐私检查是前置条件

不要提交或粘贴真人照片、脸部裁剪图、embedding、个人分析报告、截图账号、精确位置、
API Key、Token、私钥或 Cookie。不要把 `.env` 或本地配置放入 PR。

使用人工构造的 JSON 和不含个体信息的文字复现问题。公开 Issue、Discussion 和 PR
即使后来删除，内容也可能已经被查看或复制；不要先上传再尝试清理。

## 新增风格

1. 先确认属于 `family`、`expression` 还是 `recipe`，不要增加互斥的人格/身份分类。
2. 在 `references/catalog.json` 添加唯一 ID、定义、可见线索、七维区间、三模块配方和取舍。
3. `recipe` 的 `families` 必须引用已存在的基础风格；非 recipe 的 `families` 为空。
4. 七维区间描述目标造型，不是人脸概率、颜值分数或年龄/族裔判断。
5. 补充有效与无效输入测试，并同步 README；不要为新增 ID 改写通用 schema。
6. 新规则需要真实使用反馈与人工 review；结构测试通过不等于审美有效。

## 本地验证

Python 3.9+，以下命令在仓库根目录执行：

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/skill_tools.py check-catalog
.venv/bin/python scripts/skill_tools.py check-report examples/provisional-report.json
git diff --check
```

只改文档时也要检查相对链接。改渲染器时，生成合成报告并实际查看桌面/窄屏展示；
验收后删除临时产物，不要提交 `artifacts/`、`private/` 或本地环境目录。

## 提交前

- 改动范围小而清楚，说明目的、验证命令和仍然存在的限制。
- 用户偏好、照片角色和不确定性优先于模板化标签。
- 确认 Git 跟踪内容无个人信息和密钥；`.gitignore` 不能清除已提交的历史内容。
- 使用仓库的 PR 模板说明影响，不宣称未完成的测试或独立评估。

贡献内容按本仓库 [MIT License](LICENSE) 提交。维护者决定是否合并，不承诺响应时限。
