# -*- coding: utf-8 -*-
"""NOAA ONI 月度指数 × 白糖月度涨跌 相关性分析"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import pandas as pd
import numpy as np
from pathlib import Path
from io import StringIO

OUT = Path('data'); OUT.mkdir(exist_ok=True)

# === 拉 ONI ===
url = "https://psl.noaa.gov/data/correlation/oni.data"
text = requests.get(url, timeout=20).text

rows = []
for line in text.strip().splitlines():
    parts = line.split()
    if len(parts) == 13:
        try:
            year = int(parts[0])
            if 1950 <= year <= 2030:
                vals = [float(x) for x in parts[1:13]]
                for m, v in enumerate(vals, 1):
                    if v > -99:
                        rows.append({'date': pd.Timestamp(year, m, 1) + pd.offsets.MonthEnd(0), 'oni': v})
        except (ValueError, IndexError):
            continue

oni = pd.DataFrame(rows).set_index('date').sort_index()
oni.to_csv(OUT/'oni_monthly.csv', encoding='utf-8-sig')
print(f"ONI: {oni.index.min().date()} ~ {oni.index.max().date()}, {len(oni)} 月")

# === 分类: ONI ≥ 0.5 El Niño, ≤ -0.5 La Niña, 中间 Neutral ===
def classify(v):
    if v >= 1.5: return 'Strong El Niño'
    if v >= 1.0: return 'Moderate El Niño'
    if v >= 0.5: return 'Weak El Niño'
    if v <= -1.5: return 'Strong La Niña'
    if v <= -1.0: return 'Moderate La Niña'
    if v <= -0.5: return 'Weak La Niña'
    return 'Neutral'
oni['phase'] = oni['oni'].apply(classify)

# === 合白糖 ===
sr = pd.read_csv('data/sugar_monthly_with_ice.csv', parse_dates=['date']).set_index('date')
m = sr.join(oni, how='left').dropna(subset=['sr_ret%','oni'])
print(f"重叠样本: {len(m)} 月")

# === 同期相关性 ===
print("\n=== 同期相关性 (ONI vs 月涨跌) ===")
print(f"郑糖 SR vs ONI: {m[['sr_ret%','oni']].corr().iloc[0,1]:+.3f}")
print(f"ICE 11号 vs ONI: {m[['ice_ret%','oni']].corr().iloc[0,1]:+.3f}")

# === 滞后相关性 (ONI 领先 N 个月) ===
print("\n=== ONI 领先 N 个月对糖价相关性 ===")
print(f"{'滞后月数':<8} {'郑糖':>10} {'ICE':>10}")
for lag in [0, 1, 3, 6, 9, 12, 18]:
    oni_lag = m['oni'].shift(lag)
    c_sr = m['sr_ret%'].corr(oni_lag)
    c_ice = m['ice_ret%'].corr(oni_lag)
    print(f"  +{lag:>3}    {c_sr:+10.3f} {c_ice:+10.3f}")

# === 按 ONI 阶段分组的糖价表现 ===
print("\n=== 按 ENSO 状态分组：月均涨跌幅 ===")
order = ['Strong La Niña','Moderate La Niña','Weak La Niña','Neutral','Weak El Niño','Moderate El Niño','Strong El Niño']
grp = m.groupby('phase').agg(
    样本=('sr_ret%','count'),
    郑糖均值=('sr_ret%','mean'),
    郑糖胜率=('sr_ret%', lambda x: (x>0).mean()*100),
    ICE均值=('ice_ret%','mean'),
    ICE胜率=('ice_ret%', lambda x: (x>0).mean()*100),
).round(2)
grp = grp.reindex([p for p in order if p in grp.index])
print(grp.to_string())
grp.to_csv(OUT/'oni_phase_returns.csv', encoding='utf-8-sig')

# === 累积涨幅: El Niño vs La Niña 期间 ===
m['cum_elnino_sr']  = np.where(m['oni']>=0.5, m['sr_ret%']/100, 0)
m['cum_lanina_sr']  = np.where(m['oni']<=-0.5, m['sr_ret%']/100, 0)
m['cum_neutral_sr'] = np.where(m['oni'].abs()<0.5, m['sr_ret%']/100, 0)
print("\n=== 各 ENSO 阶段郑糖累积收益（简单加总月涨跌幅 %）===")
print(f"El Niño 月份累积: {m['cum_elnino_sr'].sum()*100:+.1f}%, 月数 {(m['oni']>=0.5).sum()}")
print(f"La Niña 月份累积: {m['cum_lanina_sr'].sum()*100:+.1f}%, 月数 {(m['oni']<=-0.5).sum()}")
print(f"Neutral 月份累积: {m['cum_neutral_sr'].sum()*100:+.1f}%, 月数 {(m['oni'].abs()<0.5).sum()}")

# === 滚动同期 ONI vs 糖价3M 涨幅 ===
m['sr_3m'] = m['sr_close'].pct_change(3) * 100
m['oni_lag6'] = m['oni'].shift(6)
m_clean = m.dropna(subset=['sr_3m','oni_lag6'])
print(f"\nONI(-6M) vs SR 3 月涨幅 相关性: {m_clean[['sr_3m','oni_lag6']].corr().iloc[0,1]:+.3f}")

# 输出合并数据
m[['sr_close','sr_ret%','ice_close','ice_ret%','oni','phase']].to_csv(OUT/'sugar_oni_merged.csv', encoding='utf-8-sig')
print(f"\n保存: data/oni_monthly.csv, data/oni_phase_returns.csv, data/sugar_oni_merged.csv")
