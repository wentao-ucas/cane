# cane — 大宗商品周期研究

中国期货市场的周期性大宗商品研究项目，重点是**农产品的 5 年增减产周期 + ENSO 气候因子 + 种植结构**。

## 已完成研究

### 🍬 白糖 SR0 + ICE 11 号原糖 (2006-2026)

20 年完整月度复盘，244 个月新闻原因分析 + 季节性 + 内外盘联动 + NOAA ONI ENSO 滞后效应。

**核心产出**：
- [`output/sugar_conclusions.md`](output/sugar_conclusions.md) — 核心结论 7 段式
- [`output/sugar_monthly_full_review.md`](output/sugar_monthly_full_review.md) — 244 月详细复盘（1383 行）
- [`output/sugar_monthly_heatmap.png`](output/sugar_monthly_heatmap.png) — 年×月热力图
- [`data/sugar_monthly_with_ice.csv`](data/sugar_monthly_with_ice.csv) — SR+ICE 合并月度数据
- [`data/sugar_oni_lag_analysis.csv`](data/sugar_oni_lag_analysis.csv) — ENSO 滞后分析

**关键发现**：
- 季节性真正稳定的只有 **10 月做多 (70% 胜率)** + 3 月空 ICE (29% 胜率)
- ENSO 同期相关 ≈ 0，**6-12 月滞后** 中强 El Niño +12.8% / 中强 La Niña -6.7%
- 当前 (2026-05) 处于 2024-2026 熊市第 3 年，**广西甘蔗面积仍是近 10 年峰值**，未到 2014 那种"桉进蔗退"底部条件

### ⚫ 焦煤板块

详见 `coal/` 子模块和 `output/coal_2026_analysis.md`。

### 🌱 豆粕升贴水

`scripts/get_soybean_meal.py` + `output/contango_chart.png`。

## 目录结构

```
cane/
├── README.md              # 本文件
├── CHANGELOG.md           # 研究产出时间线
├── methodology/           # 方法论文档（给 Claude Code 用）
├── scripts/               # Python 分析脚本
├── data/                  # CSV 数据
├── output/                # markdown 报告 + 图表
├── coal/                  # 焦煤研究子模块
├── articles/              # 文章草稿
└── reference/             # 参考资料
```

## 核心方法论

参见 [`methodology/`](methodology/) 目录。一句话：

> **周期农产品 = 季节性供应窗口（短期）+ ENSO 气候因子（中期 6-12 月）+ 种植周期（长期 3-7 年）+ 国内政策（独立扰动）+ 全球过剩/短缺平衡（基本面定调）**

## 环境依赖

```bash
pip install akshare pandas matplotlib yfinance requests numpy
```

## 数据源

- **国内期货**：akshare `futures_main_sina("SR0")` 等
- **海外期货**：yfinance `SB=F`（ICE 糖）、`CT=F`（棉花）、`ZC=F`（玉米）等
- **NOAA ONI**：`https://psl.noaa.gov/data/correlation/oni.data`

## 给 AI 协作者

如果你是 Claude Code 或其他 AI，想接着这个项目研究：

1. 先读 [`methodology/agricultural_commodity_framework.md`](methodology/agricultural_commodity_framework.md)
2. 再读 [`methodology/sugar_project_notes.md`](methodology/sugar_project_notes.md) 了解白糖项目细节
3. 想跑新品种？按 framework 里的"五层框架"顺序展开

## License

研究内容仅供学习交流。不构成投资建议。
