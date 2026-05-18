# Gemini任务描述：山西焦煤周期分析系统

## 你的角色
你是一个量化投资分析工程师，需要帮我构建一套钢铁/焦煤周期跟踪系统。
运行环境：Windows本地，conda `bot`环境，路径 `D:\code\bean\coal\`。

---

## 任务目标

每周运行一次，自动拉取数据，结合历史周期做**真正的分析**，输出一份有判断、有依据、有行动建议的markdown报告。

**不是数据看板。是分析报告。**

区别：
- ❌ 看板："螺纹钢3104，阈值3500，未达"
- ✅ 分析："螺纹钢现价3104，处于2016年以来历史25%分位。上一次从这个价格区间反转是2016年Q1，当时铁水产量从228万吨回升到248万吨用了11周。当前铁水234万吨，距离反转阈值250万吨还差16万吨，按近6周变化速度（+0.3万吨/周）推算，最快需要53周，除非出现政策冲击或安监事件。"

---

## 项目结构

```
D:\code\bean\coal\
├── data\
│   ├── mysteel_weekly.csv       # 手动录入，钢联周度数据
│   ├── futures\                 # tushare自动拉取，JM/RB期货
│   ├── spot\                    # akshare自动拉取，现货价格
│   └── macro\                   # akshare自动拉取，PMI/产量
├── src\
│   ├── fetch_data.py            # 数据获取模块
│   ├── cycle_score.py           # 周期评分
│   ├── reversal_signals.py      # 三层信号检测
│   ├── historical_compare.py    # 历史周期对比（核心）
│   ├── generate_report.py       # 调用Claude API生成分析文字
│   └── main.py                  # 主入口，每周运行
├── reports\                     # 输出的markdown报告
├── config.py                    # token、路径配置
└── requirements.txt
```

---

## 数据获取规格

### A. tushare自动获取（需要tushare token）

```python
# 1. JM焦煤期货连续合约
ts.pro_api().fut_daily(ts_code='JM0.DCE', start_date='20150101')
# 字段：trade_date, close, volume, oi（持仓量）

# 2. RB螺纹钢期货连续合约  
ts.pro_api().fut_daily(ts_code='RB0.SHF', start_date='20150101')

# 3. 山西焦煤个股日线（sz000983）
ts.pro_api().daily(ts_code='000983.SZ', start_date='20150101')
# 字段：trade_date, close, ma55（需自己计算）

# 4. 动力煤期货（ZC）做对比用，证明焦煤跟钢铁不跟动力煤
ts.pro_api().fut_daily(ts_code='ZC0.CZCE', start_date='20150101')
```

### B. akshare自动获取

```python
import akshare as ak

# 1. 螺纹钢现货价（上海）
ak.futures_spot_price_daily(symbol="螺纹钢")

# 2. 制造业PMI
ak.macro_china_pmi_yearly()

# 3. 粗钢月度产量（国家统计局）
ak.macro_china_steel_production()

# 4. 房地产新开工面积（同比）
ak.macro_china_real_estate()
```

### C. 手动录入CSV（mysteel_weekly.csv）

每周一手动填写以下字段，这是最核心的数据，没有替代方案：

```csv
date,hot_metal_daily,bf_utilization,mill_profit_pct,rebar_inventory,coking_utilization,coke_profit_per_ton,auction_fail_rate,coking_coal_stock_days,coke_raise_count,coke_cut_count,spot_jiaotan_lowsulfur
2026-03-06,234.0,71.6,20.0,650,71.6,-34,32.0,12.5,2,5,1650
```

字段说明：
- `hot_metal_daily`：日均铁水产量（万吨）
- `bf_utilization`：高炉开工率（%）
- `mill_profit_pct`：钢厂盈利比例（%）
- `rebar_inventory`：全国螺纹钢库存（万吨）
- `coking_utilization`：独立焦化厂开工率（%）
- `coke_profit_per_ton`：吨焦利润（元），负数正常
- `auction_fail_rate`：焦煤流拍率（%）
- `coking_coal_stock_days`：焦化厂焦煤库存天数
- `coke_raise_count`：本周焦炭提涨次数
- `coke_cut_count`：本周焦炭提降次数
- `spot_jiaotan_lowsulfur`：山西低硫主焦现货价（元/吨）

---

## 周期评分模块（cycle_score.py）

### 评分逻辑

```python
def calculate_cycle_score(mysteel_row, futures_df):
    """
    输入：最新一行mysteel数据 + 期货历史DataFrame
    输出：0-100的周期分数
    0=历史底部，100=历史顶部
    """
    
    def normalize(value, low, high, inverse=False):
        score = max(0, min(100, (value - low) / (high - low) * 100))
        return 100 - score if inverse else score
    
    # 各维度计算
    scores = {}
    
    # 1. 价格维度（权重30%）
    # 用JM期货过去5年数据计算历史分位
    jm_5yr = futures_df['JM']['close'].tail(252*5)
    jm_percentile = (futures_df['JM']['close'].iloc[-1] > jm_5yr).mean() * 100
    rb_5yr = futures_df['RB']['close'].tail(252*5)
    rb_percentile = (futures_df['RB']['close'].iloc[-1] > rb_5yr).mean() * 100
    scores['price'] = (jm_percentile + rb_percentile) / 2
    
    # 2. 开工率维度（权重30%）
    scores['utilization'] = normalize(mysteel_row['bf_utilization'], low=75, high=95)
    
    # 3. 盈利维度（权重25%）
    scores['profit'] = normalize(mysteel_row['mill_profit_pct'], low=20, high=80)
    
    # 4. 库存维度（权重15%，库存越低分越高）
    scores['inventory'] = normalize(mysteel_row['rebar_inventory'], low=300, high=800, inverse=True)
    
    total = (
        scores['price'] * 0.30 +
        scores['utilization'] * 0.30 +
        scores['profit'] * 0.25 +
        scores['inventory'] * 0.15
    )
    
    return total, scores

