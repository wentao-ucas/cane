# -*- coding: utf-8 -*-
"""按月分组: 每个月在各年的涨跌情况"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from pathlib import Path

m = pd.read_csv('data/sugar_monthly.csv')
m['date'] = pd.to_datetime(m['date'])
m = m.dropna(subset=['ret'])

Path('output').mkdir(exist_ok=True)
lines = []
for month in range(1, 13):
    sub = m[m['month'] == month].sort_values('year')
    up = (sub['ret'] > 0).sum()
    dn = (sub['ret'] < 0).sum()
    avg = sub['ret'].mean()
    lines.append(f"\n===== {month}月  样本{len(sub)}年  涨{up}/跌{dn}  均值{avg:+.2f}%  胜率{up/len(sub)*100:.0f}% =====")
    for _, r in sub.iterrows():
        arrow = '↑' if r['ret'] > 0 else '↓'
        bar = '█' * min(int(abs(r['ret'])), 20)
        lines.append(f"  {int(r['year'])}年{month:>2}月: {r['ret']:+7.2f}%  {arrow} {bar}")

out = 'output/sugar_by_month.txt'
text = '\n'.join(lines)
Path(out).write_text(text, encoding='utf-8')
print(text)
print(f"\n已保存: {out}")
