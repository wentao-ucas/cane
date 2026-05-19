# -*- coding: utf-8 -*-
"""把 CBOT 月度数据合并到大商所玉米月度 CSV"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from pathlib import Path

c = pd.read_csv('data/corn_monthly.csv', parse_dates=['date']).set_index('date')
cb = pd.read_csv('data/cbot_corn_monthly.csv', parse_dates=['date']).set_index('date')

cb = cb[['close_cbot', 'ret_cbot']]

merged = c.join(cb, how='left')
cols = ['year', 'month', 'open', 'high', 'low', 'close', 'ret', 'close_cbot', 'ret_cbot']
merged = merged[cols].rename(columns={
    'open':'c_open','high':'c_high','low':'c_low','close':'c_close','ret':'c_ret%',
    'close_cbot':'cbot_close','ret_cbot':'cbot_ret%',
})
merged['diff%'] = (merged['c_ret%'] - merged['cbot_ret%']).round(2)
merged = merged.round({'c_open':0,'c_high':0,'c_low':0,'c_close':0,'c_ret%':2,'cbot_close':2,'cbot_ret%':2})

out = 'data/corn_monthly_with_cbot.csv'
merged.to_csv(out, encoding='utf-8-sig')
print(f"已保存 {out}, {len(merged)} 行")
print(merged.head(3).to_string())
print("...")
print(merged.tail(3).to_string())
