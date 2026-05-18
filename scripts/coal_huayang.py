# -*- coding: utf-8 -*-
"""获取华阳股份(600348)精确数据"""
import sys, io, json, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd

def fetch_sina_daily(code, count=600):
    prefix = 'sh' if code.startswith('6') else 'sz'
    symbol = f"{prefix}{code}"
    url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_data=/CN_MarketDataService.getKLineData"
    params = {'symbol': symbol, 'scale': 240, 'ma': 'no', 'datalen': count}
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

# 华阳股份 = 600348 (原阳泉煤业/国阳新能)
print("华阳股份(600348) - 原阳泉煤业")
df = fetch_sina_daily("600348", count=600)
df = df[df['day'] >= '2024-01-01']
latest = df.iloc[-1]
print(f"最新: {latest['day'].strftime('%Y-%m-%d')} {latest['close']:.2f}元")

for year in [2024, 2025, 2026]:
    yr = df[df['day'].dt.year == year]
    if not yr.empty:
        gain = (yr.iloc[-1]['close'] / yr.iloc[0]['close'] - 1) * 100
        print(f"{year}: {yr.iloc[0]['close']:.2f}→{yr.iloc[-1]['close']:.2f} ({gain:+.1f}%) "
              f"低{yr['close'].min():.2f} 高{yr['close'].max():.2f}")

# 也补充华阳股份的新能源业务信息
print("\n华阳股份业务: 煤炭+新能源(钠离子电池+气凝胶)")
print("这是煤炭股中转型最激进的一家")
