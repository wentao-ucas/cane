"""
使用 akshare 获取豆粕相关真实数据
数据来源: 东方财富、新浪财经、猪网等
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os

# 设置输出目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def fetch_soybean_meal_futures():
    """获取豆粕期货主力合约历史数据"""
    print("📊 获取豆粕期货历史数据...")
    df = ak.futures_main_sina(symbol="M0")
    # 打印原始列名以便调试
    print(f"   原始列名: {df.columns.tolist()}")
    # 重命名列（适配不同版本akshare）
    rename_map = {}
    for col in df.columns:
        if "日期" in col:
            rename_map[col] = "date"
        elif "开盘" in col:
            rename_map[col] = "open"
        elif "最高" in col:
            rename_map[col] = "high"
        elif "最低" in col:
            rename_map[col] = "low"
        elif "收盘" in col:
            rename_map[col] = "close"
        elif "成交量" in col or "volume" in col.lower():
            rename_map[col] = "volume"
        elif "持仓" in col:
            rename_map[col] = "open_interest"
    df = df.rename(columns=rename_map)
    # 只保留最近2年数据
    df["date"] = pd.to_datetime(df["date"])
    two_years_ago = datetime.now() - timedelta(days=730)
    df = df[df["date"] >= two_years_ago]
    return df


def fetch_soybean_meal_inventory():
    """获取豆粕期货库存数据"""
    print("📦 获取豆粕库存数据...")
    df = ak.futures_inventory_em(symbol="豆粕")
    df = df.rename(columns={
        "日期": "date",
        "库存": "inventory",
        "增减": "change"
    })
    df["date"] = pd.to_datetime(df["date"])
    return df


def fetch_pig_prices():
    """获取生猪价格数据"""
    print("🐷 获取生猪价格数据...")
    df = ak.futures_hog_core(symbol="外三元")
    df = df.rename(columns={
        "date": "date",
        "value": "pig_price"
    })
    df["date"] = pd.to_datetime(df["date"])
    return df


def fetch_feed_costs():
    """获取饲料原料成本数据"""
    print("🌾 获取玉米价格数据...")
    corn_df = ak.futures_hog_cost(symbol="玉米")
    corn_df = corn_df.rename(columns={"date": "date", "value": "corn_price"})
    corn_df["date"] = pd.to_datetime(corn_df["date"])
    
    print("🫘 获取豆粕现货价格数据...")
    meal_df = ak.futures_hog_cost(symbol="豆粕")
    meal_df = meal_df.rename(columns={"date": "date", "value": "meal_price"})
    meal_df["date"] = pd.to_datetime(meal_df["date"])
    
    return corn_df, meal_df


def fetch_pig_grain_ratio():
    """获取猪粮比价数据"""
    print("📈 获取猪粮比价数据...")
    df = ak.futures_hog_supply(symbol="猪粮比价")
    df = df.rename(columns={
        "date": "date",
        "value": "pig_grain_ratio"
    })
    df["date"] = pd.to_datetime(df["date"])
    return df


def fetch_hog_index():
    """获取生猪市场价格指数"""
    print("📊 获取生猪市场价格指数...")
    df = ak.index_hog_spot_price()
    df = df.rename(columns={
        "日期": "date",
        "指数": "index",
        "预期均价": "expected_price",
        "成交均价": "transaction_price"
    })
    df["date"] = pd.to_datetime(df["date"])
    return df


def create_pig_cycle_csv():
    """创建猪周期相关数据CSV"""
    print("\n" + "="*50)
    print("整合猪周期数据...")
    print("="*50)
    
    # 获取各项数据
    pig_df = fetch_pig_prices()
    ratio_df = fetch_pig_grain_ratio()
    
    print(f"   生猪价格数据范围: {pig_df['date'].min()} ~ {pig_df['date'].max()}")
    print(f"   猪粮比数据范围: {ratio_df['date'].min()} ~ {ratio_df['date'].max()}")
    
    # 按周合并数据 - 使用周一作为基准
    pig_df = pig_df.set_index("date").resample("W-MON").last().reset_index()
    ratio_df = ratio_df.set_index("date").resample("W-MON").last().reset_index()
    
    # 使用merge合并
    merged = pig_df.merge(ratio_df, on="date", how="outer")
    merged = merged.sort_values("date")
    
    # 前向填充缺失值
    merged["pig_price"] = merged["pig_price"].ffill().bfill()
    merged["pig_grain_ratio"] = merged["pig_grain_ratio"].ffill().bfill()
    
    # 保留最近1年
    one_year_ago = datetime.now() - timedelta(days=365)
    merged = merged[merged["date"] >= one_year_ago]
    
    # 格式化
    merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")
    merged = merged[["date", "pig_price", "pig_grain_ratio"]].dropna()
    
    output_path = os.path.join(DATA_DIR, "pig_cycle.csv")
    merged.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 保存: {output_path}")
    print(merged.tail())
    return merged


def create_crushing_margin_csv():
    """创建压榨利润相关数据CSV"""
    print("\n" + "="*50)
    print("整合压榨利润数据...")
    print("="*50)
    
    corn_df, meal_df = fetch_feed_costs()
    
    # 按周合并
    corn_df = corn_df.set_index("date").resample("W-TUE").last().reset_index()
    meal_df = meal_df.set_index("date").resample("W-TUE").last().reset_index()
    
    # 合并
    merged = corn_df.merge(meal_df, on="date", how="outer")
    merged = merged.sort_values("date")
    merged = merged.ffill()
    
    # 估算压榨利润 (简化公式: 豆粕价格 * 0.8 + 豆油价格估算 - 大豆成本估算)
    # 这里用豆粕现货价格 - 大豆进口成本估算
    # 假设大豆到港成本约为豆粕价格的1.3倍（简化）
    merged["crushing_margin"] = merged["meal_price"] * 0.8 - merged["corn_price"] * 0.5
    
    # 保留最近1年
    one_year_ago = datetime.now() - timedelta(days=365)
    merged = merged[merged["date"] >= one_year_ago]
    
    # 格式化
    merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")
    merged = merged[["date", "meal_price", "corn_price", "crushing_margin"]].dropna()
    
    output_path = os.path.join(DATA_DIR, "crushing_margin.csv")
    merged.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 保存: {output_path}")
    print(merged.tail())
    return merged


def create_inventory_csv():
    """创建库存数据CSV"""
    print("\n" + "="*50)
    print("整合库存数据...")
    print("="*50)
    
    inv_df = fetch_soybean_meal_inventory()
    
    # 按周取最后值
    inv_df = inv_df.set_index("date").resample("W-TUE").last().reset_index()
    
    # 保留最近6个月
    six_months_ago = datetime.now() - timedelta(days=180)
    inv_df = inv_df[inv_df["date"] >= six_months_ago]
    
    # 格式化
    inv_df["date"] = inv_df["date"].dt.strftime("%Y-%m-%d")
    inv_df = inv_df[["date", "inventory"]].dropna()
    
    output_path = os.path.join(DATA_DIR, "inventory.csv")
    inv_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 保存: {output_path}")
    print(inv_df.tail())
    return inv_df


def create_futures_data_csv():
    """创建期货历史数据CSV（用于contango分析）"""
    print("\n" + "="*50)
    print("整合期货数据...")
    print("="*50)
    
    futures_df = fetch_soybean_meal_futures()
    
    # 按周取收盘价
    futures_df = futures_df.set_index("date").resample("W-TUE").last().reset_index()
    
    # 保留最近1年
    one_year_ago = datetime.now() - timedelta(days=365)
    futures_df = futures_df[futures_df["date"] >= one_year_ago]
    
    # 格式化
    futures_df["date"] = futures_df["date"].dt.strftime("%Y-%m-%d")
    # 只选择存在的列
    cols_to_keep = ["date"]
    for col in ["close", "volume", "open_interest"]:
        if col in futures_df.columns:
            cols_to_keep.append(col)
    futures_df = futures_df[cols_to_keep].dropna()
    
    output_path = os.path.join(DATA_DIR, "soybean_meal_futures.csv")
    futures_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 保存: {output_path}")
    print(futures_df.tail())
    return futures_df


def main():
    """主函数"""
    print("="*60)
    print("🫘 豆粕ETF研究 - akshare数据获取")
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        create_pig_cycle_csv()
        create_crushing_margin_csv()
        create_inventory_csv()
        create_futures_data_csv()
        
        print("\n" + "="*60)
        print("✅ 所有数据更新完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
