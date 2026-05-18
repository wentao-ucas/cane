# -*- coding: utf-8 -*-
"""把 ICE 月度数据合并到郑糖月度 CSV"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from pathlib import Path

sr = pd.read_csv('data/sugar_monthly.csv', parse_dates=['date']).set_index('date')
ic = pd.read_csv('data/ice_sugar_monthly.csv', parse_dates=['date']).set_index('date')

# 郑糖列: close, open, high, low, ret, year, month
# ICE 列: close_ice, ret_ice, year, month
ic = ic[['close_ice', 'ret_ice']]

merged = sr.join(ic, how='left')
# 列重排
cols = ['year', 'month', 'open', 'high', 'low', 'close', 'ret', 'close_ice', 'ret_ice']
merged = merged[cols].rename(columns={
    'open':'sr_open','high':'sr_high','low':'sr_low','close':'sr_close','ret':'sr_ret%',
    'close_ice':'ice_close','ret_ice':'ice_ret%',
})
merged['diff%'] = (merged['sr_ret%'] - merged['ice_ret%']).round(2)
merged = merged.round({'sr_open':0,'sr_high':0,'sr_low':0,'sr_close':0,'sr_ret%':2,'ice_close':2,'ice_ret%':2})

out = 'data/sugar_monthly_with_ice.csv'
merged.to_csv(out, encoding='utf-8-sig')
print(f"已保存 {out}, {len(merged)} 行")
print(merged.head(3).to_string())
print("...")
print(merged.tail(3).to_string())
