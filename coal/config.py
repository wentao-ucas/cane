# config.py
import os

# API Keys
TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN', '你的token')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '你的key')

# 数据路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')

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

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
