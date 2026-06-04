# -*- coding: utf-8 -*-
"""
猪周期可视化脚本
Pig Cycle Visualization
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

# 字体设置
FONT_NAME = 'Microsoft YaHei'
mpl.rcParams['axes.unicode_minus'] = False


def plot_pig_cycle(csv_path='data/pig_cycle.csv', output_path='output/pig_cycle.png'):
    """
    绘制猪周期图（双Y轴：能繁母猪存栏 vs 猪价）
    Pig cycle: Breeding sow inventory vs hog price
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 能繁母猪存栏（左Y轴）
    ax1.plot(df['date'], df['breeding_sow_inventory'], color='#3498db', linewidth=2.5,
             label='能繁母猪存栏 / Breeding Sow Inventory')
    ax1.fill_between(df['date'], df['breeding_sow_inventory'], alpha=0.2, color='#3498db')
    
    ax1.set_xlabel('日期 / Date', fontsize=11,
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax1.set_ylabel('能繁母猪存栏（万头）/ Sow Inventory (10k heads)', fontsize=11, color='#3498db',
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax1.tick_params(axis='y', labelcolor='#3498db')
    
    # 生猪价格（右Y轴）
    ax2 = ax1.twinx()
    ax2.plot(df['date'], df['hog_price'], color='#e74c3c', linewidth=2.5,
             marker='o', markersize=3, label='生猪价格 / Hog Price')
    ax2.set_ylabel('生猪价格（元/公斤）/ Hog Price (CNY/kg)', fontsize=11, color='#e74c3c',
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    # 标题
    ax1.set_title('猪周期：能繁母猪存栏与生猪价格 / Pig Cycle: Sow Inventory & Hog Price', 
                  fontsize=14, fontweight='bold', pad=15,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
               prop=mpl.font_manager.FontProperties(family=FONT_NAME, size=10))
    
    # 设置刻度标签字体
    for label in ax1.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax1.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax2.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax1.grid(alpha=0.3)
    
    ax1.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
             transform=ax1.transAxes, fontsize=8, color='gray',
             fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


def plot_hog_corn_ratio(csv_path='data/pig_cycle.csv', output_path='output/hog_corn_ratio.png'):
    """
    绘制猪粮比走势图
    Hog-corn ratio trend
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 猪粮比区间填充
    ax.axhspan(0, 6, alpha=0.15, color='#e74c3c', label='亏损区 / Loss Zone (<6:1)')
    ax.axhspan(6, 7, alpha=0.15, color='#f39c12', label='盈亏平衡区 / Break-even (6-7:1)')
    ax.axhspan(7, 15, alpha=0.15, color='#2ecc71', label='盈利区 / Profit Zone (>7:1)')
    
    # 猪粮比曲线
    ax.plot(df['date'], df['hog_corn_ratio'], color='#34495e', linewidth=2.5,
            marker='o', markersize=3)
    
    # 关键线
    ax.axhline(y=6, color='#e74c3c', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.axhline(y=7, color='#2ecc71', linestyle='--', linewidth=1.5, alpha=0.7)
    
    ax.set_title('猪粮比走势 / Hog-Corn Ratio Trend', 
                 fontsize=14, fontweight='bold', pad=15,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('日期 / Date', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('猪粮比 / Hog-Corn Ratio', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.legend(loc='upper right',
              prop=mpl.font_manager.FontProperties(family=FONT_NAME, size=10))
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.set_ylim(4, 12)
    ax.grid(alpha=0.3)
    
    ax.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=8, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


def plot_breeding_profit(csv_path='data/pig_cycle.csv', output_path='output/breeding_profit.png'):
    """
    绘制养殖利润走势图
    Hog breeding profit trend
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 养殖利润柱状图
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df['breeding_profit']]
    ax.bar(df['date'], df['breeding_profit'], width=20, color=colors, alpha=0.7)
    
    ax.axhline(y=0, color='#34495e', linewidth=1.5)
    
    ax.set_title('生猪养殖利润走势 / Hog Breeding Profit Trend', 
                 fontsize=14, fontweight='bold', pad=15,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('日期 / Date', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('养殖利润（元/头）/ Breeding Profit (CNY/head)', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.grid(axis='y', alpha=0.3)
    
    # 添加图例说明
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', alpha=0.7, label='盈利 / Profit'),
        Patch(facecolor='#e74c3c', alpha=0.7, label='亏损 / Loss')
    ]
    ax.legend(handles=legend_elements, loc='upper right',
              prop=mpl.font_manager.FontProperties(family=FONT_NAME, size=10))
    
    ax.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=8, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


if __name__ == '__main__':
    plot_pig_cycle()
    plot_hog_corn_ratio()
    plot_breeding_profit()
