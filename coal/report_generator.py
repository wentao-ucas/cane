import os
import datetime

def generate_markdown_report(data, analysis_result, output_dir="output"):
    """
    根据最新数据生成投资决策简报
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(output_dir, f"coking_coal_weekly_report_{date_str}.md")
    
    cycle_score = analysis_result['cycle_score']
    cycle_status = analysis_result['cycle_status']
    signals = analysis_result['signals']
    
    def render_layer(layer_name, signals_dict, thresholds):
        lines = []
        for key, expected in thresholds.items():
            status_icon = "✅ 满足" if signals_dict.get(key, False) else "❌ 未达"
            lines.append(f"| {expected} | {status_icon} |")
        return "\n".join(lines)
        
    l1_thresholds = {
        'rebar_above_3500': '螺纹钢均价 > 3500 (且连续4周)',
        'bf_utilization_90': '高炉开工率 > 90%',
        'hot_metal_250': '日均铁水产量 > 250万吨',
        'coking_utilization_80': '独立焦化厂开工率 > 80%',
        'mill_profit_50': '钢厂盈利比例 > 50%',
    }
    
    l2_thresholds = {
        'coke_raise_dominant': '焦炭提涨次数 > 提降次数',
        'auction_fail_low': '焦煤流拍率 < 10%',
        'coking_coal_stock_low': '焦化厂焦煤库存天数 < 10天',
        'spot_above_1600': '焦煤现货价格启动上涨',
    }

    l3_thresholds = {
        'jm_spot_above_1800': '主焦现货价 > 1800',
        'jm_futures_above_1400': 'JM主力合约 > 1400',
    }

    markdown = f"""# 山西焦煤量化跟踪简报 ({date_str})

## 🎯 核心结论

**当前周期评分：{cycle_score}/100**  
**当前状态：{cycle_status}**

---

## 📊 一、基础数据快照

### 1.1 价格与估值指标
| 指标 | 最新值 | 五年均价 | 当前位置 |
|------|--------|----------|----------|
| 焦煤连续(JM0) | ¥{data.get('jm_futures_price', 'N/A')} | ¥{data.get('jm_5yr_avg', 'N/A'):.2f} | {data.get('jm_futures_price', 0)/data.get('jm_5yr_avg', 1)*100 if data.get('jm_5yr_avg') else 0:.1f}% 分位 |
| 螺纹连续(RB0) | ¥{data.get('rb_futures_price', 'N/A')} | ¥{data.get('rb_5yr_avg', 'N/A'):.2f} | {data.get('rb_futures_price', 0)/data.get('rb_5yr_avg', 1)*100 if data.get('rb_5yr_avg') else 0:.1f}% 分位 |
| 山西低硫主焦现货 | ¥{data.get('jm_spot_price', 'N/A')} | - | - |
| 螺纹钢现货均价 | ¥{data.get('rb_spot_price', 'N/A')} | - | - |

### 1.2 供需基本面 (主要来自钢联数据 {data.get('mysteel_date', '未知日期')})
| 核心观察指标 | 当前值 | 满分阈值(100分) | 冰点阈值(0分) |
|--------------|--------|-----------------|---------------|
| 日均铁水产量 | {data.get('hot_metal_output', 'N/A')}万吨 | > 250万吨 | < 220万吨 |
| 高炉开工率   | {data.get('bf_utilization', 'N/A')}% | > 90% | < 75% |
| 钢厂盈利比例 | {data.get('mill_profit_ratio', 'N/A')}% | > 80% | < 20% |
| 螺纹钢库存   | {data.get('rb_inventory', 'N/A')}万吨 | < 300万吨 | > 800万吨 |
| 独立焦化厂开工率 | {data.get('coking_utilization', 'N/A')}% | > 80% | < 65% |
| 焦煤流拍率 | {data.get('auction_fail_rate', 'N/A')}% | < 10% | > 40% |
| 焦化厂焦煤库存天数 | {data.get('coking_coal_inventory_days', 'N/A')}天 | < 10天 | > 15天 |

---

## 🛡️ 二、反转信号系统状态

### 🟢 第一层：先行信号 (提前3-6个月)
*触发条件：需同时满足3个以上*  
**当前状态：{'已触发 ⚠️' if signals['layer1_triggered'] else '未触发 ⏳'}**

| 监测点 | 状态 |
|--------|------|
{render_layer('layer1', signals['details']['layer1'], l1_thresholds)}

### 🟡 第二层：同步确认信号 (反转时同步出现)
*触发条件：需同时满足2个以上*  
**当前状态：{'已触发 ⚠️' if signals['layer2_triggered'] else '未触发 ⏳'}**

| 监测点 | 状态 |
|--------|------|
{render_layer('layer2', signals['details']['layer2'], l2_thresholds)}

### 🔴 第三层：最终确认 (反转后1-2季度)
*触发条件：需满足2个以上*  
**当前状态：{'已触发 ⚠️' if signals['layer3_triggered'] else '未触发 ⏳'}**

| 监测点 | 状态 |
|--------|------|
{render_layer('layer3', signals['details']['layer3'], l3_thresholds)}

---
*注：本报告由代码自动生成，宏观数据和期货数据拉取自 Akshare，行业核心基本面数据来自本地 mysteel_data.csv 文件*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
        
    print(f"✅ 报告已生成至: {report_path}")
    return report_path
