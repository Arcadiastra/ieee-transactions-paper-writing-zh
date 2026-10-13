# 引用核验工具

## 分层与边界

联网出版元数据优先采用可选的 [Bibverify 官方 CLI](bibverify-integration.md)，当前锁定 0.5.0，使用独立 Python 3.11+ 环境。未安装或不兼容时，使用下列内置元数据脚本。本文所述命令、状态和退出码针对内置工具；不要套用到 Bibverify。

工具只生成报告，不修改 `.bib`、`.tex` 或引用 key。三个可执行入口共用 `scripts/citation_common.py`：

| 入口 | 用途 | 联网 |
| --- | --- | --- |
| `scripts/audit_bibtex.py` | 解析 BibTeX，检查重复 key/DOI/题名、必要字段、作者截断、年份、DOI 语法、页码连接符，以及 AUX 中未定义引用 | 从不联网 |
| `scripts/verify_metadata.py` | 内置备用元数据后端；DOI 优先核对题名、作者、年份、卷期、页码/文章号和刊名；Crossref 无记录或不可用时尝试 DataCite；无 DOI 可显式启用题名候选检索 | 必须指定 `--online`，或用 `--cache-only` |
| `scripts/check_updates.py` | 查询指向被引 DOI 的撤稿、更正、关注声明等更新通知，保留通知 DOI、类型与来源 | 必须指定 `--online`，或用 `--cache-only` |

不自动判定文献是否支持正文论断，不提供 JCR 分区，不将命中 DOI 等同于论文真实可靠。后续原文核查见 [引用支持关系流程](integrity-review.md)。

默认不设置文献数量阈值：skill 中的篇幅与文献预算可能按稿件调整，需要时显式传 `--min-count`。脚本不猜测期刊分区，也不根据刊名缩写自动判定文献质量。

## 安装与本地测试

Python 3.10 或以上。使用成熟的 `bibtexparser` 解析 BibTeX，`pylatexenc` 处理 LaTeX 文本；不使用正则表达式自行替代 BibTeX 语法解析。

以下命令在套件根目录运行。Windows 使用 PowerShell 7：

```powershell
$ErrorActionPreference = 'Stop'
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw '创建虚拟环境失败' }
& ./.venv/Scripts/python.exe -m pip install -r ./subskills/citation/scripts/requirements.txt
if ($LASTEXITCODE -ne 0) { throw '安装依赖失败' }
& ./.venv/Scripts/python.exe -X utf8 -m unittest discover -s ./subskills/citation/tests -v
if ($LASTEXITCODE -ne 0) { throw '测试失败' }
```

## 离线检查

```powershell
$ErrorActionPreference = 'Stop'
& ./.venv/Scripts/python.exe -X utf8 ./subskills/citation/scripts/audit_bibtex.py 'C:/paper/ref.bib' --aux 'C:/paper/main.aux' --out-dir './reports/offline-01'
if ($LASTEXITCODE -eq 2) { throw '核验未完成，请检查错误信息' }
```

省略 `--aux` 时检查整份文献库。提供 AUX 时仅检查已编译稿件选中的条目；BibTeX 控制条目不计入文献。重复 key 仍在整库检测。AUX 必须来自当前稿件；本工具不编译 LaTeX，也不会通过粗略扫描 `.tex` 猜测实际启用的章节。支持 `\citation`、`\abx@aux@cite`、`\abx@aux@nocite` 和 AUX 子文件；子文件不能超出根 AUX 所在目录。

## 出版元数据

```powershell
$ErrorActionPreference = 'Stop'
& ./.venv/Scripts/python.exe -X utf8 ./subskills/citation/scripts/verify_metadata.py 'C:/paper/ref.bib' --aux 'C:/paper/main.aux' --online --cache-dir './reports/cache' --out-dir './reports/metadata-01'
if ($LASTEXITCODE -eq 2) { throw '存在网络或处理失败，请先检查报告' }
```

无 DOI 的条目默认标为 `NO_DOI`。加 `--search-titles` 后向 Crossref 发送题名，返回候选而非自动认定匹配。题名相似度只用于解释差异，不用模糊阈值自动覆盖原信息。可用 `--limit 2` 冒烟测试；报告会明确标为部分检查。

