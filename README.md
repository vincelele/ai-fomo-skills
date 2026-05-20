# AI FOMO Skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#status)

为了对抗 AI FOMO，我专门做了一个 Skill。

它不是 AI 日报，也不是 prompt 合集，而是帮你从 AI 信息流里筛出真正值得看的内容，并沉淀成自己的知识库。

这是一套给 **AI 创业者、产品经理、独立开发者** 使用的 Agent Skill。它不是让 Agent 帮你多看一点信息，而是让 Agent 帮你少浪费一点注意力。

## 我真正缺的不是信息，而是判断

AI 信息太多了。

不看，怕错过真正优秀的分享、认知和机会；看了，又经常发现内容很浅、质量不高，浪费时间。每天各种 AI 博文、YouTube、小宇宙、公众号、GitHub Trending、产品更新的信息都太多了，人不可能每条都认真看。

所以我更需要的是：从这些渠道里筛选出我最关心、最值得看的内容。

AI FOMO Skills 要回答的不是“这篇内容讲了什么”，而是：

```text
这条信息值得我花时间吗？
为什么和我有关？
应该丢掉、先问我，还是沉淀成长期知识？
```

## 什么是 AI 超级对齐

这里说的 AI 超级对齐，不是宏大的 AI 安全概念，而是一个很具体的个人工作流：

```text
让 Agent 按照你的背景、目标、判断标准和长期反馈来处理信息。
```

普通总结器会问：“这篇文章说了什么？”

AI FOMO Skills 会问：

- 这件事是否影响你的产品、创业方向或技术判断？
- 这条信息是否来自你信任的来源？
- 它是新信号，还是重复噪音？
- 它应该进入长期知识库，还是只适合快速看一眼？
- 如果信息不够，应该先问你什么问题？

## 它主要做四件事

| 能力 | 它解决什么问题 |
| --- | --- |
| 总结 | 快速看懂一条内容到底在讲什么，不用先完整读完。 |
| 筛选 | 结合你的关注方向，判断它值不值得花时间看。 |
| 解释 | 告诉你它为什么重要，以及和你当前工作有什么关系。 |
| 沉淀 | 把有价值内容变成后续 Agent 还能复用的个人知识库。 |

核心不是“看更多”，而是更快判断哪些值得看，哪些可以先跳过。

## Status

Alpha / developer preview.

可以开始试用，但还不是面向所有人的稳定产品。建议先用少量公开资料跑通流程，再接入账号型数据源。

## 适合谁

- AI 创业者：需要快速判断哪些变化会影响机会、产品和市场。
- 产品经理：需要跟踪 AI 产品、模型能力、交互范式和用户行为变化。
- 独立开发者：需要发现值得尝试的新工具、开源项目和产品机会。
- 高频使用 AI Agent 的人：已经在用 Codex、Claude Code、OpenClaw、Cursor 等支持 skill 或规则文件的工具。
- 被 AI 信息流淹没的人：不想错过重要信息，也不想把时间浪费在低质量内容上。

## 不适合谁

- 你只是想看一份通用 AI 日报。
- 你不想提供任何个人背景，也不希望 Agent 根据你本人做判断。
- 你想自动抓取并公开分发别人的播客、评论或私有内容。
- 你需要一个开箱即用的 SaaS 产品，而不是本地 skill 工作流。

## 三个 Skill

| 你想做什么 | 使用哪个 skill | 它会做什么 |
| --- | --- | --- |
| 让 AI 先认识你 | [`ai-fomo-init`](ai-fomo-init/SKILL.md) | 先请你提供类似简历、个人介绍、项目经历或当前目标的材料，再通过问答补齐个人判断标准。 |
| 把信息接进来 | [`ai-fomo-sources`](ai-fomo-sources/SKILL.md) | 导入官网、RSS、GitHub、X、小宇宙、评论、转录或你手动贴的内容，先保存成可追溯 raw snapshot。 |
| 判断和沉淀 | [`ai-fomo`](ai-fomo/SKILL.md) | 把资料分成 `write now`、`ask first`、`skip`，再写入 wiki、signals 或 digests。 |

## 典型流程

### 1. 每天先让它帮你筛一遍

以播客为例：你可能关注了很多 AI 相关栏目，但根本没有时间每期都听。`ai-fomo-sources` 可以先把 episode、标题、简介、评论和转录接进来，`ai-fomo` 再结合你的个人兴趣，判断哪些值得看，哪些可以忽略，哪些只是第二优先级。

这一步最重要的不是“总结”，而是先决定要不要看。

