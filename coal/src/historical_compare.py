# src/historical_compare.py
import pandas as pd

HISTORICAL_CYCLES = {
    "2015_bottom": {
        "date_range": ("2015-09-01", "2016-01-31"),
        "description": "供给侧改革前底部",
        "jm_price_range": (700, 850),
        "rb_price_range": (1800, 2200),
        "hot_metal_range": (210, 225),
        "bf_utilization_range": (68, 73),
        "reversal_trigger": "2016年政策强制去产能，1.4亿吨地条钢出清",
        "weeks_from_bottom_to_signal": 12,
    },
    "2021_top": {
        "date_range": ("2021-04-01", "2021-09-30"),
        "description": "供改红利顶部",
        "jm_price_range": (2800, 4200),
        "rb_price_range": (5000, 6200),
        "hot_metal_range": (260, 270),
        "bf_utilization_range": (90, 95),
        "reversal_trigger": "恒大暴雷，房地产需求崩塌",
        "weeks_from_top_to_signal": 8,
    },
    "2023_mini_recovery": {
        "date_range": ("2023-01-01", "2023-05-31"),
        "description": "疫后修复小周期",
        "jm_price_range": (1400, 1800),
        "rb_price_range": (3800, 4400),
        "hot_metal_range": (238, 248),
        "bf_utilization_range": (78, 85),
        "reversal_trigger": "地产政策刺激预期落空，需求不及预期",
        "weeks_from_top_to_signal": 6,
    }
}

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REVERSAL_THRESHOLDS

def find_closest_historical_cycle(current_val, indicator):
    """
    查找当前值最接近哪个历史周期的区间
    """
    map_to_history_key = {
        'hot_metal_daily': 'hot_metal_range',
        'bf_utilization': 'bf_utilization_range',
    }
    
    if indicator not in map_to_history_key:
        return "N/A"
        
    hist_key = map_to_history_key[indicator]
    
    closest = None
    min_dist = float('inf')
    
    for cycle_name, meta in HISTORICAL_CYCLES.items():
        low, high = meta[hist_key]
        if low <= current_val <= high:
            return cycle_name
            
        # 如果不在区间内，计算距离最近端点的距离
        dist = min(abs(current_val - low), abs(current_val - high))
        if dist < min_dist:
            min_dist = dist
            closest = cycle_name
            
    return closest

def compare_with_history(current_data, mysteel_df, futures_df):
    """
    对每个关键指标计算差异和预估到达反转阈值的周数
    """
    results = {}
    
    indicators_to_check = ['hot_metal_daily', 'bf_utilization', 'mill_profit_pct']
    
    for indicator in indicators_to_check:
        current_val = current_data[indicator]
        
        # 最近6周变化速度
        # 如果数据不足6周，就利用实际长度
        window = min(6, len(mysteel_df))
        if window > 1:
            recent_vals = mysteel_df[indicator].tail(window).values
            weekly_change = (recent_vals[-1] - recent_vals[0]) / (window - 1)
        else:
            weekly_change = 0
            
        # 距离反转阈值
        threshold = REVERSAL_THRESHOLDS.get(indicator, 0)
        gap = threshold - current_val
        
        if weekly_change > 0:
            weeks_to_threshold = gap / weekly_change
        else:
            weeks_to_threshold = 999  # 方向错误或无变化 (用999表示无穷大)
            
        # 匹配最近历史节点 (利润比例没有设定的区间，特殊处理忽略)
        if indicator != 'mill_profit_pct':
            closest_cycle = find_closest_historical_cycle(current_val, indicator)
        else:
            closest_cycle = "N/A"
            
        results[indicator] = {
            "current": current_val,
            "threshold": threshold,
            "gap": round(gap, 2),
            "weekly_change_rate": round(weekly_change, 3),
            "weeks_to_threshold": round(weeks_to_threshold, 1) if weeks_to_threshold != 999 else "方向偏离",
            "closest_historical_cycle": closest_cycle,
        }
    
    return results
