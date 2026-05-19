# -*- coding: utf-8 -*-
"""NOAA ONI 月度指数 × 玉米月度涨跌 相关性分析
注意: 玉米 ENSO 敏感性方向与糖相反 —— La Niña 利多(美国玉米带干旱)
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path('data'); OUT.mkdir(exist_ok=True)

# ONI 已在 data/oni_monthly.csv (糖项目产出)，直接复用
oni = pd.read_csv('data/oni_monthly.csv', parse_dates=['date']).set_index('date')
print(f"ONI: {oni.index.min().date()} ~ {oni.index.max().date()}, {len(oni)} 月 (复用已有数据)")

def classify(v):
    if v >= 1.5: return 'Strong El Niño'
    if v >= 1.0: return 'Moderate El Niño'
    if v >= 0.5: return 'Weak El Niño'
    if v <= -1.5: return 'Strong La Niña'
    if v <= -1.0: return 'Moderate La Niña'
    if v <= -0.5: return 'Weak La Niña'
    return 'Neutral'
oni['phase'] = oni['oni'].apply(classify)

# 合玉米
c = pd.read_csv('data/corn_monthly_with_cbot.csv', parse_dates=['date']).set_index('date')
m = c.join(oni, how='left').dropna(subset=['c_ret%','oni'])
print(f"重叠样本: {len(m)} 月")

# === 同期相关性 ===
print("\n=== 同期相关性 (ONI vs 月涨跌) ===")
print(f"大商所玉米 C vs ONI: {m[['c_ret%','oni']].corr().iloc[0,1]:+.3f}")
if 'cbot_ret%' in m.columns:
    print(f"CBOT 玉米    vs ONI: {m[['cbot_ret%','oni']].corr().iloc[0,1]:+.3f}")

# === 滞后相关性 ===
print("\n=== ONI 领先 N 个月对玉米价相关性 ===")
print(f"{'滞后月数':<8} {'大商所':>10} {'CBOT':>10}")
for lag in [0, 1, 3, 6, 9, 12, 18]:
    oni_lag = m['oni'].shift(lag)
    c_c = m['c_ret%'].corr(oni_lag)
    c_cb = m['cbot_ret%'].corr(oni_lag) if 'cbot_ret%' in m.columns else np.nan
    print(f"  +{lag:>3}    {c_c:+10.3f} {c_cb:+10.3f}")

# === 按 ONI 阶段分组的玉米表现 ===
print("\n=== 按 ENSO 状态分组：月均涨跌幅 (玉米 La Niña 利多预期) ===")
order = ['Strong La Niña','Moderate La Niña','Weak La Niña','Neutral','Weak El Niño','Moderate El Niño','Strong El Niño']
agg_dict = {
    '样本': ('c_ret%','count'),
    '大商所均值': ('c_ret%','mean'),
    '大商所胜率': ('c_ret%', lambda x: (x>0).mean()*100),
}
if 'cbot_ret%' in m.columns:
    agg_dict['CBOT均值'] = ('cbot_ret%','mean')
    agg_dict['CBOT胜率'] = ('cbot_ret%', lambda x: (x>0).mean()*100)
grp = m.groupby('phase').agg(**agg_dict).round(2)
grp = grp.reindex([p for p in order if p in grp.index])
print(grp.to_string())
grp.to_csv(OUT/'corn_oni_phase_returns.csv', encoding='utf-8-sig')

# === 累积涨幅 ===
print("\n=== 各 ENSO 阶段大商所玉米累积收益（简单加总月涨跌幅 %）===")
print(f"El Niño 月份累积: {m.loc[m['oni']>=0.5, 'c_ret%'].sum():+.1f}%, 月数 {(m['oni']>=0.5).sum()}")
print(f"La Niña 月份累积: {m.loc[m['oni']<=-0.5, 'c_ret%'].sum():+.1f}%, 月数 {(m['oni']<=-0.5).sum()}")
print(f"Neutral 月份累积: {m.loc[m['oni'].abs()<0.5, 'c_ret%'].sum():+.1f}%, 月数 {(m['oni'].abs()<0.5).sum()}")

# === 滚动 ===
m['c_3m'] = m['c_close'].pct_change(3) * 100
m['oni_lag6'] = m['oni'].shift(6)
m_clean = m.dropna(subset=['c_3m','oni_lag6'])
print(f"\nONI(-6M) vs 大商所玉米 3 月涨幅 相关性: {m_clean[['c_3m','oni_lag6']].corr().iloc[0,1]:+.3f}")

# 输出
keep_cols = ['c_close','c_ret%','oni','phase']
if 'cbot_close' in m.columns:
    keep_cols = ['c_close','c_ret%','cbot_close','cbot_ret%','oni','phase']
m[keep_cols].to_csv(OUT/'corn_oni_merged.csv', encoding='utf-8-sig')
print(f"\n保存: data/corn_oni_phase_returns.csv, data/corn_oni_merged.csv")
