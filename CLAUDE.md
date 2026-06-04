# CLAUDE.md — 项目上下文（Claude Code 自动加载）

> 这是一个大宗商品周期研究项目。本文件让任何机器上的 Claude Code clone 仓库后即可无缝接续。
> 中文为主，发布文章受众是中国散户。仓库名 `cane`(README) / `bean`(agent.md)。

---

## 0. 新电脑上手（空白机器零配置）

```bash
git clone https://github.com/wentao-ucas/cane.git
cd cane
pip install akshare pandas matplotlib yfinance requests numpy pypdf
```

- **本 CLAUDE.md 会被 Claude Code 自动加载** → 新电脑的 Claude 读完即可恢复全部项目上下文
- **项目记忆**：见 `memory/` 目录（auto-memory 的副本，因为 Claude 的本机记忆不随 git 走）。如果新电脑路径也是 `D:\code\bean`，可把 `memory/*.md` 拷到 `~/.claude/projects/D--code-bean/memory/` 让其自动加载；否则直接读 `memory/` 即可
- **数据更新**：`python scripts/fetch_akshare_data.py` → `python scripts/plot_all_charts.py`
- **代理注意**：国内代理(127.0.0.1)会拦东财 push2his，海外数据(yfinance: ZC=F/SB=F等)走 yfinance 别用 akshare 东财

---

## 1. 铁律（OVERRIDE 一切默认行为）

1. **严禁编造数据**（见 `agent.md`）：所有数字必须有 CSV/XML 文件或官方链接支撑；估算必须标注"（估算）"。违规示例：随口报"压榨利润-332元"。正确：引用 `data/USDA.xml` 或标注估算。
2. **破坏性操作先确认**（见 `AGENTS.md`）：`rm`/`git reset --hard`/`git clean`/`git checkout --`/覆盖文件 等，必须先 dry-run 预览，等用户回 `确认删除` 才执行。
3. **投资相关内容**：所有结论标注"不构成投资建议"，给条件概率而非"必然"，用触发条件清单代替拍板。

---

## 2. 四条研究线（按完成度）

| 品种 | 状态 | 核心产出 |
|---|---|---|
| 🍬 **白糖 SR0 + ICE 11** | ✅ 完整 | `output/sugar_conclusions.md`、244月复盘`sugar_monthly_full_review.md`、ENSO滞后、`sugar_monthly_heatmap.png` |
| ⚫ **焦煤** | 跟踪中 | `coal/` 子模块 + `output/coal_2026_analysis.md` |
| 🌱 **豆粕 ETF** | 系列文章2篇 | `articles/01`(已发)、`articles/02`(进行中)，数据 akshare+USDA |
| 🌽 **玉米 C0 + CBOT** | ✅ 最新主线 | 见下方第3节，这是最近最活跃的工作 |

---

## 3. 玉米研究现状（最近主线，重点接续）

### 已完成的量化研究
- `output/corn_conclusions.md` — 21年结论：内外盘相关仅0.30(高度独立)、ENSO同期La Niña利多/El Niño利空(与糖相反)、季节性9-10月做多最优(9月底胜率86%)、5年政策周期
- `output/corn_monthly_full_review.md` — 262月新闻复盘(WebSearch验证)
- `output/corn_monthly_heatmap.png` — 年×月热力图

### 套利研究
- `output/corn_arbitrage_signals.md` — 跨期(calendar)+蝴蝶(butterfly)，当前全中性无信号
- `output/cross_commodity_arb_signals.md` — C-CS玉米淀粉(产业链)、Y-P豆油棕榈(2024起结构反转)

### ⭐ 做多投资逻辑（当前讨论焦点）
- `output/corn_long_thesis.md` — **完整做多投研文档**，整合：
  - 雪球@治雨《十年周期复盘与2026展望》核心观点(6000万吨缺口/保税玉米粉/库存见底，原文 `玉米.pdf`)
  - 量化对照(印证国内独立性、ENSO方向存疑)
  - 2020逼空合约级复盘(近月短命+15%/1月合约+38%)
  - 交割规则(散户8月底前必平9月合约)、陈粮逼仓压制远月验证
  - 交易结构：6-8月C2609陈粮逼仓 → 9月看新粮验证 → C2701秋冬接力
  - 情景概率 A20-25%/B50%/C25-30%，胜负手在9月新粮

