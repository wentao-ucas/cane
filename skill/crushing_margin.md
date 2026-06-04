# 压榨利润分析方法

> Crushing Margin Analysis Method

---

## 核心概念

**压榨利润 (Crushing Margin)** 是指油厂将大豆压榨成豆油和豆粕后的利润空间，是判断油厂开工意愿和豆粕供应的关键指标。

---

## 计算公式

### 基础公式

```
压榨利润 = 产出收入 - 原料成本 - 加工成本

其中：
产出收入 = 豆粕价格 × 出粕率 + 豆油价格 × 出油率
原料成本 = 大豆成本（进口或国产）
加工成本 = 加工费 + 其他费用
```

### 英文表达

```
Crushing Margin = Output Revenue - Raw Material Cost - Processing Cost

Where:
Output Revenue = Meal Price × Meal Yield + Oil Price × Oil Yield
Raw Material = Soybean Cost (Imported or Domestic)
Processing = Crushing Fee + Other Costs
```

---

## 参数详解

### 1. 出粕率 / 出油率 (Extraction Rate)

| 参数 | 典型值 | 范围 | 英文 |
|------|--------|------|------|
| 出粕率 | 78.5% | 77%-80% | Meal Yield / Extraction Rate |
| 出油率 | 18.5% | 17%-19% | Oil Yield / Extraction Rate |
| 损耗率 | 3% | 2%-4% | Loss Rate |

> 注：出粕率+出油率+损耗率 ≈ 100%

### 2. 加工费 (Crushing Fee)

- **范围**：100-150 元/吨
- **英文**：Processing Cost / Crushing Fee
- **包含**：电力、人工、设备折旧、管理费用等

### 3. 价格数据

| 数据 | 单位 | 来源 |
|------|------|------|
| 豆粕现货价 | 元/吨 | 我的农产品网、天下粮仓 |
| 豆油现货价 | 元/吨 | 我的农产品网、天下粮仓 |
| 进口大豆成本 | 元/吨 | 按进口成本公式计算 |

---

## 计算示例

### 示例：2026年1月压榨利润

**输入参数**：
- 豆粕现货价：2850 元/吨
- 豆油现货价：7800 元/吨
- 进口大豆成本：4272 元/吨
- 出粕率：78.5%
- 出油率：18.5%
- 加工费：120 元/吨

**计算过程**：
```python
# 产出收入
meal_revenue = 2850 * 0.785  # = 2237.25 元
oil_revenue = 7800 * 0.185   # = 1443.00 元
total_revenue = 2237.25 + 1443.00  # = 3680.25 元

# 压榨利润
crushing_margin = 3680.25 - 4272 - 120  # = -711.75 元/吨
```

**结果**：压榨利润约 **-712 元/吨**（亏损）

---

## 利润状态解读

### 利润区间与油厂行为

| 利润区间 | 状态 | 油厂行为 | 对豆粕影响 |
|----------|------|----------|------------|
| > 200元/吨 | 高利润 (High Margin) | 满负荷开工 | 供应充足，价格承压 |
| 0-200元/吨 | 微利 (Marginal) | 正常开工 | 供需平衡 |
| -200-0元/吨 | 微亏 (Slight Loss) | 维持开工 | 可能挺价 |
| < -200元/吨 | 深亏 (Deep Loss) | 降低开工率 | 供应收紧，支撑价格 |

### 开工率参考

| 开工率 | 状态 | 说明 |
|--------|------|------|
| > 55% | 高开工 | 利润较好或有长期订单 |
| 45%-55% | 正常 | 常规运营水平 |
| < 45% | 低开工 | 利润差或检修季节 |

---

## Python 计算函数

```python
def calc_crushing_margin(
    meal_price: float,       # 豆粕价格，元/吨
    oil_price: float,        # 豆油价格，元/吨
    soybean_cost: float,     # 大豆成本，元/吨
    meal_yield: float = 0.785,  # 出粕率
    oil_yield: float = 0.185,   # 出油率
    crushing_fee: float = 120   # 加工费，元/吨
) -> dict:
    """
    计算压榨利润
    
    Returns:
        dict: {
            'meal_revenue': 豆粕收入,
            'oil_revenue': 豆油收入,
            'total_revenue': 总收入,
            'total_cost': 总成本,
            'margin': 压榨利润,
            'margin_pct': 利润率%
        }
    """
    meal_revenue = meal_price * meal_yield
    oil_revenue = oil_price * oil_yield
    total_revenue = meal_revenue + oil_revenue
    total_cost = soybean_cost + crushing_fee
    margin = total_revenue - total_cost
    margin_pct = (margin / total_cost) * 100 if total_cost > 0 else 0
    
    return {
        'meal_revenue': round(meal_revenue, 2),
        'oil_revenue': round(oil_revenue, 2),
        'total_revenue': round(total_revenue, 2),
        'total_cost': round(total_cost, 2),
        'margin': round(margin, 2),
        'margin_pct': round(margin_pct, 2)
    }
```

---

## 影响因素分析

### 利润的主要驱动因素

```
压榨利润
├── 收入端
│   ├── 豆粕价格 ← 养殖需求（猪周期）
│   └── 豆油价格 ← 食用需求 + 生物柴油需求
│
└── 成本端
    ├── CBOT大豆价格 ← 美国/巴西产量
    ├── CNF升贴水 ← 运费 + 基差
    ├── 汇率 ← 宏观经济
    └── 关税 ← 贸易政策
```

### 敏感性分析

以基准参数为例，各因素变动1%的影响：

| 因素 | 变动 | 利润变化 | 敏感度 |
|------|------|----------|--------|
| 豆粕价格 | +1% (+28.5元) | +22.4元 | 高 |
| 豆油价格 | +1% (+78元) | +14.4元 | 中 |
| 大豆成本 | +1% (+42.7元) | -42.7元 | 最高 |

---

## 压榨利润与投资策略

### 信号判断

| 压榨利润 | 开工率 | 库存 | 豆粕价格展望 |
|----------|--------|------|--------------|
| 亏损 | 下降 | 下降 | 看涨 ↑ |
| 亏损 | 维持 | 稳定 | 中性 → |
| 盈利 | 上升 | 上升 | 看跌 ↓ |
| 高利润 | 高位 | 高位 | 看跌 ↓↓ |

### 实战应用

1. **压榨亏损 + 库存低位** → 可能是买入豆粕ETF的机会
2. **压榨高利润 + 库存高位** → 谨慎持有，考虑减仓
3. **关注油粕比**：油强粕弱时，油厂挺粕意愿更强

---

## 数据获取渠道

| 数据 | 来源 | 更新频率 |
|------|------|----------|
| 豆粕现货价 | 我的农产品网、天下粮仓 | 每日 |
| 豆油现货价 | 我的农产品网、天下粮仓 | 每日 |
| 压榨利润（计算值） | 我的农产品网 | 每日 |
| 油厂开工率 | 我的农产品网、天下粮仓 | 每周 |
| 油厂豆粕库存 | 我的农产品网 | 每周 |

---

## 注意事项

1. **区域差异**：华东、华南、华北油厂成本略有不同
2. **船期影响**：进口成本要考虑到港时间，有1-2个月滞后
3. **套保因素**：大型油厂有套保，实际利润可能与计算值不同
4. **产能利用**：还需关注检修计划、环保限产等因素
5. **期现价差**：期货利润和现货利润可能背离
