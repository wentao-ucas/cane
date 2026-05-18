import akshare as ak
import pandas as pd
import traceback

print("=== 1. Testing Futures Data (Sina) ===")
try:
    # 焦煤连续
    df_jm = ak.futures_zh_daily_sina(symbol="jm0")
    print("\nJM0 (Coking Coal Dominant) Tail:")
    print(df_jm.tail())
except Exception as e:
    print("Error fetching JM0:", e)
    traceback.print_exc()

try:
    # 螺纹钢连续
    df_rb = ak.futures_zh_daily_sina(symbol="rb0")
    print("\nRB0 (Rebar Dominant) Tail:")
    print(df_rb.tail())
except Exception as e:
    print("Error fetching RB0:", e)
    traceback.print_exc()

print("\n=== 2. Testing Macro Data ===")
try:
    df_pmi = ak.macro_china_pmi()
    print("\nManufacturing PMI Tail:")
    print(df_pmi.tail())
except Exception as e:
    print("Error fetching PMI:", e)
    traceback.print_exc()

try:
    df_ppi = ak.macro_china_ppi()
    print("\nPPI Tail:")
    print(df_ppi.tail())
except Exception as e:
    print("Error fetching PPI:", e)
    traceback.print_exc()

print("\n=== 3. Testing Spot Prices (Mysteel/Sina if available) ===")
# Let's check if there's any easy spot price for jm or rb
try:
    # 现货与期货基差等
    df_basis = ak.futures_spot_price_previous(date="20240301") # Just testing if it works
    print("\nBasis array for a date:")
    print(df_basis.head())
except Exception as e:
    pass
