# IEEE Transactions 中文论文写作技能

IEEE Transactions 论文写作 Skill：面向 Codex、 Claude Code 等 Agents 的学术论文写作与审查，由一个主 skill 和七个章节子 skill 组成。

即使这是一个 Agent 写作 skill，仍建议作者基于其思想，以简体中文**亲手完成底稿**。本 skill 更加提倡 AI 辅助规划、整理、翻译、修改和打磨，而非全权代写。

**写作即思考，底稿即逻辑。**

> *Although using AI to polish a manuscript is fine, the writing will become irrelevant when too much AI is applied.*

## 适用范围

- 面向简体中文用户，指导智能体完成 IEEE Transactions 系列期刊论文的写作与审查。
- 支持从零搭建论文框架、章节写作、已有稿件修改与审查、参考文献核验和篇幅控制。

## 安装

### 方法一：通过 npx 一键安装（推荐）

```bash
npx skills add https://github.com/Arcadiastra/ieee-transactions-writing-zh.git
```

需要已安装 Node.js 和 npm，运行后按提示选择目标工具和安装范围。

### 方法二：通过 Git 克隆

```bash
# 克隆到 Codex 的 skills 目录
git clone https://github.com/Arcadiastra/ieee-transactions-writing-zh.git ~/.agents/skills/ieee-transactions-writing-zh

# 克隆到 Claude Code 的 skills 目录
git clone https://github.com/Arcadiastra/ieee-transactions-writing-zh.git ~/.claude/skills/ieee-transactions-writing-zh
```

### 方法三：手动安装

1. 下载本项目的 ZIP 文件或克隆到本地。
2. 将解压后的文件夹重命名为 `ieee-transactions-writing-zh`，复制到对应工具的 skills 目录：

| 工具        | macOS / Linux         | Windows                           |
| ----------- | --------------------- | --------------------------------- |
| Codex       | `~/.agents/skills/` | `%USERPROFILE%\.agents\skills\` |
| Claude Code | `~/.claude/skills/` | `%USERPROFILE%\.claude\skills\` |

### 验证安装

重启对应工具或重新加载 skills 后，在对话中输入：

**Codex：**

```text
$ieee-transactions-writing-zh
```

**Claude Code：**

```text
/ieee-transactions-writing-zh
```

如果安装成功，该技能将被激活。

## 结构与入口

```text
ieee-transactions-writing-zh/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/openai.yaml
├── assets/templates/
├── references/template-guide.md
└── subskills/
    ├── abstract/SKILL.md
    ├── introduction/SKILL.md
    ├── problem-definition/SKILL.md
    ├── methodology/SKILL.md
    ├── results-and-discussions/SKILL.md
    ├── conclusion/SKILL.md
    └── citation/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── assets/
        ├── scripts/
        ├── tests/
        └── references/
```

| 入口                                                                 | 职责                                   |
| -------------------------------------------------------------------- | -------------------------------------- |
| [主 skill](SKILL.md)                                                  | 总体写作流程、论证原则、章节分工与验收 |
| [Abstract](subskills/abstract/SKILL.md)                               | 摘要与 Index Terms                     |
| [Introduction](subskills/introduction/SKILL.md)                       | 动机、相关工作、研究缺口与贡献         |
| [Problem Definition](subskills/problem-definition/SKILL.md)           | 问题形式化、符号与困难分析             |
| [Methodology](subskills/methodology/SKILL.md)                         | 创新机制、理论解释与方法图             |
| [Results and Discussions](subskills/results-and-discussions/SKILL.md) | 实验设置、图表与定性机制分析           |
| [Conclusion](subskills/conclusion/SKILL.md)                           | 研究总结、机制价值与未来工作           |
| [Citation](subskills/citation/SKILL.md)                               | 引用支持关系、来源核验与参考文献格式   |

## 使用

将整个套件目录放在宿主支持的 skill 目录中，主 skill 可按章节导航加载子 skill。

在支持 skill 名称调用的环境中，可使用：

```text
$ieee-transactions-writing-zh，先审查论文结构与贡献链，给出修改详案，暂不改正文。

$ieee-transactions-writing-abstract-zh，按正文内容修改摘要，并提供原文、改文及修改理由。

$ieee-transactions-writing-results-and-discussions-zh，检查结果分析是否回应问题与机制，避免复述图表数字。
```

若宿主没有发现子 skill，指定对应文件路径，或通过主 skill 请求处理该章节。

主 skill 和七个子 skill 均提供 `agents/openai.yaml`，包含显示名称、简短说明与默认调用提示。

## 引用核验脚本

已提供三组只读检查入口：离线 BibTeX/AUX 检查、Crossref/DataCite 出版元数据核验、Crossref 出版更新通知检查。报告保留 citation key、输入哈希和来源证据。

联网元数据另支持 **Bibverify 0.5.0 官方 CLI 可选后端**。使用独立环境与 `--dry-run --json`；内置元数据脚本保留为备用。安装与调用见 [Bibverify 接入说明](subskills/citation/references/bibverify-integration.md)。

- [安装、命令、退出码与状态说明](subskills/citation/references/tools.md)
- [原文引用支持关系的人工核查流程](subskills/citation/references/integrity-review.md)
- [公开工具比较、来源与模板取舍](subskills/citation/references/source-comparison.md)

## 元数据与工具

每个 `SKILL.md` 均包含 `name`、`description`、`license`、`allowed-tools` 和 `metadata`。

- `metadata.trigger`：使用简体中文处理 IEEE Transactions 形式学术论文的触发场景；子 skill 进一步限定到对应章节。
- `metadata.target-venue`：`IEEE Transactions journals`。
- `metadata.language`：`zh-CN`。
- `metadata.repository`：本 skill 的 Github 仓库地址。
- `allowed-tools`：列出文件读取与编辑、文件检索、命令执行和网页检索等工具名称；主 skill 与摘要子 skill 另列 `Task` 以支持独立审查。

`allowed-tools` 中采用常见的工具名称约定。不同宿主可能使用不同名称或不支持该字段，实际可用性与权限由宿主决定；该声明不会自动授予权限。在要求 PowerShell 的环境中，命令必须使用 `pwsh`，遵守环境既有的错误处理与 UTF-8 编码要求。`metadata.trigger` 是描述性元数据，不保证宿主将它作为专用自动触发机制解析。

## 写作约定

摘要不列具体数值，结果讨论不复述图表数据；正文围绕问题、机制与证据组织。默认以完整稿件 10 页为篇幅预算，并按目标期刊与用户要求调整。具体章节的字数、页数、文献预算及审批流程见相应 SKILL.md。

## 许可证

本项目采用 [MIT License](LICENSE)。
