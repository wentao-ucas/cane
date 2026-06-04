# -*- coding: utf-8 -*-
"""
库存数据可视化脚本
Inventory Visualization
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


def plot_inventory(csv_path='data/inventory.csv', output_path='output/inventory.png'):
    """
    绘制库存走势图（港口大豆库存 + 油厂豆粕库存）
    Inventory trend: Port soybean + Plant meal inventory
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    # 取最近一年数据
    df = df.tail(52).copy()
    
    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 港口大豆库存（左Y轴）
    ax1.fill_between(df['date'], df['port_soybean_inventory'], alpha=0.3, color='#3498db')
    ax1.plot(df['date'], df['port_soybean_inventory'], color='#3498db', linewidth=2,
             label='港口大豆库存 / Port Soybean Inventory')
    
    ax1.set_xlabel('日期 / Date', fontsize=11,
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax1.set_ylabel('港口大豆库存（万吨）/ Port Inventory (10k MT)', fontsize=11, color='#3498db',
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax1.tick_params(axis='y', labelcolor='#3498db')
    
    # 油厂豆粕库存（右Y轴）
    ax2 = ax1.twinx()
    ax2.fill_between(df['date'], df['plant_meal_inventory'], alpha=0.3, color='#e74c3c')
    ax2.plot(df['date'], df['plant_meal_inventory'], color='#e74c3c', linewidth=2,
             label='油厂豆粕库存 / Plant Meal Inventory')
    ax2.set_ylabel('油厂豆粕库存（万吨）/ Plant Meal Inventory (10k MT)', fontsize=11, color='#e74c3c',
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    # 标题
    ax1.set_title('大豆与豆粕库存走势 / Soybean & Meal Inventory Trend', 
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


def plot_days_of_supply(csv_path='data/inventory.csv', output_path='output/days_of_supply.png'):
    """
    绘制可用天数走势图
    Days of supply trend
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    # 取最近一年数据
    df = df.tail(52).copy()
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 区域填充
    ax.axhspan(0, 14, alpha=0.15, color='#e74c3c', label='偏紧 / Tight (<14天)')
    ax.axhspan(14, 18, alpha=0.15, color='#f39c12', label='正常 / Normal (14-18天)')
    ax.axhspan(18, 30, alpha=0.15, color='#2ecc71', label='宽松 / Ample (>18天)')
    
    # 可用天数曲线
    ax.plot(df['date'], df['days_of_supply'], color='#34495e', linewidth=2.5,
            marker='o', markersize=3)
    
    ax.set_title('大豆库存可用天数 / Soybean Days of Supply', 
                 fontsize=14, fontweight='bold', pad=15,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('日期 / Date', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('可用天数 / Days of Supply', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.legend(loc='upper right',
              prop=mpl.font_manager.FontProperties(family=FONT_NAME, size=10))
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.set_ylim(10, 25)
    ax.grid(alpha=0.3)
    
    ax.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=8, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


if __name__ == '__main__':
    plot_inventory()
    plot_days_of_supply()
