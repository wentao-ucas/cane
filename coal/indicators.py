def normalize(val, low, high, inverse=False):
    """
    将指标标准化为 0-100 的分数
    """
    if val is None:
        return 0
        
    if inverse:
        # 逆向指标：值越低，分数越高 (例如库存)
        if val <= low:
            return 100
        elif val >= high:
            return 0
        else:
            return 100 - ((val - low) / (high - low) * 100)
    else:
        # 正向指标：值越高，分数越高 (例如开工率，利润比例)
        if val <= low:
            return 0
        elif val >= high:
            return 100
        else:
            return ((val - low) / (high - low) * 100)

def price_score(rebar_ratio, jm_ratio):
    """
    价格维度的评分: 当前价格/五年均价 的比例
    越低代表越超跌，分数越高
    """
    if rebar_ratio is None or jm_ratio is None:
        return 0
        
    # 假设跌倒5年均价的70%是极度低估(100分)，回到100%是正常(0分)
    rebar_score = normalize(rebar_ratio, low=0.7, high=1.0, inverse=True)
    jm_score = normalize(jm_ratio, low=0.7, high=1.0, inverse=True)
    
    return (rebar_score + jm_score) / 2

def calculate_cycle_score(data):
    """
    计算周期位置评分 (0=底部，100=顶部)
    返回0-100的分数
    """
    score = 0
    
    # 1. 价格维度（权重30%）
    rebar_vs_5yr = data.get('rb_spot_price', 0) / data.get('rb_5yr_avg', 1) if data.get('rb_5yr_avg') else None
    jm_vs_5yr = data.get('jm_spot_price', 0) / data.get('jm_5yr_avg', 1) if data.get('jm_5yr_avg') else None
    price_s = price_score(rebar_vs_5yr, jm_vs_5yr)
    score += price_s * 0.3
    
    # 2. 开工率维度（权重30%）
    # 高炉开工率 normalize: 75% -> 0分, 95% -> 100分
    util_s = normalize(data.get('bf_utilization'), low=75, high=95)
    score += util_s * 0.3
    
    # 3. 盈利维度（权重25%）
    # 钢厂盈利比例 normalize: 20% -> 0分, 80% -> 100分
    profit_s = normalize(data.get('mill_profit_ratio'), low=20, high=80)
    score += profit_s * 0.25
    
    # 4. 库存维度（权重15%）
    # 螺纹钢库存 normalize: 300 -> 100分, 800 -> 0分 (逆向)
    inv_s = normalize(data.get('rb_inventory'), low=300, high=800, inverse=True)
    score += inv_s * 0.15
    
    return round(score, 2)

def check_reversal_signals(data):
    """
    检测反转信号分层情况
    """
    signals = {
        'layer1': {
            'rebar_above_3500': data.get('rb_spot_price', 0) > 3500,
            'bf_utilization_90': data.get('bf_utilization', 0) > 90,
            'hot_metal_250': data.get('hot_metal_output', 0) > 250,
            'coking_utilization_80': data.get('coking_utilization', 0) > 80,
            'mill_profit_50': data.get('mill_profit_ratio', 0) > 50,
        },
        'layer2': {
            'coke_raise_dominant': data.get('coke_raise_count', 0) > data.get('coke_reduce_count', 0),
            'auction_fail_low': data.get('auction_fail_rate', 100) < 10,
            'coking_coal_stock_low': data.get('coking_coal_inventory_days', 100) < 10,
            # 现货连续三周上涨 这里简化为单周趋势预留，需要历史数据才能完全判断连续3周
            'spot_above_1600': data.get('jm_spot_price', 0) > 1600, 
        },
        'layer3': {
            'jm_spot_above_1800': data.get('jm_spot_price', 0) > 1800,
            'jm_futures_above_1400': data.get('jm_futures_price', 0) > 1400,
        }
    }
    
    layer1_count = sum(signals['layer1'].values())
    layer2_count = sum(signals['layer2'].values())
    layer3_count = sum(signals['layer3'].values())
    
    status = {
        'layer1_triggered': layer1_count >= 3,
        'layer2_triggered': layer2_count >= 2,
        'layer3_triggered': layer3_count >= 2,
        'details': signals
    }
    
    return status

def analyze(data):
    """综合分析入口"""
    cycle_score = calculate_cycle_score(data)
    signals = check_reversal_signals(data)
    
    # 状态判定
    if cycle_score < 25:
        cycle_status = "📉 周期底部区域 - 可考虑逢低布局"
    elif cycle_score < 50:
        cycle_status = "🌱 复苏早期 - 持有为主"
    elif cycle_score < 75:
        cycle_status = "📈 景气中期 - 持有并准备止盈"
    else:
        cycle_status = "⚠️ 顶部区域 - 建议逐步减仓"
        
    return {
        "cycle_score": cycle_score,
        "cycle_status": cycle_status,
        "signals": signals
    }
