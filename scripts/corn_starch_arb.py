# -*- coding: utf-8 -*-
"""
玉米 vs 玉米淀粉 跨品种套利 (C-CS 产业链)
逻辑: 玉米 + 加工费 → 玉米淀粉, 价差 CS-C 长期稳定
价差扩大→做空淀粉做多玉米, 价差收窄→做多淀粉做空玉米
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False

OUT_DATA = Path('data'); OUT_DATA.mkdir(exist_ok=True)
OUT_FIG = Path('output'); OUT_FIG.mkdir(exist_ok=True)

# === 1. 主连数据：长期回测 ===
print("拉取玉米 C0 + 玉米淀粉 CS0 主连日线...")
c = ak.futures_main_sina(symbol="C0")
cs = ak.futures_main_sina(symbol="CS0")
for df in (c, cs):
    df.columns = [col.lower() for col in df.columns]
    df.rename(columns={'日期': 'date', '收盘价': 'close'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])

c = c[['date', 'close']].rename(columns={'close': 'c_close'}).set_index('date')
cs = cs[['date', 'close']].rename(columns={'close': 'cs_close'}).set_index('date')

m = c.join(cs, how='inner').dropna()
m['spread'] = m['cs_close'] - m['c_close']
m['ratio'] = m['cs_close'] / m['c_close']
print(f"C0+CS0 重叠 {len(m)} 天 ({m.index.min().date()} ~ {m.index.max().date()})")

# === 2. 价差统计 ===
mu, sigma = m['spread'].mean(), m['spread'].std()
cur_spread = m['spread'].iloc[-1]
cur_z = (cur_spread - mu) / sigma
cur_pct = (m['spread'] <= cur_spread).mean() * 100

print(f"\n=== CS-C 价差全样本统计 ===")
print(f"  样本天数: {len(m)}")
print(f"  价差均值: {mu:.0f} 元/吨")
print(f"  价差 std: {sigma:.0f} 元/吨")
print(f"  价差范围: {m['spread'].min():.0f} ~ {m['spread'].max():.0f}")
print(f"  当前价差: {cur_spread:.0f} 元/吨 ({m.index[-1].date()})")
print(f"  当前 Z:   {cur_z:+.2f}")
print(f"  当前分位: {cur_pct:.0f}%")

# === 3. 分时段统计（看价差是否漂移）===
print(f"\n=== 分年价差均值（看产业利润漂移）===")
m['year'] = m.index.year
yearly = m.groupby('year').agg(均值=('spread','mean'),std=('spread','std'),
                                最小=('spread','min'),最大=('spread','max'),
                                样本=('spread','count')).round(0)
print(yearly.to_string())

# === 4. 当前活跃同期合约对（CS2607 vs C2607 等）===
print(f"\n=== 拉当前活跃 CS+C 同期合约 ===")
CORN_MONTHS = [1, 3, 5, 7, 9, 11]
current_year = 2026
pairs = []
for y in [current_year, current_year + 1]:
    for mo in CORN_MONTHS:
        yy = f"{y % 100:02d}"
        pairs.append((f"C{yy}{mo:02d}", f"CS{yy}{mo:02d}"))

active = []
for c_code, cs_code in pairs:
    try:
        c_df = ak.futures_zh_daily_sina(symbol=c_code)
        cs_df = ak.futures_zh_daily_sina(symbol=cs_code)
        if c_df is None or cs_df is None or len(c_df) == 0 or len(cs_df) == 0:
            continue
        c_df['date'] = pd.to_datetime(c_df['date'])
        cs_df['date'] = pd.to_datetime(cs_df['date'])
        c_last = c_df.iloc[-1]
        cs_last = cs_df.iloc[-1]
        # 同一日有数据才算
        common_dates = sorted(set(c_df['date']) & set(cs_df['date']))
        if len(common_dates) < 30: continue
        merged = pd.merge(c_df[['date','close']].rename(columns={'close':'c'}),
                          cs_df[['date','close']].rename(columns={'close':'cs'}),
                          on='date').sort_values('date')
        merged['spread'] = merged['cs'] - merged['c']
        last = merged.iloc[-1]
        mu_p = merged['spread'].mean()
        sd_p = merged['spread'].std()
        z = (last['spread'] - mu_p) / sd_p if sd_p > 0 else 0
        pct = (merged['spread'] <= last['spread']).mean() * 100
        active.append({
            '合约对': f'{c_code} ↔ {cs_code}',
            '日期': str(last['date'].date()),
            'C 价': last['c'], 'CS 价': last['cs'],
            'CS-C 价差': round(last['spread'], 0),
            '历史均值': round(mu_p, 0),
            'std': round(sd_p, 0),
            'Z': round(z, 2),
            '分位': round(pct, 0),
            '样本': len(merged),
        })
        print(f"  {c_code}↔{cs_code}: {len(merged)} 天, 当前 CS-C={last['spread']:.0f}, Z={z:+.2f}")
    except Exception as e:
        continue

active_df = pd.DataFrame(active)
if len(active_df):
    active_df['信号'] = active_df['Z'].apply(
        lambda z: '🔴 强信号(|Z|≥2)' if abs(z) >= 2 else ('🟡 弱信号(|Z|≥1.5)' if abs(z) >= 1.5 else '中性'))
    active_df['方向'] = active_df['Z'].apply(
        lambda z: '卖CS+买C' if z > 1.5 else ('买CS+卖C' if z < -1.5 else '-'))
    active_df.to_csv(OUT_DATA/'corn_starch_active_pairs.csv', encoding='utf-8-sig', index=False)

# === 5. 保存主连价差时间序列 ===
m.reset_index().to_csv(OUT_DATA/'corn_starch_spread.csv', encoding='utf-8-sig', index=False)

# === 6. 画图 ===
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# 上图：CS 和 C 两条价格曲线
ax = axes[0]
ax.plot(m.index, m['cs_close'], label='CS (玉米淀粉)', color='#FF8C00', linewidth=1.2)
ax.plot(m.index, m['c_close'], label='C (玉米)', color='#2E7D32', linewidth=1.2)
ax.set_ylabel('价格 (元/吨)')
ax.set_title('玉米 C0 vs 玉米淀粉 CS0 主连日线')
ax.legend(); ax.grid(alpha=0.3)

# 中图：价差 + 均值带
ax = axes[1]
ax.plot(m.index, m['spread'], color='#1976D2', linewidth=1.2)
ax.axhline(mu, color='red', linestyle='--', label=f'均值 {mu:.0f}')
ax.axhline(mu + sigma, color='gray', linestyle=':', alpha=0.7, label=f'+1σ {mu+sigma:.0f}')
ax.axhline(mu - sigma, color='gray', linestyle=':', alpha=0.7, label=f'-1σ {mu-sigma:.0f}')
ax.axhline(mu + 2*sigma, color='orange', linestyle=':', alpha=0.7, label=f'+2σ {mu+2*sigma:.0f}')
ax.axhline(mu - 2*sigma, color='orange', linestyle=':', alpha=0.7, label=f'-2σ {mu-2*sigma:.0f}')
ax.set_ylabel('CS - C 价差 (元/吨)')
ax.set_title(f'价差时间序列 (当前 {cur_spread:.0f} / Z={cur_z:+.2f} / {cur_pct:.0f}%分位)')
ax.legend(loc='best', fontsize=9); ax.grid(alpha=0.3)

# 下图：rolling 60 日 Z-score
ax = axes[2]
m['roll_mean'] = m['spread'].rolling(60).mean()
m['roll_std'] = m['spread'].rolling(60).std()
m['roll_z'] = (m['spread'] - m['roll_mean']) / m['roll_std']
ax.plot(m.index, m['roll_z'], color='#7B1FA2', linewidth=1.0)
ax.axhline(0, color='black', linewidth=0.5)
ax.axhline(2, color='red', linestyle='--', alpha=0.7, label='+2σ 入场')
ax.axhline(-2, color='red', linestyle='--', alpha=0.7, label='-2σ 入场')
ax.axhline(1.5, color='orange', linestyle=':', alpha=0.5)
ax.axhline(-1.5, color='orange', linestyle=':', alpha=0.5)
ax.set_ylabel('60 日滚动 Z-score')
ax.set_title('短期入场信号（突破 ±2 入场）')
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_FIG/'corn_starch_arb.png', dpi=140, bbox_inches='tight')
print(f"\n已保存图: {OUT_FIG/'corn_starch_arb.png'}")
plt.close()

# === 7. 历史信号事件回溯：|滚动Z|>2 触发次数 ===
m = m.dropna(subset=['roll_z'])
events = m[m['roll_z'].abs() > 2].copy()
print(f"\n=== 60 日滚动 Z>2 历史触发事件: {len(events)} 次 ===")
# 合并连续触发
if len(events):
    events['gap'] = events.index.to_series().diff().dt.days
    events['cluster'] = (events['gap'] > 5).cumsum()
    grouped = []
    for cid, sub in events.groupby('cluster'):
        idx_extreme = sub['roll_z'].abs().idxmax()
        grouped.append({
            '起始': sub.index.min().date(),
            '终止': sub.index.max().date(),
            '天数': len(sub),
            '极值Z': round(sub.loc[idx_extreme, 'roll_z'], 2),
            '极值价差': round(sub.loc[idx_extreme, 'spread'], 0),
        })
    cl_df = pd.DataFrame(grouped)
    cl_df.to_csv(OUT_DATA/'corn_starch_signal_events.csv', encoding='utf-8-sig', index=False)
    print(f"\n=== 历史触发事件 (合并连续) Top 15 by |Z| ===")
    print(cl_df.iloc[cl_df['极值Z'].abs().sort_values(ascending=False).index[:15]].to_string(index=False))
