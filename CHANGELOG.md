# Changelog

研究项目产出时间线。每次完成阶段性研究在顶部追加一条。

---

## 2026-05-18 白糖期货 20 年完整复盘

- 拉取白糖主连 SR0 日线 2006-01 ~ 2026-05 (5122 行)，resample 月度
- 叠加 ICE 11 号原糖 SB=F (yfinance) 20 年数据，单位美分/磅
- 用 4 个并行 Agent + WebSearch 完成 **244 个月度新闻复盘**
- 拉 NOAA ONI 月度指数 (1950-2026)，做 ENSO 滞后效应分析
- **核心发现**：
  - 季节性真正稳定的只有 10 月做多 (70% 胜率) + 3 月空 ICE (29% 胜率)
  - ENSO 同期相关 ≈ 0，**6-12 月滞后** El Niño +12.8% / La Niña -6.7%
  - 5 年增减产周期清晰，当前 2024-2026 处于熊市第 3 年
  - 广西甘蔗面积 1234 万亩仍是近 10 年峰值，**未到 2014 那种"桉进蔗退"底部条件**
- 产出：`output/sugar_conclusions.md`、`sugar_monthly_full_review.md` (1383 行)、`sugar_monthly_heatmap.png`
- 数据：`data/sugar_monthly_with_ice.csv`、`oni_monthly.csv`、`sugar_oni_lag_analysis.csv` 等 13 份
- 脚本：`scripts/sugar_monthly.py` 等 8 份

## 2026-03-07 焦煤板块跟踪

- 抓取焦煤板块全部个股数据 (`data/coal_all_stocks.json`)
- 牛市 v2 分析 (`data/coal_bull_market_v2.json`)
- 当前精准持仓 (`data/coal_current_precise.json`)
- coal/ 子模块：完整分析框架 + 数据抓取 + 报告生成

## 2026-03-03 焦煤 2026 年度展望

- 输出 `output/coal_2026_analysis.md`

## 早期 豆粕升贴水分析

- `scripts/get_soybean_meal.py` 获取豆粕各合约价格
- 计算升贴水 + Term Structure
- 产出：`output/contango_chart.png`、`output/term_structure.png`、`data/soybean_meal_contango.csv`

---

## 方法论

参见 `~/.claude/projects/D--code-bean/memory/feedback_ag_commodity_method.md` —— 农产品周期研究五层叠加分析框架（季节性 + 内外联动 + ENSO 滞后 + 成本/种植周期 + 5 年增减产周期）。
