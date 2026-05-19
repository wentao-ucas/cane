# -*- coding: utf-8 -*-
"""
玉米主连(C0) 月度涨跌 & 季节性分析
上市日期: 2004-09-22 (大商所)
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import akshare as ak
import pandas as pd
import numpy as np
from pathlib import Path

OUT = Path('data')
OUT.mkdir(exist_ok=True)

def fetch_daily():
    df = ak.futures_main_sina(symbol="C0")
    df.columns = [c.lower() for c in df.columns]
    date_col = '日期' if '日期' in df.columns else 'date'
    close_col = '收盘价' if '收盘价' in df.columns else 'close'
    df = df.rename(columns={date_col: 'date', close_col: 'close'})
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').set_index('date')
    return df

def to_monthly(df):
    m = df['close'].resample('ME').last().to_frame('close')
    m['open']  = df['open' if 'open' in df.columns else df.columns[0]].resample('ME').first()
    m['high']  = df['high'].resample('ME').max() if 'high' in df.columns else np.nan
    m['low']   = df['low'].resample('ME').min()  if 'low'  in df.columns else np.nan
    m['ret']   = m['close'].pct_change() * 100
    m['year']  = m.index.year
    m['month'] = m.index.month
    return m

def seasonality(m):
    g = m.groupby('month')['ret']
    s = pd.DataFrame({
        '平均涨幅%': g.mean().round(2),
        '中位数%':   g.median().round(2),
        '胜率%':     (g.apply(lambda x: (x > 0).mean()) * 100).round(1),
        '最大%':     g.max().round(2),
        '最小%':     g.min().round(2),
        '样本数':    g.count(),
    })
    return s

def pivot_table(m):
    return m.pivot_table(index='year', columns='month', values='ret').round(2)

def main():
    print("拉取玉米主连(C0)日线…")
    df = fetch_daily()
    print(f"日线区间: {df.index.min().date()} ~ {df.index.max().date()}, 共 {len(df)} 行")

    m = to_monthly(df)
    m.to_csv(OUT/'corn_monthly.csv', encoding='utf-8-sig')

    pv = pivot_table(m)
    pv.to_csv(OUT/'corn_monthly_pivot.csv', encoding='utf-8-sig')

    s = seasonality(m)
    s.to_csv(OUT/'corn_seasonality.csv', encoding='utf-8-sig')

    print("\n=== 季节性统计 (按自然月) ===")
    print(s.to_string())

    print("\n=== 年×月 涨跌幅矩阵 (%) ===")
    print(pv.to_string())

    big = m[m['ret'].abs() >= 8].sort_values('ret')
    print(f"\n=== 月度大波动 |涨跌|≥8% 共 {len(big)} 次 ===")
    print(big[['close', 'ret']].round(2).to_string())
    big.to_csv(OUT/'corn_big_moves.csv', encoding='utf-8-sig')

    print(f"\n文件已写入 data/: corn_monthly.csv, corn_monthly_pivot.csv, corn_seasonality.csv, corn_big_moves.csv")

if __name__ == '__main__':
    main()
