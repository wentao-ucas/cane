# -*- coding: utf-8 -*-
"""
玉米蝴蝶价差 (Butterfly Spread) 统计套利分析

蝴蝶定义: fly = 2 × 中月 - 近月 - 远月 (理论上中月 = (近+远)/2 时 fly = 0)
方向解读:
  - fly > 0: 中月相对偏贵 → 卖出中月 × 2 + 买入近+远 (做空蝴蝶)
  - fly < 0: 中月相对便宜 → 买入中月 × 2 + 卖出近+远 (做多蝴蝶)

经典玉米蝴蝶:
  1-5-9 (年内三大主力月)
  5-9-1+ (新粮过渡)
  7-9-11 (秋收前后)
  9-11-1+ (新粮收割+冬储)

输出:
  data/corn_butterfly_spreads.csv     - 时间序列
  data/corn_butterfly_signals.csv     - 当前 Z + 信号
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path('data'); OUT.mkdir(exist_ok=True)

df = pd.read_csv('data/corn_contracts_daily.csv', parse_dates=['date'])
wide = df.pivot(index='date', columns='contract', values='close').sort_index()
LAST = wide.index.max()
print(f"加载 {df['contract'].nunique()} 合约, 最后交易日 {LAST.date()}")

def code(year, month):
    return f"C{year % 100:02d}{month:02d}"

# === 定义蝴蝶组合 (近, 中, 远, 名称) ===
flies = []
for year in range(2019, 2028):
    # 标准年内三蝶
    flies.append((code(year, 1),    code(year, 5),    code(year, 9),    f'C{year%100:02d}: 1-5-9'))
    flies.append((code(year, 3),    code(year, 5),    code(year, 7),    f'C{year%100:02d}: 3-5-7'))
    flies.append((code(year, 5),    code(year, 7),    code(year, 9),    f'C{year%100:02d}: 5-7-9'))
    flies.append((code(year, 7),    code(year, 9),    code(year, 11),   f'C{year%100:02d}: 7-9-11'))
    flies.append((code(year, 9),    code(year, 11),   code(year+1, 1),  f'C{year%100:02d}: 9-11-1+'))
    # 跨年蝶
    flies.append((code(year, 5),    code(year, 9),    code(year+1, 1),  f'C{year%100:02d}: 5-9-1+'))
    flies.append((code(year, 9),    code(year+1, 1),  code(year+1, 5),  f'C{year%100:02d}: 9-1-5+'))

# 过滤
valid = [(n,m,f,name) for n,m,f,name in flies if n in wide.columns and m in wide.columns and f in wide.columns]
print(f"有效蝴蝶组合 {len(valid)} 个")

# === 计算 fly = 2*中 - 近 - 远 ===
fly_series = {}
current_rows = []
historical_rows = []

for near, mid, far, name in valid:
    series = (2 * wide[mid] - wide[near] - wide[far]).dropna()
    if len(series) < 30: continue
    fly_series[name] = series

    # 判断是否当前可交易
    active_now = all(not pd.isna(wide.loc[LAST, c]) for c in [near, mid, far])

    mu, sigma = series.mean(), series.std()

    if active_now:
        cur = 2 * wide.loc[LAST, mid] - wide.loc[LAST, near] - wide.loc[LAST, far]
        z = (cur - mu) / sigma if sigma > 0 else 0
        pct = (series <= cur).mean() * 100
        sig = '🔴 强信号 (|Z|≥2)' if abs(z) >= 2.0 else ('🟡 弱信号 (|Z|≥1.5)' if abs(z) >= 1.5 else '中性')
        direction = '做空蝶 (卖中×2, 买近+远)' if z > 0 else '做多蝶 (买中×2, 卖近+远)'
        current_rows.append({
            '组合': name,
            '近': near, '中': mid, '远': far,
            '样本': len(series),
            '当前fly': round(cur, 1),
            '均值': round(mu, 1),
            'std': round(sigma, 1),
            '最大': round(series.max(), 1),
            '最小': round(series.min(), 1),
            'Z': round(z, 2),
            '分位': round(pct, 0),
            '信号': sig,
            '方向': direction if abs(z) >= 1.5 else '-',
        })
    else:
        last_v = series.iloc[-1]
        last_z = (last_v - mu) / sigma if sigma > 0 else 0
        historical_rows.append({
            '组合': name,
            '近': near, '中': mid, '远': far,
            '样本': len(series),
            '终值': round(last_v, 1),
            '终日': str(series.index[-1].date()),
            '均值': round(mu, 1),
            'std': round(sigma, 1),
            '最大': round(series.max(), 1),
            '最小': round(series.min(), 1),
            '终值Z': round(last_z, 2),
        })

# 时间序列输出
fly_df = pd.DataFrame(fly_series)
fly_df.to_csv(OUT/'corn_butterfly_spreads.csv', encoding='utf-8-sig')

cur_stats = pd.DataFrame(current_rows).sort_values('Z', key=lambda x: x.abs(), ascending=False)
cur_stats.to_csv(OUT/'corn_butterfly_signals.csv', encoding='utf-8-sig', index=False)

hist_stats = pd.DataFrame(historical_rows).sort_values('终值Z', key=lambda x: x.abs(), ascending=False)
hist_stats.to_csv(OUT/'corn_butterfly_history.csv', encoding='utf-8-sig', index=False)

print(f"\n{'='*70}")
print(f"=== 当前可交易蝴蝶 ({LAST.date()} 三合约都活跃) ===")
print(f"{'='*70}")
if len(cur_stats):
    print(cur_stats.to_string(index=False))

print(f"\n{'='*70}")
print(f"=== 历史已完成蝴蝶 Top 10 (按 |终值Z|，验证均值回归) ===")
print(f"{'='*70}")
print(hist_stats.head(10).to_string(index=False))

# === 当前活跃合约的所有"连续三合约"蝴蝶 ===
active = [c for c in wide.columns if not pd.isna(wide.loc[LAST, c])]
active.sort()  # 按合约代码排序 = 按时间排序
print(f"\n{'='*70}")
print(f"=== 当前活跃合约 {len(active)} 个 — 所有连续三合约蝴蝶 ===")
print(f"{'='*70}")
adjacent_rows = []
for i in range(len(active) - 2):
    n, m, f = active[i], active[i+1], active[i+2]
    series = (2 * wide[m] - wide[n] - wide[f]).dropna()
    if len(series) < 30: continue
    cur = 2 * wide.loc[LAST, m] - wide.loc[LAST, n] - wide.loc[LAST, f]
    mu, sigma = series.mean(), series.std()
    z = (cur - mu) / sigma if sigma > 0 else 0
    pct = (series <= cur).mean() * 100
    sig = '🔴 强信号' if abs(z) >= 2.0 else ('🟡 弱信号' if abs(z) >= 1.5 else '中性')
    direction = '做空蝶' if z > 0 else '做多蝶'
    adjacent_rows.append({
        '组合': f'{n}-{m}-{f}',
        '样本': len(series),
        '当前fly': round(cur, 1),
        '均值': round(mu, 1),
        'std': round(sigma, 1),
        '最大': round(series.max(), 1),
        '最小': round(series.min(), 1),
        'Z': round(z, 2),
        '分位': round(pct, 0),
        '信号': sig,
        '方向': direction if abs(z) >= 1.5 else '-',
    })
adj_df = pd.DataFrame(adjacent_rows).sort_values('Z', key=lambda x: x.abs(), ascending=False)
adj_df.to_csv(OUT/'corn_butterfly_active.csv', encoding='utf-8-sig', index=False)
print(adj_df.to_string(index=False))

print(f"\n保存:")
print(f"  data/corn_butterfly_spreads.csv     ({fly_df.shape[0]} 天 × {fly_df.shape[1]} 蝶时间序列)")
print(f"  data/corn_butterfly_signals.csv     ({len(cur_stats)} 个当前可交易标准蝶)")
print(f"  data/corn_butterfly_active.csv      ({len(adj_df)} 个活跃合约连续三蝶)")
print(f"  data/corn_butterfly_history.csv     ({len(hist_stats)} 个历史已完成)")
