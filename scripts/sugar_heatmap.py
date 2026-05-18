# -*- coding: utf-8 -*-
"""白糖月度涨跌热力图: 年×月"""
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

pv = pd.read_csv('data/sugar_monthly_pivot.csv', index_col=0)
pv.columns = [int(c) for c in pv.columns]

fig, ax = plt.subplots(figsize=(12, 10))
vmax = np.nanmax(np.abs(pv.values))
im = ax.imshow(pv.values, cmap='RdYlGn', vmin=-vmax, vmax=vmax, aspect='auto')

ax.set_xticks(range(12))
ax.set_xticklabels([f'{m}月' for m in range(1, 13)])
ax.set_yticks(range(len(pv.index)))
ax.set_yticklabels(pv.index)

for i in range(pv.shape[0]):
    for j in range(pv.shape[1]):
        v = pv.values[i, j]
        if not np.isnan(v):
            color = 'white' if abs(v) > vmax * 0.55 else 'black'
            ax.text(j, i, f'{v:.1f}', ha='center', va='center', color=color, fontsize=8)

cbar = plt.colorbar(im, ax=ax, shrink=0.7)
cbar.set_label('月涨跌幅 %')
ax.set_title('白糖主连 SR0 月度涨跌幅 (2006-01 ~ 2026-05)', fontsize=14, pad=12)
ax.set_xlabel('月份')
ax.set_ylabel('年份')

Path('output').mkdir(exist_ok=True)
out = 'output/sugar_monthly_heatmap.png'
plt.tight_layout()
plt.savefig(out, dpi=140, bbox_inches='tight')
print(f'已保存: {out}')
