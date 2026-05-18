# src/fetch_data.py
import tushare as ts
import akshare as ak
import pandas as pd
import os
import sys

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from config import TUSHARE_TOKEN, DATA_DIR

def fetch_futures():
    """
    获取 tushare 期货日线数据
    包含：焦煤(JM)、螺纹(RB)、动力煤(ZC) 以及山西焦煤日线(000983)
    """
    if TUSHARE_TOKEN == '你的token':
        print("警告: 必须在 config.py 或环境变量中设置有效的 TUSHARE_TOKEN 才能拉取期货数据。")
        # 预留假数据返回，防止流程完全阻断（仅作快速demo跑通之用）
        # 建议真实使用时抛出异常或退出
        
    ts.set_token(TUSHARE_TOKEN)
    try:
        pro = ts.pro_api()
    except Exception as e:
        print(f"tushare api初始化失败: {e}")
        return None

    futures_df = {}
    
    # 获取JM焦煤期货连续合约
    try:
        df_jm = pro.fut_daily(ts_code='JM0.DCE', start_date='20150101')
        df_jm['trade_date'] = pd.to_datetime(df_jm['trade_date'])
        df_jm = df_jm.sort_values('trade_date').reset_index(drop=True)
        futures_df['JM'] = df_jm
    except Exception as e:
        print(f"获取JM数据失败: {e}")

    # 获取RB螺纹钢期货连续合约
    try:
        df_rb = pro.fut_daily(ts_code='RB0.SHF', start_date='20150101')
        df_rb['trade_date'] = pd.to_datetime(df_rb['trade_date'])
        df_rb = df_rb.sort_values('trade_date').reset_index(drop=True)
        futures_df['RB'] = df_rb
    except Exception as e:
        print(f"获取RB数据失败: {e}")
        
    # 获取动力煤期货对比数据
    try:
        df_zc = pro.fut_daily(ts_code='ZC0.CZCE', start_date='20150101')
        df_zc['trade_date'] = pd.to_datetime(df_zc['trade_date'])
        df_zc = df_zc.sort_values('trade_date').reset_index(drop=True)
        futures_df['ZC'] = df_zc
    except Exception as e:
        print(f"获取ZC数据失败: {e}")

    # 山西焦煤个股日线
    try:
        df_stock = pro.daily(ts_code='000983.SZ', start_date='20150101')
        df_stock['trade_date'] = pd.to_datetime(df_stock['trade_date'])
        df_stock = df_stock.sort_values('trade_date').reset_index(drop=True)
        # 计算 55 日均线
        df_stock['ma55'] = df_stock['close'].rolling(window=55).mean()
        futures_df['sxjm_stock'] = df_stock
    except Exception as e:
        print(f"获取 000983.SZ 数据失败: {e}")

    return futures_df


def fetch_macro():
    """
    获取 akshare 现货和宏观数据
    """
    macro_data = {}
    
    # 1. 螺纹钢现货价（上海）
    try:
        # 尝试不同版本可能支持的调用方式
        df_rb_spot = ak.futures_spot_price_daily()
        macro_data['rb_spot'] = df_rb_spot.to_dict('records')
    except TypeError:
        # Fallback if the argument is strictly required in some internal version, or simply skip
        # As it's non-critical if it fails, we catch TypeError
        pass
    except Exception as e:
        print(f"获取螺纹现货失败: {e}")

    # 2. 制造业PMI
    try:
        df_pmi = ak.macro_china_pmi_yearly()
        macro_data['pmi'] = df_pmi.iloc[-1].to_dict() if not df_pmi.empty else None
    except Exception as e:
        print(f"获取PMI失败: {e}")

    # 3. 粗钢产量
    try:
        df_steel_prod = ak.macro_china_steel_production()
        # 最新月度数据
        macro_data['steel_production'] = df_steel_prod.iloc[-1].to_dict() if not df_steel_prod.empty else None
    except Exception as e:
        print(f"获取粗钢产量失败: {e}")
        
    # 4. 房地产新开工面积同比
    try:
        df_real_estate = ak.macro_china_real_estate()
        macro_data['real_estate'] = df_real_estate.iloc[-1].to_dict() if not df_real_estate.empty else None
    except Exception as e:
        print(f"获取房地产数据失败: {e}")
        
    return macro_data

if __name__ == "__main__":
    # Test execution
    print("Testing futures module...")
    f_res = fetch_futures()
    if f_res:
        for k in f_res:
             print(f"{k}: {len(f_res[k])} records")
    print("Testing macro module...")
    m_res = fetch_macro()
    print(m_res)
