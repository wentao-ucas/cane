---
name: 白糖期货 20 年研究项目
description: SR0+ICE 11 号糖 2006-2026 月度复盘项目的产出文件索引、关键发现、可继续推进方向
type: project
originSessionId: 904702b7-067e-4911-a713-9a8501263c64
---
# 白糖期货 SR0 + ICE 11 号糖 20 年研究 (2006-2026)

**Why**: 用户在 2026-05 期间做的完整研究，验证了五层框架方法论。所有数据、新闻、分析都在 `D:/code/bean/` 下。

**How to apply**: 当用户后续问白糖、想继续推进这个研究、或想用同样方法做其他品种时，可以直接引用这些产出，不用从头再做。

## 数据文件 (data/)

- `sugar_monthly.csv` — SR0 日线 resample 月度
- `sugar_monthly_pivot.csv` — 年×月涨跌幅矩阵
- `sugar_seasonality.csv` — 12 个月季节性统计
- `sugar_big_moves.csv` — |涨跌|≥8% 的 23 个月份
- `sugar_by_month.txt` — 按月分组的年度对比（横向）
- `ice_sugar_monthly.csv` — ICE 11 号糖月度 (yfinance SB=F)
- `ice_sugar_seasonality.csv` — ICE 季节性
- `sugar_monthly_with_ice.csv` — **SR+ICE 合并主表（最常用）**
- `sugar_ice_sr_divergence.csv` — 内外盘背离 Top 15
- `oni_monthly.csv` — NOAA ONI 1950-2026
- `sugar_oni_merged.csv` — SR+ICE+ONI 三合一
- `sugar_oni_lag_analysis.csv` — ENSO 滞后效应数据

## 输出文档 (output/)

- `sugar_monthly_full_review.md` — **244 月完整新闻复盘**（1383 行，分年组织）
- `sugar_conclusions.md` — 核心结论 7 段式
- `sugar_monthly_news.md` — 2024 年单独样本
- `sugar_monthly_news_2006_2010.md` 等 4 个分段文件（用并行 Agent 生成的源文件）
- `sugar_monthly_heatmap.png` — 年×月热力图

## 脚本 (scripts/)

- `sugar_monthly.py` — 主连日线 → 月度
- `sugar_heatmap.py` — 热力图
- `sugar_by_month.py` — 按月分组对比
- `ice_sugar_monthly.py` — ICE 数据 + 内外盘对比（**用 yfinance SB=F，不要用 akshare 东财，会被代理拦**）
- `merge_sr_ice.py` — SR+ICE 合并
- `oni_sugar_analysis.py` — ONI 同期 + 分桶
- `oni_sugar_lag.py` — ONI 滞后效应（关键）
- `merge_news.py` — 合并 4 个分段 MD

## 关键发现

### 季节性（已验证）
- **10 月最强**：SR 70% 胜率 / ICE 60%，全球供应真空期
- **3 月最弱**：ICE 29% 胜率，巴西+印度泰国压榨高峰
- 大部分其他月份的"季节性"是 2008-2010 牛熊周期带偏的伪信号

### ENSO 滞后效应（关键发现）
- 同期相关 -0.04（无效），**6-12 月滞后相关 +0.15-0.18**
- 中强 El Niño (ONI≥1.0) → 未来 12 月 +12.8% 胜率 62.5%
- 中强 La Niña (ONI≤-1.0) → 未来 12 月 -6.7% 胜率仅 28.6%
- 5 次 ONI 突破 ±1.0 关键时点，3 次完美验证、2 次反例（反例都是国内政策压过）

### 5 年增减产周期
- 2009-2011 牛 / 2012-2014 熊 / 2015-2016 牛 / 2017-2018 熊 / 2019-2020 反弹被疫情中断 / 2021-2023 牛 / **2024-2026 熊（当前）**

### 2026-05 当前位置评估
- 价格 5429，10 年偏下区间
- ONI=-0.51（刚出 La Niña，中性）
- **关键问题：广西甘蔗面积 1234 万亩仍是近 10 年峰值** —— 还未到 2014 那种"桉进蔗退"减种状态
- 累计跌幅 -25%（vs 2011-2014 上轮 -42%），下行空间仍有 10-15%
- 三种情景概率判断：**A 立即大牛 20% / B 磨底慢牛 55% / C 再杀一波 25%**

## 底部信号 watchlist（需跟踪）

1. **2026 年 3-5 月广西春耕新植率**（最硬信号，<18% 触发）
2. 2025/26 榨季蔗农实际收入（2026-06 出炉）
3. 2026 NOAA ONI 走向（H2 突破 +0.5 = El Niño 信号）
4. 巴西 2026/27 产量预估（2026-04 起）
5. 国内工业库存能否从历史高位回落
6. 价格关键位：跌破 5000 = 恐慌低点；企稳 5200 = 底部确认

## 可继续推进方向

- [ ] 2 月（春节）、6 月（ICE 反转）的驱动机制深挖
- [ ] CFTC 净持仓资金面分析
- [ ] 巴西糖醇比（含水乙醇 vs 糖）量化模型
- [ ] 用同套方法跑棉花 CF0 / 玉米 C0 / 棕榈油 P0
- [ ] 把底部信号 watchlist 做成可跟踪 dashboard

## 重要技术细节

- 国内代理 (127.0.0.1:10808) 会拦截东财 push2his.eastmoney.com → **海外期货数据用 yfinance**
- ICE 11 号糖代码：yfinance 是 SB=F，akshare 东财是 SB00Y（不稳定）
- ONI 数据：NOAA `https://psl.noaa.gov/data/correlation/oni.data`（纯文本，13 列，年+12 月值）
- Windows 编码：脚本开头要加 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')`
- 中文 matplotlib：`mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']`