# 解读映射
CYCLE_INTERPRETATION = {
    (0, 25): ("周期底部", "可考虑分批布局"),
    (25, 50): ("复苏早期", "持有，等反转信号确认"),
    (50, 75): ("景气中期", "持有，准备止盈计划"),
    (75, 100): ("顶部区域", "逐步减仓"),
}
```

---

## 历史周期对比模块（historical_compare.py）—— 最重要

这是Gemini写的版本最缺的部分。需要实现以下功能：

### 1. 标记历史关键节点

```python
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
```

### 2. 当前位置与历史对比函数

```python
def compare_with_history(current_data, futures_df):
    """
    对每个关键指标，计算：
    1. 当前值处于哪个历史节点的区间内
    2. 距离反转阈值还差多少
    3. 按最近N周变化速度，推算最快何时能触发
    """
    results = {}
    
    for indicator in ['hot_metal_daily', 'bf_utilization', 'mill_profit_pct']:
        current_val = current_data[indicator]
        
        # 最近6周变化速度
        recent = mysteel_df[indicator].tail(6)
        weekly_change = (recent.iloc[-1] - recent.iloc[0]) / 6
        
        # 距离反转阈值
        threshold = REVERSAL_THRESHOLDS[indicator]
        gap = threshold - current_val
        
        # 推算时间（线性外推，仅供参考）
        if weekly_change > 0:
            weeks_to_threshold = gap / weekly_change
        else:
            weeks_to_threshold = float('inf')  # 方向错误，无法自然到达
        
        # 最相似的历史节点
        closest_cycle = find_closest_historical_cycle(current_val, indicator)
        
        results[indicator] = {
            "current": current_val,
            "threshold": threshold,
            "gap": gap,
            "weekly_change_rate": weekly_change,
            "weeks_to_threshold": weeks_to_threshold,
            "closest_historical_cycle": closest_cycle,
        }
    
    return results
```

---

## 报告生成模块（generate_report.py）

**这是关键**：不要用模板字符串拼报告，要调用Claude API让AI真正分析数据后生成文字。

```python
import anthropic
import json

def generate_analysis_report(cycle_score, signal_status, historical_compare, raw_data):
    """
    把所有量化数据打包，调用Claude API生成真正的分析文字
    """
    client = anthropic.Anthropic()  # 从环境变量读ANTHROPIC_API_KEY
    
    data_package = {
        "report_date": str(date.today()),
        "cycle_score": cycle_score,  # 0-100
        "signal_status": signal_status,  # 三层信号状态
        "current_indicators": raw_data,  # 当日所有指标原始值
        "historical_comparison": historical_compare,  # 历史对比结果
        "historical_cycles_reference": HISTORICAL_CYCLES,  # 历史节点定义
    }
    
    prompt = f"""
你是一个专注于中国黑色系商品的量化分析师，专门研究钢铁/焦煤投资周期。

以下是今日的量化数据包：
{json.dumps(data_package, ensure_ascii=False, indent=2)}

## 核心认知前提（必须遵守）
- 焦煤跟钢铁走，不跟动力煤。核心驱动是铁水日产量
- 焦煤反转永远滞后钢价1-2个季度，但涨幅是螺纹钢的2-3倍
- 中国钢铁需求已永久性结构转变：建筑占比从50%降至<35%，制造业接棒但填不满缺口
- 历史上供需反转只有两种路径：政策强制去产能（如2016年）或需求端超预期爆发

## 请生成一份分析报告，必须包含以下内容：

### 1. 周期位置判断（300字）
- 当前评分{cycle_score['total']:.1f}/100意味着什么
- 与2015年底部、2021年顶部的关键指标对比，说明现在离底部有多近/多远
- 哪个指标当前最接近历史底部，哪个还有下行空间

### 2. 反转路径推演（400字）
- 基于当前各指标的变化速度，推算自然复苏情景下何时能触发第一层信号
- 说明哪个指标是最大瓶颈（最慢到达阈值的那个）
- 什么样的外生冲击（政策/事故/进口减少）能加速这个过程，加速多少

### 3. 焦煤vs钢铁的传导时滞（200字）
- 如果钢铁指标先触发反转，焦煤会在多久之后跟上
- 历史上2016年这个时滞是多少周

### 4. 本周操作建议（150字）
- 山西焦煤个股：距55日线触发买点还有多远
- 需要重点关注的下周数据更新
- 有没有任何信号发生边际变化（哪怕还未触发）

## 写作要求
- 用数字说话，每个判断必须有对应数据支撑
- 不要用"可能"、"或许"这种模糊表述，用"按当前速度"、"历史对比"来表达不确定性
- 不要重复展示原始数据表格，直接进入分析
- 结尾给一句话结论：现在是"等待"、"准备"还是"行动"
"""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text
```

---

## 主入口（main.py）

```python
# main.py
import os
from datetime import date
from src.fetch_data import fetch_futures, fetch_macro
from src.cycle_score import calculate_cycle_score
from src.reversal_signals import check_all_layers
from src.historical_compare import compare_with_history
from src.generate_report import generate_analysis_report
import pandas as pd

