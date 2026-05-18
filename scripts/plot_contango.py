# -*- coding: utf-8 -*-
"""
豆粕期货升贴水可视化脚本
生成用于雪球文章的图表
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

# 设置中文字体 - 直接在每个Text对象上设置
# 这样可以绕过matplotlib的全局字体管理问题
FONT_NAME = 'Microsoft YaHei'

# 基础配置
mpl.rcParams['axes.unicode_minus'] = False

def plot_contango_chart(csv_path='data/soybean_meal_contango.csv', output_path='output/contango_chart.png'):
    """
    绘制升贴水柱状图
    """
    # 读取数据
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # 过滤有效数据
    df_valid = df[df['价差'].notna()].copy()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150, facecolor='white')
    
    # 设置颜色：贴水绿色（正面），升水红色（负面）
    colors = ['#2ecc71' if x < 0 else '#e74c3c' for x in df_valid['价差']]
    
    # 绘制柱状图
    bars = ax.bar(df_valid['合约'], df_valid['价差'], color=colors, edgecolor='white', linewidth=1.5)
    
    # 添加数据标签
    for bar, val, pct in zip(bars, df_valid['价差'], df_valid['价差比例(%)']):
        height = bar.get_height()
        ax.annotate(f'{val:.0f}\n({pct:.1f}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5 if height > 0 else -5),
                    textcoords="offset points",
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=10, fontweight='bold', fontname=FONT_NAME)
    
    # 添加零线
    ax.axhline(y=0, color='#34495e', linestyle='-', linewidth=1.5)
    
    # 设置标题和标签 - 使用fontproperties
    ax.set_title('豆粕期货各合约升贴水情况', fontsize=16, fontweight='bold', 
                 pad=20, fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('合约', fontsize=12, fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('价差（元/吨）', fontsize=12, fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 添加图例说明
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', edgecolor='white', label='贴水（移仓收益）'),
        Patch(facecolor='#e74c3c', edgecolor='white', label='升水（移仓损耗）')
    ]
    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=10, 
                       prop=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 添加时间戳
    ax.text(0.02, 0.02, f'数据时间: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=9, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    
    plt.close()
    return output_path


def plot_term_structure(csv_path='data/soybean_meal_contango.csv', output_path='output/term_structure.png'):
    """
    绘制期限结构图（价格曲线）
    """
    # 读取数据
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150, facecolor='white')
    
    # 绘制价格曲线
    ax.plot(df['合约'], df['收盘价'], 'o-', color='#3498db', linewidth=2.5, 
            markersize=10, markerfacecolor='white', markeredgewidth=2.5, label='收盘价')
    ax.plot(df['合约'], df['结算价'], 's--', color='#9b59b6', linewidth=2, 
            markersize=8, markerfacecolor='white', markeredgewidth=2, alpha=0.7, label='结算价')
    
    # 添加价格标签
    for i, (contract, price) in enumerate(zip(df['合约'], df['收盘价'])):
        ax.annotate(f'{price:.0f}', (contract, price), 
                    textcoords="offset points", xytext=(0, 12),
                    ha='center', fontsize=10, fontweight='bold', color='#2c3e50',
                    fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 填充升贴水区域
    ax.fill_between(df['合约'], df['收盘价'], df['收盘价'].iloc[0], 
                    alpha=0.1, color='#3498db')
    
    # 设置标题和标签
    ax.set_title('豆粕期货期限结构', fontsize=16, fontweight='bold', pad=20,
                 fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_xlabel('合约月份', fontsize=12, 
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    ax.set_ylabel('价格（元/吨）', fontsize=12,
                  fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 设置刻度标签字体
    for label in ax.get_xticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    for label in ax.get_yticklabels():
        label.set_fontproperties(mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 图例
    legend = ax.legend(loc='upper right', fontsize=10,
                       prop=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 设置Y轴范围，留出标签空间
    y_min, y_max = df['收盘价'].min(), df['收盘价'].max()
    y_range = y_max - y_min
    ax.set_ylim(y_min - y_range * 0.1, y_max + y_range * 0.15)
    
    # 添加时间戳
    ax.text(0.02, 0.02, f'数据时间: {datetime.now().strftime("%Y-%m-%d")}',
            transform=ax.transAxes, fontsize=9, color='gray',
            fontproperties=mpl.font_manager.FontProperties(family=FONT_NAME))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"图表已保存至: {output_path}")
    
    plt.close()
    return output_path


def main():
    import os
    
    # 确保输出目录存在
    os.makedirs('output', exist_ok=True)
    
    print("=" * 50)
    print("豆粕期货升贴水可视化")
    print("=" * 50)
    
    # 生成升贴水柱状图
    print("\n正在生成升贴水柱状图...")
    plot_contango_chart()
    
    # 生成期限结构图
    print("\n正在生成期限结构图...")
    plot_term_structure()
    
    print("\n✅ 所有图表生成完成！")


if __name__ == "__main__":
    main()
