# -*- coding: utf-8 -*-
"""
做多玉米：5 月中旬入场，9月合约 vs 次年1月合约 历史回测
对比:
  1. 同期对比 (5月→8月底)：剔除持有期长短，纯看季节性
  2. 完整持有：短持9月到交割 vs 长持1月到交割
"""
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from pathlib import Path

df = pd.read_csv('data/corn_contracts_daily.csv', parse_dates=['date'])
wide = df.pivot(index='date', columns='contract', values='close').sort_index()

def get_price(contract, target, tol=15):
    """取 contract 在 target 日或之前最近的收盘价，超出容差返回 None"""
    if contract not in wide.columns:
        return None
    s = wide[contract].dropna()
    s = s[s.index <= pd.Timestamp(target)]
    if len(s) == 0:
        return None
    if (pd.Timestamp(target) - s.index[-1]).days > tol:
        return None
    return float(s.iloc[-1])

rows = []
for Y in range(2019, 2026):
    c09 = f"C{Y % 100:02d}09"          # 当年 9 月合约
    c01 = f"C{(Y+1) % 100:02d}01"      # 次年 1 月合约

    entry      = f"{Y}-05-15"
    exit_aug   = f"{Y}-08-29"          # 9月合约交割前 / 同期对比平仓点
    exit_jan   = f"{Y+1}-01-08"        # 1月合约交割前

    p_entry_09 = get_price(c09, entry)
    p_entry_01 = get_price(c01, entry)
    p_aug_09   = get_price(c09, exit_aug)
    p_aug_01   = get_price(c01, exit_aug)
    p_jan_01   = get_price(c01, exit_jan)

    if None in (p_entry_09, p_entry_01, p_aug_09, p_aug_01, p_jan_01):
        rows.append({'年份': Y, '备注': '数据缺失', 'C09': c09, 'C01': c01})
        continue

    ret_09_same = (p_aug_09 / p_entry_09 - 1) * 100      # 9月合约 5→8月底
    ret_01_same = (p_aug_01 / p_entry_01 - 1) * 100      # 1月合约 5→8月底（同期）
    ret_01_full = (p_jan_01 / p_entry_01 - 1) * 100      # 1月合约 5→次年1月（完整）

    rows.append({
        '年份': Y,
        'C09合约': c09, 'C01合约': c01,
        '入场09': round(p_entry_09), '入场01': round(p_entry_01),
        '同期9月%': round(ret_09_same, 1),
        '同期1月%': round(ret_01_same, 1),
        '同期赢家': '1月' if ret_01_same > ret_09_same else '9月',
        '1月完整%': round(ret_01_full, 1),
    })

res = pd.DataFrame(rows)
print("=" * 90)
print("做多玉米回测：每年 5/15 入场")
print("=" * 90)
print(res.to_string(index=False))

valid = res[res['同期9月%'].notna()] if '同期9月%' in res.columns else pd.DataFrame()
if len(valid):
    print("\n" + "=" * 90)
    print("【对比 1】同期 5月→8月底（公平，剔除持有期长短，纯看持有这段的季节性）")
    print("=" * 90)
    n = len(valid)
    win_01 = (valid['同期1月%'] > valid['同期9月%']).sum()
    print(f"  9月合约平均: {valid['同期9月%'].mean():+.1f}%  (胜率 {(valid['同期9月%']>0).mean()*100:.0f}%)")
    print(f"  1月合约平均: {valid['同期1月%'].mean():+.1f}%  (胜率 {(valid['同期1月%']>0).mean()*100:.0f}%)")
    print(f"  1月合约跑赢9月合约: {win_01}/{n} 年 ({win_01/n*100:.0f}%)")
    print(f"  → 平均超额: {(valid['同期1月%'] - valid['同期9月%']).mean():+.1f}%/年")

    print("\n" + "=" * 90)
    print("【对比 2】完整持有：短持9月(5→8月底) vs 长持1月(5→次年1月)")
    print("=" * 90)
    print(f"  短持9月合约平均: {valid['同期9月%'].mean():+.1f}%  (胜率 {(valid['同期9月%']>0).mean()*100:.0f}%)")
    print(f"  长持1月合约平均: {valid['1月完整%'].mean():+.1f}%  (胜率 {(valid['1月完整%']>0).mean()*100:.0f}%)")
    print(f"  长持1月跑赢短持9月: {(valid['1月完整%']>valid['同期9月%']).sum()}/{n} 年")

    res.to_csv('data/corn_long_entry_backtest.csv', encoding='utf-8-sig', index=False)
    print(f"\n保存: data/corn_long_entry_backtest.csv")
