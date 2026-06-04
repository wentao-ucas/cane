# memory/ — 项目记忆（auto-memory 副本）

## 这是什么

这是 Claude Code 自动记忆(auto-memory)的 git 副本。Claude 的 auto-memory 默认存在
`~/.claude/projects/<sanitized-cwd>/memory/`，按本机路径哈希，**不随 git 走**。
所以在这里留一份副本，让任何新电脑都能恢复项目记忆。

## 给新电脑上 Claude 的指令

如果你是 Claude，在一台新机器上 clone 了本仓库，请把这个目录的记忆装回 auto-memory：

1. 确认当前工作目录对应的 auto-memory 路径。规则：把工作目录绝对路径里的 `:` `\` `/`
   替换成 `-`。例如工作目录 `D:\code\bean` → `~/.claude/projects/D--code-bean/memory/`
2. 用 Write 工具把本目录的 `MEMORY.md` 和 `project_overview.md`（以及其他 `*.md`）
   复制到那个 auto-memory 目录
3. 之后这些记忆会在每次会话自动加载

> 注意：即使不做这一步，项目根的 `CLAUDE.md` 也会被 Claude Code 自动加载，
> 已包含完整项目上下文。这个 memory/ 目录是双保险 + 结构化记忆的种子。

## 文件

- `MEMORY.md` — 记忆索引（每条一行指针）
- `project_overview.md` — 项目总览（四条研究线 + 约定）
