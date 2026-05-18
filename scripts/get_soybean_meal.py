# -*- coding: utf-8 -*-
"""
豆粕期货升贴水数据获取脚本
用于分析各合约升贴水情况，判断移仓成本
"""

import sys
import io

# Windows 编码处理
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import akshare as ak
import pandas as pd
from datetime import datetime


def get_soybean_meal_futures():
    """
    获取豆粕期货各合约行情数据
    返回: DataFrame 包含各合约价格信息
    """
    try:
        # 获取豆粕期货实时行情
        df = ak.futures_zh_spot(symbol="M0", market="DCE", adjust="0")
        return df
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return None


def get_soybean_meal_daily():
    """
    获取豆粕主力合约日线数据
    """
    try:
        # 获取豆粕主力连续合约数据
        df = ak.futures_main_sina(symbol="M0")
        return df
    except Exception as e:
        print(f"获取日线数据失败: {e}")
        return None


def get_all_contracts_price():
    """
    获取豆粕所有合约价格，计算升贴水
    """
    try:
        # 获取大商所豆粕期货行情
        df = ak.get_futures_daily(start_date='20260101', end_date=datetime.now().strftime('%Y%m%d'), market='DCE')
        
        # 筛选豆粕合约 (合约代码以 M 开头)
        df_m = df[df['symbol'].str.startswith('M')]
        return df_m
    except Exception as e:
        print(f"获取合约数据失败: {e}")
        # 备用方案
        return get_contracts_via_sina()


def get_contracts_via_sina():
    """
    通过新浪接口获取豆粕各合约数据
    """
    try:
        # 动态生成合约月份 - 豆粕主要交易月份为1、3、5、7、8、9、11月
        # 根据当前时间选择合适的合约
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # 豆粕合约月份
        contract_months = [1, 3, 5, 7, 8, 9, 11]
        contracts = []
        
        # 生成当前年份和下一年份的合约
        for year in [current_year, current_year + 1]:
            year_suffix = str(year)[2:]  # 取后两位，如2026->26
            for month in contract_months:
                # 跳过已过期的合约（当年已过的月份）
                if year == current_year and month < current_month:
                    continue
                contract = f"M{year_suffix}{month:02d}"
                contracts.append(contract)
        
        # 只取前7个活跃合约
        contracts = contracts[:7]
        print(f"正在获取合约: {contracts}")
        
        result = []
        for contract in contracts:
            try:
                df = ak.futures_zh_daily_sina(symbol=contract)
                if df is not None and len(df) > 0:
                    latest = df.iloc[-1]
                    result.append({
                        '合约': contract,
                        '日期': latest.get('date', 'N/A'),
                        '收盘价': latest.get('close', 0),
                        '结算价': latest.get('settle', latest.get('close', 0)),
                        '持仓量': latest.get('hold', 0)
                    })
            except Exception as e:
                print(f"获取 {contract} 失败: {e}")
                continue
        
        return pd.DataFrame(result)
    except Exception as e:
        print(f"新浪接口获取失败: {e}")
        return None


def calculate_contango_backwardation(df):
    """
    计算升贴水情况
    升水(Contango): 远月价格 > 近月价格，移仓时亏损
    贴水(Backwardation): 远月价格 < 近月价格，移仓时盈利
    
    参数:
        df: 包含各合约价格的 DataFrame
    返回:
        带有升贴水计算结果的 DataFrame
    """
    if df is None or len(df) == 0:
        print("无数据可计算")
        return None
    
    # 按合约排序 (时间顺序)
    df = df.sort_values('合约').reset_index(drop=True)
    
    # 计算相邻合约价差
    df['下一合约价格'] = df['收盘价'].shift(-1)
    df['价差'] = df['下一合约价格'] - df['收盘价']
    df['价差比例(%)'] = (df['价差'] / df['收盘价'] * 100).round(2)
    
    # 判断升贴水
    def judge_contango(row):
        if pd.isna(row['价差']):
            return '-'
        elif row['价差'] > 0:
            return '升水(移仓亏)'
        elif row['价差'] < 0:
            return '贴水(移仓赚)'
        else:
            return '平水'
    
    df['升贴水状态'] = df.apply(judge_contango, axis=1)
    
    return df


def main():
    print("=" * 60)
    print("豆粕期货升贴水分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取各合约价格
    print("\n正在获取豆粕各合约数据...")
    df = get_contracts_via_sina()
    
    if df is not None and len(df) > 0:
        print("\n【各合约最新价格】")
        print(df.to_string(index=False))
        
        # 计算升贴水
        print("\n【升贴水分析】")
        df_result = calculate_contango_backwardation(df)
        if df_result is not None:
            display_cols = ['合约', '收盘价', '价差', '价差比例(%)', '升贴水状态']
            print(df_result[display_cols].to_string(index=False))
            
            # 总结
            print("\n【移仓成本总结】")
            total_spread = df_result['价差'].dropna().sum()
            if total_spread > 0:
                print(f"整体呈现升水结构，如持有ETF，展期会有约 {abs(total_spread):.0f} 元/吨的损耗")
            elif total_spread < 0:
                print(f"整体呈现贴水结构，如持有ETF，展期会有约 {abs(total_spread):.0f} 元/吨的收益")
            else:
                print("整体接近平水，展期成本较低")
            
            # 保存结果
            output_file = 'data/soybean_meal_contango.csv'
            df_result.to_csv(output_file, encoding='utf-8-sig', index=False)
            print(f"\n数据已保存至: {output_file}")
    else:
        print("未能获取到数据，请检查网络连接或数据源")


if __name__ == "__main__":
    main()
