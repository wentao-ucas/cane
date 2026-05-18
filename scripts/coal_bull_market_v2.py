# -*- coding: utf-8 -*-
"""
2005-2007年煤炭大牛市复盘 - 数据获取脚本 v2
使用不复权价格显示 + 后复权价格计算真实涨幅
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import akshare as ak
import pandas as pd
import json

# 主要煤炭股列表（2005-2007年存在的股票）
coal_stocks = {
    "600188": "兖州煤业",
    "000983": "西山煤电",
    "600395": "盘江股份",
    "601001": "大同煤业",
    "600508": "上海能源",
    "600123": "兰花科创",
    "600971": "恒源煤电",
    "601666": "平煤股份",
    "002128": "露天煤业",
    "600997": "开滦股份",
    "600348": "阳泉煤业",
}

all_results = []

# ==================== 上证指数 ====================
print("=" * 100)
print("【上证指数 2005-2007年行情】")
print("=" * 100)
try:
    sh_index = ak.stock_zh_index_daily(symbol="sh000001")
    sh_index['date'] = pd.to_datetime(sh_index['date'])
    sh = sh_index[(sh_index['date'] >= '2005-01-01') & (sh_index['date'] <= '2007-12-31')].copy()
    
    # 关键节点
    sh_2005 = sh[sh['date'].dt.year == 2005]
    sh_2006 = sh[sh['date'].dt.year == 2006]
    sh_2007 = sh[sh['date'].dt.year == 2007]
    
    min_2005 = sh_2005.loc[sh_2005['close'].idxmin()]
    max_2007 = sh_2007.loc[sh_2007['close'].idxmax()]
    
    print(f"  2005年初: {sh.iloc[0]['date'].strftime('%Y-%m-%d')} 收盘 {sh.iloc[0]['close']:.2f}")
    print(f"  2005年最低: {min_2005['date'].strftime('%Y-%m-%d')} 收盘 {min_2005['close']:.2f}")
    print(f"  2005年末: {sh_2005.iloc[-1]['date'].strftime('%Y-%m-%d')} 收盘 {sh_2005.iloc[-1]['close']:.2f}")
    print(f"  2006年末: {sh_2006.iloc[-1]['date'].strftime('%Y-%m-%d')} 收盘 {sh_2006.iloc[-1]['close']:.2f}")
    print(f"  2007年最高: {max_2007['date'].strftime('%Y-%m-%d')} 收盘 {max_2007['close']:.2f}")
    print(f"  2007年末: {sh_2007.iloc[-1]['date'].strftime('%Y-%m-%d')} 收盘 {sh_2007.iloc[-1]['close']:.2f}")
    print(f"  998->6124 总涨幅: {(max_2007['close']/min_2005['close']-1)*100:.0f}%")
    
    # 各阶段
    dates_map = {}
    for _, row in sh.iterrows():
        dates_map[row['date'].strftime('%Y-%m-%d')] = row['close']
    
    print(f"\n  【阶段划分】")
    # 阶段1: 底部酝酿 2005.06-2006.06 (998-1700)
    s1s = sh[(sh['date'] >= '2005-06-01') & (sh['date'] <= '2005-06-30')]
    s1e = sh[(sh['date'] >= '2006-06-01') & (sh['date'] <= '2006-06-30')]
    if not s1s.empty and not s1e.empty:
        print(f"  阶段1 底部启动期 (2005.06-2006.06): {s1s.iloc[0]['close']:.0f} -> {s1e.iloc[-1]['close']:.0f}, 涨幅{(s1e.iloc[-1]['close']/s1s.iloc[0]['close']-1)*100:.0f}%")
    
    # 阶段2: 主升浪 2006.07-2007.05 (1700-4300)
    s2s = sh[(sh['date'] >= '2006-07-01') & (sh['date'] <= '2006-07-31')]
    s2e = sh[(sh['date'] >= '2007-05-01') & (sh['date'] <= '2007-05-31')]
    if not s2s.empty and not s2e.empty:
        print(f"  阶段2 主升浪期 (2006.07-2007.05): {s2s.iloc[0]['close']:.0f} -> {s2e.iloc[-1]['close']:.0f}, 涨幅{(s2e.iloc[-1]['close']/s2s.iloc[0]['close']-1)*100:.0f}%")
    
    # 530大跌及后续
    s_530 = sh[(sh['date'] >= '2007-05-29') & (sh['date'] <= '2007-06-05')]
    if not s_530.empty:
        print(f"  530暴跌: {s_530.iloc[0]['close']:.0f} -> {s_530.iloc[-1]['close']:.0f}")
    
    # 阶段3: 加速赶顶 2007.06-2007.10 (3400-6124)
    s3s = sh[(sh['date'] >= '2007-06-01') & (sh['date'] <= '2007-06-30')]
    s3e = sh[(sh['date'] >= '2007-10-01') & (sh['date'] <= '2007-10-31')]
    if not s3s.empty and not s3e.empty:
        print(f"  阶段3 加速冲顶 (2007.06-2007.10): {s3s.iloc[0]['close']:.0f} -> {s3e.iloc[-1]['close']:.0f}, 涨幅{(s3e.iloc[-1]['close']/s3s.iloc[0]['close']-1)*100:.0f}%")
        
except Exception as e:
    print(f"获取上证指数失败: {e}")
    import traceback; traceback.print_exc()

# ==================== 煤炭个股 ====================
print("\n" + "=" * 100)
print("【煤炭个股 2005-2007年行情 (不复权实际价格)】")
print("=" * 100)

for code, name in coal_stocks.items():
    print(f"\n{'─'*80}")
    print(f"  {name} ({code})")
    print(f"{'─'*80}")
    try:
        # 不复权价格 - 展示用
        df_raw = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20050101", end_date="20071231", adjust="")
        # 后复权价格 - 计算涨幅用
        df_hfq = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20050101", end_date="20071231", adjust="hfq")
        
        if df_raw.empty:
            print(f"  无数据")
            continue
        
        df_raw['日期'] = pd.to_datetime(df_raw['日期'])
        df_hfq['日期'] = pd.to_datetime(df_hfq['日期'])
        
        first_date = df_raw['日期'].iloc[0]
        last_date = df_raw['日期'].iloc[-1]
        
        # 不复权的最高最低（展示用）
        max_idx_raw = df_raw['收盘'].idxmax()
        min_idx_raw = df_raw['收盘'].idxmin()
        
        print(f"  数据范围: {first_date.strftime('%Y-%m-%d')} ~ {last_date.strftime('%Y-%m-%d')}")
        print(f"  起始价(不复权): {df_raw['收盘'].iloc[0]:.2f}元")
        print(f"  结束价(不复权): {df_raw['收盘'].iloc[-1]:.2f}元")
        print(f"  最低价(不复权): {df_raw.loc[min_idx_raw, '日期'].strftime('%Y-%m-%d')} {df_raw.loc[min_idx_raw, '收盘']:.2f}元")
        print(f"  最高价(不复权): {df_raw.loc[max_idx_raw, '日期'].strftime('%Y-%m-%d')} {df_raw.loc[max_idx_raw, '收盘']:.2f}元")
        
        # 后复权的最低到最高涨幅（真实收益）
        max_idx_hfq = df_hfq['收盘'].idxmax()
        min_idx_hfq = df_hfq['收盘'].idxmin()
        max_hfq = df_hfq.loc[max_idx_hfq, '收盘']
        min_hfq = df_hfq.loc[min_idx_hfq, '收盘']
        max_date_hfq = df_hfq.loc[max_idx_hfq, '日期']
        min_date_hfq = df_hfq.loc[min_idx_hfq, '日期']
        
        if min_date_hfq < max_date_hfq:
            total_gain = (max_hfq / min_hfq - 1) * 100
            print(f"  后复权最低到最高真实涨幅: {total_gain:.0f}% ({max_hfq/min_hfq:.1f}倍)")
            print(f"    ({min_date_hfq.strftime('%Y-%m-%d')} {min_hfq:.2f} -> {max_date_hfq.strftime('%Y-%m-%d')} {max_hfq:.2f})")
        
        # 整段涨幅
        total_period_gain = (df_hfq['收盘'].iloc[-1] / df_hfq['收盘'].iloc[0] - 1) * 100
        print(f"  全段持有涨幅(后复权): {total_period_gain:.0f}%")
        
        # 年度表现
        print(f"\n  【年度表现】(不复权价格)")
        for year in [2005, 2006, 2007]:
            yr = df_raw[df_raw['日期'].dt.year == year]
            yr_hfq = df_hfq[df_hfq['日期'].dt.year == year]
            if not yr.empty:
                yr_gain = (yr_hfq['收盘'].iloc[-1] / yr_hfq['收盘'].iloc[0] - 1) * 100
                print(f"    {year}年: {yr['收盘'].iloc[0]:.2f}→{yr['收盘'].iloc[-1]:.2f}元, "
                      f"最低{yr['收盘'].min():.2f}, 最高{yr['收盘'].max():.2f}, "
                      f"后复权涨幅{yr_gain:.0f}%")
        
        # 阶段涨幅
        print(f"\n  【阶段表现】(后复权计算涨幅)")
        
        # 阶段1: 底部启动 (2005.06-2006.06)
        s1_hfq = df_hfq[(df_hfq['日期'] >= '2005-06-01') & (df_hfq['日期'] <= '2006-06-30')]
        s1_raw = df_raw[(df_raw['日期'] >= '2005-06-01') & (df_raw['日期'] <= '2006-06-30')]
        if not s1_hfq.empty and len(s1_hfq) > 5:
            s1_gain = (s1_hfq['收盘'].iloc[-1] / s1_hfq['收盘'].iloc[0] - 1) * 100
            print(f"    阶段1 底部启动(2005.06-2006.06): "
                  f"不复权 {s1_raw['收盘'].iloc[0]:.2f}→{s1_raw['收盘'].iloc[-1]:.2f}元, 后复权涨幅{s1_gain:.0f}%")
        
        # 阶段2: 主升浪 (2006.07-2007.05)
        s2_hfq = df_hfq[(df_hfq['日期'] >= '2006-07-01') & (df_hfq['日期'] <= '2007-05-31')]
        s2_raw = df_raw[(df_raw['日期'] >= '2006-07-01') & (df_raw['日期'] <= '2007-05-31')]
        if not s2_hfq.empty and len(s2_hfq) > 5:
            s2_gain = (s2_hfq['收盘'].iloc[-1] / s2_hfq['收盘'].iloc[0] - 1) * 100
            print(f"    阶段2 主升浪期(2006.07-2007.05): "
                  f"不复权 {s2_raw['收盘'].iloc[0]:.2f}→{s2_raw['收盘'].iloc[-1]:.2f}元, 后复权涨幅{s2_gain:.0f}%")
        
        # 阶段3: 加速冲顶 (2007.06-2007.10)
        s3_hfq = df_hfq[(df_hfq['日期'] >= '2007-06-01') & (df_hfq['日期'] <= '2007-10-31')]
        s3_raw = df_raw[(df_raw['日期'] >= '2007-06-01') & (df_raw['日期'] <= '2007-10-31')]
        if not s3_hfq.empty and len(s3_hfq) > 5:
            s3_gain = (s3_hfq['收盘'].iloc[-1] / s3_hfq['收盘'].iloc[0] - 1) * 100
            print(f"    阶段3 加速冲顶(2007.06-2007.10): "
                  f"不复权 {s3_raw['收盘'].iloc[0]:.2f}→{s3_raw['收盘'].iloc[-1]:.2f}元, 后复权涨幅{s3_gain:.0f}%")
        
        # 阶段4: 回调 (2007.11-2007.12)
        s4_hfq = df_hfq[(df_hfq['日期'] >= '2007-11-01') & (df_hfq['日期'] <= '2007-12-31')]
        s4_raw = df_raw[(df_raw['日期'] >= '2007-11-01') & (df_raw['日期'] <= '2007-12-31')]
        if not s4_hfq.empty and len(s4_hfq) > 5:
            s4_gain = (s4_hfq['收盘'].iloc[-1] / s4_hfq['收盘'].iloc[0] - 1) * 100
            print(f"    阶段4 见顶回调(2007.11-2007.12): "
                  f"不复权 {s4_raw['收盘'].iloc[0]:.2f}→{s4_raw['收盘'].iloc[-1]:.2f}元, 后复权涨幅{s4_gain:.0f}%")
        
        # 收集结果
        result = {
            'code': code,
            'name': name,
            'data_start': first_date.strftime('%Y-%m-%d'),
            'data_end': last_date.strftime('%Y-%m-%d'),
            'start_price': float(df_raw['收盘'].iloc[0]),
            'end_price': float(df_raw['收盘'].iloc[-1]),
            'raw_min': float(df_raw['收盘'].min()),
            'raw_min_date': df_raw.loc[min_idx_raw, '日期'].strftime('%Y-%m-%d'),
            'raw_max': float(df_raw['收盘'].max()),
            'raw_max_date': df_raw.loc[max_idx_raw, '日期'].strftime('%Y-%m-%d'),
            'hfq_total_gain_pct': float(total_period_gain),
        }
        if min_date_hfq < max_date_hfq:
            result['hfq_min_to_max_gain_pct'] = float(total_gain)
        all_results.append(result)
        
    except Exception as e:
        print(f"  获取失败: {e}")
        import traceback; traceback.print_exc()

# ==================== 排名汇总 ====================
print("\n" + "=" * 100)
print("【煤炭个股涨幅排名 (后复权全段持有涨幅)】")
print("=" * 100)
sorted_results = sorted(all_results, key=lambda x: x.get('hfq_total_gain_pct', 0), reverse=True)
for i, r in enumerate(sorted_results, 1):
    gain_str = f"{r['hfq_total_gain_pct']:.0f}%"
    max_gain_str = f"最低到最高{r.get('hfq_min_to_max_gain_pct', 0):.0f}%" if r.get('hfq_min_to_max_gain_pct') else ""
    print(f"  {i}. {r['name']}({r['code']}): 全段涨幅{gain_str}, {max_gain_str}")
    print(f"     不复权: {r['start_price']:.2f}→{r['end_price']:.2f}, 最低{r['raw_min']:.2f}({r['raw_min_date']}), 最高{r['raw_max']:.2f}({r['raw_max_date']})")

# 保存结果
output = {
    'index': {
        'name': '上证指数',
        'low': '2005-07-11 1011.50',
        'high': '2007-10-16 6092.06',
    },
    'stocks': all_results,
}
with open('D:/code/bean/data/coal_bull_market_v2.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n数据已保存到 D:/code/bean/data/coal_bull_market_v2.json")
