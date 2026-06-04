# 数据来源说明 / Data Source Documentation

> 📊 **本项目使用 akshare 自动获取真实市场数据**

## 数据获取方式

使用 [akshare](https://akshare.akfamily.xyz/) 库自动从多个数据源获取真实数据：

```bash
# 更新所有数据
python scripts/fetch_akshare_data.py

# 重新生成图表
python scripts/plot_all_charts.py
```

---

## 数据文件说明

### ✅ 真实数据 (Real Data from akshare)

| 数据文件 | 内容 | akshare 函数 | 原始数据源 |
|---------|------|-------------|-----------|
| `pig_cycle.csv` | 生猪价格、猪粮比 | `futures_hog_core()`, `futures_hog_supply()` | 东方财富/猪网 |
| `crushing_margin.csv` | 豆粕价格、玉米价格、压榨利润 | `futures_hog_cost()` | 猪网 |
| `inventory.csv` | 豆粕期货库存 | `futures_inventory_em()` | 东方财富 |
| `soybean_meal_futures.csv` | 豆粕期货历史价格 | `futures_main_sina()` | 新浪财经 |

### 📄 静态数据

| 数据文件 | 来源 | 说明 |
|---------|------|------|
| `USDA.xml` | USDA WASDE-667 | 美国农业部月度供需报告原始XML |

---

## akshare 可用数据接口

### 豆粕相关

```python
import akshare as ak

# 豆粕期货主力合约历史数据
df = ak.futures_main_sina(symbol="M0")

# 豆粕期货库存（东方财富）
df = ak.futures_inventory_em(symbol="豆粕")

# 豆粕现货价格
df = ak.futures_hog_cost(symbol="豆粕")
```

### 生猪相关

```python
# 生猪价格 - 外三元/内三元/土杂猪
df = ak.futures_hog_core(symbol="外三元")

# 猪粮比价
df = ak.futures_hog_supply(symbol="猪粮比价")

# 生猪市场价格指数
df = ak.index_hog_spot_price()
```

### 饲料原料

```python
# 玉米价格
df = ak.futures_hog_cost(symbol="玉米")

# 豆粕价格
df = ak.futures_hog_cost(symbol="豆粕")
```

---

## 最新数据快照

> 数据更新时间: 2026-01-29

### 期货价格
| 品种 | 价格 | 单位 | 来源 |
|-----|------|-----|------|
| 豆粕主力(M0) | 2782 | 元/吨 | 新浪财经 |

### 现货价格
| 品种 | 价格 | 单位 | 来源 |
|-----|------|-----|------|
| 豆粕现货 | 2996 | 元/吨 | 猪网 |
| 玉米 | 2339 | 元/吨 | 猪网 |
| 外三元生猪 | 12.73 | 元/公斤 | 猪网 |

### 库存与指标
| 指标 | 数值 | 单位 | 来源 |
|-----|------|-----|------|
| 豆粕期货库存 | 33,428 | 吨 | 东方财富 |
| 猪粮比 | 5.40 | :1 | 猪网 |

---

## 其他数据查询渠道

### 免费数据源
- **USDA报告**: https://usda.gov/oce/commodity/wasde
- **CME Group**: https://cmegroup.com (CBOT价格)
- **中国养猪网**: https://zhuwang.com.cn (生猪/饲料价格)

### 付费数据源（更完整）
- Wind金融终端
- Bloomberg Terminal
- 卓创资讯
- 涌益咨询
- 天下粮仓 (cofeed.com)

---

## 数据更新频率

| 数据类型 | 更新频率 | 操作 |
|---------|---------|------|
| 期货价格 | 每日 | `python scripts/fetch_akshare_data.py` |
| 库存数据 | 每周 | 同上 |
| USDA报告 | 每月 | 手动下载更新 `data/USDA.xml` |

---

*最后更新: 2026-01-29*
