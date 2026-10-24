---
name: ieee-transactions-writing-zh
description: 使用简体中文规划、撰写、修改和审查 IEEE Transactions 学术论文。以贡献和创新机制为主线，协调七个子技能，组织论文框架与章节论证，强调肯定式表达、句间逻辑、跨章节照应及篇幅控制。
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash WebSearch WebFetch Task
metadata:
  language: zh-CN
  trigger: 使用简体中文规划、撰写、修改和审查 IEEE Transactions 形式的学术论文。
  target-venue: IEEE Transactions journals
  repository: https://github.com/Arcadiastra/ieee-transactions-writing-zh.git
---
# IEEE Transactions Writing

## 定位与使用

主 skill 负责全篇原则、章节分工和验收；七个子 skill 各自负责一个写作部分。按任务只读取相关子 skill。

| 子 skill                | 文件                                                  | 负责内容                                 |
| ----------------------- | ----------------------------------------------------- | ---------------------------------------- |
| abstract                | [SKILL.md](subskills/abstract/SKILL.md)                | 无具体数字的摘要与关键词精炼             |
| introduction            | [SKILL.md](subskills/introduction/SKILL.md)            | 动机、相关工作、研究缺口、方案概述与贡献 |
| problem definition      | [SKILL.md](subskills/problem-definition/SKILL.md)      | 问题建模、必要条件、困难分析与设计需求   |
| methodology             | [SKILL.md](subskills/methodology/SKILL.md)             | 机制阐述、数学表达、方法图与问题回应     |
| results and discussions | [SKILL.md](subskills/results-and-discussions/SKILL.md) | 精简 setup、定性机制分析、实验图表       |
| conclusion              | [SKILL.md](subskills/conclusion/SKILL.md)              | 已验证贡献、机制价值与研究意义           |
| citation                | [SKILL.md](subskills/citation/SKILL.md)                | 引用论证、出版信息核验与文献显示规范     |

## 写作流程方法论

### 目标期刊与研究范围核验

在规划、撰写、修改或审查论文之前，首先明确目标期刊。目标期刊未明确时，先向用户确认；随后联网检索并阅读期刊或所属学会的官方页面，核实其 Topics within the journal scope、topics out-of-scope 或同等含义的范围说明，记录来源链接和核验日期。官网未单列范围外主题时，如实注明；无法取得官方依据时，明确告知用户该项检查失败。

根据官方范围，识别与本文相关的范围内主题及核心研究对象名词或名词短语，保留主题中的研究对象、应用场景和其他必要限定条件。结合论文的研究问题、核心贡献和验证内容逐项核对，并检查相关范围外条目。已有稿件以现有内容为依据；尚未成稿时，先核对拟研究的问题、对象和贡献。

**标题、摘要和关键词三处必须分别明确呈现至少一个与本文实质一致的范围内主题，并分别出现至少一处相应的核心研究对象词**。主题允许采用准确的规范同义表达，同一短语可以同时满足两项要求。

**任何阶段发现 `out of scope` 风险，立即提醒用户；无论是否支持弹窗，都等待用户确认后再继续相关修改。**

### LaTeX 写作模板

需要搭建章节结构时，按 [模板索引](references/template-guide.md) 选择指南和 `.tex` 骨架。模板仅提示章节顺序与段落职责，可按研究内容调整，不替代官方排版模板或既有修订审批流程。

根据当前工作区状态和用户反馈，灵活调整策略。以下流程默认以当前工作区为空为前提。

### 搭建骨架

若用户无特殊要求且尚未提供写作大纲，则首先列写论文纲要：按照 IEEE Transactions 初投稿要求组织，将篇幅规划为 10 页。

如用户未提供，则采用官方 LaTeX 模板：[journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/)；若用户的格式与该模板不符，立刻告知用户。

如用户无特殊要求，论文正文固定采用五段式结构，结合摘要和引用，限制最终总 PDF 页数不超过 10 页。具体结构如下：

| 子章节                  | 推荐篇幅           |
| ----------------------- | ------------------ |
| abstract                | 150-200 words      |
| introduction            | 0.9-1.3 页         |
| problem definition      | 1.5-2.5 页         |
| methodology             | 2.5-3.5 页         |
| results and discussions | 2.0-3.0 页         |
| conclusion              | 150-200 words      |
| citation                | ≥ 30 篇，0.7-1 页 |

