# 公开引用工具的比较与取舍

检索及源码审阅日期：2026-10-12。范围是公开 GitHub 项目、其说明、关键核验代码和部分测试，不是所有商业产品的排名，也不是在统一大规模标注集上进行的准确率测评。

## 适配结论

在本轮检查的项目中，**Bibverify 是最适合作为整体核验架构参考的候选**：标识符优先、可解释匹配、结构化失败状态、写入保护及跨平台测试的组织较完整。这个判断是代码与维护结构的适配评估，不是“全行业准确率最高”的结论。

本套件保留小型只读工具，并已增加 [Bibverify 官方 CLI 可选接入](bibverify-integration.md)，不将其设为基础依赖，不启动 MCP 服务。已验证的发行版为 0.5.0，默认只启用 Crossref；需要其他来源时再按访问条件明确启用。仓库主分支功能不等于已发布包功能，具体调用以锁定发行版为准。

## 比较

| 项目 | 检查到的有用设计 | 对本套件的取舍 |
| --- | --- | --- |
| [Hylouis233/bibverify](https://github.com/Hylouis233/bibverify) | DOI/其他标识符优先，题名、作者、年份、来源和页码的可解释匹配，独立 provider 状态，源文件保护测试 | 作为主要架构参考；采用逐字段报告、冲突不被搜索结果掩盖、未核验范围明确列出，不自动合并 |
| [chrisyangsong/citegate](https://github.com/chrisyangsong/citegate) | 引用检查退出码与 CI 工作流，Crossref 更新通知检查 | 吸收出版状态检查；报告通知事实，不直接将所有更新视为撤稿 |
| [ComDec/citekeep](https://github.com/ComDec/citekeep) | citation key 保留、逐条决定及证据记录、未确认条目保留 | 吸收保留 key 与审查记录思想；当前脚本完全不写回，因此也没有自动修正路径 |
| [Altman-conquer/bibtex-verifier](https://github.com/Altman-conquer/bibtex-verifier) | 成熟 BibTeX 解析器、逐字段比较、Crossref/DataCite 回退、年份差异说明 | 用成熟解析器，保留不同出版日期；作者检查包括顺序和名字差异，不仅检查题名 |
| [tvquynh/citation-verifier](https://github.com/tvquynh/citation-verifier) | DOI 可解析但题名不同的冲突检查；请求失败与未找到区分 | 吸收状态边界；不采用简化 BibTeX 解析器，也不以单一题名阈值给出整条 VERIFIED |
| [QuiXamii/refright](https://github.com/QuiXamii/refright) | 题名、刊名的规范化与差异解释，书目核验工具组织 | 参考刊名缩写比较方向；不引入自动修复与宽松模糊接受规则 |
| [CloudWave818/ieee-skills](https://github.com/CloudWave818/ieee-skills) | 将引用逻辑、出版元数据、格式检查分开 | 适合人工/代理审查流程；其 citation 模块主要是指导文件，不把它当作可运行的验证脚本 |

## 不混淆三类“好”

- 数据库覆盖多，不表示每条引用已经匹配正确。
- 元数据核验成熟，不表示它能判断正文论断得到原文支持。
- 支持自动修正，不表示适合默认修改已经校对过的文献库。

本套件因此将静态检查、元数据、出版更新、原文支持关系四层分开。对于后者，采用原文定位与人工确认，而非声称已有脚本可以全自动证明引用恰当。

## 固定源码依据

以下列出本轮实际审阅的关键文件与版本，方便复核；不要求运行时联网读取它们。

- Bibverify `17d65e3a178e055e649d09c88fa22b56e2599b52`：[matching.py](https://github.com/Hylouis233/bibverify/blob/17d65e3a178e055e649d09c88fa22b56e2599b52/src/bibverify/matching.py)、[源文件保护测试](https://github.com/Hylouis233/bibverify/blob/17d65e3a178e055e649d09c88fa22b56e2599b52/tests/test_golden_workflow.py)、[小型回归案例](https://github.com/Hylouis233/bibverify/blob/17d65e3a178e055e649d09c88fa22b56e2599b52/benchmarks/cases.json)。这些测试已阅读，未在本地运行整个上游测试集。
- Citegate `94cc0a02a63a11154664c88b25923cbd0dc7c028`：[sources.py](https://github.com/chrisyangsong/citegate/blob/94cc0a02a63a11154664c88b25923cbd0dc7c028/src/citegate/sources.py)、[core.py](https://github.com/chrisyangsong/citegate/blob/94cc0a02a63a11154664c88b25923cbd0dc7c028/src/citegate/core.py)。
- CiteKeep `e7f2c92d5d06e30e44cd4e056b08750512ee630e`：[core.py](https://github.com/ComDec/citekeep/blob/e7f2c92d5d06e30e44cd4e056b08750512ee630e/src/citekeep/core.py)。
- BibTeX Verifier `5b4961e574aad56d86ad05470b14068fbb89a612`：[loader.py](https://github.com/Altman-conquer/bibtex-verifier/blob/5b4961e574aad56d86ad05470b14068fbb89a612/bibtex_verifier/loader.py)、[comparator.py](https://github.com/Altman-conquer/bibtex-verifier/blob/5b4961e574aad56d86ad05470b14068fbb89a612/bibtex_verifier/comparator.py)、[apis.py](https://github.com/Altman-conquer/bibtex-verifier/blob/5b4961e574aad56d86ad05470b14068fbb89a612/bibtex_verifier/apis.py)。
- Citation Verifier `e6e8ae0bc2913fcba88536751760c59733b2d0f8`：[verify_citations.py](https://github.com/tvquynh/citation-verifier/blob/e6e8ae0bc2913fcba88536751760c59733b2d0f8/verify_citations.py)。
- Refright `6ff5b9958f54a287d344b3e97b797045c1e19ea5`：[match.py](https://github.com/QuiXamii/refright/blob/6ff5b9958f54a287d344b3e97b797045c1e19ea5/refright/match.py)。
- IEEE Skills `ee30fda73e76b93ede86c07b90bcd09319a50f16`：[metadata-check.md](https://github.com/CloudWave818/ieee-skills/blob/ee30fda73e76b93ede86c07b90bcd09319a50f16/skills/ieee-citation/static/fragments/task_type/metadata-check.md)。

上述仓库本轮查询的许可证均为 MIT。本套件采用独立实现和自建测试，未复制或打包其源文件。通过 requirements 安装的解析库保留各自许可证；将来若直接移植上游实现，必须保留相应版权声明。

## Research-Paper-Writing-Skills 的模板是否需要引入

[Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills)，本轮查看版本 `77e7c2c1ba06f7d71844873147665437a03aac1b`。

其 [摘要模板](https://github.com/Master-cai/Research-Paper-Writing-Skills/blob/77e7c2c1ba06f7d71844873147665437a03aac1b/research-paper-writing/references/examples/abstract/template-b.md) 和 [方法总览模板](https://github.com/Master-cai/Research-Paper-Writing-Skills/blob/77e7c2c1ba06f7d71844873147665437a03aac1b/research-paper-writing/references/examples/method/overview-template.md) 是写作句段骨架，不是 IEEEtran 文档类或官方排版模板。

建议借鉴而非整套引入：摘要的“挑战 -> 洞察 -> 贡献”、方法总览的信息流导航、逐段反向提纲检查，均与本套件相容。原模板中面向具体视觉任务的名称、否定对照及示例数字需要通用化处理，不能直接覆盖肯定式表达与摘要无具体数字规则。

该次调研没有直接导入上游模板或改动已确认的章节写作结构。当前套件已提供简化的本地结构骨架，见 [模板索引](../../../references/template-guide.md)；继续以官方 IEEE 模板负责排版。

## 官方核验依据

- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [Crossref 更新与撤稿数据说明](https://www.crossref.org/blog/retraction-watch-retractions-now-in-the-crossref-api/)
- [Crossref 版本、更正与撤稿原则](https://www.crossref.org/documentation/principles-practices/best-practices/versioning)
- [BibtexParser 解析器说明](https://bibtexparser.readthedocs.io/en/v1.4.0/bibtexparser.html)
