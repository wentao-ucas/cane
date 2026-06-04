# -*- coding: utf-8 -*-
"""
压榨利润可视化脚本
Crushing Margin Visualization
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


def plot_crushing_margin(csv_path='data/crushing_margin.csv', output_path='output/crushing_margin.png'):
    """
    绘制压榨利润走势图（双Y轴：利润+开工率）
    Crushing margin trend with utilization rate
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    # 压榨利润柱状图（左Y轴）
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df['crushing_margin']]
    bars = ax1.bar(df['date'], df['crushing_margin'], width=20, color=colors, alpha=0.7,
                   label='压榨利润 / Crushing Margin')
    
    ax1.axhline(y=0, color='#34495e', linestyle='-', linewidth=1.5)
    ax1.axhline(y=-200, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axhline(y=200, color='#2ecc71', linestyle='--', linewidth=1, alpha=0.5)
    
    ax1.set_xlabel('日期 / Date', fontsize=11,
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax1.set_ylabel('压榨利润（元/吨）/ Crushing Margin (CNY/MT)', fontsize=11, color='#34495e',
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax1.tick_params(axis='y', labelcolor='#34495e')
    
    # 开工率折线图（右Y轴）
    ax2 = ax1.twinx()
    ax2.plot(df['date'], df['utilization_rate'], color='#3498db', linewidth=2.5, 
             marker='o', markersize=4, label='开工率 / Utilization Rate')
    ax2.set_ylabel('开工率 (%) / Utilization Rate (%)', fontsize=11, color='#3498db',
                   fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax2.tick_params(axis='y', labelcolor='#3498db')
    ax2.set_ylim(30, 70)
    
    # 设置标题
    ax1.set_title('豆粕压榨利润与开工率 / Crushing Margin & Utilization Rate', 
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
    
    ax1.grid(axis='y', alpha=0.3)
    
    ax1.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
             transform=ax1.transAxes, fontsize=8, color='gray',
             fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


def plot_crushing_breakdown(csv_path='data/crushing_margin.csv', output_path='output/crushing_breakdown.png'):
    """
    绘制压榨收益/成本分解图（最新数据）
    Crushing revenue/cost breakdown
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    latest = df.iloc[-1]
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150, facecolor='white')
    
    # 数据准备
    categories = ['豆粕收入\nMeal Revenue', '豆油收入\nOil Revenue', 
                  '大豆成本\nSoybean Cost', '加工费\nProcessing']
    values = [latest['meal_revenue'], latest['oil_revenue'], 
              -latest['soybean_cost'], -latest['crushing_fee']]
    colors = ['#2ecc71', '#27ae60', '#e74c3c', '#c0392b']
    
    bars = ax.barh(categories, values, color=colors, edgecolor='white', linewidth=1.5)
    
    # 添加数值标签
    for bar, val in zip(bars, values):
        width = bar.get_width()
        ax.annotate(f'{abs(val):.0f}',
                    xy=(width + (50 if width > 0 else -50), bar.get_y() + bar.get_height()/2),
                    ha='left' if width > 0 else 'right', va='center',
                    fontsize=11, fontweight='bold',
                    fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.axvline(x=0, color='#34495e', linewidth=1.5)
    
    # 添加利润标注
    margin = latest['crushing_margin']
    margin_color = '#2ecc71' if margin >= 0 else '#e74c3c'
    margin_text = f'压榨利润 / Margin: {margin:.0f} 元/吨'
    ax.annotate(margin_text, xy=(0.5, 0.95), xycoords='axes fraction',
                ha='center', va='top', fontsize=12, fontweight='bold',
                color=margin_color,
                fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME),
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=margin_color, alpha=0.8))
    
    ax.set_title(f'压榨利润分解 / Crushing Margin Breakdown\n({latest["date"].strftime("%Y-%m-%d")})', 
                 fontsize=14, fontweight='bold', pad=15,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('金额（元/吨）/ Amount (CNY/MT)', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


if __name__ == '__main__':
    plot_crushing_margin()
    plot_crushing_breakdown()
