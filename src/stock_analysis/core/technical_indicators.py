# -*- coding: utf-8 -*-
"""
技术指标计算模块
包含所有技术指标的计算函数
"""
import logging
from typing import Tuple, Optional, List

import pandas as pd
import numpy as np

from stock_analysis.constants import (
    MIN_DATA_DAYS,
    MIN_DAYS_FOR_KDJ,
    MIN_DAYS_FOR_MACD,
    MIN_DAYS_FOR_BBI,
    MIN_DAYS_FOR_ZHIXING_MULTI,
    KDJ_N, KDJ_M1, KDJ_M2,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    RSI_PERIOD,
    BOLL_PERIOD, BOLL_STD_DEV,
    BBI_PERIODS,
    ZHIXING_TREND_PERIOD,
    ZHIXING_MULTI_PERIODS,
    MA_PERIODS,
    EMA_PERIODS,
    EPSILON,
)

logger = logging.getLogger(__name__)


# ============ 基础指标 ============

def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """
    计算简单移动平均线 (SMA)
    
    Args:
        data: 价格序列
        window: 窗口大小
        
    Returns:
        SMA 序列
    """
    return data.rolling(window=window).mean()


def calculate_ema(data: pd.Series, window: int) -> pd.Series:
    """
    计算指数移动平均线 (EMA)
    
    Args:
        data: 价格序列
        window: 窗口大小
        
    Returns:
        EMA 序列
    """
    return data.ewm(span=window, adjust=False).mean()


# ============ KDJ 指标 ============

