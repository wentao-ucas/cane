# -*- coding: utf-8 -*-
"""ICE 11号原糖(SB=F) 月度数据 + 与郑糖对比"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path('data'); OUT.mkdir(exist_ok=True)

# === ICE 11号糖 ===
ice = yf.download('SB=F', start='2006-01-01', end='2026-05-19', auto_adjust=False, progress=False)
ice.columns = ice.columns.get_level_values(0)  # 拍平 MultiIndex
ice = ice[['Open','High','Low','Close']].rename(columns=str.lower)
ice.index.name = 'date'

print(f"ICE 日线: {ice.index.min().date()} ~ {ice.index.max().date()}, {len(ice)} 行, 价格 {ice['close'].min():.2f}-{ice['close'].max():.2f} 美分/磅")

# 月度
ice_m = ice['close'].resample('ME').last().to_frame('close_ice')
ice_m['ret_ice'] = ice_m['close_ice'].pct_change() * 100
ice_m['year']  = ice_m.index.year
ice_m['month'] = ice_m.index.month
ice_m.round(3).to_csv(OUT/'ice_sugar_monthly.csv', encoding='utf-8-sig')

# === 郑糖月度（已有） ===
sr = pd.read_csv('data/sugar_monthly.csv', parse_dates=['date'])
sr = sr.set_index('date')[['close','ret']].rename(columns={'close':'close_sr','ret':'ret_sr'})

# === 合并 ===
m = sr.join(ice_m[['close_ice','ret_ice']], how='outer')
m['diff_ret'] = (m['ret_sr'] - m['ret_ice']).round(2)
m.round(2).to_csv(OUT/'sugar_ice_vs_sr_monthly.csv', encoding='utf-8-sig')

# === ICE 季节性 ===
gd = ice_m.dropna(subset=['ret_ice']).groupby('month')['ret_ice']
seas = pd.DataFrame({
    'ICE平均%':  gd.mean().round(2),
    'ICE中位%':  gd.median().round(2),
    'ICE胜率%':  (gd.apply(lambda x: (x > 0).mean()) * 100).round(1),
    'ICE最大%':  gd.max().round(2),
    'ICE最小%':  gd.min().round(2),
    '样本':       gd.count(),
})
print("\n=== ICE 11号糖 月度季节性 (2006-2026, n≈20) ===")
print(seas.to_string())
seas.to_csv(OUT/'ice_sugar_seasonality.csv', encoding='utf-8-sig')

# === 内外盘对比 ===
both = m.dropna(subset=['ret_sr','ret_ice']).copy()
print(f"\n重叠月份 {len(both)} 个")
print(f"郑糖 vs ICE 月度涨跌幅相关系数: {both[['ret_sr','ret_ice']].corr().iloc[0,1]:.3f}")

# 分时段相关性
def corr_period(start, end):
    sub = both.loc[start:end]
    return f"  {start}~{end}: n={len(sub):>3}, corr={sub[['ret_sr','ret_ice']].corr().iloc[0,1]:+.3f}"
print("\n分时段相关性:")
for s,e in [('2006-01','2010-12'),('2011-01','2015-12'),('2016-01','2020-12'),('2021-01','2026-05')]:
    print(corr_period(s, e))

print("\n=== 内外盘月度背离最大的 15 个月 (|郑糖-ICE|) ===")
both['abs_diff'] = both['diff_ret'].abs()
top = both.sort_values('abs_diff', ascending=False).head(15)
print(top[['ret_sr','ret_ice','diff_ret']].round(2).to_string())
top[['ret_sr','ret_ice','diff_ret']].to_csv(OUT/'sugar_ice_sr_divergence.csv', encoding='utf-8-sig')

# === 内外盘联合季节性: 两边都涨/都跌的月份 ===
print("\n=== 内外盘同步涨/跌 vs 背离 (按月份统计) ===")
def joint(row, mo):
    sub = both[both.index.month == mo]
    both_up   = ((sub['ret_sr']>0) & (sub['ret_ice']>0)).sum()
    both_dn   = ((sub['ret_sr']<0) & (sub['ret_ice']<0)).sum()
    sr_up_ic_dn = ((sub['ret_sr']>0) & (sub['ret_ice']<0)).sum()
    sr_dn_ic_up = ((sub['ret_sr']<0) & (sub['ret_ice']>0)).sum()
    return both_up, both_dn, sr_up_ic_dn, sr_dn_ic_up, len(sub)
rows = []
for mo in range(1,13):
    bu, bd, sui, sdi, n = joint(None, mo)
    rows.append([mo, n, bu, bd, sui, sdi])
joint_df = pd.DataFrame(rows, columns=['月','样本','同涨','同跌','SR涨/IC跌','SR跌/IC涨'])
print(joint_df.to_string(index=False))
joint_df.to_csv(OUT/'sugar_ice_sr_joint.csv', encoding='utf-8-sig', index=False)

print(f"\n文件已写入 data/: ice_sugar_monthly.csv, sugar_ice_vs_sr_monthly.csv, ice_sugar_seasonality.csv, sugar_ice_sr_divergence.csv, sugar_ice_sr_joint.csv")
