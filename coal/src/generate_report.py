# src/generate_report.py
import json
import os
import sys
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.historical_compare import HISTORICAL_CYCLES

def generate_analysis_report(cycle_score, signal_status, historical_compare, raw_data):
    """
    因为不需要外部 LLM API，所以这里改为把所有量化数据按照格式输出为一个 Prompt 模板
    然后由当前的 AI 助手在聊天中或者运行时读取并生成真正的分析文字。
    这里会返回一个带清晰指令的 Markdown 文本片段用于让 AI 接管，不再发起网络请求。
    """
    
    data_package = {
        "report_date": str(date.today()),
        "cycle_score": cycle_score,  # 0-100
        "signal_status": signal_status,  # 三层信号状态
        "current_indicators": raw_data,  # 当日所有指标原始值
        "historical_comparison": historical_compare,  # 历史对比结果
        "historical_cycles_reference": HISTORICAL_CYCLES,  # 历史节点定义
    }
    
    prompt = f"""
## 给 AI 分析助手的分析指令数据包

以下是今日的量化数据包，请根据这些数据进行深度分析并输出最终的焦煤市场周报段落：
```json
{json.dumps(data_package, ensure_ascii=False, indent=2, default=str)}
```

### 【你的任务：基于上述数据，按照以下四个要求写出最终的报告正文】

#### 1. 周期位置判断（约300字）
- 根据当前评分（例如 {cycle_score['total']:.1f}/100）说明现在属于周期的什么位置。
- 与2015年底部、2021年顶部的关键指标对比，说明现在离历史极端底部有多近或多远。
- 哪个指标当前最接近历史底部，哪个还有下行空间。

#### 2. 反转路径推演（约400字）
- 基于当前各指标的变化速度(weekly_change_rate)和距离阈值的差距(gap)，直接推算自然复苏情景下，最快几周(weeks_to_threshold)能触发第一层信号。
- 明确指出哪个指标是反转的最大瓶颈（即所需时间最长的那个）。
- 结合你的知识，推演什么样的外生冲击（例如政策、矿难事故、进口减少）能加速这个过程及可能的影响程度。

#### 3. 焦煤vs钢铁的传导时滞（约200字）
- 解释：如果钢铁指标先触发反转，焦煤会在多久之后跟上（回顾2016年底部的时滞经验值）。

#### 4. 本周操作建议（约150字）
- 回顾当前操作策略。山西焦煤个股的买入线参考（当前个股与55日线的对比如果数据允许的情况下）。
- 需要重点关注的下周数据更新点。
- 指出是否有任何信号发生边际变化（例如虽然未触发，但方向已经在好转）。

### 写作要求
- 用**实实在在的数字说话**，不要空谈，每个判断必须引用数据包中的数据计算。
- 不要用"可能"、"或许"这种模糊表述，用"按当前速度"、"历史对比"来表达不确定性。
- **不要回复"好的"或"收到"**，直接开始输出上面1到4点的报告正文部分。
- 结尾给一句话明确结论：现在的应对策略是"等待"、"准备"还是"行动"。
"""
    return prompt
