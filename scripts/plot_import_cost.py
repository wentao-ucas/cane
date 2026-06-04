# -*- coding: utf-8 -*-
"""
进口成本可视化脚本
Import Cost Visualization
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


def plot_import_cost_breakdown(csv_path='data/import_cost.csv', output_path='output/import_cost_breakdown.png'):
    """
    绘制进口成本构成堆叠柱状图
    Shows breakdown of import cost components
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    # 取最近12个月数据
    df = df.tail(12).copy()
    df['month'] = df['date'].dt.strftime('%Y-%m')
    
    # 计算各成本组成部分（简化计算）
    df['cbot_cny'] = df['cbot_price_usd_mt'] * df['fx_rate']  # CBOT成本（人民币）
    df['premium_cny'] = df['cnf_premium_brazil'] * df['fx_rate']  # 升贴水（含运费）
    df['tariff_cny'] = (df['cbot_cny'] + df['premium_cny']) * df['tariff_brazil']  # 关税
    df['vat_cny'] = (df['cbot_cny'] + df['premium_cny'] + df['tariff_cny']) * 0.09  # 增值税
    df['port_charge'] = 120  # 港杂费
    
    fig, ax = plt.subplots(figsize=(14, 7), dpi=150, facecolor='white')
    
    # 堆叠柱状图
    x = range(len(df))
    width = 0.6
    
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']
    
    bars1 = ax.bar(x, df['cbot_cny'], width, label='CBOT成本 / CBOT Cost', color=colors[0])
    bars2 = ax.bar(x, df['premium_cny'], width, bottom=df['cbot_cny'], 
                   label='升贴水+运费 / Premium+Freight', color=colors[1])
    bars3 = ax.bar(x, df['tariff_cny'], width, 
                   bottom=df['cbot_cny']+df['premium_cny'], 
                   label='关税 / Tariff', color=colors[2])
    bars4 = ax.bar(x, df['vat_cny'], width, 
                   bottom=df['cbot_cny']+df['premium_cny']+df['tariff_cny'], 
                   label='增值税 / VAT', color=colors[3])
    bars5 = ax.bar(x, df['port_charge'], width, 
                   bottom=df['cbot_cny']+df['premium_cny']+df['tariff_cny']+df['vat_cny'], 
                   label='港杂费 / Port Charges', color=colors[4])
    
    # 添加总成本标签
    for i, (idx, row) in enumerate(df.iterrows()):
        total = row['import_cost_brazil']
        ax.annotate(f'{total:.0f}',
                    xy=(i, total + 50),
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold',
                    fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['month'], rotation=45, ha='right',
                       fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.set_title('巴西大豆进口成本构成 / Brazil Soybean Import Cost Breakdown', 
                 fontsize=14, fontweight='bold', pad=15,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('月份 / Month', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('成本（元/吨）/ Cost (CNY/MT)', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.legend(loc='upper right', 
              prop=mpl.font_manager.FontProperties(family=FONT_NAME, size=9))
    
    ax.set_ylim(0, df['import_cost_brazil'].max() * 1.15)
    ax.grid(axis='y', alpha=0.3)
    
    # 添加数据时间戳
    ax.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=8, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


def plot_import_cost_trend(csv_path='data/import_cost.csv', output_path='output/import_cost_trend.png'):
    """
    绘制进口成本走势图（巴西 vs 美国对比）
    Import cost trend comparison: Brazil vs US
    """
    df = pd.read_csv(csv_path, encoding='utf-8-sig', parse_dates=['date'])
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150, facecolor='white')
    
    ax.plot(df['date'], df['import_cost_brazil'], 
            color='#2ecc71', linewidth=2.5, marker='o', markersize=4,
            label='巴西大豆成本 / Brazil Soybean Cost')
    ax.plot(df['date'], df['import_cost_us'], 
            color='#e74c3c', linewidth=2.5, marker='s', markersize=4,
            label='美国大豆成本 / US Soybean Cost')
    
    # 添加差价区域
    ax.fill_between(df['date'], df['import_cost_brazil'], df['import_cost_us'],
                    alpha=0.2, color='#e74c3c', label='美豆溢价 / US Premium')
    
    ax.set_title('进口大豆成本走势对比 / Import Soybean Cost Comparison', 
                 fontsize=14, fontweight='bold', pad=15,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('日期 / Date', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('成本（元/吨）/ Cost (CNY/MT)', fontsize=11,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.legend(loc='upper right', 
              prop=mpl.font_manager.FontProperties(family=FONT_NAME, size=10))
    
    ax.grid(alpha=0.3)
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    ax.text(0.02, 0.02, f'数据时间 / Data Date: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=8, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    plt.close()
    return output_path


if __name__ == '__main__':
    plot_import_cost_breakdown()
    plot_import_cost_trend()
