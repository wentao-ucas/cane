# -*- coding: utf-8 -*-
"""
豆粕ETF研究 - 图表生成脚本
使用 akshare 获取的真实数据生成所有图表
"""

import sys
import io

# Windows 编码处理
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
import os

# 字体设置
FONT_NAME = 'Microsoft YaHei'
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['font.family'] = ['Microsoft YaHei', 'DejaVu Sans']

# 颜色主题
COLORS = {
    'primary': '#3498db',
    'secondary': '#e74c3c', 
    'tertiary': '#2ecc71',
    'warning': '#f39c12',
    'neutral': '#7f8c8d'
}

# 路径设置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def get_font_props(size=10):
    """获取字体属性"""
    return mpl.font_manager.FontProperties(family=FONT_NAME, size=size)


def add_watermark(ax):
    """添加数据来源水印"""
    ax.text(0.02, 0.02, 
            f'数据来源: akshare | {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=8, color='gray',
            fontproperties=get_font_props(8))


def plot_pig_cycle():
    """绘制猪周期图表 - 生猪价格与猪粮比"""
    print("📈 生成猪周期图表...")
    
    df = pd.read_csv(os.path.join(DATA_DIR, "pig_cycle.csv"), 
                     encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 生猪价格（左Y轴）
    ax1.plot(df['date'], df['pig_price'], color=COLORS['primary'], 
             linewidth=2.5, label='生猪价格 / Hog Price')
    ax1.fill_between(df['date'], df['pig_price'], alpha=0.2, color=COLORS['primary'])
    
    ax1.set_xlabel('日期 / Date', fontsize=11, fontproperties=get_font_props(11))
    ax1.set_ylabel('生猪价格（元/公斤）/ Hog Price (CNY/kg)', fontsize=11, 
                   color=COLORS['primary'], fontproperties=get_font_props(11))
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
    
    # 猪粮比（右Y轴）
    ax2 = ax1.twinx()
    ax2.plot(df['date'], df['pig_grain_ratio'], color=COLORS['secondary'], 
             linewidth=2.5, linestyle='--', label='猪粮比 / Hog-Grain Ratio')
    
    # 添加猪粮比警戒线
    ax2.axhline(y=6.0, color=COLORS['warning'], linestyle=':', alpha=0.7, linewidth=1.5)
    ax2.axhline(y=7.0, color=COLORS['tertiary'], linestyle=':', alpha=0.7, linewidth=1.5)
    ax2.text(df['date'].iloc[-1], 6.0, ' 盈亏平衡线', fontsize=9, 
             color=COLORS['warning'], va='center', fontproperties=get_font_props(9))
    ax2.text(df['date'].iloc[-1], 7.0, ' 合理利润区', fontsize=9,
             color=COLORS['tertiary'], va='center', fontproperties=get_font_props(9))
    
    ax2.set_ylabel('猪粮比 / Hog-Grain Ratio', fontsize=11, 
                   color=COLORS['secondary'], fontproperties=get_font_props(11))
    ax2.tick_params(axis='y', labelcolor=COLORS['secondary'])
    
    # 标题
    ax1.set_title('猪周期与饲料需求 / Hog Cycle & Feed Demand', 
                  fontsize=14, fontweight='bold', pad=15, fontproperties=get_font_props(14))
    
    # 图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
               prop=get_font_props(10))
    
    ax1.grid(alpha=0.3)
    add_watermark(ax1)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "pig_cycle.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   ✅ 保存: {output_path}")


def plot_crushing_margin():
    """绘制压榨利润与饲料价格图表"""
    print("📈 生成压榨利润图表...")
    
    df = pd.read_csv(os.path.join(DATA_DIR, "crushing_margin.csv"), 
                     encoding='utf-8-sig', parse_dates=['date'])
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), dpi=150, facecolor='white')
    
    # 上图：豆粕与玉米价格
    ax1.plot(df['date'], df['meal_price'], color=COLORS['primary'], 
             linewidth=2.5, label='豆粕价格 / Soybean Meal Price')
    ax1.plot(df['date'], df['corn_price'], color=COLORS['tertiary'], 
             linewidth=2.5, label='玉米价格 / Corn Price')
    
    ax1.set_ylabel('价格（元/吨）/ Price (CNY/MT)', fontsize=11, 
                   fontproperties=get_font_props(11))
    ax1.set_title('饲料原料价格走势 / Feed Ingredient Prices', 
                  fontsize=14, fontweight='bold', pad=10, fontproperties=get_font_props(14))
    ax1.legend(loc='upper right', prop=get_font_props(10))
    ax1.grid(alpha=0.3)
    
    # 添加最新价格标注
    latest = df.iloc[-1]
    ax1.annotate(f'豆粕: {latest["meal_price"]:.0f}', 
                 xy=(latest['date'], latest['meal_price']),
                 xytext=(10, 10), textcoords='offset points',
                 fontsize=10, color=COLORS['primary'],
                 fontproperties=get_font_props(10))
    ax1.annotate(f'玉米: {latest["corn_price"]:.0f}', 
                 xy=(latest['date'], latest['corn_price']),
                 xytext=(10, -15), textcoords='offset points',
                 fontsize=10, color=COLORS['tertiary'],
                 fontproperties=get_font_props(10))
    
    # 下图：压榨利润
    ax2.fill_between(df['date'], df['crushing_margin'], alpha=0.3, color=COLORS['secondary'])
    ax2.plot(df['date'], df['crushing_margin'], color=COLORS['secondary'], 
             linewidth=2.5, label='压榨利润(估算) / Crushing Margin (Est.)')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    ax2.set_xlabel('日期 / Date', fontsize=11, fontproperties=get_font_props(11))
    ax2.set_ylabel('压榨利润（元/吨）/ Crushing Margin (CNY/MT)', fontsize=11, 
                   fontproperties=get_font_props(11))
    ax2.set_title('油厂压榨利润估算 / Crushing Margin Estimation', 
                  fontsize=14, fontweight='bold', pad=10, fontproperties=get_font_props(14))
    ax2.legend(loc='upper right', prop=get_font_props(10))
    ax2.grid(alpha=0.3)
    add_watermark(ax2)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "crushing_margin.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   ✅ 保存: {output_path}")


