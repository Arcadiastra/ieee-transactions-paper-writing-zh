---
name: ieee-transactions-paper-writing-abstract-zh
description: 使用简体中文规划、撰写、修改和审查 IEEE Transactions 学术论文的摘要与 Index Terms。组织问题、挑战、创新机制和定性验证的自包含论述，禁止具体数值，并提炼适合检索的关键词。
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash WebSearch WebFetch Task
metadata:
  language: zh-CN
  trigger: 使用简体中文规划、撰写、修改和审查 IEEE Transactions 形式的学术论文的摘要与 Index Terms。
  target-venue: IEEE Transactions journals
  repository: https://github.com/Arcadiastra/ieee-transactions-paper-writing-zh.git
---
# Abstract

如未读过 [主 skill](../../SKILL.md) 的共同原则，先阅读它。本文件只负责摘要部分。该部分通常是在正文 results and discussions、problem definition、methodology 和 introduction 均完成后，与 conclusion 一同撰写，是对全文的精炼概括。摘要推荐在 150-200 词之间，硬上限为 250 词。

**必须在一个紧凑段落内完成，严禁分段。**

## 所需输入

起草时可按 [模板指南](references/template-guide.md) 使用 LaTeX 结构骨架，并按实际研究内容调整。

已完成的 results and discussions、problem definition、methodology 和 introduction 四章。缺少关键证据时，明确向用户提出。

## 逻辑结构

按照背景 -> 问题现状与重要性 -> 当前场景下面临的关键挑战 -> 传统方法的 research gap -> 为解决该问题，研究提出某创新方案 -> 创新机制及作用简述 -> 各实验结论分别如何支撑了什么结论。各功能可合并，不机械限定句数。背景从具体问题起笔，快速进入本文工作。

## 写作规范

- 必须包含至少一个在目标期刊范围的主题与至少一个明确的目标期刊核心研究对象名词。
- 必须具备完全的自包含性（Self-contained）。读者仅凭摘要就需要判断这篇论文是否值得下载或引用。因此，自身逻辑链必须完整，且能够与正文相对独立。
- 禁止具体数字：性能数值、提升百分比、数据量、算例规模、模块数量、超参数和训练配置均不写；不能把阿拉伯数字换成英文拼写规避规则。
- 必要的固定领域术语不按结果数值处理，例如 three-dimensional；按语义判断，不全局删字符。
- 不写引用、公式、图表索引或工程清单。缩写只在必要时引入，首次给全称，避免摘要变成缩写表。
- 说明最关键的机制如何应对挑战，不把所有组件名串联当作贡献。
- 结果用有依据的定性判断，指出优势出现的条件或维度；尽量不用无证据的 universal、optimal、state-of-the-art。
- 禁止使用一切否定语气，必须从正面简要表述。research gap 也写明传统方案面对什么困境，而非不能处理什么。
- 不突出局限，不自动以未来工作收尾；可以保留影响理解的必要适用条件。
- 严禁出现未定义的生僻缩写、文献引用序号（如 `[1]`）以及正文图表索引（如 `Fig. 3`）。

# Index Terms

核心逻辑在于 **在准确表达论文实质的前提下，兼顾文献检索的召回率与精准度**，并为编辑匹配审稿人提供清晰的主题线索。

## 五词策略

本 skill 默认采用五个关键词或关键词短语，覆盖研究链条。注意与目标期刊主题范围的一致性：**务必至少包含一个明确在目标期刊 scope 内的关键词**：

1. 研究对象或应用场景（1 个）：明确本研究所属的系统。例：`Distribution networks`（配电网）、`Microgrids`（微电网）、`Power transmission systems`（输电系统）等。
2. 核心研究任务（1 个）：直接说明论文解决什么问题。例如 `State estimation`（状态估计）、`Optimal power flow`（最优潮流）、`Network reconfiguration`（网络重构）等。
3. 关键数据、量测条件或问题特征（1 个）：优先选择对论文贡献有实质作用的特征，例如 `Pseudo-measurements`（伪量测）、`Smart meters`（智能电表）、`Advanced metering infrastructure`（高级量测基础设施）与 `Phasor measurement units`（同步相量测量单元）等。
4. 核心方法机制与理论基础（2 个）：优先各选一个互补术语，例如 `Attention mechanisms`（注意力机制）、`Bayesian decision theory`（贝叶斯决策理论）、`Graph theory`（图论）、`Deep reinforcement learning`（深度强化学习）、`Mixed-integer linear programming`（混合整数线性规划）等。

## 三大核心提炼原则

**原则一：尽量与 Title 形成“正交互补”，补充同义词、上位词或标题未涵盖的技术特征。**

例：若 Title 包含 *Deep Learning Approaches for Feeder Parameter Estimation*，Index Terms 可不必再写 *Deep learning*，而改为补充正文实际采用的具体模型、学习范式或其他技术特征，如：*Convolutional neural networks*、*Supervised learning*。

特别地，核心专业术语若与标题重复，可以原样保留作为关键词。

**原则二：对齐官方受控词表（Controlled Vocabulary）。**

IEEE 有官方维护的分类词库。优先选用官方词典中的规范词，有助于术语一致性与检索匹配：

* **IEEE Taxonomy / IEEE Thesaurus：** 官方收录的标准化技术术语（如用 *Phasor measurement units* 而非口语化的 *Synchrophasor devices*）。
* 禁止使用内部或自创代号，而应写其本质技术属性。

**原则三：颗粒度精准适中。** 例：

* **过宽：** *Algorithm*、*Model*、*Optimization*、*Simulation*、*Power*。
* **过窄：** *3-layer residual graph attention with leaky ReLU*。
* **恰当：** *Graph attention networks*、*Non-convex optimization*、*Measurement uncertainty*。

# 检查与交付

派出单独的审查子智能体，首先仅阅读论文标题、摘要和关键词并进行目标期刊主题范围检索，并返回：

1. 标题、摘要和关键词中是否均包含至少一个在目标期刊范围的主题与至少一个明确的目标期刊核心研究对象名词，以及文章被以 `out of scope` 直接拒稿的可能性。
2. 正文内容的推测和创新性、论文质量的预估：该文段本身是否拥有足够的自明性，是否存在无任何上下文的疑似论文内部代号；

若无法派出子智能体，则由主智能体替代该部分审查。

其次，阅读检查每个方法和结果判断能否在正文找到依据，是否含具体数值，是否保留结构要求的完整逻辑链，句间衔接词使用是否流畅、是否与句间逻辑关系一致，以及是否满足已知目标期刊字数要求。

修订时，先写修改详案，用户批准后再落盘。摘要的修改详案必须包括整个摘要的原文及其翻译、改文及其翻译、修改理由和对应的正文内容六部分。

篇幅必须在硬限制以内。
