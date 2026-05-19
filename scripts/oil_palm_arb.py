# -*- coding: utf-8 -*-
"""
豆油 Y vs 棕榈油 P 跨品种套利 (油脂替代)
逻辑: 两者都是食用油 + 工业油脂, 高度替代
Y 偏高端 (健康/瓶装), P 偏低端 (餐饮/工业), 长期价差 Y-P 在 -500~+1000 区间
价差极端时套利
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

# === 1. 主连数据 ===
print("拉取豆油 Y0 + 棕榈油 P0 主连日线...")
y = ak.futures_main_sina(symbol="Y0")
p = ak.futures_main_sina(symbol="P0")
for df in (y, p):
    df.columns = [col.lower() for col in df.columns]
    df.rename(columns={'日期': 'date', '收盘价': 'close'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])

y = y[['date', 'close']].rename(columns={'close': 'y_close'}).set_index('date')
p = p[['date', 'close']].rename(columns={'close': 'p_close'}).set_index('date')

m = y.join(p, how='inner').dropna()
m['spread'] = m['y_close'] - m['p_close']
m['ratio'] = m['y_close'] / m['p_close']
print(f"Y0+P0 重叠 {len(m)} 天 ({m.index.min().date()} ~ {m.index.max().date()})")

# === 2. 价差统计 ===
mu, sigma = m['spread'].mean(), m['spread'].std()
cur_spread = m['spread'].iloc[-1]
cur_z = (cur_spread - mu) / sigma
cur_pct = (m['spread'] <= cur_spread).mean() * 100

print(f"\n=== Y-P 价差全样本统计 ===")
print(f"  样本天数: {len(m)}")
print(f"  价差均值: {mu:.0f} 元/吨")
print(f"  价差 std: {sigma:.0f} 元/吨")
print(f"  价差范围: {m['spread'].min():.0f} ~ {m['spread'].max():.0f}")
print(f"  当前价差: {cur_spread:.0f} 元/吨 ({m.index[-1].date()})")
print(f"  当前 Z:   {cur_z:+.2f}")
print(f"  当前分位: {cur_pct:.0f}%")

# 比值
mu_r, sd_r = m['ratio'].mean(), m['ratio'].std()
cur_r = m['ratio'].iloc[-1]
cur_rz = (cur_r - mu_r) / sd_r
print(f"\n=== Y/P 比值 ===")
print(f"  均值: {mu_r:.3f}, std: {sd_r:.3f}")
print(f"  当前: {cur_r:.3f}, Z: {cur_rz:+.2f}")

# === 3. 分时段统计 ===
m['year'] = m.index.year
print(f"\n=== 分年价差均值 ===")
yearly = m.groupby('year').agg(均值=('spread','mean'),std=('spread','std'),
                                最小=('spread','min'),最大=('spread','max'),
                                样本=('spread','count')).round(0)
print(yearly.to_string())

# === 4. 保存 ===
m.reset_index().to_csv(OUT_DATA/'oil_palm_spread.csv', encoding='utf-8-sig', index=False)

# === 5. 画图 ===
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

ax = axes[0]
ax.plot(m.index, m['y_close'], label='Y (豆油)', color='#FFB300', linewidth=1.2)
ax.plot(m.index, m['p_close'], label='P (棕榈油)', color='#E64A19', linewidth=1.2)
ax.set_ylabel('价格 (元/吨)')
ax.set_title('豆油 Y0 vs 棕榈油 P0 主连日线')
ax.legend(); ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(m.index, m['spread'], color='#1976D2', linewidth=1.0)
ax.axhline(mu, color='red', linestyle='--', label=f'均值 {mu:.0f}')
ax.axhline(mu + sigma, color='gray', linestyle=':', alpha=0.7, label=f'+1σ {mu+sigma:.0f}')
ax.axhline(mu - sigma, color='gray', linestyle=':', alpha=0.7, label=f'-1σ {mu-sigma:.0f}')
ax.axhline(mu + 2*sigma, color='orange', linestyle=':', alpha=0.7, label=f'+2σ {mu+2*sigma:.0f}')
ax.axhline(mu - 2*sigma, color='orange', linestyle=':', alpha=0.7, label=f'-2σ {mu-2*sigma:.0f}')
ax.set_ylabel('Y - P 价差 (元/吨)')
ax.set_title(f'Y-P 价差 (当前 {cur_spread:.0f} / Z={cur_z:+.2f} / {cur_pct:.0f}%分位)')
ax.legend(loc='best', fontsize=9); ax.grid(alpha=0.3)

ax = axes[2]
m['roll_mean'] = m['spread'].rolling(60).mean()
m['roll_std'] = m['spread'].rolling(60).std()
m['roll_z'] = (m['spread'] - m['roll_mean']) / m['roll_std']
ax.plot(m.index, m['roll_z'], color='#7B1FA2', linewidth=1.0)
ax.axhline(0, color='black', linewidth=0.5)
ax.axhline(2, color='red', linestyle='--', alpha=0.7, label='±2σ 入场阈值')
ax.axhline(-2, color='red', linestyle='--', alpha=0.7)
ax.axhline(1.5, color='orange', linestyle=':', alpha=0.5)
ax.axhline(-1.5, color='orange', linestyle=':', alpha=0.5)
ax.set_ylabel('60 日滚动 Z-score')
ax.set_title('短期入场信号')
ax.legend(); ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_FIG/'oil_palm_arb.png', dpi=140, bbox_inches='tight')
print(f"\n已保存图: {OUT_FIG/'oil_palm_arb.png'}")
plt.close()

# === 6. 历史 |Z|>2 触发回溯 ===
m = m.dropna(subset=['roll_z'])
events = m[m['roll_z'].abs() > 2].copy()
print(f"\n=== 60 日滚动 Z>2 历史触发事件: {len(events)} 次 ===")
if len(events):
    events['gap'] = events.index.to_series().diff().dt.days
    events['cluster'] = (events['gap'] > 5).cumsum()
    grouped = []
    for cid, sub in events.groupby('cluster'):
        z_extreme = sub.loc[sub['roll_z'].abs().idxmax(), 'roll_z']
        grouped.append({
            '起始': sub.index.min().date(),
            '终止': sub.index.max().date(),
            '天数': len(sub),
            '极值Z': round(z_extreme, 2),
            '极值价差': round(sub.loc[sub['roll_z'].abs().idxmax(), 'spread'], 0),
        })
    cl_df = pd.DataFrame(grouped)
    print(cl_df.to_string(index=False))
    cl_df.to_csv(OUT_DATA/'oil_palm_signal_events.csv', encoding='utf-8-sig', index=False)
