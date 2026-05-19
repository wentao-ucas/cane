# -*- coding: utf-8 -*-
"""CBOT 玉米(ZC=F) 月度数据 + 与大商所玉米对比"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path('data'); OUT.mkdir(exist_ok=True)

# === CBOT 玉米 ===
cb = yf.download('ZC=F', start='2005-01-01', end='2026-05-19', auto_adjust=False, progress=False)
cb.columns = cb.columns.get_level_values(0)
cb = cb[['Open','High','Low','Close']].rename(columns=str.lower)
cb.index.name = 'date'

print(f"CBOT 玉米日线: {cb.index.min().date()} ~ {cb.index.max().date()}, {len(cb)} 行, 价格 {cb['close'].min():.2f}-{cb['close'].max():.2f} 美分/蒲")

# 月度
cb_m = cb['close'].resample('ME').last().to_frame('close_cbot')
cb_m['ret_cbot'] = cb_m['close_cbot'].pct_change() * 100
cb_m['year']  = cb_m.index.year
cb_m['month'] = cb_m.index.month
cb_m.round(3).to_csv(OUT/'cbot_corn_monthly.csv', encoding='utf-8-sig')

# === 大商所玉米月度（已有） ===
c = pd.read_csv('data/corn_monthly.csv', parse_dates=['date'])
c = c.set_index('date')[['close','ret']].rename(columns={'close':'close_c','ret':'ret_c'})

# === 合并 ===
m = c.join(cb_m[['close_cbot','ret_cbot']], how='outer')
m['diff_ret'] = (m['ret_c'] - m['ret_cbot']).round(2)
m.round(2).to_csv(OUT/'corn_cbot_vs_c_monthly.csv', encoding='utf-8-sig')

# === CBOT 季节性 ===
gd = cb_m.dropna(subset=['ret_cbot']).groupby('month')['ret_cbot']
seas = pd.DataFrame({
    'CBOT平均%':  gd.mean().round(2),
    'CBOT中位%':  gd.median().round(2),
    'CBOT胜率%':  (gd.apply(lambda x: (x > 0).mean()) * 100).round(1),
    'CBOT最大%':  gd.max().round(2),
    'CBOT最小%':  gd.min().round(2),
    '样本':       gd.count(),
})
print("\n=== CBOT 玉米 月度季节性 (2005-2026, n≈21) ===")
print(seas.to_string())
seas.to_csv(OUT/'cbot_corn_seasonality.csv', encoding='utf-8-sig')

# === 内外盘对比 ===
both = m.dropna(subset=['ret_c','ret_cbot']).copy()
print(f"\n重叠月份 {len(both)} 个")
print(f"大商所玉米 vs CBOT 玉米 月度涨跌幅相关系数: {both[['ret_c','ret_cbot']].corr().iloc[0,1]:.3f}")

# 分时段相关性
def corr_period(start, end):
    sub = both.loc[start:end]
    return f"  {start}~{end}: n={len(sub):>3}, corr={sub[['ret_c','ret_cbot']].corr().iloc[0,1]:+.3f}"
print("\n分时段相关性:")
for s,e in [('2005-01','2010-12'),('2011-01','2015-12'),('2016-01','2020-12'),('2021-01','2026-05')]:
    print(corr_period(s, e))

print("\n=== 内外盘月度背离最大的 15 个月 (|大商所-CBOT|) ===")
both['abs_diff'] = both['diff_ret'].abs()
top = both.sort_values('abs_diff', ascending=False).head(15)
print(top[['ret_c','ret_cbot','diff_ret']].round(2).to_string())
top[['ret_c','ret_cbot','diff_ret']].to_csv(OUT/'corn_cbot_divergence.csv', encoding='utf-8-sig')

# === 内外盘联合季节性 ===
print("\n=== 内外盘同步涨/跌 vs 背离 (按月份统计) ===")
def joint(mo):
    sub = both[both.index.month == mo]
    both_up   = ((sub['ret_c']>0) & (sub['ret_cbot']>0)).sum()
    both_dn   = ((sub['ret_c']<0) & (sub['ret_cbot']<0)).sum()
    c_up_cb_dn = ((sub['ret_c']>0) & (sub['ret_cbot']<0)).sum()
    c_dn_cb_up = ((sub['ret_c']<0) & (sub['ret_cbot']>0)).sum()
    return both_up, both_dn, c_up_cb_dn, c_dn_cb_up, len(sub)
rows = []
for mo in range(1,13):
    bu, bd, cui, cdi, n = joint(mo)
    rows.append([mo, n, bu, bd, cui, cdi])
joint_df = pd.DataFrame(rows, columns=['月','样本','同涨','同跌','C涨/CBOT跌','C跌/CBOT涨'])
print(joint_df.to_string(index=False))
joint_df.to_csv(OUT/'corn_cbot_joint.csv', encoding='utf-8-sig', index=False)

print(f"\n文件已写入 data/: cbot_corn_monthly.csv, corn_cbot_vs_c_monthly.csv, cbot_corn_seasonality.csv, corn_cbot_divergence.csv, corn_cbot_joint.csv")
