# -*- coding: utf-8 -*-
"""
2005-2007年煤炭大牛市复盘 - 数据获取脚本
获取上证指数和主要煤炭股的历史行情数据
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import akshare as ak
import pandas as pd
import json
from datetime import datetime

# 主要煤炭股列表（2005-2007年存在的股票）
coal_stocks = {
    "600188": "兖州煤业",      # 1998年上市
    "000983": "西山煤电",      # 2000年上市
    "600395": "盘江股份",      # 2001年上市 (原盘江精煤)
    "601001": "大同煤业",      # 2006年6月上市
    "601088": "中国神华",      # 2007年10月A股上市
    "600508": "上海能源",      # 2001年上市
    "601898": "中煤能源",      # 2008年上市，不在范围内
    "600123": "兰花科创",      # 2000年上市
    "600971": "恒源煤电",      # 2004年上市
    "601666": "平煤股份",      # 2006年11月上市 (原平煤天安)
    "002128": "露天煤业",      # 2007年上市
    "600997": "开滦股份",      # 2004年上市
    "600348": "阳泉煤业",      # 2003年上市 (原国阳新能)
}

results = {}

# 获取上证指数
print("=" * 80)
print("获取上证指数数据...")
try:
    sh_index = ak.stock_zh_index_daily(symbol="sh000001")
    sh_index['date'] = pd.to_datetime(sh_index['date'])
    sh_2005_2007 = sh_index[(sh_index['date'] >= '2005-01-01') & (sh_index['date'] <= '2007-12-31')]
    
    # 关键节点
    print(f"\n上证指数 2005-2007年关键数据:")
    print(f"  2005年初: {sh_2005_2007.iloc[0]['date'].strftime('%Y-%m-%d')}, 收盘: {sh_2005_2007.iloc[0]['close']:.2f}")
    
    # 2005年最低点
    sh_2005 = sh_2005_2007[sh_2005_2007['date'].dt.year == 2005]
    min_idx = sh_2005['close'].idxmin()
    print(f"  2005年最低点: {sh_2005.loc[min_idx, 'date'].strftime('%Y-%m-%d')}, 收盘: {sh_2005.loc[min_idx, 'close']:.2f}")
    
    # 2007年最高点  
    sh_2007 = sh_2005_2007[sh_2005_2007['date'].dt.year == 2007]
    max_idx = sh_2007['close'].idxmax()
    print(f"  2007年最高点: {sh_2007.loc[max_idx, 'date'].strftime('%Y-%m-%d')}, 收盘: {sh_2007.loc[max_idx, 'close']:.2f}")
    print(f"  2007年末: {sh_2005_2007.iloc[-1]['date'].strftime('%Y-%m-%d')}, 收盘: {sh_2005_2007.iloc[-1]['close']:.2f}")
    
    # 各年末数据
    for year in [2005, 2006, 2007]:
        year_data = sh_2005_2007[sh_2005_2007['date'].dt.year == year]
        if not year_data.empty:
            print(f"  {year}年末收盘: {year_data.iloc[-1]['close']:.2f} ({year_data.iloc[-1]['date'].strftime('%Y-%m-%d')})")
    
    # 阶段划分
    # 阶段1: 2005年6月-2006年6月
    stage1_start = sh_2005_2007[(sh_2005_2007['date'] >= '2005-06-01') & (sh_2005_2007['date'] <= '2005-06-30')]
    stage1_end = sh_2005_2007[(sh_2005_2007['date'] >= '2006-06-01') & (sh_2005_2007['date'] <= '2006-06-30')]
    if not stage1_start.empty and not stage1_end.empty:
        print(f"\n  阶段1 (2005.06-2006.06): {stage1_start.iloc[0]['close']:.2f} -> {stage1_end.iloc[-1]['close']:.2f}")
    
    # 阶段2: 2006年7月-2007年5月
    stage2_start = sh_2005_2007[(sh_2005_2007['date'] >= '2006-07-01') & (sh_2005_2007['date'] <= '2006-07-31')]
    stage2_end = sh_2005_2007[(sh_2005_2007['date'] >= '2007-05-01') & (sh_2005_2007['date'] <= '2007-05-31')]
    if not stage2_start.empty and not stage2_end.empty:
        print(f"  阶段2 (2006.07-2007.05): {stage2_start.iloc[0]['close']:.2f} -> {stage2_end.iloc[-1]['close']:.2f}")
    
    # 阶段3: 2007年6月-2007年10月
    stage3_start = sh_2005_2007[(sh_2005_2007['date'] >= '2007-06-01') & (sh_2005_2007['date'] <= '2007-06-30')]
    stage3_end = sh_2005_2007[(sh_2005_2007['date'] >= '2007-10-01') & (sh_2005_2007['date'] <= '2007-10-31')]
    if not stage3_start.empty and not stage3_end.empty:
        print(f"  阶段3 (2007.06-2007.10): {stage3_start.iloc[0]['close']:.2f} -> {stage3_end.iloc[-1]['close']:.2f}")
    
    results['上证指数'] = {
        'start': float(sh_2005_2007.iloc[0]['close']),
        'end': float(sh_2005_2007.iloc[-1]['close']),
    }
except Exception as e:
    print(f"获取上证指数失败: {e}")

print("\n" + "=" * 80)
print("获取煤炭个股数据...")
print("=" * 80)

# 获取个股数据
for code, name in coal_stocks.items():
    print(f"\n--- {name} ({code}) ---")
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20050101", end_date="20071231", adjust="qfq")
        if df.empty:
            print(f"  无数据")
            continue
        
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 基本信息
        first_date = df['日期'].iloc[0]
        last_date = df['日期'].iloc[-1]
        first_close = df['收盘'].iloc[0]
        last_close = df['收盘'].iloc[-1]
        
        print(f"  数据起始: {first_date.strftime('%Y-%m-%d')}, 收盘(前复权): {first_close:.2f}")
        print(f"  数据结束: {last_date.strftime('%Y-%m-%d')}, 收盘(前复权): {last_close:.2f}")
        
        # 最高和最低
        max_idx = df['收盘'].idxmax()
        min_idx = df['收盘'].idxmin()
        max_price = df.loc[max_idx, '收盘']
        min_price = df.loc[min_idx, '收盘']
        max_date = df.loc[max_idx, '日期']
        min_date = df.loc[min_idx, '日期']
        
        print(f"  期间最低: {min_date.strftime('%Y-%m-%d')}, {min_price:.2f}")
        print(f"  期间最高: {max_date.strftime('%Y-%m-%d')}, {max_price:.2f}")
        
        # 从最低点到最高点的涨幅
        if min_date < max_date:
            gain = (max_price / min_price - 1) * 100
            print(f"  最低到最高涨幅: {gain:.1f}% ({max_price/min_price:.2f}倍)")
        
        # 各年度表现
        for year in [2005, 2006, 2007]:
            year_data = df[df['日期'].dt.year == year]
            if not year_data.empty:
                y_start = year_data['收盘'].iloc[0]
                y_end = year_data['收盘'].iloc[-1]
                y_max = year_data['收盘'].max()
                y_min = year_data['收盘'].min()
                y_change = (y_end / y_start - 1) * 100
                print(f"  {year}年: 开始{y_start:.2f} -> 结束{y_end:.2f}, 涨跌{y_change:.1f}%, 最高{y_max:.2f}, 最低{y_min:.2f}")
        
        # 分阶段
        # 阶段1: 底部启动 (2005.06-2006.06)
        s1 = df[(df['日期'] >= '2005-06-01') & (df['日期'] <= '2006-06-30')]
        if not s1.empty:
            print(f"  阶段1(2005.06-2006.06): {s1['收盘'].iloc[0]:.2f} -> {s1['收盘'].iloc[-1]:.2f}, 涨幅{(s1['收盘'].iloc[-1]/s1['收盘'].iloc[0]-1)*100:.1f}%")
        
        # 阶段2: 加速上涨 (2006.07-2007.05)  
        s2 = df[(df['日期'] >= '2006-07-01') & (df['日期'] <= '2007-05-31')]
        if not s2.empty:
            print(f"  阶段2(2006.07-2007.05): {s2['收盘'].iloc[0]:.2f} -> {s2['收盘'].iloc[-1]:.2f}, 涨幅{(s2['收盘'].iloc[-1]/s2['收盘'].iloc[0]-1)*100:.1f}%")
        
        # 阶段3: 疯狂冲顶 (2007.06-2007.10)
        s3 = df[(df['日期'] >= '2007-06-01') & (df['日期'] <= '2007-10-31')]
        if not s3.empty:
            print(f"  阶段3(2007.06-2007.10): {s3['收盘'].iloc[0]:.2f} -> {s3['收盘'].iloc[-1]:.2f}, 涨幅{(s3['收盘'].iloc[-1]/s3['收盘'].iloc[0]-1)*100:.1f}%")
        
        # 保存结果
        results[f"{name}({code})"] = {
            'first_date': first_date.strftime('%Y-%m-%d'),
            'last_date': last_date.strftime('%Y-%m-%d'),
            'first_close': float(first_close),
            'last_close': float(last_close),
            'max_price': float(max_price),
            'max_date': max_date.strftime('%Y-%m-%d'),
            'min_price': float(min_price),
            'min_date': min_date.strftime('%Y-%m-%d'),
            'total_gain': float((max_price / min_price - 1) * 100) if min_date < max_date else None,
        }
        
    except Exception as e:
        print(f"  获取失败: {e}")

# 保存JSON
with open('D:/code/bean/data/coal_bull_market_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 80)
print("数据已保存到 D:/code/bean/data/coal_bull_market_data.json")
print("=" * 80)
