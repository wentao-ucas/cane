# -*- coding: utf-8 -*-
"""
获取申万煤炭板块 全部成分股 数据
用新浪API避免代理问题
"""
import sys, io, json, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd

def fetch_sina_daily(code, count=600):
    prefix = 'sh' if code.startswith('6') else 'sz'
    symbol = f"{prefix}{code}"
    url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_data=/CN_MarketDataService.getKLineData"
    params = {'symbol': symbol, 'scale': 240, 'ma': 'no', 'datalen': count}
    try:
        r = requests.get(url, params=params, timeout=15)
        text = r.text
        start = text.index('[')
        end = text.rindex(']') + 1
        data = json.loads(text[start:end])
        df = pd.DataFrame(data)
        df['day'] = pd.to_datetime(df['day'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        return df
    except:
        return pd.DataFrame()

# 之前已有的19只
done = {"601088","601225","601898","600188","000983","601699","600985",
        "600546","601001","600348","600123","600395","600971","600997",
        "002128","000937","600256","600403","601015"}

# 需要补充的（申万煤炭板块成分股，去掉退市的和已有的）
missing_stocks = {
    "600508": "上海能源",
    "601918": "新集能源",
    "601666": "平煤股份",
    "600157": "永泰能源",
    "000723": "美锦能源",
    "600575": "淮河能源",
    "600121": "郑州煤电",
    "601162": "辽宁能源",
    "603151": "苏能股份",
    "601989": "陕西能源",
    "000552": "甘肃能化",
    "600792": "云煤能源",
    "601011": "宝泰隆",
    "603092": "物产环能",
    "601101": "昊华能源",
    "603977": "国泰集团",
    "601186": "力量发展",  # 原中国铁建物资更名
    "600397": "安源煤业",
    "600740": "山西焦化",
    "002554": "惠博普",    # 可能不在
    "002684": "猛狮科技",  # 可能不在
    "600725": "云维股份",
    "002882": "金龙羽",    # 可能不在
}

all_results = []

print(f"补充获取 {len(missing_stocks)} 只煤炭股数据")
print("=" * 90)

for idx, (code, name) in enumerate(missing_stocks.items()):
    if idx > 0:
        time.sleep(2)
    
    print(f"[{idx+1}/{len(missing_stocks)}] {name} ({code})", end="", flush=True)
    
    df = fetch_sina_daily(code, count=600)
    if df.empty:
        print(f" ❌ 无数据")
        continue
    
    df = df[df['day'] >= '2024-01-01'].copy()
    if df.empty:
        print(f" ❌ 无2024+数据")
        continue
    
    latest = df.iloc[-1]
    result = {'code': code, 'name': name,
              'latest_date': latest['day'].strftime('%Y-%m-%d'),
              'latest_price': float(latest['close'])}
    
    for year in [2024, 2025, 2026]:
        yr = df[df['day'].dt.year == year]
        if not yr.empty:
            gain = (yr.iloc[-1]['close'] / yr.iloc[0]['close'] - 1) * 100
            result[f'y{year}_gain'] = float(gain)
            result[f'y{year}_start'] = float(yr.iloc[0]['close'])
            result[f'y{year}_end'] = float(yr.iloc[-1]['close'])
            result[f'y{year}_low'] = float(yr['close'].min())
            result[f'y{year}_high'] = float(yr['close'].max())
    
    total_gain = (latest['close'] / df.iloc[0]['close'] - 1) * 100
    result['total_gain'] = float(total_gain)
    
    sep = df[(df['day'] >= '2024-09-01') & (df['day'] <= '2024-09-30')]
    if not sep.empty:
        sep_low = sep['close'].min()
        result['sep_low'] = float(sep_low)
        result['sep_gain'] = float((latest['close'] / sep_low - 1) * 100)
    
    result['all_min'] = float(df['close'].min())
    result['all_min_date'] = df.loc[df['close'].idxmin(), 'day'].strftime('%Y-%m-%d')
    result['all_max'] = float(df['close'].max())
    result['all_max_date'] = df.loc[df['close'].idxmax(), 'day'].strftime('%Y-%m-%d')
    
    sep_str = f" 924至今{result['sep_gain']:+.0f}%" if 'sep_gain' in result else ""
    y24 = f" 24:{result.get('y2024_gain',0):+.0f}%" if 'y2024_gain' in result else ""
    y25 = f" 25:{result.get('y2025_gain',0):+.0f}%" if 'y2025_gain' in result else ""
    y26 = f" 26:{result.get('y2026_gain',0):+.0f}%" if 'y2026_gain' in result else ""
    print(f" ✅ {latest['close']:.2f}元 总{total_gain:+.0f}%{sep_str}{y24}{y25}{y26}")
    
    all_results.append(result)

# 合并之前的数据
print(f"\n{'='*90}")
print("合并之前的数据...")
try:
    with open('D:/code/bean/data/coal_current_precise.json', 'r', encoding='utf-8') as f:
        prev = json.load(f)
    prev_stocks = prev.get('stocks', [])
    print(f"  之前的: {len(prev_stocks)}只")
    print(f"  新增的: {len(all_results)}只")
    combined = prev_stocks + all_results
    print(f"  合计: {len(combined)}只")
except:
    combined = all_results

# 排名
print(f"\n{'='*90}")
print("【全部煤炭股 2024初至今涨幅排名】")
print("=" * 90)
for i, r in enumerate(sorted(combined, key=lambda x: x.get('total_gain', 0), reverse=True), 1):
    sep = f" 924至今{r['sep_gain']:+.0f}%" if 'sep_gain' in r else ""
    print(f"  {i:2d}. {r['name']}({r['code']}): {r['total_gain']:+.0f}%{sep} 最新{r['latest_price']:.2f}")

print(f"\n{'='*90}")
print("【全部煤炭股 2026年YTD排名】")
print("=" * 90)
has_2026 = [r for r in combined if 'y2026_gain' in r]
for i, r in enumerate(sorted(has_2026, key=lambda x: x.get('y2026_gain', 0), reverse=True), 1):
    print(f"  {i:2d}. {r['name']}({r['code']}): {r['y2026_gain']:+.1f}% ({r['y2026_start']:.2f}→{r['y2026_end']:.2f})")

# 保存
with open('D:/code/bean/data/coal_all_stocks.json', 'w', encoding='utf-8') as f:
    json.dump({'stocks': combined, 'count': len(combined)}, f, ensure_ascii=False, indent=2)
print(f"\n✅ 保存到 D:/code/bean/data/coal_all_stocks.json ({len(combined)}只)")