如文章无特殊性，即按照该结构组织撰写。若用户目标期刊页数不为 10 页，则将所有章节的页数限制、参考文献数量预算均按比例缩放。适当撰写 `.latexmkrc` 以使 PDF 可以自动编译正常生成。若已有论文，且其结构与该结构严重不符，立刻停下来询问用户，给出三个选项：

1. 按照推荐结构，对全文进行结构性大修或推翻重写（推荐）
2. 停用该 skill
3. 用户自定义方案

若用户选择选项 1，则继续向下执行；若用户选择选项 2，则在本 session 里停用该 skill；若用户选择选项 3，则按照用户的自定义方案执行。

### 写作顺序

除非用户有其他明确要求，按以下顺序进行，跳过已有内容；若已有内容与以下格式严重不符，则撰写大修或推翻重写详案，用户批准后执行：

1. 凝练出 3-5 条本研究明确的贡献，均采用名词/动名词（统一全用名词或全用动名词）+ 修饰语的形式，如 `a xxx algorithm that...` 或 `Proposing xxx algorithm that...`，在 introduction 章节作为列表明确写出。
2. 筛选出所有能够为贡献提供佐证的实验，至少包含一个详细解释说明的主实验结果，以及至多两个佐证机制的辅助实验结果。
3. 利用 results and discussions skill 完成 results and discussions 章节的撰写，控制在相应篇幅硬上限以内。
4. 完成 problem definition 和 methodology 的撰写，控制在相应篇幅硬上限以内。
5. 完成 introduction 的撰写和 citations 的整理与校对，控制在相应篇幅硬上限以内。
6. 完成 abstract、keywords 和 conclusion 的总结精炼，控制在相应篇幅硬上限以内。
7. 进行全文验收检查，但不限制总页数。
8. 针对最终页数情况，进行整体内容的压缩或扩充，使得总 PDF 页数与上限一致。首先，将摘要严格控制在 150-200 词之间；然后，对于末页，若分两栏，要求左栏完整、右栏内容达到正文版心高度的约 60%；若不分栏，要求内容达到正文版心高度的约 80%。
9. 进行全文验收检查。

撰稿阶段，必须遵守各 skill 内部规定的篇幅硬限制；进入最终的篇幅控制阶段后，再参考推荐长度区间，保证总篇幅符合要求。

## 全篇第一性原则

- 确保研究问题、核心贡献和验证内容与目标期刊范围一致；前述目标期刊与研究范围核验通过。
- 围绕贡献组织论证：重要问题 -> 关键障碍 -> 创新机制 -> 实验证据 -> 研究意义。
- 以机制创新分配篇幅，严禁正文写成工程配置清单或研究过程流水账。严禁出现任何文件目录信息。尽量不出现内部代号，若无法避免，必须在该代号第一次出现时写明全称。
- 正面讲清本文解决了什么、如何解决、为何有效。除非用户明确要求，禁止在除 limitations and future work 段以外的任何区域撰写任何有关当前研究局限性、未完成工作、否定语气的边界澄清等任何防御性解释的内容。
- 保留结论成立所必需的条件和证据范围；注意严谨性，可以适当弱化语气，但禁止将结论弱化到对论文贡献毫无帮助的程度，关键结论必须是完全正面表达的。
- 摘要禁止具体数值；实验分析正文禁止复述图表数值。正文尽量少列数字，必要数值交给图表或数学表达。
- 默认初投稿完整 PDF 不超过 10 页，包括参考文献。

## 正文五部分与创新点分工

正文默认采用 Introduction -> Problem Definition and Analysis -> Methodology -> Results and Discussions -> Conclusion 五段式。

先在工作草稿中建立“问题障碍 -> 方法机制 -> 实验检验 -> 贡献结论”的对应关系，无需将这份工作表放入论文。引言提出的问题应在后文有回应，方法重点应有证据支持，结果解释应回到问题与机制。

论文不同部分对于论文核心创新点的写法侧重区别：摘要给出完整的微型论述；引言末部方案概述承接研究缺口并侧重于解释机制协同；贡献列表明确其原创研究增量；结论凝练经过实验验证的价值。禁止四处复制同一组句子。

## 肯定式表达

重点审查 instead、instead of、rather than、not、but not、without、unlike、as opposed to、not only ... but also。对于修辞性“不是 A，而是 B”，删除否定部分 A，直接陈述 B。本 skill 和后续子 skill 中提到禁用否定语气时，上述表达也一并绝对禁用。确实无法正面等义表达或判断反例性质时，允许停下来请作者确认。

