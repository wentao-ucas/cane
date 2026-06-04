# -*- coding: utf-8 -*-
"""
玉米做多最佳建仓月：每月底建仓，持有 1/2/3/6 个月的前瞻收益
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np

m = pd.read_csv('data/corn_monthly.csv', parse_dates=['date']).set_index('date')
m = m.sort_index()

# 前瞻收益（在当月底建仓，持有 N 个月）
for n in [1, 2, 3, 6]:
    m[f'fwd_{n}'] = (m['close'].shift(-n) / m['close'] - 1) * 100

print("=" * 80)
print("玉米做多：每月底建仓，未来 N 个月收益 (2005-2026, 21年)")
print("=" * 80)

rows = []
for mo in range(1, 13):
    sub = m[m['month'] == mo]
    r = {'建仓月(月底)': f'{mo}月底'}
    for n in [1, 2, 3, 6]:
        vals = sub[f'fwd_{n}'].dropna()
        r[f'未来{n}月均值'] = round(vals.mean(), 1)
        r[f'未来{n}月胜率'] = round((vals > 0).mean() * 100, 0)
    rows.append(r)

res = pd.DataFrame(rows)
# 只显示均值
mean_cols = ['建仓月(月底)', '未来1月均值', '未来2月均值', '未来3月均值', '未来6月均值']
print("\n【未来收益 均值 %】")
print(res[mean_cols].to_string(index=False))

win_cols = ['建仓月(月底)', '未来1月胜率', '未来2月胜率', '未来3月胜率', '未来6月胜率']
print("\n【未来收益 胜率 %】")
print(res[win_cols].to_string(index=False))

# 综合评分：未来3月 + 未来6月 的均值和胜率
res['综合分'] = (res['未来3月均值'] + res['未来6月均值']) / 2
best = res.sort_values('综合分', ascending=False)
print("\n" + "=" * 80)
print("【按 (未来3月+6月)/2 综合排序 — 最佳做多建仓月】")
print("=" * 80)
print(best[['建仓月(月底)', '未来3月均值', '未来3月胜率', '未来6月均值', '未来6月胜率', '综合分']].to_string(index=False))

res.to_csv('data/corn_entry_month.csv', encoding='utf-8-sig', index=False)
print("\n保存: data/corn_entry_month.csv")
