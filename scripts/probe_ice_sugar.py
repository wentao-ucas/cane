# -*- coding: utf-8 -*-
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import akshare as ak

print("\n=== 新浪 ZSD (11号原糖) ===")
try:
    df = ak.futures_foreign_hist(symbol='ZSD')
    print(f"shape={df.shape}, 区间={df.iloc[0,0]} ~ {df.iloc[-1,0]}")
    print("columns:", list(df.columns))
    print(df.head(3))
    print(df.tail(3))
except Exception as e:
    print(f"err: {e}")

print("\n=== 东财 SB00Y (糖11号当月连续) ===")
try:
    df = ak.futures_global_hist_em(symbol='SB00Y')
    print(f"shape={df.shape}, 区间={df.iloc[0,0]} ~ {df.iloc[-1,0]}")
    print("columns:", list(df.columns))
    print(df.head(3))
    print(df.tail(3))
except Exception as e:
    print(f"err: {e}")