### 2. 遇到感兴趣的，再让它深挖

如果某一期、某篇文章或某个 GitHub repo 确实值得看，Agent 会继续做系统总结，提炼里面哪些判断值得学习，哪些 know-how 可以迁移到你的产品、创业或开发工作里。

它不是简单复述内容，而是提炼：哪些判断值得留下，哪些可以复用。

### 3. 用久了，就变成你的 AI 知识库

长期协作之后，它会持续记录你看过什么、判断过什么、关心什么，以及哪些知识以后还可能复用。

这不是一个收藏夹，而是一个会被 Agent 反复读取和更新的个人 AI 知识库。

## 不懂代码怎么安装

最推荐的方式是：直接把下面这段话复制给你的 Agent。

```text
帮我安装这个 AI FOMO skill 套件：
https://github.com/vincelele/ai-fomo-skills

请安装里面的 ai-fomo-init、ai-fomo-sources、ai-fomo 这三个 skill。
如果需要选择安装目录，请安装到当前 Agent 默认的 skills 目录。
```

如果你的 Agent 支持逐个安装，也可以复制这三条：

```text
帮我安装这个 skill：https://github.com/vincelele/ai-fomo-skills/tree/main/ai-fomo-init
帮我安装这个 skill：https://github.com/vincelele/ai-fomo-skills/tree/main/ai-fomo-sources
帮我安装这个 skill：https://github.com/vincelele/ai-fomo-skills/tree/main/ai-fomo
```

安装完成后，重启 Agent，让它重新加载 skill。

## 第一次怎么用

### 1. 先让 AI 认识你

直接对 Agent 说：

```text
Use $ai-fomo-init to initialize a local AI FOMO workspace.

我不懂代码。请一步步带我完成：
1. 先让我提供一份类似简历、个人介绍、项目经历或当前目标的材料；
2. 再问我几个必要问题，补齐你判断信息价值所需的背景；
3. 最后告诉我你准备创建哪些本地文件，确认后再写入。
```

### 2. 再导入第一条资料

你可以直接贴链接或内容：

```text
Use $ai-fomo-sources to import this source into my AI FOMO workspace.

链接是：PASTE_URL_HERE

请先 dry-run，展示你准备保存的 raw snapshot，不要直接写入。
```

如果没有链接，只有一段文字，也可以说：

```text
Use $ai-fomo-sources.

我现在直接贴一段内容，请帮我生成 manual raw snapshot，并保留来源、日期和我为什么保存它。
```

### 3. 最后让 AI 做判断

```text
Use $ai-fomo to review my latest raw inbox.

请不要只总结。请把每条资料分成：
- write now：值得立刻沉淀
- ask first：需要先问我一个问题
- skip：不值得进入长期知识库

每条都说明为什么和我有关，或为什么不值得看。
```

## 常见使用场景

| 你可以这样说 | 会发生什么 |
| --- | --- |
| “帮我初始化 AI FOMO 工作区，先问我背景。” | `ai-fomo-init` 会走个人背景和 QA 流程。 |
| “把这个 OpenAI 更新导入，然后判断是否值得沉淀。” | 先保存 raw snapshot，再由 `ai-fomo` 判断。 |
| “把这个 GitHub repo 作为来源导入。” | 保存 repo metadata 和 README 线索。 |
| “帮我看看最近 GitHub Trending 里有没有值得关注的 AI 项目。” | 抓取 trending snapshot，再筛选。 |
| “帮我接入小宇宙订阅，先不要写入，只 dry-run。” | 走小宇宙账号接入预检流程。 |
| “抓这期小宇宙的评论和转录，之后判断是否值得写入 wiki。” | 评论、转录和 episode 信息会分开保存，再进入判断。 |

## 当前支持的数据源

| 数据源 | 难度 | 是否需要账号或 token | 说明 |
| --- | --- | --- | --- |
| 直接贴内容或导出文件 | 最简单 | 不需要 | 没有 connector 时也能先保存 manual snapshot。 |
| 公司官网、博客、changelog | 简单 | 不需要 | 适合 OpenAI、Anthropic、Google、Meta 等官方页面。 |
| RSS / Atom | 简单 | 不需要 | 适合博客、更新日志、newsletter feed。 |
| GitHub repo | 简单 | 不需要 | 导入 repo metadata 和 README。 |
| GitHub Trending | 简单 | 不需要 | 抓取某个时间点的 trending snapshot。 |
| YouTube / 公众号 / 其他内容 | 简单 | 看来源而定 | 先通过链接、字幕、转录、导出文件或手动粘贴保存 manual snapshot。 |
| X 用户时间线 | 中等 | 需要 `X_BEARER_TOKEN` | 使用 X API v2。token 不要提交到 GitHub。 |
| 小宇宙公开 episode | 中等 | 通常不需要 | 导入公开 episode metadata 和 show notes。 |
| 小宇宙订阅 inbox | 高 | 需要登录和本地 bridge | 可批量导入已订阅节目。 |
| 小宇宙评论 | 高 | 需要登录和本地 bridge | 可抓主评论，也可选择抓回复。 |
| 音频转录 | 高 | 需要 `DASHSCOPE_API_KEY` | 使用 DashScope Fun-ASR，可能较慢或产生费用。 |

