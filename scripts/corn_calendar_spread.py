# -*- coding: utf-8 -*-
"""
玉米跨期价差分析 (Calendar Spread)

经典玉米跨期组合:
  1-5  (年内陈粮)
  5-9  (陈粮 vs 新粮，最受关注)
  9-1  (新粮跨年)
  9-5  (完整新粮周期)

输出:
  data/corn_calendar_spreads.csv  - 所有价差的时间序列
  data/corn_spread_signals.csv    - 当前 Z-score + 分位数 + 入场信号
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
print(f"加载 {len(df):,} 行 / {df['contract'].nunique()} 合约 / {df['date'].min().date()} ~ {df['date'].max().date()}")

# 透视为宽表: date × contract
wide = df.pivot(index='date', columns='contract', values='close')
wide = wide.sort_index()
print(f"宽表: {wide.shape[0]} 天 × {wide.shape[1]} 合约")

def contract_code(year, month):
    return f"C{year % 100:02d}{month:02d}"

# === 定义所有要追踪的跨期组合 ===
# 每个组合: (近月, 远月, 名称) ， 价差 = 近 - 远 (习惯：近月 - 远月)
pairs = []
for year in range(2019, 2027):
    # 同年内
    pairs.append((contract_code(year, 1), contract_code(year, 5), f'C{year%100:02d}: 1-5'))
    pairs.append((contract_code(year, 5), contract_code(year, 9), f'C{year%100:02d}: 5-9'))
    # 跨年
    pairs.append((contract_code(year, 9), contract_code(year+1, 1), f'C{year%100:02d}9-{(year+1)%100:02d}1'))
    pairs.append((contract_code(year, 9), contract_code(year+1, 5), f'C{year%100:02d}9-{(year+1)%100:02d}5'))

# 过滤掉缺失合约
valid_pairs = []
for n, f, name in pairs:
    if n in wide.columns and f in wide.columns:
        valid_pairs.append((n, f, name))

print(f"\n有效跨期组合 {len(valid_pairs)} 个")

# === 计算每个价差的时间序列 ===
LAST_TRADING_DAY = wide.index.max()
print(f"\n最后交易日: {LAST_TRADING_DAY.date()}")

spreads = {}
historical_rows = []  # 已完成（双合约都已退市或一方退市）
current_rows = []     # 当前可交易（两个合约都在最后交易日有数据）

for near, far, name in valid_pairs:
    s = (wide[near] - wide[far]).dropna()
    if len(s) < 30: continue
    spreads[name] = s

    # 判断"当前可交易"：两合约在最近交易日都还有数据
    both_active = (
        not pd.isna(wide.loc[LAST_TRADING_DAY, near]) and
        not pd.isna(wide.loc[LAST_TRADING_DAY, far])
    )

    mu, sigma = s.mean(), s.std()
    last_val = s.iloc[-1]
    last_z = (last_val - mu) / sigma if sigma > 0 else 0
    last_pct = (s <= last_val).mean() * 100
    last_date = s.index[-1].date()

    if both_active:
        # 当前可交易：取 2026-05-18 当日价差
        cur = wide.loc[LAST_TRADING_DAY, near] - wide.loc[LAST_TRADING_DAY, far]
        z = (cur - mu) / sigma if sigma > 0 else 0
        pct = (s <= cur).mean() * 100
        sig = '🔴 强信号 (|Z|≥2)' if abs(z) >= 2.0 else ('🟡 弱信号 (|Z|≥1.5)' if abs(z) >= 1.5 else '中性')
        direction = '做空近-多远' if z > 0 else '做多近-空远'

        current_rows.append({
            '组合': name,
            '近月': near, '远月': far,
            '样本数': len(s),
            '当日价差': round(cur, 1),
            '历史均值': round(mu, 1),
            'std': round(sigma, 1),
            '最大': round(s.max(), 1),
            '最小': round(s.min(), 1),
            '当前Z': round(z, 2),
            '当前分位': round(pct, 0),
            '信号': sig,
            '方向': direction if abs(z) >= 1.5 else '-',
        })
    else:
        # 历史已完成：记录到期前最终 Z（用于研究均值回归）
        historical_rows.append({
            '组合': name,
            '近月': near, '远月': far,
            '样本数': len(s),
            '终值': round(last_val, 1),
            '终日': str(last_date),
            '均值': round(mu, 1),
            'std': round(sigma, 1),
            '最大': round(s.max(), 1),
            '最小': round(s.min(), 1),
            '终值Z': round(last_z, 2),
            '终值分位': round(last_pct, 0),
        })

# 输出价差时间序列
spread_df = pd.DataFrame(spreads)
spread_df.to_csv(OUT/'corn_calendar_spreads.csv', encoding='utf-8-sig')

# 当前可交易信号
cur_stats = pd.DataFrame(current_rows).sort_values('当前Z', key=lambda x: x.abs(), ascending=False)
cur_stats.to_csv(OUT/'corn_spread_signals_current.csv', encoding='utf-8-sig', index=False)

# 历史回溯
hist_stats = pd.DataFrame(historical_rows).sort_values('终日', ascending=False)
hist_stats.to_csv(OUT/'corn_spread_signals_history.csv', encoding='utf-8-sig', index=False)

print(f"\n{'='*70}")
print(f"=== 当前可交易跨期组合 (在 {LAST_TRADING_DAY.date()} 都活跃) ===")
print(f"{'='*70}")
if len(cur_stats):
    print(cur_stats.to_string(index=False))
else:
    print("无")

print(f"\n{'='*70}")
print(f"=== 历史已退市/部分退市的组合 (按时间倒序，前 10 个) ===")
print(f"{'='*70}")
print(hist_stats.head(10).to_string(index=False))

# === 同类别均值回归特征统计（用历史已完成样本）===
print(f"\n{'='*70}")
print("=== 同类别历史均值回归统计 ===")
print(f"{'='*70}")
all_stats = pd.concat([cur_stats.rename(columns={'当日价差':'终值','当前Z':'终值Z','当前分位':'终值分位'}),
                       hist_stats], ignore_index=True)
for typ_key, label in [('1-5', '同年 1-5 (年初-年中)'),
                       ('5-9', '同年 5-9 (陈粮-新粮)'),
                       ('9-1', '跨年 9-1 (新粮-下年初)'),
                       ('9-5', '跨年 9-5 (新粮全周期)')]:
    if '组合' not in all_stats.columns: continue
    sub = all_stats[all_stats['组合'].str.contains(typ_key, regex=False)]
    if len(sub) == 0: continue
    print(f"\n【{label}】 {len(sub)} 个样本")
    print(f"  历史均值跨年区间: {sub['均值'].min():.0f} ~ {sub['均值'].max():.0f}")
    print(f"  历年 std 区间:    {sub['std'].min():.0f} ~ {sub['std'].max():.0f}")
    print(f"  最大 |终值Z|:     {sub['终值Z'].abs().max():.2f}")

print(f"\n保存:")
print(f"  data/corn_calendar_spreads.csv         ({spread_df.shape[0]} 天 × {spread_df.shape[1]} 价差时间序列)")
print(f"  data/corn_spread_signals_current.csv   ({len(cur_stats)} 个当前可交易)")
print(f"  data/corn_spread_signals_history.csv   ({len(hist_stats)} 个历史已完成)")

# === 当前所有活跃合约的两两配对 ===
active = [c for c in wide.columns if not pd.isna(wide.loc[LAST_TRADING_DAY, c])]
print(f"\n{'='*70}")
print(f"=== 当前活跃合约 {len(active)} 个: {active} ===")
print(f"=== 所有相邻配对 + 远期配对的当日价差 + Z-score ===")
print(f"{'='*70}")
active_rows = []
for i, near in enumerate(active):
    for far in active[i+1:]:
        s = (wide[near] - wide[far]).dropna()
        if len(s) < 30: continue
        cur = wide.loc[LAST_TRADING_DAY, near] - wide.loc[LAST_TRADING_DAY, far]
        mu, sigma = s.mean(), s.std()
        z = (cur - mu) / sigma if sigma > 0 else 0
        pct = (s <= cur).mean() * 100
        sig = '🔴 强信号 (|Z|≥2)' if abs(z) >= 2.0 else ('🟡 弱信号 (|Z|≥1.5)' if abs(z) >= 1.5 else '中性')
        direction = '做空近-多远' if z > 0 else '做多近-空远'
        active_rows.append({
            '组合': f"{near}-{far}",
            '近月': near, '远月': far,
            '样本': len(s),
            '当前价差': round(cur, 1),
            '均值': round(mu, 1),
            'std': round(sigma, 1),
            '最大': round(s.max(), 1),
            '最小': round(s.min(), 1),
            'Z': round(z, 2),
            '分位': round(pct, 0),
            '信号': sig,
            '方向': direction if abs(z) >= 1.5 else '-',
        })
active_df = pd.DataFrame(active_rows).sort_values('Z', key=lambda x: x.abs(), ascending=False)
active_df.to_csv(OUT/'corn_spread_active_pairs.csv', encoding='utf-8-sig', index=False)
print(active_df.to_string(index=False))
print(f"\n  → 保存: data/corn_spread_active_pairs.csv ({len(active_df)} 个活跃配对)")
