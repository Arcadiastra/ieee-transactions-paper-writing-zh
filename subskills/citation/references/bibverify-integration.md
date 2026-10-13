# Bibverify 官方 CLI 接入

## 接入方式

直接调用官方 CLI，不维护自定义适配脚本，不复制上游核验引擎，不启动 MCP 服务。当前兼容基线为 **Bibverify 0.5.0、Python 3.11+**，以 PyPI 已发布包及实际 `--help` 为依据，不从开发分支文档推断已安装版本的功能。

Bibverify 是可选的联网元数据后端。优先保留本套件的离线检查、出版更新检查、原文支持关系审查和作者审批规则。

| 工作 | 工具 |
| --- | --- |
| BibTeX 结构、重复条目与 AUX 实际引用范围 | `scripts/audit_bibtex.py` |
| 联网出版元数据 | 已安装且兼容的官方 Bibverify CLI |
| 未安装或版本不兼容时的元数据检查 | 内置 `scripts/verify_metadata.py`，明确报告所用后端 |
| 撤稿、更正、关注声明 | `scripts/check_updates.py` |
| 原文论断支持、JCR 分区与最终显示格式 | 按 citation skill 单独核验 |

## 可选安装

仅在用户要求安装或接入时执行；不能在普通写作任务中自动安装或升级。使用独立环境，避免与内置脚本锁定的解析器版本冲突。安装包包括上游 MCP 依赖，但本接入不运行服务器、不注册 MCP、不修改宿主配置。

以下示例从套件根目录执行，使用 PowerShell 7；本机有 Python 3.12 时可用：

```powershell
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath './.venv-bibverify') { throw '环境已存在，请先检查版本，不要覆盖' }
py -3.12 -m venv .venv-bibverify
if ($LASTEXITCODE -ne 0) { throw '创建环境失败' }
& ./.venv-bibverify/Scripts/python.exe -m pip install --index-url https://pypi.org/simple -r ./subskills/citation/scripts/requirements-bibverify.txt
if ($LASTEXITCODE -ne 0) { throw '安装失败' }
& ./.venv-bibverify/Scripts/python.exe -m bibverify --version
if ($LASTEXITCODE -ne 0) { throw '版本检查失败' }
& ./.venv-bibverify/Scripts/python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw '依赖冲突' }
```

其他系统使用其 Python 3.11+ 与虚拟环境路径。安装前检查环境可用性，不将 Windows 路径硬套到其他平台。只支持已验证版本；未来升级需重新确认只读行为、配置字段、JSON 结构和退出码。

## 联网范围与默认配置

使用 [只读配置](../assets/bibverify-readonly.json)，不直接使用启用了多个数据库的上游默认配置：

- 仅启用 Crossref，无需 API Key。
- 关闭其余来源、持久化缓存以及工具自己的报告、备份、更新文献和待审文献输出。
- 联系邮箱默认为空，不向 API 发送虚构邮箱。用户可通过官方 `BIBVERIFY_EMAIL` 环境变量提供真实联系邮箱。
- 若要启用 OpenAlex、Semantic Scholar、arXiv、DBLP 等，先说明将查询哪些来源及其当前访问条件，再在工作目录复制并调整配置；不静默扩展联网范围。密钥只通过环境变量或受保护的本地配置提供，不写入仓库。

**`--dry-run` 仅表示不写文件，不表示离线。** DOI 查询或题名回退会向启用的数据库发送书目信息，仍需用户授权联网核验。它不负责 JCR，也不核验正文结论。

运行前必须确认输入范围：官方 CLI 核验整个输入 `.bib`，没有本套件的 `--aux` 过滤参数。若用户只要求当前稿件已引用条目，先用离线工具核对当前 AUX，再使用已准备好的引用子集副本；不把包含未引用或私有条目的整库直接上传查询。子集保留 citation key 和必要书目字段，避免带入私人 `file`、笔记或完整摘要。没有可核对的子集时先明确范围，不假装已经按 AUX 过滤。

## 只读调用与报告保留

以下命令直接运行官方程序，由 PowerShell 捕获原始 JSON；不是自定义适配器。将示例输入改为已经确认范围的文献库绝对路径。

