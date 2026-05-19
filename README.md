# AI FOMO Skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#status)

让 AI 先理解你，再帮你筛选、判断和沉淀 AI 信息。

如果你每天看到很多 AI 新闻、产品更新、论文、播客、X 讨论、GitHub 项目，但不知道哪些真的和你有关，这套 skill 的目标就是让 Agent 回答一个问题：

```text
这条信息值得我花时间吗？为什么和我有关？应该丢掉、先问我，还是沉淀成长期知识？
```

这不是一个“AI 新闻总结器”。它更像是给 Agent 装上的个人判断系统：先理解你的背景、目标、偏好和反馈，再处理外部信息。

## Status

Alpha / developer preview.

可以开始试用，但还不是面向所有人的稳定产品。建议先用少量公开资料跑通流程，再接入账号型数据源。

## 适合谁

- 你不是程序员，但已经在用 Codex、Claude Code、OpenClaw、Cursor 这类 AI Agent。
- 你经常被 AI 信息流淹没，不想每条都看。
- 你希望 AI 不只是总结，而是能判断“这和我有什么关系”。
- 你想把有价值的信息沉淀成自己的本地知识库、signal 和 digest。
- 你接受一个基本原则：私人资料、账号数据、评论、转录和个人画像都应该留在本地，不要传到公开 GitHub 仓库。

## 不适合谁

- 你只是想看一份通用 AI 日报。
- 你不想提供任何个人背景，也不希望 Agent 根据你本人做判断。
- 你想自动抓取并公开分发别人的播客、评论或私有内容。
- 你需要一个开箱即用的 SaaS 产品，而不是本地 skill 工作流。

## 三个 Skill

| 你想做什么 | 使用哪个 skill | 它会做什么 |
| --- | --- | --- |
| 让 AI 先认识你 | [`ai-fomo-init`](ai-fomo-init/SKILL.md) | 先请你提供类似简历/项目/目标的背景，再通过问答补齐个人判断标准。 |
| 把信息接进来 | [`ai-fomo-sources`](ai-fomo-sources/SKILL.md) | 导入官网、RSS、GitHub、X、小宇宙、评论、转录或你手动贴的内容，先保存成可追溯 raw snapshot。 |
| 判断和沉淀 | [`ai-fomo`](ai-fomo/SKILL.md) | 把资料分成 `write now`、`ask first`、`skip`，再写入 wiki、signals 或 digests。 |

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
| RSS / Atom | 简单 | 不需要 | 适合博客、更新日志、 newsletter feed。 |
| GitHub repo | 简单 | 不需要 | 导入 repo metadata 和 README。 |
| GitHub Trending | 简单 | 不需要 | 抓取某个时间点的 trending snapshot。 |
| X 用户时间线 | 中等 | 需要 `X_BEARER_TOKEN` | 使用 X API v2。token 不要提交到 GitHub。 |
| 小宇宙公开 episode | 中等 | 通常不需要 | 导入公开 episode metadata 和 show notes。 |
| 小宇宙订阅 inbox | 高 | 需要登录和本地 bridge | 可批量导入已订阅节目。 |
| 小宇宙评论 | 高 | 需要登录和本地 bridge | 可抓主评论，也可选择抓回复。 |
| 音频转录 | 高 | 需要 `DASHSCOPE_API_KEY` | 使用 DashScope Fun-ASR，可能较慢或产生费用。 |

原则：能公开访问的来源先接，账号型来源后接；任何会写入本地文件、消耗 API 费用或涉及账号风险的操作，都应该先 dry-run。

## 小宇宙怎么接

小宇宙是高级能力，因为它可能涉及账号登录、订阅列表、评论和音频转录。

你可以先这样让 Agent 带你走：

```text
Use $ai-fomo-sources to set up Xiaoyuzhou account import.

我不懂代码。请先解释你需要什么、会保存什么、有哪些账号和数据风险。
先检查环境和 dry-run，不要直接登录、不要直接写入、不要转录全部音频。
```

接入后可以做这些事：

- 批量导入订阅 inbox 里的 episode。
- 抓某期 episode 的评论。
- 抓评论回复。
- 对音频做转录。
- 把 episode、评论、转录分别保存成 raw snapshot，之后再交给 `ai-fomo` 判断。

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