def plot_inventory():
    """绘制期货库存图表"""
    print("📈 生成库存图表...")
    
    df = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"), 
                     encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 库存柱状图
    ax.bar(df['date'], df['inventory'] / 10000, color=COLORS['primary'], 
           alpha=0.7, width=5, label='期货库存 / Futures Inventory')
    
    ax.set_xlabel('日期 / Date', fontsize=11, fontproperties=get_font_props(11))
    ax.set_ylabel('库存（万吨）/ Inventory (10k MT)', fontsize=11, 
                  fontproperties=get_font_props(11))
    ax.set_title('豆粕期货库存 / Soybean Meal Futures Inventory', 
                 fontsize=14, fontweight='bold', pad=15, fontproperties=get_font_props(14))
    
    # 添加最新数据标注
    latest = df.iloc[-1]
    ax.annotate(f'{latest["inventory"]/10000:.2f}万吨', 
                xy=(latest['date'], latest['inventory']/10000),
                xytext=(0, 10), textcoords='offset points',
                fontsize=11, color=COLORS['primary'], ha='center',
                fontproperties=get_font_props(11))
    
    ax.legend(loc='upper left', prop=get_font_props(10))
    ax.grid(alpha=0.3, axis='y')
    add_watermark(ax)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "inventory.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   ✅ 保存: {output_path}")


def plot_futures_price():
    """绘制期货价格走势图"""
    print("📈 生成期货价格图表...")
    
    df = pd.read_csv(os.path.join(DATA_DIR, "soybean_meal_futures.csv"), 
                     encoding='utf-8-sig', parse_dates=['date'])
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), dpi=150, 
                                    facecolor='white', height_ratios=[2, 1])
    
    # 上图：价格走势
    ax1.plot(df['date'], df['close'], color=COLORS['primary'], 
             linewidth=2.5, label='收盘价 / Close Price')
    ax1.fill_between(df['date'], df['close'], alpha=0.2, color=COLORS['primary'])
    
    # 添加均线
    if len(df) > 20:
        df['ma20'] = df['close'].rolling(window=20).mean()
        ax1.plot(df['date'], df['ma20'], color=COLORS['warning'], 
                 linewidth=1.5, linestyle='--', label='20周均线 / MA20')
    
    ax1.set_ylabel('价格（元/吨）/ Price (CNY/MT)', fontsize=11, 
                   fontproperties=get_font_props(11))
    ax1.set_title('豆粕期货主力合约价格 / Soybean Meal Futures Main Contract', 
                  fontsize=14, fontweight='bold', pad=10, fontproperties=get_font_props(14))
    ax1.legend(loc='upper right', prop=get_font_props(10))
    ax1.grid(alpha=0.3)
    
    # 最新价格标注
    latest = df.iloc[-1]
    ax1.annotate(f'最新: {latest["close"]:.0f}', 
                 xy=(latest['date'], latest['close']),
                 xytext=(10, 10), textcoords='offset points',
                 fontsize=11, color=COLORS['primary'],
                 fontproperties=get_font_props(11),
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 下图：成交量
    if 'volume' in df.columns:
        ax2.bar(df['date'], df['volume'] / 10000, color=COLORS['neutral'], 
                alpha=0.7, width=5, label='成交量 / Volume')
        ax2.set_xlabel('日期 / Date', fontsize=11, fontproperties=get_font_props(11))
        ax2.set_ylabel('成交量（万手）/ Volume (10k lots)', fontsize=11, 
                       fontproperties=get_font_props(11))
        ax2.legend(loc='upper right', prop=get_font_props(10))
        ax2.grid(alpha=0.3, axis='y')
    
    add_watermark(ax2)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "futures_price.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   ✅ 保存: {output_path}")


