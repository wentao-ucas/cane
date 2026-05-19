# -*- coding: utf-8 -*-
"""合并 4 个分段 markdown -> 完整玉米月度复盘"""
import sys, io, re
from pathlib import Path
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT = Path('output')

def read(p):
    return Path(p).read_text(encoding='utf-8')

def extract_year_chunk(md, year):
    """从分段 md 抽出指定年份的所有内容（## 脉络 + 该年所有 ###）"""
    pat_year_head = re.compile(rf'^## {year}\s')
    pat_other_year_head = re.compile(r'^## (?:20\d{2})\s')
    pat_h3 = re.compile(rf'^### {year}-')
    pat_h3_other = re.compile(r'^### (?:20\d{2})-')

    lines = md.splitlines()
    out = []
    in_year = False
    for ln in lines:
        if pat_year_head.match(ln):
            in_year = True; out.append(ln); continue
        if in_year and pat_other_year_head.match(ln):
            in_year = False
        if pat_h3.match(ln):
            in_year = True; out.append(ln); continue
        if in_year and pat_h3_other.match(ln):
            in_year = False
        if in_year:
            out.append(ln)
    return '\n'.join(out).strip()

md_05_10 = read('output/corn_monthly_news_2005_2010.md')
md_11_15 = read('output/corn_monthly_news_2011_2015.md')
md_16_20 = read('output/corn_monthly_news_2016_2020.md')
md_21_26 = read('output/corn_monthly_news_2021_2026.md')

parts = []
parts.append("""# 大商所玉米 C0 + CBOT 玉米 ZC=F 月度涨跌复盘 (2005-2026)

> **数据**：大商所玉米 C0 主连日线月末重采样；CBOT 玉米来自 yfinance (ZC=F)，单位美分/蒲式耳。
> **方法**：每月一次 WebSearch 查公开报道/研报，AI 汇总要点。
> **范围**：2005-02 ~ 2026-05，共约 256 个完整月（2005-01 无前值无涨跌）。

## 大主线快览（5 年增减产周期 + 政策史）

- **2005-2007** 临储建立前：WTO 后进口配额制度（720 万吨/年）保护下，价格低位横盘 1100-1700 元/吨。CBOT 受乙醇需求驱动暴涨，国内独立。
- **2008-2010 临储元年 + 全球粮食危机 + 金融危机**：东北临储制度建立（2008-10），收储 4250 万吨；2010 起首次大规模进口美玉米（157 万吨）。CBOT 三年大幅波动 (200→800→400→700 美分)，国内被临储锁死。
- **2011-2014 临储扩张 + 价格僵化**：临储价从 1980 涨到 2240，国家累计收储 1.5 亿吨；CBOT 2012 美国百年大旱单月 +21%，国内 C 几乎无反应（仅 -1.35%）。**史上最大内外背离时段**。
- **2015 临储拐点**：临储价首次下调（2240→2000），全年单边下跌 -10.7%，7 月单月 -13% 是最大警讯。DDGS+高粱+大麦进口围攻替代。
- **2016 临储取消改革（12 年制度终结）**：2 月 -19.76% 创历史最大单月跌幅，全年 V 型 — 上半年崩塌、10 月价补分离落地后反转。
- **2017-2019 去库存期 + 非洲猪瘟冲击**：临储拍卖年均 5000 万吨清库存；2018-08 非洲猪瘟爆发，生猪存栏暴跌 → 饲料需求骤降。价格在 1700-1900 磨底。
- **2020 大反转**：临储清库 + 生猪存栏恢复 + 新冠粮食恐慌，下半年单月连涨（7月 +11%、9月 +9%），全年 +33%。
- **2021-2022 后临储新时代 + 进口巅峰**：2021 进口 2900 万吨创纪录（是过去 4 倍），俄乌战争 2022-02 推 CBOT 至 800 美分。国内 C0 在 2800-3000 高位震荡。
- **2023-2024 转基因元年 + 增产开端**：第一批 27 个转基因品种审定 (2023)，内蒙东北试点推广。国内 2024 丰收 + 进口大豆增加，价格转向下行。
- **2025-2026 系统性下行**：进口从 2900 万吨骤降至 ~500 万吨，但国内连续增产 + 库存高企，价格在 2300-2500 寻底。

## 季节性核心规律

| 月 | C0 均值/胜率 | CBOT 均值/胜率 | 解读 |
|---|---|---|---|
| 2 月 | +0.89% / 77.3% | +1.47% / 63.6% | 春节备货 + CBOT 南半球收割平稳 |
| 6 月 | -1.09% / 42.9% | -2.16% / 28.6% | CBOT 美玉米授粉天气溢价 |
| 7 月 | **-1.55% / 28.6%** | **-4.66% / 33.3%** | 双双最弱 — 美玉米丰产预期落地 |
| 9 月 | -1.13% / 33.3% | **+2.44% / 76.2%** | 内外分歧最大 — 国内秋收压力 vs CBOT 已定价丰产开始反弹 |
| 10 月 | **+1.62% / 71.4%** | +3.14% / 66.7% | 两边都强 — 秋收兑现+冬储 |
| 11 月 | +1.59% / 71.4% | -1.01% / 33.3% | 内外分歧 — 国内秋粮收储溢价 |
| **12 月** | +0.97% / 52.4% | **+6.16% / 90.5%** | CBOT 12月胜率历史最强 |

## ENSO 信号（与糖相反）

- 同期相关 C0 vs ONI: **-0.184**（糖只有 -0.04），玉米对 ENSO 同期反应**远强于糖**
- **La Niña 利多玉米**：中强 La Niña 月均 +2.7% 胜率 87.5%；79 个月累积 +105.8%
- **El Niño 利空玉米**：强 El Niño 月均 -2.97% 胜率 35%
- **但 6-12 月滞后效应失灵**（中强 La Niña 后 12 月仅 -5.8% 胜率 21%）—— 与糖正相反
- 机理：玉米一年生作物，ENSO 当月就完全定价；糖甘蔗多年生，需 6-12 月传导

---

# 月度详细复盘 (按年倒序)
""")

year_to_source = {}
for y in range(2005, 2011): year_to_source[y] = md_05_10
for y in range(2011, 2016): year_to_source[y] = md_11_15
for y in range(2016, 2021): year_to_source[y] = md_16_20
for y in range(2021, 2027): year_to_source[y] = md_21_26

for y in range(2026, 2004, -1):
    src = year_to_source.get(y)
    if src is None: continue
    chunk = extract_year_chunk(src, y)
    if chunk:
        parts.append('\n' + chunk + '\n')

merged = '\n'.join(parts)
out_path = 'output/corn_monthly_full_review.md'
Path(out_path).write_text(merged, encoding='utf-8')
n_months = len(re.findall(r'^### ', merged, re.M))
print(f"已生成 {out_path}")
print(f"总月份数: {n_months}")
print(f"文件大小: {len(merged):,} 字符")
