# 方法论文档（Methodology）

> 这个目录是给 **Claude Code / 其他 AI 协作者** 看的核心方法论文档。
> 想做新的农产品周期研究？先读 `agricultural_commodity_framework.md`。

## 文件说明

| 文件 | 用途 |
|---|---|
| `agricultural_commodity_framework.md` | **核心方法论** — 农产品周期五层叠加分析框架，含每个品种的 yfinance 代码、ENSO 敏感性方向、写作偏好 |
| `sugar_project_notes.md` | 白糖项目的产出索引 + 关键发现 + 当前位置评估 + watchlist |
| `INDEX.md` | 简短索引（=原始 MEMORY.md） |

## 给 Claude Code 用户的提示

如果你 clone 了这个 repo 想接着研究：

1. **先读 `agricultural_commodity_framework.md`** 理解整套方法
2. 把这三份文件复制到你的 Claude Code memory 目录：
   ```bash
   # macOS/Linux
   cp methodology/*.md ~/.claude/projects/<your-project-id>/memory/

   # Windows
   cp methodology/*.md "C:/Users/<user>/.claude/projects/<your-project-id>/memory/"
   ```
3. 把 `INDEX.md` 重命名为 `MEMORY.md`，更新里面的相对路径指向你自己的 memory 文件
4. 启动 Claude Code 后，它会自动加载这些 memory

## 框架核心一句话

> **周期农产品 = 季节性供应窗口（短期）+ ENSO 气候因子（中期 6-12 月）+ 种植周期（长期 3-7 年）+ 国内政策（独立扰动）+ 全球过剩/短缺平衡（基本面定调）**

## 适用品种

已验证：白糖 (SR0/SB=F)

可类推：棉花 (CF0/CT=F)、玉米 (C0/ZC=F)、豆粕 (M0/ZM=F)、棕榈油 (P0)、橡胶 (RU0)、可可、咖啡等

## 通用规律（跨品种已验证）

1. **ENSO 同期相关 ≈ 0**，但**滞后 6-12 月**显著
2. **种植周期决定波动周期**：一年生 2-3 年、宿根 5-7 年、永久作物 10-15 年
3. **底部真信号是面积/产能下降**，不是价格便宜
4. **"利好兑现即顶部"** 在政策驱动品种里反复出现
