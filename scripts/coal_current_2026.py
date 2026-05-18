# -*- coding: utf-8 -*-
"""
2026年煤炭板块精确数据 v6
东方财富API被v2rayN TUN封锁，改用新浪财经API
"""
import sys, io, os, time, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import pandas as pd
from datetime import datetime

# 新浪财经日K线API（和akshare获取上证指数用的同一个源）
def fetch_sina_daily(code, scale=240, count=600):
    """
    通过新浪财经API获取日K线
    code: 如 sh601088, sz000983
    scale: 240=日K
    count: 获取多少根K线
    """
    prefix = 'sh' if code.startswith('6') else 'sz'
    symbol = f"{prefix}{code}"
    
    url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_data=/CN_MarketDataService.getKLineData"
    params = {
        'symbol': symbol,
        'scale': scale,
        'ma': 'no',
        'datalen': count,
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        text = r.text
        # 解析 jsonp
        start = text.index('[')
        end = text.rindex(']') + 1
        data = json.loads(text[start:end])
        
        df = pd.DataFrame(data)
        df['day'] = pd.to_datetime(df['day'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        return df
    except Exception as e:
        return pd.DataFrame()

# 新浪实时行情API
def fetch_sina_realtime(codes):
    """批量获取实时行情"""
    symbols = []
    for code in codes:
        prefix = 'sh' if code.startswith('6') else 'sz'
        symbols.append(f"{prefix}{code}")
    
    url = f"https://hq.sinajs.cn/list={','.join(symbols)}"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = 'gbk'
        results = {}
        for line in r.text.strip().split('\n'):
            if '=' not in line:
                continue
            parts = line.split('=')
            symbol = parts[0].split('_')[-1].replace('"', '')
            code = symbol[2:]  # remove sh/sz prefix
            data = parts[1].replace('"', '').replace(';', '').split(',')
            if len(data) > 3:
                results[code] = {
                    'name': data[0],
                    'open': float(data[1]) if data[1] else 0,
                    'prev_close': float(data[2]) if data[2] else 0,
                    'price': float(data[3]) if data[3] else 0,
                    'high': float(data[4]) if data[4] else 0,
                    'low': float(data[5]) if data[5] else 0,
                    'volume': float(data[8]) if data[8] else 0,
                    'amount': float(data[9]) if data[9] else 0,
                    'date': data[30] if len(data) > 30 else '',
                }
        return results
    except Exception as e:
        print(f"  实时行情失败: {e}")
        return {}

coal_stocks = [
    ("601088", "中国神华"),
    ("601225", "陕西煤业"),
    ("601898", "中煤能源"),
    ("600188", "兖矿能源"),
    ("000983", "山西焦煤"),
    ("601699", "潞安环能"),
    ("600985", "淮北矿业"),
    ("600546", "山煤国际"),
    ("601001", "晋控煤业"),
    ("600348", "阳泉煤业"),
    ("600123", "兰花科创"),
    ("600395", "盘江股份"),
    ("600971", "恒源煤电"),
    ("600997", "开滦股份"),
    ("002128", "电投能源"),
    ("000937", "冀中能源"),
    ("600256", "广汇能源"),
    ("600403", "大有能源"),
    ("601015", "陕西黑猫"),
]

all_results = []

# ============ 实时行情 ============
print("=" * 90)
print("【新浪实时行情 - 一次性获取】")
print("=" * 90)
codes_list = [c for c, _ in coal_stocks]
realtime = fetch_sina_realtime(codes_list)

if realtime:
    print(f"  成功获取 {len(realtime)} 只股票实时数据")
    for code, data in sorted(realtime.items(), key=lambda x: x[1].get('price', 0), reverse=True):
        if data['price'] > 0:
            chg = (data['price'] / data['prev_close'] - 1) * 100 if data['prev_close'] > 0 else 0
            print(f"  {data['name']} ({code}): {data['price']:.2f}元 ({chg:+.2f}%)")
else:
    print("  ❌ 实时行情获取失败")

# ============ 日K线历史数据 ============
print(f"\n{'='*90}")
print("【新浪日K线 - 历史数据】")
print(f"{'='*90}")

for idx, (code, name) in enumerate(coal_stocks):
    if idx > 0:
        time.sleep(2)  # 间隔2秒
    
    print(f"\n[{idx+1}/{len(coal_stocks)}] {name} ({code})", end="", flush=True)
    
    df = fetch_sina_daily(code, count=600)  # ~2.5年日K
    if df.empty:
        print(f" ❌ 失败")
        continue
    
    # 筛选2024年以来
    df = df[df['day'] >= '2024-01-01'].copy()
    if df.empty:
        print(f" ❌ 无2024+数据")
        continue
    
    latest = df.iloc[-1]
    
    # 年度数据
    result = {'code': code, 'name': name,
              'latest_date': latest['day'].strftime('%Y-%m-%d'),
              'latest_price': float(latest['close'])}
    
    year_lines = []
    for year in [2024, 2025, 2026]:
        yr = df[df['day'].dt.year == year]
        if not yr.empty:
            gain = (yr.iloc[-1]['close'] / yr.iloc[0]['close'] - 1) * 100
            year_lines.append(
                f"  {year}: {yr.iloc[0]['close']:.2f}→{yr.iloc[-1]['close']:.2f} ({gain:+.1f}%) "
                f"低{yr['close'].min():.2f} 高{yr['close'].max():.2f}")
            result[f'y{year}_start'] = float(yr.iloc[0]['close'])
            result[f'y{year}_end'] = float(yr.iloc[-1]['close'])
            result[f'y{year}_gain'] = float(gain)
            result[f'y{year}_low'] = float(yr['close'].min())
            result[f'y{year}_high'] = float(yr['close'].max())
    
    total_gain = (latest['close'] / df.iloc[0]['close'] - 1) * 100
    result['total_gain'] = float(total_gain)
    
    # 924低点
    sep = df[(df['day'] >= '2024-09-01') & (df['day'] <= '2024-09-30')]
    if not sep.empty:
        sep_low = sep['close'].min()
        sep_gain = (latest['close'] / sep_low - 1) * 100
        result['sep_low'] = float(sep_low)
        result['sep_gain'] = float(sep_gain)
    
    result['all_min'] = float(df['close'].min())
    result['all_min_date'] = df.loc[df['close'].idxmin(), 'day'].strftime('%Y-%m-%d')
    result['all_max'] = float(df['close'].max())
    result['all_max_date'] = df.loc[df['close'].idxmax(), 'day'].strftime('%Y-%m-%d')
    
    sep_str = f" 924至今{result['sep_gain']:+.0f}%" if 'sep_gain' in result else ""
    print(f" ✅ {latest['close']:.2f}元 总{total_gain:+.0f}%{sep_str}")
    for l in year_lines:
        print(l)
    
    all_results.append(result)

# ============ 排名汇总 ============
if all_results:
    print(f"\n{'='*90}")
    print("【涨幅排名】")
    print("=" * 90)
    
    print("\n📊 2024年初至今总涨幅:")
    for i, r in enumerate(sorted(all_results, key=lambda x: x.get('total_gain', 0), reverse=True), 1):
        sep = f" 924至今{r['sep_gain']:+.0f}%" if 'sep_gain' in r else ""
        print(f"  {i:2d}. {r['name']}({r['code']}): {r['total_gain']:+.0f}%{sep} 最新{r['latest_price']:.2f}")
    
    for year_label, year_key in [("📊 2024年涨幅", "y2024_gain"), ("📊 2025年涨幅", "y2025_gain"), ("📊 2026年YTD", "y2026_gain")]:
        has = [r for r in all_results if year_key in r]
        if has:
            print(f"\n{year_label}:")
            for i, r in enumerate(sorted(has, key=lambda x: x[year_key], reverse=True), 1):
                start_key = year_key.replace('gain', 'start')
                end_key = year_key.replace('gain', 'end')
                print(f"  {i:2d}. {r['name']}: {r[year_key]:+.1f}% ({r[start_key]:.2f}→{r[end_key]:.2f})")

with open('D:/code/bean/data/coal_current_precise.json', 'w', encoding='utf-8') as f:
    json.dump({'stocks': all_results, 'realtime': realtime}, f, ensure_ascii=False, indent=2)
print(f"\n✅ 保存到 D:/code/bean/data/coal_current_precise.json")
