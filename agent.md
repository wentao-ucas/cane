# 豆粕ETF研究项目 - Agent 工作文档

> 本文档记录项目背景、数据来源、工作流程和注意事项

---

## ⚠️ 重要原则

### 🚫 数据准确性要求

**绝对禁止编造任何数据！** 所有数据必须有明确来源：

1. **有数据文件支撑**：如 `data/USDA.xml`、`data/*.csv`
2. **有官方来源链接**：如 USDA、农业农村部官网
3. **明确标注估算**：如果是估算数据，必须注明"（估算）"或"（示例数据）"

**违规示例**：
- ❌ "当前压榨利润：-332元/吨" —— 未提供数据来源
- ❌ "CBOT价格：980美分/蒲" —— 未验证的当前价格
- ❌ "能繁母猪：3938万头" —— 未提供官方数据链接

**正确做法**：
- ✅ "根据USDA WASDE-667报告，美国产量为115.99百万公吨"
- ✅ "（以下为示例数据，实际请查询实时行情）"
- ✅ 提供数据来源文件路径或官方链接

### 📊 CSV数据文件说明

本项目使用 **akshare** 库自动获取真实市场数据。

**真实数据（通过akshare获取）**：
- `pig_cycle.csv` - 生猪价格+猪粮比（数据源：akshare → 东方财富/猪网）
- `crushing_margin.csv` - 豆粕+玉米价格（数据源：akshare → 猪网）
- `inventory.csv` - 豆粕期货库存（数据源：akshare → 东方财富）
- `soybean_meal_futures.csv` - 豆粕期货历史价格（数据源：akshare → 新浪财经）

**静态数据**：
- `USDA.xml` - USDA WASDE-667报告原始数据 ✅

**数据更新命令**：
```bash
python scripts/fetch_akshare_data.py  # 获取最新数据
python scripts/plot_all_charts.py     # 重新生成图表
```

详细说明见 `data/README.md`

---

## 项目概述

**目标**：撰写系列文章，帮助普通投资者理解豆粕ETF投资

**系列文章规划**：
1. ✅ 《一文读懂豆粕ETF：从入门到看懂价格逻辑》 - 已完成
2. 🚧 《豆粕供需分析：从数据到投资决策》 - 进行中
3. 📋 （待定）实战篇/案例篇

---

## 数据来源清单

### 供给端数据

| 数据项 | 中文名 | 英文名 | 来源 | 官方链接 | 更新频率 |
|--------|--------|--------|------|----------|----------|
| CBOT大豆 | 芝加哥大豆期货 | CBOT Soybean Futures (ZS) | CME Group | cmegroup.com | 实时 |
| 美国供需 | USDA月度报告 | WASDE | USDA | usda.gov/oce/commodity/wasde | 每月 |
| 美国供需(中文) | WASDE中文翻译 | - | 天下粮仓/中华粮网 | cofeed.com / cngrain.com | 每月 |
| 巴西产量 | 巴西大豆产量 | Brazil Soybean Production | CONAB | conab.gov.br/info-agro/safras | 每月 |
| 阿根廷产量 | 阿根廷大豆产量 | Argentina Soybean Production | Bolsa de Rosario | bcr.com.ar | 每月 |
| PSD数据库 | 历史供需数据 | Production, Supply & Distribution | USDA FAS | apps.fas.usda.gov/psdonline | 随时查询 |
| 海运费 | 巴西-中国运费 | Brazil-China Panamax Freight | Platts / Baltic | - | 每日 |
| 汇率 | 美元人民币 | USD/CNY Exchange Rate | 中国人民银行 | chinamoney.com.cn | 每日 |
| 港口库存 | 港口大豆库存 | Port Soybean Inventory | 我的农产品网 | myagric.com.cn | 每周 |
| 油厂库存 | 油厂豆粕库存 | Crushing Plant Meal Inventory | 我的农产品网 | myagric.com.cn | 每周 |
| 压榨利润 | 大豆压榨利润 | Soybean Crushing Margin | 天下粮仓 | cofeed.com | 每日 |
| 开工率 | 油厂开工率 | Crushing Capacity Utilization | 我的农产品网 | myagric.com.cn | 每周 |

### 需求端数据

| 数据项 | 中文名 | 英文名 | 来源 | 官方链接 | 更新频率 |
|--------|--------|--------|------|----------|----------|
| 能繁母猪 | 能繁母猪存栏量 | Breeding Sow Inventory | 农业农村部 | moa.gov.cn | 每月 |
| 生猪存栏 | 生猪存栏量 | Hog Inventory | 农业农村部 | moa.gov.cn | 每月 |
| 生猪价格 | 生猪出栏价 | Hog Price | 涌益咨询 / 卓创资讯 | - | 每日 |
| 猪粮比 | 猪粮比价 | Hog-Corn Ratio | 发改委 | ndrc.gov.cn | 每周 |
| 蛋鸡存栏 | 蛋鸡存栏量 | Layer Inventory | 卓创资讯 | - | 每月 |
| 肉鸡存栏 | 肉鸡存栏量 | Broiler Inventory | 卓创资讯 | - | 每月 |

### 报告获取渠道汇总

