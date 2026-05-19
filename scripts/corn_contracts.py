# -*- coding: utf-8 -*-
"""
拉取玉米全部活跃合约 (C 系列) 日线数据
玉米交易月份: 1, 3, 5, 7, 9, 11
合约范围: 2018-2027 (10 年 × 6 月 = 60 合约)
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import akshare as ak
import pandas as pd
from pathlib import Path

OUT = Path('data'); OUT.mkdir(exist_ok=True)

# 生成 2018-2027 年所有玉米合约代码
CORN_MONTHS = [1, 3, 5, 7, 9, 11]
contracts = []
for year in range(2018, 2028):
    yy = f"{year % 100:02d}"
    for m in CORN_MONTHS:
        contracts.append(f"C{yy}{m:02d}")

print(f"目标合约 {len(contracts)} 个: {contracts[0]} ~ {contracts[-1]}")

all_data = []
fail = []
for code in contracts:
    try:
        df = ak.futures_zh_daily_sina(symbol=code)
        if df is None or len(df) == 0:
            fail.append(code); continue
        # 列：date, open, high, low, close, volume, hold, settle
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        df['date'] = pd.to_datetime(df['date'])
        df['contract'] = code
        # 只保留持仓量 > 0 的"活跃期"
        if 'hold' in df.columns:
            df = df[df['hold'] > 0]
        all_data.append(df)
        print(f"  {code}: {len(df):>5} 行 | {df['date'].min().date()} ~ {df['date'].max().date()} | 价格 {df['close'].min():.0f}-{df['close'].max():.0f}")
    except Exception as e:
        fail.append(code)
        print(f"  {code}: 失败 ({e})")

print(f"\n成功 {len(all_data)} / 失败 {len(fail)}: {fail}")

if all_data:
    full = pd.concat(all_data, ignore_index=True)
    # 标准列顺序
    cols = ['date', 'contract', 'open', 'high', 'low', 'close']
    for c in ['settle', 'volume', 'hold']:
        if c in full.columns:
            cols.append(c)
    full = full[cols].sort_values(['date', 'contract']).reset_index(drop=True)

    out_path = OUT / 'corn_contracts_daily.csv'
    full.to_csv(out_path, encoding='utf-8-sig', index=False)
    print(f"\n保存 {out_path}: {len(full):,} 行 × {len(cols)} 列")
    print(f"时间范围: {full['date'].min().date()} ~ {full['date'].max().date()}")
    print(f"覆盖合约: {full['contract'].nunique()} 个")

    # 简要统计
    print("\n=== 各合约样本量（按持仓量加权选最近 10 个）===")
    summary = full.groupby('contract').agg(
        样本=('close', 'count'),
        起始=('date', 'min'),
        截止=('date', 'max'),
        最高=('close', 'max'),
        最低=('close', 'min'),
    ).sort_values('截止', ascending=False).head(15)
    print(summary.to_string())