| 原表达                                                                                                                    | 肯定式方向                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Instead of processing each source separately, the method jointly models their interactions.                               | The method jointly models interactions among the sources.                                          |
| The improvement is not merely empirical but reflects the value of complementary information.                              | The improvement reflects the value of complementary information.                                   |
| The discussion explains how the mechanism addresses the identified challenge rather than repeating the numerical results. | The discussion explains how the mechanism addresses the identified challenge.                      |
| The experiment is not a comparison of unrelated architectures but a controlled evaluation of the proposed component.      | The experiment is a controlled evaluation of the proposed component.                               |
| Without changing the input information, the comparison isolates the effect of the interaction mechanism.                  | With identical input information, the comparison isolates the effect of the interaction mechanism. |
| The evaluation varies the operating conditions but not the underlying system.                                             | The evaluation varies the operating conditions within the same underlying system.                  |
| The framework not only integrates heterogeneous observations but also models their interactions.                          | The framework integrates heterogeneous observations and models their interactions.                 |
| The analysis focuses on the mechanism's contribution as opposed to routine implementation details.                        | The analysis focuses on the mechanism's contribution.                                              |

必要边界也尽量从正面写，例如 `Under the stated assumptions, ...`。对相关工作的问题分析应尽量归类简化描述，评价语句务必直接切中其具体 research gap，服务于本文动机。

## 句间逻辑与术语

- 段落内尽量采用总-分结构，并做好段间衔接，尽量使用恰当的衔接词。
- 每段推进一个中心判断，可按“主题 -> 依据或机制 -> 推论 -> 衔接”组织。
- 先判断句间是因果、递进、并列、对照、条件还是归纳，再决定使用 therefore、furthermore、meanwhile、however、under、taken together 等连接方式，还是不加连接词。
- 核心术语、模块名称、缩写、符号与图题全篇一致；不为词汇多样性改名。
- 如篇幅超支，可优先删去空泛强调和模板化套话，让每句承担信息或推理功能。

## 图表规范

- **图应有自明性，所有符号都必须自明或在 problem definition 与 methodology 里出现明确定义。严禁在图表中添加任何形式的灰体小号字的解释说明短语或句子。**
- 图表无需添加标题，在 LaTeX 的 caption 中体现即可。
- 对于表意不十分明确的图，建议添加图例。
- **图表标题最好为简洁的短语或短句，硬限制为：不得超过 15 词，且在渲染得到的 PDF 中，所有图表标题必须为一行。**
- 所有图表都必须在正文中得到引用。
- 严禁同时使用图表描述同一组数据。对于实验组数很多、侧重于趋势的图，建议选用折线图；对于实验组数较少、强调对比的图，建议选用柱状图；对于强调占比的图，建议选用饼图。对于大量密集异构的重要数据，建议采用表格展示。

## 格式规范

在生成或修改的论文正文、图注、表注及表格单元格中，严禁使用 `\textbf{...}`、`\bfseries`、旧式 `\bf` 及 `\fontseries{b}\selectfont`、`\fontseries{bx}\selectfont` 等方式人为加粗文字。不得通过自定义宏、局部字体设置或数学模式绕过此限制。贡献、术语、结论和段落引导语均使用常规字体，通过内容与结构表达重点。

此限制不适用于官方模板或文档类自动生成的字体样式，`\section{...}`、`\subsection{...}`、`\paragraph{...}` 等结构命令不因最终显示为粗体而禁用。保留具有数学语义的 `\mathbf{...}`、`\boldsymbol{...}`、`\bm{...}`，例如向量和矩阵符号，但不得用它们加粗普通文字。

## 语言规范

1. 直接陈述问题、机制、证据与结论。禁止自行假设读者的误解或质疑，再加入对论文核心贡献论证无明确帮助的否定、转折或免责声明回应。
2. 如果一句话的唯一作用是辩解、预防质疑或反复提醒结论边界，而没有增加必要的事实、条件或推理，则将其删除。
3. 严禁在每个判断、来源或建议后重复补充“但这不能说明...”之类的声明。
4. 减少冗余表达，对于同一连续论证中的条件或不确定性，只首次相关处说明，后文直接承接。

自检：

* 删除这句话后，论断是否仍然准确、推理是否仍然完整？若均成立，且表达更直接，则删除。
* 对于条件或不确定性的说明，是否删掉或替换为简单指代后可以自动承接上文，不影响表义？若成立，则删除或替换。

## 发布会原则

