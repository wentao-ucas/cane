# -*- coding: utf-8 -*-
"""合并 4 个分段 markdown + 2024 样本 -> 完整白糖月度复盘"""
import sys, io, re
from pathlib import Path
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT = Path('output')

def read(p):
    return Path(p).read_text(encoding='utf-8')

def strip_top_header(md):
    """去掉文件最顶上的 # 大标题 + 引用说明，保留 ## 起的内容"""
    lines = md.splitlines()
    start = 0
    for i, ln in enumerate(lines):
        if ln.startswith('## '):
            start = i
            break
    return '\n'.join(lines[start:])

def extract_year_chunk(md, year):
    """从一份分段 md 里抽出指定年份的所有内容（## 脉络 + 该年所有 ###）"""
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
            # 进入了别的年的 ###
            in_year = False
        if in_year:
            out.append(ln)
    return '\n'.join(out).strip()

# 读 5 个文件
md_2024 = read('output/sugar_monthly_news.md')
md_06_10 = read('output/sugar_monthly_news_2006_2010.md')
md_11_15 = read('output/sugar_monthly_news_2011_2015.md')
md_16_20 = read('output/sugar_monthly_news_2016_2020.md')
md_21_26 = read('output/sugar_monthly_news_2021_2026.md')

# 抽取 2024 年的所有 ### （样本文件不含 ## 年脉络，只有月份）
md_2024_clean = strip_top_header(md_2024)

# 总文件
parts = []
parts.append("""# 白糖主连(SR0) + ICE 11 号原糖 月度涨跌复盘 (2006-2026)

> **数据**：郑糖 SR0 主连日线月末重采样；ICE 11 号原糖来自 yfinance (SB=F)，单位美分/磅。
> **方法**：每月一次 WebSearch 查公开报道/研报，AI 汇总要点。
> **范围**：2006-02 ~ 2026-05，共 244 个完整月（2006-01 无前值无涨跌）。

## 大主线快览

- **2006-2008**：上市初期资金推高 → 国储抛储 + 增产 + 金融危机，三年熊市。期价最高 6030 → 最低 2852（-53%）。
- **2009-2011 "糖高宗"牛市**：印度产量骤减 + 中国连续减产 + QE 流动性 → ICE 创 27 年新高，郑糖 11 月 2010 触及 7500 历史高位，全年 +31%。
- **2011-2014 漫长熊市**：进口暴增 + 走私泛滥 + 增产周期，连续 4 年下跌；国储 360 万吨史无前例收储未能托底。2014-01 触底 4386（自高点 -42%）。
- **2015-2016 反转牛市**：减产 + 配额收紧 + 走私整治，2015 全年 +27%，2016 顶部 7100+。
- **2017-2018 双熊市**：增产 + 全球过剩，5/22 保障措施落地反而"利好兑现即出货"。从 7100 跌至 4700（-35%）。
- **2019-2020 反弹被疫情中断**：印泰减产预期推动，2020 年 3-4 月疫情+原油暴跌冲击，4 月单月 -8.87%。
- **2021-2022 大宗商品牛市跟随**：巴西干旱霜冻 + 集装箱紧张，但被国内高库存压制，全年 +10.8%。
- **2023 糖高宗回归**：印泰双减产，ICE 突破 27 美分创 12 年新高，3-4 月单月 +8.4%/+9.1%。
- **2024 三段式**：高位震荡 → 增产+进口压垮 → 糖浆管控反弹。
- **2025-2026 系统性下行**：巴西 4000+ 万吨增产明牌 + 国内 3 年增产，2025 年 -12%，2026 在 5200-5450 寻底。

## 季节性核心规律

| 月 | 郑糖均值/胜率 | ICE均值/胜率 | 解读 |
|---|---|---|---|
| 2月 | +2.13% / 62% | +0.76% / 52% | 内强外弱 — 春节备货独有 |
| 3月 | -0.21% / 48% | **-6.62% / 29%** | ICE 极弱 — 巴西/印度新榨季压力 |
| 4月 | -1.14% / 38% | -1.81% / 29% | 都弱 |
| 6月 | -0.68% / 55% | **+4.41% / 60%** | ICE 反转最猛 |
| 10月 | **+2.41% / 70%** | **+3.81% / 60%** | 唯一两边都强的月份 |
| 11月 | -0.03% / 40% | -1.06% / 35% | 都弱 |

---

# 月度详细复盘 (按年倒序)
""")

# 按倒序追加年份内容
year_to_source = {}
for y in range(2006, 2011): year_to_source[y] = md_06_10
for y in range(2011, 2016): year_to_source[y] = md_11_15
for y in range(2016, 2021): year_to_source[y] = md_16_20
for y in [2021, 2022, 2023, 2025, 2026]: year_to_source[y] = md_21_26
year_to_source[2024] = None  # 单独处理

for y in range(2026, 2005, -1):
    if y == 2024:
        # 2024 样本里无 ## 大标题，自己加上
        parts.append(f"\n## {y} 年脉络")
        parts.append("郑糖 2024 年三段走势：一季度高位震荡(6200-6700) → 二三季度逐步下行(8 月中创年内低点 5536) → 四季度底部回升。全年现货均价从 6704 跌至 6250，跌 6.77%。\n")
        # 抽 ### 2024-XX 月内容
        m_2024_months = re.findall(r'(### 2024-\d{2}.*?)(?=\n### |\Z)', md_2024_clean, re.S)
        for blk in m_2024_months:
            parts.append(blk.strip())
            parts.append('')
    else:
        src = year_to_source.get(y)
        if src is None: continue
        chunk = extract_year_chunk(src, y)
        if chunk:
            parts.append('\n' + chunk + '\n')

merged = '\n'.join(parts)
out_path = 'output/sugar_monthly_full_review.md'
Path(out_path).write_text(merged, encoding='utf-8')
n_months = len(re.findall(r'^### ', merged, re.M))
print(f"已生成 {out_path}")
print(f"总月份数: {n_months}")
print(f"文件大小: {len(merged):,} 字符")