def run_weekly_analysis():
    print(f"=== 焦煤周期分析 {date.today()} ===")
    
    # 1. 加载数据
    print("正在获取期货数据...")
    futures_df = fetch_futures()  # tushare
    
    print("正在获取宏观数据...")
    macro_df = fetch_macro()  # akshare
    
    print("读取钢联手动数据...")
    mysteel_df = pd.read_csv('data/mysteel_weekly.csv', parse_dates=['date'])
    latest_mysteel = mysteel_df.sort_values('date').iloc[-1]
    
    # 2. 计算周期评分
    cycle_score, score_breakdown = calculate_cycle_score(latest_mysteel, futures_df)
    
    # 3. 检测三层信号
    signal_status = check_all_layers(mysteel_df, futures_df)
    
    # 4. 历史对比
    historical_compare = compare_with_history(latest_mysteel, mysteel_df, futures_df)
    
    # 5. 调用Claude生成分析报告
    print("正在生成分析报告...")
    raw_data = {
        "cycle_score": {"total": cycle_score, "breakdown": score_breakdown},
        "mysteel": latest_mysteel.to_dict(),
        "jm_close": futures_df['JM']['close'].iloc[-1],
        "rb_close": futures_df['RB']['close'].iloc[-1],
    }
    
    report_text = generate_analysis_report(
        cycle_score=raw_data['cycle_score'],
        signal_status=signal_status,
        historical_compare=historical_compare,
        raw_data=raw_data
    )
    
    # 6. 保存报告
    report_date = date.today().strftime('%Y%m%d')
    report_path = f'reports/coking_coal_report_{report_date}.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 山西焦煤周期分析报告 {date.today()}\n\n")
        f.write(f"**周期评分：{cycle_score:.1f}/100**\n\n")
        f.write("---\n\n")
        f.write(report_text)
    
    print(f"报告已生成：{report_path}")

if __name__ == "__main__":
    run_weekly_analysis()
```

---

## config.py

```python
# config.py
import os

TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN', '你的token')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '你的key')

# 数据路径
DATA_DIR = r'D:\code\bean\coal\data'
REPORT_DIR = r'D:\code\bean\coal\reports'

# 反转阈值（第一层先行信号）
REVERSAL_THRESHOLDS = {
    'hot_metal_daily': 250,        # 万吨/天
    'bf_utilization': 90,          # %
    'mill_profit_pct': 50,         # %
    'rebar_price': 3500,           # 元/吨
    'coking_utilization': 80,      # %
}

# 止损线
STOP_LOSS = {
    'rebar_price_exit': 3000,      # 螺纹钢跌破此价格退出等待
    'stock_loss_pct': -15,         # 个股止损比例
}
```

---

## requirements.txt

```
tushare>=1.2.89
akshare>=1.12.0
anthropic>=0.25.0
pandas>=2.0.0
numpy>=1.24.0
```

---

## 给Gemini的执行指令

请按照以上规格，帮我完整实现这个项目的所有Python文件。具体要求：

1. **fetch_data.py**：实现tushare和akshare的数据获取，处理好异常和缺失值，数据存到`data/`子目录

2. **cycle_score.py**：完整实现评分逻辑，历史分位用实际期货数据计算，不要hardcode

3. **reversal_signals.py**：三层信号检测，第一层需要判断"连续N周"的时序条件

4. **historical_compare.py**：实现当前指标与三个历史节点的对比，输出每个指标距离阈值的距离和按当前速度到达的预估周数

5. **generate_report.py**：调用Claude API，prompt按照上面写的结构，不要简化

6. **main.py**：串联所有模块，最终输出一个可读的markdown文件到`reports/`目录

运行方式：`conda activate bot && python D:\code\bean\coal\src\main.py`

所有代码加中文注释，变量名用英文。
```