**英文原版**：
- USDA WASDE: https://www.usda.gov/oce/commodity/wasde
- USDA油籽报告: https://www.fas.usda.gov/data/oilseeds-world-markets-and-trade
- PSD数据库: https://apps.fas.usda.gov/psdonline/app/index.html
- CFTC持仓: https://www.cftc.gov/MarketReports/CommitmentsofTraders/
- 巴西CONAB: https://www.conab.gov.br/info-agro/safras

**中文翻译/解读**：
- 天下粮仓: https://www.cofeed.com （USDA翻译最详细）
- 中华粮网: http://www.cngrain.com （翻译最快）
- 我的农产品网: https://www.myagric.com.cn （结合国内分析）
- 金十数据: https://www.jin10.com （实时快讯）

---

## 关键公式

### 进口大豆成本计算

```
进口成本(元/吨) = (CBOT价格 × 单位转换 + 升贴水) × 汇率 × (1 + 关税) × (1 + 增值税) + 港杂费

其中：
- CBOT价格：美分/蒲式耳
- 单位转换：1蒲式耳 ≈ 27.22公斤，即 ×0.367437 转为美元/吨
- 升贴水(Premium/Discount)：CNF基差，美元/吨
- 汇率：USD/CNY
- 关税：巴西3%，美国13%（2018年后）
- 增值税：9%
- 港杂费：约100-120元/吨
```

### 压榨利润计算

```
压榨利润(元/吨) = 豆粕价格 × 出粕率 + 豆油价格 × 出油率 - 大豆成本 - 加工费

其中：
- 出粕率：约78.5%
- 出油率：约18.5%
- 加工费：约100-120元/吨
```

### 猪周期时滞关系

```
能繁母猪存栏变化 → (4个月) → 仔猪出生 → (6个月) → 生猪出栏
                                        ↓
              豆粕需求变化 ← (约10个月滞后于能繁母猪变化)
```

---

## 文件结构

```
bean/
├── agent.md                    # 本文档
├── skill/                      # 技能/方法论文档
│   ├── import_cost.md          # 进口成本计算方法（含收获季节）
│   ├── crushing_margin.md      # 压榨利润分析
│   ├── pig_cycle.md            # 猪周期分析方法
│   ├── usda_reports.md         # USDA报告解读指南
│   └── usda_xml_structure.md   # ⭐USDA XML数据结构索引（新增）
├── articles/                   # 发布文章
│   ├── 01_soybean_meal_etf_intro.md
│   └── 02_soybean_meal_supply_demand.md
├── data/                       # 数据文件
│   ├── USDA.xml                # ⭐USDA WASDE-667原始数据（新增）
│   ├── soybean_meal_contango.csv
│   ├── cbot_soybean.csv
│   ├── import_cost.csv
│   ├── crushing_margin.csv
│   ├── pig_cycle.csv
│   └── inventory.csv
├── scripts/                    # 数据与可视化脚本
│   ├── fetch_akshare_data.py   # ⭐akshare数据获取（新增）
│   ├── plot_all_charts.py      # ⭐一键生成所有图表（新增）
│   ├── plot_contango.py
│   ├── plot_import_cost.py
│   └── get_soybean_meal.py
├── output/                     # 图表输出
│   ├── pig_cycle.png           # 猪周期图表
│   ├── crushing_margin.png     # 压榨利润图表
│   ├── inventory.png           # 库存图表
│   ├── futures_price.png       # 期货价格图表
│   └── supply_demand_summary.png # ⭐供需分析仪表盘
└── reference/                  # 参考资料
    └── table_formats.md
```

---

## 工作流程

### 数据更新流程

1. **每周更新**：库存数据、开工率
2. **每月更新**：USDA报告、能繁母猪存栏、CONAB报告
3. **文章发布前**：更新所有数据，重新生成图表

### 数据与图表更新命令

```powershell
# 🔄 一键更新所有数据（从akshare获取真实数据）
python scripts/fetch_akshare_data.py

# 📊 一键生成所有图表
python scripts/plot_all_charts.py

# 👆 上述两个命令即可完成全部更新

# 单独图表（可选）
python scripts/plot_contango.py       # 升贴水图表
python scripts/plot_import_cost.py    # 进口成本图表
```

### akshare 可用数据接口

| 数据类型 | akshare 函数 | 说明 |
|---------|-------------|------|
| 豆粕期货历史 | `futures_main_sina("M0")` | 主力合约日K线 |
| 豆粕期货库存 | `futures_inventory_em("豆粕")` | 交易所注册仓单 |
| 生猪价格 | `futures_hog_core("外三元")` | 全国均价 |
| 玉米价格 | `futures_hog_cost("玉米")` | 饲料原料价格 |
| 豆粕现货 | `futures_hog_cost("豆粕")` | 饲料原料价格 |
| 猪粮比 | `futures_hog_supply("猪粮比价")` | 历史序列 |
| 生猪指数 | `index_hog_spot_price()` | 市场综合指数 |

---

## 注意事项

1. **数据时效性**：文章中的数据需标注截止日期
2. **单位统一**：价格统一用元/吨，存栏用万头
3. **图表风格**：保持一致的配色方案（绿色=有利，红色=不利）
4. **免责声明**：所有文章结尾需加免责声明
5. **中英双语**：关键术语需标注英文名称

---

## 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-01-28 | 完成第一篇文章 |
| 2026-01-29 | 开始第二篇文章，创建项目文档 |
| 2026-01-29 | 🎉 引入 akshare 自动获取真实数据，重构数据获取流程 |