1. 只围绕论文创新贡献和实验中能支撑贡献的显著优势组织叙事；
2. 不按“做了什么、试过什么、哪些失败了”的过程写；
3. 严禁对论文核心贡献进行任何自我削弱表达，如“遗憾的是”“仅”“仍明显落后”“效果有限”，不替审稿人总结弱点；
4. 在不回避该领域标准指标的前提下，尽量不采用对支持论文核心贡献不利的指标，而是寻求有利于支撑论文创新贡献且同样符合学术规范的评价维度或比较口径；
5. 对于不占优的结果，禁止对论文核心贡献进行任何直接否定或弱化，而是结合研究目标、适用条件及合理权衡给出有依据的解释；
6. 优势必须主动说清楚，别指望审稿人自己从表格里发现；
7. 每个实验必须有论证职责，没有就删；
8. 结论只强化记忆点，不突然自我否定。

## 修改与验收流程

该流程中，对于词汇拼写、语法、格式、标点等不涉及实质性内容的问题，允许直接修改。对于实质性内容修改，除非用户特别要求免除，都要写修改详案。对于非章节收尾、非 abstract、conclusion 的修改详案，该详案至少包括 12 个部分：上文原文、上文中文翻译、该段与上文的衔接关系、下文原文、下文中文翻译、该段与下文的衔接关系、原文、原文中文翻译、改文、改文中文翻译、修改依据、修改要点总结。在用户同意后，落盘此修改，并进入下一处。

新增段落没有原文、章节首末没有上下文时，将对应部分改为简要文字说明。

校对修改流程：

1. 期刊主题范围核查，若存在明确 `out of scope` 风险，立刻通过当前环境提供的用户确认弹窗提醒用户，说明对应的官方范围条目、论文现状，以及风险属于表述不明确还是研究实质不匹配。无弹窗工具时，以明确的对话提醒替代，并等待确认。
2. 文章结构与本 skill 的标准五段式的一致性核查，不一致则弹窗询问用户是否大修/重写；
3. 每个子章节的内部结构与相应子 skill 的规定的一致性核查，不一致则弹窗询问用户是否大修/重写；
4. 核查全文中明显的拼写、语法与格式错误；
5. 优化全文用词、语法、句子与段落结构，以及句间衔接；
6. 论文内部存在的明显的错配与自相矛盾之处的修订；
7. 论文内部表意不当、结论显著过强部分的审查与修订；
8. 论文前后明显表意冗余之处的压缩，一般来讲只留一处关键性详述，或各部分分别侧重不同角度；
9. 其他深入的细节修改；
10. 篇幅与投稿要求的对齐处理。

修改要点：

1. 读取现有主稿及对应资料，确认编辑范围、编译入口、目标版本和用户要求。先写修改详案，用户明确要求修改时，再落盘；
2. 优先整体检查贡献链和章节职责，再用相关子 skill 修改句段。事实缺失时列出待确认项；
3. 仅改授权范围，保存已有用户修改；
4. 排版修改后编译，检查完整 PDF 页数、引用、编号、溢出及关键页面渲染；
5. 超过指定页数时，先报告并提出低损失压缩方案：重复论述 -> 修辞性否定 -> 非核心工程细节 -> 图表冗余和留白。严禁擅自改模板页边距、缩字体或删除必要机制说明。
6. **若现存图表有明显的伪造痕迹，立刻弹窗提醒用户学术风险。**
7. **若现存图表外观高度疑似 AI 生成，立刻弹窗提醒用户这点对论文发表的可能不利影响，并提出重绘方案。**
8. 图表一定要尽量裁切白边，且尽量使用宽高比 ≥ 4:3 的图，以减少篇幅占用，美化排版。若存在宽 < 高的图，向用户提出修改优化建议，如旋转、坐标轴仿射变换、图内元素的位置与结构调整等。

## 总体验收要求

- 文章切合目标期刊的部分主题范围，并在标题、摘要和关键词中均包含至少一个在目标期刊范围的主题与至少一个明确的目标期刊核心研究对象名词。
- 核心贡献都有问题动机、方法落点和证据。
- 各创新点互相照应且各有侧重。
- 文章结构与该 skill 及其子 skill 的要求，或用户指定的要求一致。
- 摘要无具体数值，实验分析没有复述图表数字。
- 实验 setup 足够精简，没有无端引入多随机种子或全面工程复现要求。
- 保留真实条件，连接词匹配逻辑。
- 图、式、文、引用一致，完整 PDF 满足篇幅目标。
- 图表不存在明显的 AI 生成痕迹或伪造痕迹；且图表之间、图表与正文之间满足一致性要求。