```powershell
$ErrorActionPreference = 'Stop'
$python = (Resolve-Path './.venv-bibverify/Scripts/python.exe').Path
$config = (Resolve-Path './subskills/citation/assets/bibverify-readonly.json').Path
$bib = (Resolve-Path 'C:/paper/references.cited.bib').Path
$reportFile = Join-Path (Get-Location) 'reports/bibverify-01.json'
if (Test-Path -LiteralPath $reportFile) { throw '报告已存在，请选择新文件名' }
$before = (Get-FileHash -LiteralPath $bib -Algorithm SHA256).Hash
$jsonLines = & $python -X utf8 -m bibverify check $bib --config $config --dry-run --json
$code = $LASTEXITCODE
if ($before -ne (Get-FileHash -LiteralPath $bib -Algorithm SHA256).Hash) { throw '源文件发生变化，停止处理' }
if (-not $jsonLines) { throw "未返回 JSON，退出码 $code" }
$jsonText = $jsonLines -join "`n"
$report = $jsonText | ConvertFrom-Json
if ($report.dry_run -ne $true -or $report.applied -ne $false) { throw '只读状态不符合预期' }
New-Item -ItemType Directory -Path (Split-Path $reportFile) -Force | Out-Null
$jsonText | Set-Content -LiteralPath $reportFile -Encoding UTF8
Write-Output "Bibverify 退出码：$code；原始报告：$reportFile"
if ($code -notin @(0, 2, 3, 4)) { throw '输入或运行错误，请检查诊断信息' }
```

不传 `--apply`。不要把候选 `.bib` 自动覆盖原文献库。`--dry-run` 禁用上游持久缓存和文件输出；需要审计凭据时保存原始 stdout JSON，不声称存在未生成的磁盘缓存。

## 报告解读

下表是 **官方 Bibverify 0.5.0** 的退出码，不能与本套件脚本的 0/1/2 混用：

| 退出码 | 处理 |
| --- | --- |
| 0 | 查看逐条结果，仍需检查字段建议与未比较信号 |
| 2 | 存在更新建议，不代表已经修改文件；列出待审差异 |
| 3 | 模糊匹配、未找到或标识符冲突；人工核查 |
| 4 | 来源不可用或核验不完整；保留失败原因，不算核验通过 |
| 5 | 输入或配置无效；修复调用条件后再运行 |
| 1 / 其他 | 运行异常；保存诊断，不将其解释为引用错误 |

读取 `complete`、`counts`、`entries[].provider_status`、`entries[].candidates`、`entries[].field_diffs`、`dry_run` 和 `applied`。

**即使退出码为 0、状态为 `verified`，也不能直接写“所有字段已核验无误”。** 本轮测试中，原条目缺少作者或页码时，官方程序仍可认定文献身份匹配，同时在 `field_diffs` 中给出 `add` 建议。对非 `keep_original` 的动作逐项检查，缺失或未比较的信号单独报告。

原始状态与原始 JSON 必须保留；可以另用中文解释，但不能把 `not_found` 翻译成“伪造”，不能把 `source_unavailable` 翻译成“没有这篇文献”。

## 降级与后续修改

- 未安装、Python 不兼容或版本未经验证：说明原因，使用内置后端；不自动安装、不自动升级。
- 数据库超时、限流或返回冲突：保留该结果。可以经用户同意查询另一来源，但新来源的命中不能抹掉已有冲突或失败。
- 参考文献修订继续使用原有审批流程：给出原字段、拟改字段、来源和理由，作者同意后再修改。
- 联网核验完成后，根据需要运行出版更新脚本；原文支持关系与最终 IEEE 显示格式仍单独验收。

## 版本依据

- [PyPI 0.5.0](https://pypi.org/project/bibverify/0.5.0/)
- [上游 v0.5.0](https://github.com/Hylouis233/bibverify/releases/tag/v0.5.0)
- [v0.5.0 CLI 源码](https://github.com/Hylouis233/bibverify/blob/v0.5.0/src/bibverify/cli.py)

本接入不运行 `agent init` 或 `skill export` 覆盖本套件，不添加自动安装、自动修复或 MCP 配置。
