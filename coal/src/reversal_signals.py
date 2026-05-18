# src/reversal_signals.py
import pandas as pd

def check_all_layers(mysteel_df, futures_df):
    """
    检查反转信号的三层状态，支持时序条件(如连续N周)
    """
    latest = mysteel_df.iloc[-1]
    
    signals = {
        'layer1': {},
        'layer2': {},
        'layer3': {}
    }
    
    # === Layer 1: 先行信号 (需满足3个以上) ===
    # 连续4周均价 > 3500 (结合期货和现货粗略算)
    # 取近20个交易日均价是否大于3500作为"连续4周"的代理指标
    if 'RB' in futures_df and not futures_df['RB'].empty:
        recent_rb = futures_df['RB'].tail(20)
        rebar_above_3500 = (recent_rb['close'] > 3500).all() if len(recent_rb) == 20 else False
    else:
        rebar_above_3500 = False
        
    signals['layer1']['rebar_above_3500'] = bool(rebar_above_3500)
    signals['layer1']['bf_utilization_90'] = bool(latest['bf_utilization'] > 90)
    signals['layer1']['hot_metal_250'] = bool(latest['hot_metal_daily'] > 250)
    signals['layer1']['coking_utilization_80'] = bool(latest['coking_utilization'] > 80)
    signals['layer1']['mill_profit_50'] = bool(latest['mill_profit_pct'] > 50)
    
    # === Layer 2: 同步信号 (需满足2个以上) ===
    signals['layer2']['coke_raise_dominant'] = bool(latest['coke_raise_count'] > latest['coke_cut_count'])
    
    # 连续3周流拍率 < 10%
    if len(mysteel_df) >= 3:
        recent_auction = mysteel_df['auction_fail_rate'].tail(3)
        signals['layer2']['auction_fail_low'] = bool((recent_auction < 10).all())
    else:
        signals['layer2']['auction_fail_low'] = bool(latest['auction_fail_rate'] < 10)
        
    signals['layer2']['coking_coal_stock_low'] = bool(latest['coking_coal_stock_days'] < 10)
    
    # 现货连续3周上涨 (mysteel spot_jiaotan_lowsulfur)
    if len(mysteel_df) >= 4:
        # 判断最后三周是否都比前一周高
        recent_spot = mysteel_df['spot_jiaotan_lowsulfur'].tail(4).values
        spot_rising = (recent_spot[1] > recent_spot[0]) and (recent_spot[2] > recent_spot[1]) and (recent_spot[3] > recent_spot[2])
        signals['layer2']['spot_rising'] = bool(spot_rising)
    else:
        signals['layer2']['spot_rising'] = False

    # === Layer 3: 最终确认 (需满足2个以上) ===
    signals['layer3']['jm_spot_above_1800'] = bool(latest['spot_jiaotan_lowsulfur'] > 1800)
    if 'JM' in futures_df and not futures_df['JM'].empty:
        signals['layer3']['jm_futures_above_1400'] = bool(futures_df['JM']['close'].iloc[-1] > 1400)
    else:
        signals['layer3']['jm_futures_above_1400'] = False

    # 全行业吨焦利润转正且持续4周
    if len(mysteel_df) >= 4:
        recent_coke_profit = mysteel_df['coke_profit_per_ton'].tail(4)
        signals['layer3']['coke_profit_positive'] = bool((recent_coke_profit > 0).all())
    else:
        signals['layer3']['coke_profit_positive'] = bool(latest['coke_profit_per_ton'] > 0)
        
    # 计算触发数量
    l1_count = sum(signals['layer1'].values())
    l2_count = sum(signals['layer2'].values())
    l3_count = sum(signals['layer3'].values())
    
    status = {
        'layer1_triggered': l1_count >= 3,
        'layer2_triggered': l2_count >= 2,
        'layer3_triggered': l3_count >= 2,
        'details': signals,
        'counts': {'layer1': l1_count, 'layer2': l2_count, 'layer3': l3_count}
    }
    
    return status
