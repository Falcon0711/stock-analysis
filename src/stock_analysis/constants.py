# -*- coding: utf-8 -*-
"""
常量定义模块
集中管理所有魔法数字和配置常量
"""

# ============ 数据获取相关 ============
# 最小数据天数要求
MIN_DATA_DAYS = 20

# 默认历史数据天数
DEFAULT_HISTORY_DAYS = 30

# 技术指标计算所需的最小天数
MIN_DAYS_FOR_KDJ = 9
MIN_DAYS_FOR_MACD = 26
MIN_DAYS_FOR_BBI = 24
MIN_DAYS_FOR_ZHIXING_MULTI = 114

# 移动平均线周期
MA_PERIODS = {
    "MA5": 5,
    "MA10": 10,
    "MA20": 20,
    "MA30": 30,
    "MA60": 60,
}

# EMA周期
EMA_PERIODS = {
    "EMA13": 13,
}

# ============ 技术指标参数 ============
# KDJ 参数
KDJ_N = 9      # RSV周期
KDJ_M1 = 3     # K值平滑周期
KDJ_M2 = 3     # D值平滑周期

# MACD 参数
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# RSI 参数
RSI_PERIOD = 14

# 布林带参数
BOLL_PERIOD = 20
BOLL_STD_DEV = 2.0

# BBI 参数
BBI_PERIODS = [3, 6, 12, 24]

# 知行指标参数
ZHIXING_TREND_PERIOD = 10
ZHIXING_MULTI_PERIODS = (14, 28, 57, 114)

# ============ 交易信号阈值 ============
# 涨跌幅阈值
CHANGE_PCT_HIGH = 5.0    # 大涨/大跌阈值
CHANGE_PCT_MEDIUM = 3.0  # 中等涨跌阈值
CHANGE_PCT_LOW = 2.0     # 小涨跌阈值

# 乖离率阈值
BIAS_THRESHOLD = 5.0     # 乖离率超过此值不追高

# 情绪评分阈值
SENTIMENT_BULLISH = 0.7
SENTIMENT_NEUTRAL = 0.4

# ============ API 配置 ============
# 请求超时 (秒)
REQUEST_TIMEOUT = 10
AI_REQUEST_TIMEOUT = 60

# 重试次数
MAX_RETRIES = 3

# 请求延迟 (秒)
DEFAULT_REQUEST_DELAY = 30

# ============ 股票代码验证 ============
# 有效的股票代码前缀
VALID_SH_PREFIXES = ("5", "6", "9")          # 上海
VALID_SZ_PREFIXES = ("0", "1", "2", "3")     # 深圳
VALID_BJ_PREFIXES = ("4", "8")               # 北京
VALID_INDEX_CODES = {
    "000001": "sh",  # 上证指数
    "000300": "sh",  # 沪深300
    "399001": "sz",  # 深证成指
    "399006": "sz",  # 创业板指
    "399005": "sz",  # 中小板指
    "399300": "sz",  # 沪深300(深交所)
}

# ============ 日志配置 ============
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件大小限制 (bytes)
LOG_MAX_BYTES = 10 * 1024 * 1024      # 10MB
DEBUG_LOG_MAX_BYTES = 50 * 1024 * 1024  # 50MB
LOG_BACKUP_COUNT = 5
DEBUG_LOG_BACKUP_COUNT = 3

# ============ 并发配置 ============
DEFAULT_MAX_WORKERS = 3
TASK_TIMEOUT = 30  # 单个任务超时 (秒)

# ============ 数值精度 ============
# 用于避免除零错误的小常数
EPSILON = 1e-10