def plot_supply_demand_summary():
    """绘制供需分析汇总图"""
    print("📈 生成供需分析汇总图...")
    
    # 读取所有数据获取最新值
    pig_df = pd.read_csv(os.path.join(DATA_DIR, "pig_cycle.csv"), encoding='utf-8-sig')
    margin_df = pd.read_csv(os.path.join(DATA_DIR, "crushing_margin.csv"), encoding='utf-8-sig')
    inv_df = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"), encoding='utf-8-sig')
    futures_df = pd.read_csv(os.path.join(DATA_DIR, "soybean_meal_futures.csv"), encoding='utf-8-sig')
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=150, facecolor='white')
    
    # 左上：期货价格
    ax1 = axes[0, 0]
    futures_df['date'] = pd.to_datetime(futures_df['date'])
    ax1.plot(futures_df['date'], futures_df['close'], color=COLORS['primary'], linewidth=2)
    ax1.fill_between(futures_df['date'], futures_df['close'], alpha=0.2, color=COLORS['primary'])
    ax1.set_title('豆粕期货价格 / Futures Price', fontsize=12, fontweight='bold',
                  fontproperties=get_font_props(12))
    ax1.set_ylabel('元/吨', fontproperties=get_font_props(10))
    ax1.grid(alpha=0.3)
    latest_price = futures_df['close'].iloc[-1]
    ax1.annotate(f'{latest_price:.0f}', xy=(0.95, 0.95), xycoords='axes fraction',
                 fontsize=20, fontweight='bold', color=COLORS['primary'], ha='right',
                 fontproperties=get_font_props(20))
    
    # 右上：猪周期
    ax2 = axes[0, 1]
    pig_df['date'] = pd.to_datetime(pig_df['date'])
    ax2.plot(pig_df['date'], pig_df['pig_price'], color=COLORS['secondary'], linewidth=2)
    ax2.fill_between(pig_df['date'], pig_df['pig_price'], alpha=0.2, color=COLORS['secondary'])
    ax2.set_title('生猪价格 / Hog Price', fontsize=12, fontweight='bold',
                  fontproperties=get_font_props(12))
    ax2.set_ylabel('元/公斤', fontproperties=get_font_props(10))
    ax2.grid(alpha=0.3)
    latest_pig = pig_df['pig_price'].iloc[-1]
    ax2.annotate(f'{latest_pig:.2f}', xy=(0.95, 0.95), xycoords='axes fraction',
                 fontsize=20, fontweight='bold', color=COLORS['secondary'], ha='right',
                 fontproperties=get_font_props(20))
    
    # 左下：饲料价格
    ax3 = axes[1, 0]
    margin_df['date'] = pd.to_datetime(margin_df['date'])
    ax3.plot(margin_df['date'], margin_df['meal_price'], color=COLORS['primary'], 
             linewidth=2, label='豆粕')
    ax3.plot(margin_df['date'], margin_df['corn_price'], color=COLORS['tertiary'], 
             linewidth=2, label='玉米')
    ax3.set_title('饲料价格 / Feed Prices', fontsize=12, fontweight='bold',
                  fontproperties=get_font_props(12))
    ax3.set_ylabel('元/吨', fontproperties=get_font_props(10))
    ax3.legend(prop=get_font_props(9))
    ax3.grid(alpha=0.3)
    
    # 右下：库存
    ax4 = axes[1, 1]
    inv_df['date'] = pd.to_datetime(inv_df['date'])
    ax4.bar(inv_df['date'], inv_df['inventory']/10000, color=COLORS['warning'], alpha=0.7, width=5)
    ax4.set_title('期货库存 / Futures Inventory', fontsize=12, fontweight='bold',
                  fontproperties=get_font_props(12))
    ax4.set_ylabel('万吨', fontproperties=get_font_props(10))
    ax4.grid(alpha=0.3, axis='y')
    latest_inv = inv_df['inventory'].iloc[-1]
    ax4.annotate(f'{latest_inv/10000:.2f}万吨', xy=(0.95, 0.95), xycoords='axes fraction',
                 fontsize=16, fontweight='bold', color=COLORS['warning'], ha='right',
                 fontproperties=get_font_props(16))
    
    # 总标题
    fig.suptitle('豆粕供需分析仪表盘 / Soybean Meal Supply-Demand Dashboard', 
                 fontsize=16, fontweight='bold', y=1.02,
                 fontproperties=get_font_props(16))
    
    add_watermark(axes[1, 1])
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "supply_demand_summary.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"   ✅ 保存: {output_path}")


def main():
    """生成所有图表"""
    print("="*60)
    print("🫘 豆粕ETF研究 - 图表生成")
    print(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        plot_pig_cycle()
        plot_crushing_margin()
        plot_inventory()
        plot_futures_price()
        plot_supply_demand_summary()
        
        print("\n" + "="*60)
        print("✅ 所有图表生成完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
