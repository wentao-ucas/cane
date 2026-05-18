import akshare as ak
import pandas as pd
import os
import datetime

# CSV 文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MYSTEEL_DATA_FILE = os.path.join(DATA_DIR, "mysteel_data.csv")
MACRO_DATA_FILE = os.path.join(DATA_DIR, "macro_data.csv")

def get_latest_futures_data():
    """获取最新焦煤和螺纹钢主力合约数据"""
    data = {}
    try:
        # 获取焦煤主力合约
        df_jm = ak.futures_zh_daily_sina(symbol="jm0")
        latest_jm = df_jm.iloc[-1]
        data['jm_futures_price'] = latest_jm['close']
        data['jm_futures_date'] = latest_jm['date']
        
        # 获取螺纹钢主力合约
        df_rb = ak.futures_zh_daily_sina(symbol="rb0")
        latest_rb = df_rb.iloc[-1]
        data['rb_futures_price'] = latest_rb['close']
        data['rb_futures_date'] = latest_rb['date']

        # 获取五年均价 (简单估算: 近1000个交易日)
        data['jm_5yr_avg'] = df_jm['close'].tail(1000).mean() if len(df_jm) > 1000 else df_jm['close'].mean()
        data['rb_5yr_avg'] = df_rb['close'].tail(1000).mean() if len(df_rb) > 1000 else df_rb['close'].mean()

    except Exception as e:
        print(f"获取期货数据失败: {e}")
        data['jm_futures_price'] = None
        data['rb_futures_price'] = None
    
    return data

def get_macro_data():
    """获取宏观数据 (PMI, PPI)"""
    data = {}
    try:
        df_pmi = ak.macro_china_pmi()
        latest_pmi = df_pmi.iloc[-1]
        data['pmi'] = latest_pmi['制造业-指数']
        data['pmi_date'] = latest_pmi['月份']
    except Exception as e:
        print(f"获取PMI数据失败: {e}")
        data['pmi'] = None

    try:
        df_ppi = ak.macro_china_ppi()
        latest_ppi = df_ppi.iloc[-1]
        data['ppi_yoy'] = latest_ppi['当月同比增长']
        data['ppi_date'] = latest_ppi['月份']
    except Exception as e:
        print(f"获取PPI数据失败: {e}")
        data['ppi_yoy'] = None
    
    return data

def get_mysteel_data():
    """读取本地维护的钢联等核心手工数据"""
    if not os.path.exists(MYSTEEL_DATA_FILE):
        print(f"警告: 找不到本地手工数据文件 {MYSTEEL_DATA_FILE}")
        return None
    
    try:
        df = pd.read_csv(MYSTEEL_DATA_FILE)
        if df.empty:
            return None
            
        # 按照日期排序确保最后一行是最新的
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values(by='日期')
        
        # 返回最新的一周数据
        return df.iloc[-1].to_dict()
    except Exception as e:
        print(f"读取本地手工数据失败: {e}")
        return None

def fetch_all_data():
    """汇总所有数据源"""
    print("开始获取数据...")
    
    ret = {
        "fetch_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 1. 期货数据
    futures_data = get_latest_futures_data()
    ret.update(futures_data)
    
    # 2. 宏观数据
    macro_data = get_macro_data()
    ret.update(macro_data)
    
    # 3. 钢联手工数据
    mysteel_data = get_mysteel_data()
    if mysteel_data:
        # 修改key使其更符合英文变量名（内部计算用）
        mapping = {
            '日期': 'mysteel_date',
            '螺纹钢均价': 'rb_spot_price',
            '山西低硫主焦现货价': 'jm_spot_price',
            '高炉开工率': 'bf_utilization',
            '日均铁水产量': 'hot_metal_output',
            '独立焦化厂开工率': 'coking_utilization',
            '钢厂盈利比例': 'mill_profit_ratio',
            '焦炭提涨次数': 'coke_raise_count',
            '焦炭提降次数': 'coke_reduce_count',
            '焦化厂焦煤库存天数': 'coking_coal_inventory_days',
            '焦煤流拍率': 'auction_fail_rate',
            '螺纹钢库存': 'rb_inventory',
        }
        for k, v in mysteel_data.items():
            if k in mapping:
                # 转换日期格式防止变成Timestamp对象导致json序列化失败
                if k == '日期' and isinstance(v, pd.Timestamp):
                    ret[mapping[k]] = v.strftime("%Y-%m-%d")
                else:
                    ret[mapping[k]] = v
                    
    return ret

if __name__ == "__main__":
    import pprint
    data = fetch_all_data()
    print("\n获取到的综合数据快照:")
    pprint.pprint(data)
