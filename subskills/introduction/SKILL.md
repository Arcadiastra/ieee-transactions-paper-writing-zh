---
name: ieee-transactions-paper-writing-introduction-zh
description: 使用简体中文规划、撰写、修改和审查 IEEE Transactions 学术论文的引言。组织场景需求、关键挑战、相关工作、研究缺口、方案概述与贡献列表，建立通向问题分析和方法创新的论证。
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash WebSearch WebFetch
metadata:
  language: zh-CN
  trigger: 使用简体中文规划、撰写、修改和审查 IEEE Transactions 形式的学术论文的引言。
  target-venue: IEEE Transactions journals
  repository: https://github.com/Arcadiastra/ieee-transactions-paper-writing-zh.git
---
# Introduction

先读 [主 skill](../../SKILL.md)。涉及文献事实时按 [citation](../citation/SKILL.md) 核查。若为初稿，本章推荐页数为 0.9-1.3 页，硬上限为 2 页。本章节主体应当在 results and discussions、problem definition 与 methodology 三章完成后撰写，而 contributions 部分应当是全文首先组织的部分，详见主 skill 的写作流程。

**本章严禁分小节，严禁出现任何具体的实验设计方案或相关具体数值。一般来讲无需撰写公式。**

## 目标与输入

起草时可按 [模板指南](references/template-guide.md) 使用 LaTeX 结构骨架，并按实际研究内容调整。

必须严格遵照主 skill 的第一性原理，本章节的一切论述皆服务于凸显 problem definition 与 methodology 两章以及提前拟定的 contributions 部分所代表的论文主要工作的创新性与实用价值。

以现实场景的缺口和需求、现有研究的 research gap 作为 motivation，凸显本文原创增量的重要性。除 contributions 部分外，本章节基于 results and discussions、problem definition 与 methodology 三章撰写。

## 逻辑结构

1. 整个课题的定义、研究课题大领域本身的重要性概述，可单独成段。
2. background——problem definition 对应的目标真实场景中，存在的具体实际需求与挑战，说明为何需要解决该问题。注意：此处必须将研究面向的具体实际场景定义清楚。
3. 该场景下，课题任务的关键困难，依次列举困难产生的机制及其后果。
4. 现有研究综述：采用总-分-总结构，先将所有文献按研究路线分组，讲述为了解决这些困难，现有研究分为哪些路线；然后整体交代各组的基本思路，以及在本文面向的场景下，面对上一步列举的部分关键困难，该路线存在什么固有缺陷及其原因（research gap）。最后再总写这些研究都未能做到在本文面向的那个特定场景下，同时解决那些关键困难。
5. 方案概述：为了解决该场景下的那些困难，本文提出了怎样的方法，通过怎样的（粗略、定性描述的）机制解决了困难，并引出本文贡献（To summarize, the contributions of this paper include:）。
6. 贡献列表，这部分最先拟好，见主 skill。
7. 必要的章节导航。The remainder of this paper is organized as follows. 然后每一章的功能用几个词概括。

现有研究综述部分，严禁写成逐篇列举文献具体方案和评价的流水账。

## 写作规范

- 严禁出现任何实验数字。
- 方案概述部分粗略、定性描述机制，重点描述放在方法章节，拒绝冗余。
- 每项贡献必须写清“提出或建立的内容 & 关键新意 + 对问题的价值”，并保持平行句法和相近粒度。
- 理论分析、建模与方法机制可分别成项，前提是各有独立增量，且在后文撰写对应内容。
- 常规组件、实现工作量和实验数量等工程设计本身不是创新。实验贡献应强调建立了什么创新性认识或验证了什么先进能力。
- 未明确时，不用 first、首次、全面解决等过强的词描述贡献。

## 连接与边界

相关工作之间按问题和机制递进；确有对照才用 however，多个瓶颈汇聚到设计需求时再用 therefore 或 these challenges motivate。

对先前研究的批评须明确、局部、与研究条件相关，引用尽量贴近所支持的论断。严禁以任何形式再次否定这些批评。

## 验收

- 每个重要缺口和挑战均被第二章深化、第三章回应、第四章检验。
- 符合本 skill 的基本写作逻辑结构。
- 各条贡献可以逐项在后文定位。
- 方案概述明确区别于摘要和贡献清单。
- 删去泛背景和非必要工程数字。
- 篇幅在硬限制以内。
