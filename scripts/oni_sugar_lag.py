# -*- coding: utf-8 -*-
"""ENSO 滞后效应分析: 6M 滑动 ONI -> 后续 6-12 月糖价前瞻收益"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from pathlib import Path

m = pd.read_csv('data/sugar_oni_merged.csv', parse_dates=['date']).set_index('date')

# 6 个月平滑 ONI（去掉短期噪音）
m['oni_6m'] = m['oni'].rolling(6).mean()
# 前瞻收益（未来 N 月累积）
m['fwd_6m']  = m['sr_close'].shift(-6)  / m['sr_close'] - 1
m['fwd_12m'] = m['sr_close'].shift(-12) / m['sr_close'] - 1
m['fwd_18m'] = m['sr_close'].shift(-18) / m['sr_close'] - 1
m[['fwd_6m','fwd_12m','fwd_18m']] *= 100

# 按 6M 平滑 ONI 分组
def bucket(v):
    if v >= 1.0: return 'A. ONI≥1.0 (中强 El Niño)'
    if v >= 0.5: return 'B. 0.5≤ONI<1.0 (弱 El Niño)'
    if v >= -0.5: return 'C. -0.5<ONI<0.5 (中性)'
    if v >= -1.0: return 'D. -1.0<ONI≤-0.5 (弱 La Niña)'
    return 'E. ONI≤-1.0 (中强 La Niña)'

m['bucket'] = m['oni_6m'].apply(bucket)
sample = m.dropna(subset=['oni_6m','fwd_6m','fwd_12m'])

print(f"样本数: {len(sample)}\n")
print("=== 按 6 个月平滑 ONI 分组：未来 6/12/18 月郑糖前瞻收益 ===")
g = sample.groupby('bucket').agg(
    样本=('fwd_6m','count'),
    fwd6均值=('fwd_6m','mean'),
    fwd6胜率=('fwd_6m', lambda x: (x>0).mean()*100),
    fwd12均值=('fwd_12m','mean'),
    fwd12胜率=('fwd_12m', lambda x: (x>0).mean()*100),
    fwd18均值=('fwd_18m','mean'),
).round(1)
print(g.to_string())

# 相关性
print(f"\n6M 平滑 ONI vs 后续 6 月收益相关性:  {sample[['oni_6m','fwd_6m']].corr().iloc[0,1]:+.3f}")
print(f"6M 平滑 ONI vs 后续 12 月收益相关性: {sample[['oni_6m','fwd_12m']].corr().iloc[0,1]:+.3f}")
print(f"6M 平滑 ONI vs 后续 18 月收益相关性: {sample[['oni_6m','fwd_18m']].corr().iloc[0,1]:+.3f}")

# 绝对值相关性: ENSO 极端度 vs 后续波动率
m['oni_abs'] = m['oni_6m'].abs()
m['fwd_12m_abs'] = m['fwd_12m'].abs()
sample2 = m.dropna(subset=['oni_abs','fwd_12m_abs'])
print(f"\n|ONI 6M| vs |后续 12 月收益| 相关性: {sample2[['oni_abs','fwd_12m_abs']].corr().iloc[0,1]:+.3f}")
print("（验证：ENSO 强度是否预示未来糖价波动幅度）")

# 输出关键转折点：ONI 突破 ±1.0 时刻
print("\n=== ONI 6M 平滑突破 ±1.0 的关键时点 ===")
m['oni_cross'] = ((m['oni_6m'].abs() >= 1.0) & (m['oni_6m'].shift(1).abs() < 1.0))
crosses = m[m['oni_cross']][['oni','oni_6m','sr_close']]
for d, r in crosses.iterrows():
    fwd_6 = m.loc[d, 'fwd_6m'] if 'fwd_6m' in m.columns else None
    fwd_12 = m.loc[d, 'fwd_12m'] if 'fwd_12m' in m.columns else None
    state = "El Niño" if r['oni_6m'] > 0 else "La Niña"
    fwd6 = f"{fwd_6:+.1f}%" if pd.notna(fwd_6) else "n/a"
    fwd12 = f"{fwd_12:+.1f}%" if pd.notna(fwd_12) else "n/a"
    print(f"  {d.strftime('%Y-%m')} {state} 突破 (ONI={r['oni']:+.2f}, 6M均={r['oni_6m']:+.2f}, 糖价{r['sr_close']:.0f}) -> 6M:{fwd6}, 12M:{fwd12}")

m[['sr_close','sr_ret%','oni','oni_6m','bucket','fwd_6m','fwd_12m','fwd_18m']].round(2).to_csv('data/sugar_oni_lag_analysis.csv', encoding='utf-8-sig')
print("\n保存: data/sugar_oni_lag_analysis.csv")