## 撤稿与更正通知

```powershell
$ErrorActionPreference = 'Stop'
& ./.venv/Scripts/python.exe -X utf8 ./subskills/citation/scripts/check_updates.py 'C:/paper/ref.bib' --aux 'C:/paper/main.aux' --online --cache-dir './reports/cache' --out-dir './reports/updates-01'
if ($LASTEXITCODE -eq 2) { throw '更新通知检查未完整完成' }
```

查询 Crossref `updates:DOI`，核对通知的 `update-to` 确实指向目标 DOI。撤稿通知与被撤论文不是同一个文献，不能倒置方向。发现任何通知都交给作者阅读，不自动删引用。最多读取每个 DOI 的前 100 条更新；超过上限标为 `PARTIAL`，不声称检查完整。无通知只能报告 `NO_UPDATE_FOUND`，不能报告“保证未撤稿”。

## 输出、隐私与状态

每次生成 UTF-8 JSON 和 Markdown 报告，记录源文献库 SHA-256、选择范围及逐条状态。联网响应存入缓存并附请求 URL 和获取时间，便于复核。默认缓存有效期为 24 小时；用 `--cache-hours` 调整，用 `--cache-only --cache-dir ...` 离线复查。过期、损坏或不存在的缓存不会在离线模式下偷偷触发网络。

输出报告不覆盖同名已有文件；每轮选择新的 `--out-dir`。公共缓存可重复使用，过期响应在显式联网后刷新；需保留历史证据时，每轮使用独立缓存目录。

联网仅向 Crossref、DataCite 发送 DOI；题名仅在显式启用题名检索时发送。可选 `--email` 会把联系邮箱放入 API User-Agent。脚本不上传正文、PDF、完整 BibTeX 或密钥，不访问文献库中的任意 URL。不要给未公开研究条目启用题名检索而忽略其信息披露。

| 状态 | 含义 |
| --- | --- |
| `LOCAL_ONLY` | 仅本地检查，未核验出版事实 |
| `MATCHED_FIELDS` | 实际比较的字段一致；同时列出未比较字段，不代表整条完全正确；若先前来源失败，即使回退成功，`provider_complete` 仍为 false |
| `REVIEW` | 返回记录与本地字段有差异，需人工核查 |
| `NO_DOI` / `TITLE_CANDIDATES` | 缺少 DOI 或仅有题名候选，尚未确认 |
| `NOT_INDEXED` | 本轮查询的索引未返回 DOI 记录，不等于伪造 |
| `UNAVAILABLE` | 网络、限流、缓存或响应格式导致未完成，不等于查无记录 |
| `UPDATE_NOTICE` | 找到指向该 DOI 的更新通知，需阅读出版社通知 |
| `NO_UPDATE_FOUND` | 本轮没有查到通知，不保证永不撤稿或无更正 |
| `PARTIAL` | 更新通知结果超过读取上限，检查不完整 |

退出码：`0` 为流程完成且没有触发本轮错误门槛，`1` 为需要审查的错误/差异/通知，`2` 为输入、输出、网络或处理未完成。警告和未核实项目仍可能出现在退出码 0 的报告中。联网脚本加 `--strict` 可将未确认或部分检查也纳入非零退出；即使严格模式通过，也不替代原文审查。

## 已知限制

- `@string`、嵌套花括号和字符串拼接由解析器处理；`crossref` 父条目继承不自动合并，报告提示人工检查。
- 为防止损坏 BibTeX 被静默跳过，遇到疑似未解析条目会停止；在显式注释中保存完整 BibTeX 示例也可能触发此保护。
- `.bbl`、任意 `.tex` 宏展开、多文献库合并和编译错误诊断不在当前范围内。可先使用 TeX 工具生成当前 AUX。
- 姓名异体、团体作者、刊名缩写、预印本改题和出版年份变体可能需要人工判断；脚本宁可标待审，不自动纠正。
- 月份、IEEEtran 最终显示样式、来源缺失字段、JCR 分区和原文论断支持关系需另行核查。
- 当前多来源策略是注册机构回退，不是多个独立数据库的一致性证明；不把 Crossref 与 DataCite 的无记录解释为两个独立的真实性否定证据。