原则：能公开访问的来源先接，账号型来源后接；任何会写入本地文件、消耗 API 费用或涉及账号风险的操作，都应该先 dry-run。

## 小宇宙能力

小宇宙是这套 skill 的核心高阶能力之一，因为很多高质量 AI 讨论发生在播客里，而不是文章里。

当前已经支持：

- 自动安装本地小宇宙 bridge。
- 通过短信验证码登录。
- 批量导入订阅 inbox 里的 episode。
- 抓取 episode 评论。
- 可选抓取评论回复。
- 对音频做转录。
- 将 episode、comments、transcript 分开保存成 raw snapshot。
- 再交给 `ai-fomo` 判断：哪些值得看、哪些值得沉淀、哪些可以跳过。

你可以先这样让 Agent 带你走：

```text
Use $ai-fomo-sources to set up Xiaoyuzhou account import.

我不懂代码。请先解释你需要什么、会保存什么、有哪些账号和数据风险。
先检查环境和 dry-run，不要直接登录、不要直接写入、不要转录全部音频。
```

注意：小宇宙账号导入涉及登录态、订阅内容、评论和音频转录。请只处理你有权访问和处理的内容，不要把转录、评论或账号数据公开上传。

更详细的说明在 [`ai-fomo-sources/references/xiaoyuzhou-account.md`](ai-fomo-sources/references/xiaoyuzhou-account.md)。

## 安全边界

请公开这个 repo 里的 skill、模板、示例和脚本。

不要公开：

- `raw/inbox/` 里的真实资料
- `raw/state/` 状态文件
- 播客转录、评论、账号订阅数据
- `.env*`、`.secrets/`、cookies、tokens、API keys、登录 session
- 真实的 `self-context/`、`wiki/`、`signals/`、`digests/`
- `.tools/` 里的本地 bridge checkout

更完整的边界说明见：

- [`docs/public-sharing-policy.md`](docs/public-sharing-policy.md)
- [`docs/public-skill-boundaries.md`](docs/public-skill-boundaries.md)

## 给懂命令行的人

Codex skill installer:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo vincelele/ai-fomo-skills \
  --path ai-fomo-init ai-fomo-sources ai-fomo
```

手动安装：

```bash
git clone https://github.com/vincelele/ai-fomo-skills.git
cd ai-fomo-skills
cp -R ai-fomo-init ai-fomo-sources ai-fomo ~/.codex/skills/
```

导入公开页面，先 dry-run：

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/import_source.py \
  --workspace /path/to/workspace \
  --dry-run \
  official-page \
  --url https://example.com/changelog
```

小宇宙 bridge 预检：

```bash
python ~/.codex/skills/ai-fomo-sources/scripts/xiaoyuzhou_account.py \
  --workspace /path/to/workspace \
  install-bridge \
  --dry-run
```

## 当前缺口

- scheduled collection 还没做。只有当某个 source 被证明长期有价值后，才建议自动化。
- 完整小宇宙订阅列表导出还没做。
- connector 目前偏轻量，有些网站后续需要单独适配。
- 核心判断质量取决于你的 `self-context` 和持续反馈。

## 项目结构

```text
.
|-- ai-fomo-init/       # 初始化和个人对齐层
|-- ai-fomo-sources/    # 数据源导入、connector、模板
|-- ai-fomo/            # 判断、归档、signal、digest
|-- docs/               # 公开边界和分享策略
|-- LICENSE
`-- README.md
```

## Contributing

欢迎贡献：

- 新的数据源导入器
- 更安全的 dry-run 和校验流程
- 更适合非程序员的新手引导
- starter workspace 模板
- 使用公开或合成内容的示例

请不要贡献真实私人 workspace、账号导出、评论、转录、cookies、tokens 或个人画像。

## License

MIT. See [`LICENSE`](LICENSE).