### 玉米关键事实（已用数据验证）
- 挂牌月份：1/3/5/7/9/11(六个奇数月)；**主力月只有 1、5、9**(占主力天数83%)，3/7/11是换月过渡棒
- 散户不能进交割：9月合约(C2609)必须8月底前平仓
- 当前(2026-05)：C0约2300-2360，远期曲线V型(C2611新粮深贴)，做多赔率约3:1但需等9月验证

### 玉米脚本（可重跑）
`corn_monthly.py` `cbot_corn_monthly.py` `merge_c_cbot.py` `corn_heatmap.py` `oni_corn_analysis.py` `oni_corn_lag.py` `corn_by_month.py` `merge_corn_news.py` `corn_contracts.py` `corn_calendar_spread.py` `corn_butterfly.py` `corn_arbitrage_plot.py` `corn_starch_arb.py` `oil_palm_arb.py` `corn_long_entry_backtest.py` `corn_entry_month.py`

---

## 4. 方法论（所有品种共用）

`methodology/agricultural_commodity_framework.md` — **五层叠加框架**：
> 季节性供应窗口(短期) + ENSO气候因子(中期6-12月) + 种植周期(长期3-7年) + 国内政策(独立扰动) + 全球过剩/短缺(基本面定调)

各品种 ENSO 方向不同：糖/棕榈/可可 El Niño利多；**大豆/玉米 La Niña利多**。
玉米特殊：一年生作物，ENSO **同期**就定价(滞后失灵)，与糖(甘蔗多年生需6-12月传导)相反。

---

## 5. 数据源映射

| 品种 | 国内主连(akshare) | 海外(yfinance) | 基本面 |
|---|---|---|---|
| 白糖 | SR0 | SB=F | NOAA ONI、广西甘蔗面积 |
| 玉米 | C0 | ZC=F | USDA、临储/进口政策、生猪存栏 |
| 豆粕 | M0 | ZM=F | USDA、南美天气 |
| 玉米淀粉 | CS0 | — | 加工利润 |
| 豆油/棕榈 | Y0/P0 | — | 印尼B40、MPOB |

- ONI：`https://psl.noaa.gov/data/correlation/oni.data`（已存 `data/oni_monthly.csv`）
- 合约日线：`ak.futures_zh_daily_sina(symbol="C2609")`
- Windows编码：脚本开头加 `sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')`
- 中文matplotlib：`mpl.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei']`

---

## 6. 仓库地图

```
cane/
├── CLAUDE.md            # 本文件(自动加载)
├── AGENTS.md            # 安全规则(破坏性操作确认)
├── agent.md             # 豆粕项目文档 + 数据真实性铁律 + 公式
├── README.md            # 项目总览
├── CHANGELOG.md         # 研究时间线
├── memory/              # 项目记忆(auto-memory副本)
├── methodology/         # 五层框架方法论
├── scripts/             # 所有分析脚本
├── data/                # CSV/XML 数据
├── output/              # 报告.md + 图.png
├── coal/                # 焦煤子模块
├── articles/            # 豆粕系列文章
├── skill/               # 豆粕方法论(进口成本/压榨/猪周期/USDA)
└── 玉米.pdf             # 治雨原文
```

---

## 7. 用户偏好（验证过的写作风格）

- 表格对比 > 文字描述
- Top N 极端样本举例 > 平均值
- "实操含义"段 > "理论分析"段
- 条件概率(A 20%/B 50%/C 30%) > "很可能/不太可能"
- 列触发条件清单让用户自己跟踪，不直接说"必然反转"
- 用户是做期货/量化的，可以直接、有观点、用"bro"语气

---

## 8. 已知的待清理项（动前问用户）

- 仓库根有 6 个 `(2)` 后缀副本(早期 Windows 复制粘贴产物，内容多与原文件重复)
- 4 个 stale 豆粕文件(`soybean_meal_contango.csv`等被回退成旧数据，git HEAD 里是好版本)
- 这些**不要主动删**，按 AGENTS.md 先问
