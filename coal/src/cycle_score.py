# src/cycle_score.py
import pandas as pd

CYCLE_INTERPRETATION = {
    (0, 25): ("周期底部", "可考虑分批布局"),
    (25, 50): ("复苏早期", "持有，等反转信号确认"),
    (50, 75): ("景气中期", "持有，准备止盈计划"),
    (75, 100): ("顶部区域", "逐步减仓"),
}

def normalize(value, low, high, inverse=False):
    """
    通用归一化函数，约束到0-100范围内
    """
    # 约束在low和high之间
    clamped_value = max(low, min(high, value))
    score = (clamped_value - low) / (high - low) * 100
    
    if inverse:
        return 100 - score
    return score

def calculate_cycle_score(mysteel_row, futures_df):
    """
    输入：最新一行mysteel数据 + 期货历史DataFrame字典
    输出：0-100的周期分数, 及分数明细
    0=历史底部，100=历史顶部
    """
    scores = {}
    
    # 1. 价格维度（权重30%）
    # 用JM期货过去5年数据计算历史分位 (1年按252个交易日估算)
    if 'JM' in futures_df and not futures_df['JM'].empty:
        jm_5yr = futures_df['JM']['close'].tail(252*5)
        current_jm = futures_df['JM']['close'].iloc[-1]
        jm_percentile = (current_jm > jm_5yr).mean() * 100
    else:
        jm_percentile = 50.0  # fallback
        
    if 'RB' in futures_df and not futures_df['RB'].empty:
        rb_5yr = futures_df['RB']['close'].tail(252*5)
        current_rb = futures_df['RB']['close'].iloc[-1]
        rb_percentile = (current_rb > rb_5yr).mean() * 100
    else:
        rb_percentile = 50.0  # fallback

    scores['price'] = (jm_percentile + rb_percentile) / 2
    
    # 2. 开工率维度（权重30%）
    scores['utilization'] = normalize(mysteel_row['bf_utilization'], low=75, high=95)
    
    # 3. 盈利维度（权重25%）
    scores['profit'] = normalize(mysteel_row['mill_profit_pct'], low=20, high=80)
    
    # 4. 库存维度（权重15%，库存越低分越高，此处按逆向指标处理）
    scores['inventory'] = normalize(mysteel_row['rebar_inventory'], low=300, high=800, inverse=True)
    
    total = (
        scores['price'] * 0.30 +
        scores['utilization'] * 0.30 +
        scores['profit'] * 0.25 +
        scores['inventory'] * 0.15
    )
    
    return total, scores

def interpret_score(score):
    """
    将分数匹配为状态文本
    """
    for (low, high), label in CYCLE_INTERPRETATION.items():
        if low <= score <= high:
            return label
    return CYCLE_INTERPRETATION[(75, 100)]
