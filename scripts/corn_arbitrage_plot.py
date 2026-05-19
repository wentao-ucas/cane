# -*- coding: utf-8 -*-
"""玉米跨期 + 蝴蝶价差可视化"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False

OUT = Path('output'); OUT.mkdir(exist_ok=True)

# ===== 1. 跨期价差 4 大类对比图 =====
spreads = pd.read_csv('data/corn_calendar_spreads.csv', parse_dates=['date']).set_index('date')

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
categories = [
    ('1-5', '同年 1-5 价差 (年初 vs 年中陈粮)'),
    ('5-9', '同年 5-9 价差 (陈粮 vs 新粮，最经典)'),
    ('9-1', '跨年 9-1 价差 (新粮 vs 下年初)'),
    ('9-5', '跨年 9-5 价差 (新粮全周期)'),
]
for (key, title), ax in zip(categories, axes.flatten()):
    cols = [c for c in spreads.columns if key in c]
    for col in cols:
        s = spreads[col].dropna()
        ax.plot(s.index, s.values, label=col, linewidth=1.2, alpha=0.85)
    ax.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    ax.set_title(title)
    ax.set_ylabel('价差 (元/吨)')
    ax.legend(loc='lower left', fontsize=8, ncol=2)
    ax.grid(alpha=0.3)

plt.suptitle('玉米跨期价差 4 大类（按年份叠加）', fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig(OUT/'corn_calendar_spread_chart.png', dpi=140, bbox_inches='tight')
print(f"已保存: {OUT/'corn_calendar_spread_chart.png'}")
plt.close()

# ===== 2. 当前活跃合约的价差曲线（实操菜单）=====
fig, ax = plt.subplots(figsize=(14, 7))
active_cols = ['C2607-C2609', 'C2607-C2611', 'C2607-C2701',
               'C2609-C2611', 'C2609-C2701', 'C2609-C2703',
               'C2611-C2701', 'C2611-C2703',
               'C2701-C2703']
df_contracts = pd.read_csv('data/corn_contracts_daily.csv', parse_dates=['date'])
wide = df_contracts.pivot(index='date', columns='contract', values='close').sort_index()
for pair in active_cols:
    near, far = pair.split('-')
    if near in wide.columns and far in wide.columns:
        s = (wide[near] - wide[far]).dropna()
        if len(s) >= 30:
            ax.plot(s.index, s.values, label=pair, linewidth=1.3)
ax.axhline(0, color='black', linewidth=0.5)
ax.set_title('当前活跃合约 5 个 - 9 个相邻配对价差 (近 - 远)')
ax.set_ylabel('价差 (元/吨)')
ax.legend(loc='upper left', fontsize=9, ncol=3)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT/'corn_active_spreads_chart.png', dpi=140, bbox_inches='tight')
print(f"已保存: {OUT/'corn_active_spreads_chart.png'}")
plt.close()

# ===== 3. 蝴蝶价差 - 5 大经典组合按年份叠加 =====
fly = pd.read_csv('data/corn_butterfly_spreads.csv', parse_dates=['date']).set_index('date')

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fly_categories = [
    ('1-5-9', '1-5-9 蝴蝶 (年内三大主力)'),
    ('3-5-7', '3-5-7 蝴蝶 (春季)'),
    ('5-7-9', '5-7-9 蝴蝶 (春夏)'),
    ('7-9-11', '7-9-11 蝴蝶 (秋收前后)'),
    ('9-11-1+', '9-11-1+ 蝴蝶 (新粮收割+冬储)'),
    ('5-9-1+', '5-9-1+ 蝴蝶 (新粮过渡跨年)'),
]
for (key, title), ax in zip(fly_categories, axes.flatten()):
    cols = [c for c in fly.columns if key in c]
    for col in cols:
        s = fly[col].dropna()
        ax.plot(s.index, s.values, label=col, linewidth=1.1, alpha=0.85)
    ax.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    ax.set_title(title)
    ax.set_ylabel('fly (元/吨)')
    ax.legend(loc='best', fontsize=7, ncol=2)
    ax.grid(alpha=0.3)

plt.suptitle('玉米蝴蝶价差 6 大类（fly = 2×中 - 近 - 远）', fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig(OUT/'corn_butterfly_chart.png', dpi=140, bbox_inches='tight')
print(f"已保存: {OUT/'corn_butterfly_chart.png'}")
plt.close()

# ===== 4. 当前价差结构 - 远期曲线 (term structure) =====
df_last = df_contracts[df_contracts['date'] == df_contracts['date'].max()].sort_values('contract')
active = df_last[df_last['hold'] > 0] if 'hold' in df_last.columns else df_last
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(active['contract'], active['close'], 'o-', markersize=10, linewidth=2, color='#2E7D32')
for _, r in active.iterrows():
    ax.annotate(f'{r["close"]:.0f}', (r['contract'], r['close']),
                textcoords='offset points', xytext=(0, 10), ha='center', fontsize=10)
ax.set_title(f'玉米远期曲线 (Term Structure) - {df_contracts["date"].max().date()}')
ax.set_xlabel('合约代码')
ax.set_ylabel('收盘价 (元/吨)')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT/'corn_term_structure.png', dpi=140, bbox_inches='tight')
print(f"已保存: {OUT/'corn_term_structure.png'}")
plt.close()

print("\n4 张图已保存到 output/")