def calculate_kdj(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    n: int = KDJ_N,
    m1: int = KDJ_M1,
    m2: int = KDJ_M2
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算 KDJ 指标
    
    Args:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        n: RSV 周期 (默认 9)
        m1: K 值平滑周期 (默认 3)
        m2: D 值平滑周期 (默认 3)
        
    Returns:
        (K, D, J) 三个序列的元组
    """
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    
    rsv = (close - lowest_low) / (highest_high - lowest_low + EPSILON) * 100
    
    k = rsv.ewm(alpha=1/m1, adjust=False).mean()
    d = k.ewm(alpha=1/m2, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return k, d, j


# ============ MACD 指标 ============

def calculate_macd(
    close: pd.Series,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算 MACD 指标
    
    Args:
        close: 收盘价序列
        fast: 快线周期 (默认 12)
        slow: 慢线周期 (默认 26)
        signal: 信号线周期 (默认 9)
        
    Returns:
        (MACD 线, 信号线, 柱状图) 三个序列的元组
    """
    ema_fast = calculate_ema(close, fast)
    ema_slow = calculate_ema(close, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = (macd_line - signal_line) * 2  # 柱状图乘以 2
    
    return macd_line, signal_line, histogram


# ============ RSI 指标 ============

def calculate_rsi(close: pd.Series, window: int = RSI_PERIOD) -> pd.Series:
    """
    计算 RSI 相对强弱指标
    
    Args:
        close: 收盘价序列
        window: 计算周期 (默认 14)
        
    Returns:
        RSI 序列
    """
    delta = close.diff()
    
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / (loss + EPSILON)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


# ============ BBI 指标 ============

def calculate_bbi(close: pd.Series, periods: List[int] = None) -> pd.Series:
    """
    计算 BBI 多空指标 (Bull and Bear Index)
    
    BBI = (MA3 + MA6 + MA12 + MA24) / 4
    
    Args:
        close: 收盘价序列
        periods: 周期列表 (默认 [3, 6, 12, 24])
        
    Returns:
        BBI 序列
    """
    if periods is None:
        periods = BBI_PERIODS
    
    ma_values = [calculate_sma(close, period) for period in periods]
    bbi = sum(ma_values) / len(ma_values)
    
    return bbi


# ============ 布林带 ============

def calculate_bollinger_bands(
    close: pd.Series,
    window: int = BOLL_PERIOD,
    num_std: float = BOLL_STD_DEV
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带
    
    Args:
        close: 收盘价序列
        window: 计算周期 (默认 20)
        num_std: 标准差倍数 (默认 2)
        
    Returns:
        (上轨, 中轨, 下轨) 三个序列的元组
    """
    sma = calculate_sma(close, window)
    std = close.rolling(window=window).std()
    
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    
    return upper_band, sma, lower_band


# ============ 知行指标 ============

def calculate_zhixing_trend_line(close: pd.Series) -> pd.Series:
    """
    计算知行短期趋势线
    
    公式: EMA(EMA(C, 10), 10)
    
    Args:
        close: 收盘价序列
        
    Returns:
        趋势线序列
    """
    try:
        ema1 = close.ewm(span=ZHIXING_TREND_PERIOD, adjust=False).mean()
        ema2 = ema1.ewm(span=ZHIXING_TREND_PERIOD, adjust=False).mean()
        return ema2
    except Exception as e:
        logger.error(f"计算知行趋势线失败: {e}")
        return pd.Series(index=close.index, dtype=float)


def calculate_zhixing_multi_line(
    close: pd.Series,
    m1: int = None,
    m2: int = None,
    m3: int = None,
    m4: int = None
) -> pd.Series:
    """
    计算知行多空线
    
    公式: (MA(CLOSE, M1) + MA(CLOSE, M2) + MA(CLOSE, M3) + MA(CLOSE, M4)) / 4
    
    Args:
        close: 收盘价序列
        m1, m2, m3, m4: 周期参数 (默认 14, 28, 57, 114)
        
    Returns:
        多空线序列
    """
    if m1 is None:
        m1, m2, m3, m4 = ZHIXING_MULTI_PERIODS
    
    try:
        ma1 = close.rolling(window=m1).mean()
        ma2 = close.rolling(window=m2).mean()
        ma3 = close.rolling(window=m3).mean()
        ma4 = close.rolling(window=m4).mean()
        
        return (ma1 + ma2 + ma3 + ma4) / 4
    except Exception as e:
        logger.error(f"计算知行多空线失败: {e}")
        return pd.Series(index=close.index, dtype=float)


# ============ 振荡器 ============

def calculate_oscillator(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    period: int = RSI_PERIOD
) -> pd.Series:
    """
    计算振荡器指标（范围 -50 到 150）
    
    基于 RSI 和成交量的复合指标
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        volume: 成交量序列
        period: 计算周期
        
    Returns:
        振荡器序列
    """
    try:
        # 计算 RSI
        rsi = calculate_rsi(close, period)
        
        # 映射到 -50 ~ 150 范围
        oscillator = (rsi / 100) * 200 - 50
        
        # 成交量增强因子
        volume_ma = volume.rolling(window=period).mean()
        volume_ratio = volume / (volume_ma + EPSILON)
        volume_factor = 0.8 + 0.2 * volume_ratio.clip(0.5, 2.0)
        
        oscillator = oscillator * volume_factor
        
        return oscillator.clip(-50, 150)
    except Exception as e:
        logger.error(f"计算振荡器失败: {e}")
        return pd.Series(index=close.index, dtype=float)


# ============ 综合计算 ============

def calculate_all_indicators(data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    计算所有技术指标并添加到 DataFrame
    
    Args:
        data: 包含 date, open, high, low, close, volume 的 DataFrame
        
    Returns:
        添加了所有指标列的 DataFrame，数据不足返回 None
    """
    if data is None or len(data) < MIN_DATA_DAYS // 4:  # 至少需要 5 天数据
        logger.warning("数据不足，无法计算技术指标")
        return None
    
    data = data.copy()
    
    # KDJ (需要至少 9 天数据)
    if len(data) >= MIN_DAYS_FOR_KDJ:
        k, d, j = calculate_kdj(data["high"], data["low"], data["close"])
        data["kdj_k"] = k
        data["kdj_d"] = d
        data["kdj_j"] = j
    
    # MACD (需要至少 26 天数据)
    if len(data) >= MIN_DAYS_FOR_MACD:
        macd, signal, hist = calculate_macd(data["close"])
        data["macd"] = macd
        data["macd_signal"] = signal
        data["macd_hist"] = hist
    
    # BBI (需要至少 24 天数据)
    if len(data) >= MIN_DAYS_FOR_BBI:
        data["bbi"] = calculate_bbi(data["close"])
    
    # 知行指标
    data["zhixing_trend"] = calculate_zhixing_trend_line(data["close"])
    
    # 知行多空线 (需要至少 114 天数据)
    if len(data) >= MIN_DAYS_FOR_ZHIXING_MULTI:
        data["zhixing_multi"] = calculate_zhixing_multi_line(data["close"])
    
    # 移动平均线
    for name, period in MA_PERIODS.items():
        if len(data) >= period:
            data[name.lower()] = calculate_sma(data["close"], period)
    
    # EMA
    for name, period in EMA_PERIODS.items():
        if len(data) >= period:
            data[name.lower()] = calculate_ema(data["close"], period)
    
    # RSI (需要至少 14 天数据)
    if len(data) >= RSI_PERIOD:
        data["rsi"] = calculate_rsi(data["close"], RSI_PERIOD)
    
    # ====== 买卖信号计算 ======
    _calculate_signals(data)
    
    return data


def _calculate_signals(data: pd.DataFrame) -> None:
    """
    计算买卖信号（原地修改 DataFrame）
    
    Args:
        data: 包含技术指标的 DataFrame
    """
    # KDJ 金叉死叉
    if "kdj_k" in data.columns and "kdj_d" in data.columns:
        kdj_diff = data["kdj_k"] - data["kdj_d"]
        data["signal_buy_kdj"] = (kdj_diff > 0) & (kdj_diff.shift(1) <= 0)
        data["signal_sell_kdj"] = (kdj_diff < 0) & (kdj_diff.shift(1) >= 0)
    
    # MACD 金叉死叉
    if "macd" in data.columns and "macd_signal" in data.columns:
        macd_diff = data["macd"] - data["macd_signal"]
        data["signal_buy_macd"] = (macd_diff > 0) & (macd_diff.shift(1) <= 0)
        data["signal_sell_macd"] = (macd_diff < 0) & (macd_diff.shift(1) >= 0)
    
    # 价格突破知行趋势线
    if "zhixing_trend" in data.columns:
        price_vs_trend = data["close"] - data["zhixing_trend"]
        data["signal_buy_trend"] = (price_vs_trend > 0) & (price_vs_trend.shift(1) <= 0)
        data["signal_sell_trend"] = (price_vs_trend < 0) & (price_vs_trend.shift(1) >= 0)
    
    # 综合买卖信号 (任一指标触发即标记)
    data["signal_buy"] = False
    data["signal_sell"] = False
    
    for signal_col in ["signal_buy_kdj", "signal_buy_macd", "signal_buy_trend"]:
        if signal_col in data.columns:
            data["signal_buy"] |= data[signal_col]
    
    for signal_col in ["signal_sell_kdj", "signal_sell_macd", "signal_sell_trend"]:
        if signal_col in data.columns:
            data["signal_sell"] |= data[signal_col]


def calculate_basic_technical_indicators(
    current_price: float,
    historical_data: List[float] = None
) -> dict:
    """
    为单个股票计算基本技术指标
    
    Args:
        current_price: 当前价格
        historical_data: 历史价格数据列表
        
    Returns:
        包含基本技术指标的字典
    """
    indicators = {
        "current_price": current_price,
        "MA5": None,
        "MA10": None,
        "MA20": None,
        "RSI": None,
        "MACD": None,
        "signal": "neutral",  # neutral, buy, sell
    }
    
    if not historical_data or len(historical_data) < MIN_DATA_DAYS:
        return indicators
    
    prices = pd.Series(historical_data)
    
    # 计算移动平均线
    if len(historical_data) >= MA_PERIODS["MA5"]:
        indicators["MA5"] = float(prices.tail(MA_PERIODS["MA5"]).mean())
    
    if len(historical_data) >= MA_PERIODS["MA10"]:
        indicators["MA10"] = float(prices.tail(MA_PERIODS["MA10"]).mean())
    
    if len(historical_data) >= MA_PERIODS["MA20"]:
        indicators["MA20"] = float(prices.tail(MA_PERIODS["MA20"]).mean())
    
    # 计算 RSI
    if len(historical_data) >= RSI_PERIOD:
        rsi_series = calculate_rsi(prices, RSI_PERIOD)
        last_rsi = rsi_series.iloc[-1]
        if not pd.isna(last_rsi):
            indicators["RSI"] = float(last_rsi)
    
    return indicators
