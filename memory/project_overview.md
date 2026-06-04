---
name: project_overview
description: D:\code\bean repo overview — multi-commodity cycle research (sugar/coal/soybean meal/corn), structure, conventions
type: project
---
`D:\code\bean` 是用户的大宗商品周期研究项目，名为 cane（README）/ bean（agent.md）。中文文档为主，发布文章受众是中国散户。**项目根有 `CLAUDE.md` 会自动加载，是完整上下文入口。**

**研究主题**（按完成度）：
1. 🍬 白糖 SR0 + ICE 11 — 完整 20 年月度复盘 + ENSO 滞后 + 5 年增减产周期，`output/sugar_conclusions.md` 是核心结论
2. ⚫ 焦煤 — `coal/` 子模块 + `output/coal_2026_analysis.md`
3. 🌱 豆粕 ETF — 系列文章 2 篇（articles/01, 02），数据来自 akshare + USDA WASDE XML
4. 🌽 玉米 C0 + CBOT — **最新主线**。21年量化结论 `output/corn_conclusions.md`、262月复盘、跨期/蝴蝶/跨品种套利、做多投研 `output/corn_long_thesis.md`(整合雪球@治雨观点+量化对照+2020逼空复盘+交割规则)

**关键约定**：
- 安全规则在 `AGENTS.md`：破坏性操作（rm、git reset --hard、git clean、git checkout --）必须先 dry-run 并等用户回 "确认删除"
- 数据来源在 `agent.md`：**严禁编造任何数据**，必须有 CSV/XML 文件或官方链接支撑；估算数据必须标注"（估算）"
- 数据获取：`python scripts/fetch_akshare_data.py` → `python scripts/plot_all_charts.py`
- 方法论框架：`methodology/agricultural_commodity_framework.md` — 五层叠加（季节性 + 内外联动 + ENSO 滞后 + 成本/种植周期 + 5 年增减产）
- 玉米特殊：一年生作物 ENSO **同期**定价(滞后失灵)、内外盘相关仅0.30(高度独立)、主力月只有1/5/9、散户9月合约须8月底前平仓

**Why:** 项目跨多个品种但共享同一套方法论；用户严格区分"真实数据 vs 估算"以保证文章可信度。用户是做期货/量化的，可直接、有观点交流。
**How to apply:** 接到新任务先问是哪个品种；写文章/报告前确认数据来源；不要主动删文件（仓库根有"(2)"后缀副本+stale豆粕文件，动前先问）。
