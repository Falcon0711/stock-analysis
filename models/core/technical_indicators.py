"""
技术指标计算模块
包含所有技术指标的计算函数
"""
import pandas as pd
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# 最小数据天数要求
MIN_DATA_DAYS = 20


def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """计算简单移动平均线 (SMA)"""
    return data.rolling(window=window).mean()


def calculate_ema(data: pd.Series, window: int) -> pd.Series:
    """计算指数移动平均线 (EMA)"""
    return data.ewm(span=window, adjust=False).mean()


def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 9, m1: int = 3, m2: int = 3) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算KDJ指标
    Args:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        n: RSV周期 (默认9)
        m1: K值平滑周期 (默认3)
        m2: D值平滑周期 (默认3)
    Returns:
        (K, D, J) 三个序列
    """
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low + 1e-10) * 100
    k = rsv.ewm(alpha=1/m1, adjust=False).mean()
    d = k.ewm(alpha=1/m2, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j


def calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算MACD指标
    Args:
        close: 收盘价序列
        fast: 快线周期 (默认12)
        slow: 慢线周期 (默认26)
        signal: 信号线周期 (默认9)
    Returns:
        (MACD线, 信号线, 柱状图)
    """
    ema_fast = calculate_ema(close, fast)
    ema_slow = calculate_ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = (macd_line - signal_line) * 2  # 柱状图乘以2
    return macd_line, signal_line, histogram


def calculate_bbi(close: pd.Series, periods: list = None) -> pd.Series:
    """
    计算BBI多空指标 (Bull and Bear Index)
    BBI = (MA3 + MA6 + MA12 + MA24) / 4
    """
    if periods is None:
        periods = [3, 6, 12, 24]
    ma_values = [calculate_sma(close, period) for period in periods]
    bbi = sum(ma_values) / len(ma_values)
    return bbi


def calculate_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """计算RSI相对强弱指标"""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))


def calculate_bollinger_bands(close: pd.Series, window: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带
    Returns:
        (上轨, 中轨, 下轨)
    """
    sma = calculate_sma(close, window)
    std = close.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, sma, lower_band


def calculate_zhixing_trend_line(close: pd.Series) -> pd.Series:
    """
    计算知行短期趋势线
    公式: EMA(EMA(C,10),10)
    """
    try:
        ema1 = close.ewm(span=10, adjust=False).mean()
        ema2 = ema1.ewm(span=10, adjust=False).mean()
        return ema2
    except Exception as e:
        logger.error(f"计算知行趋势线失败: {e}")
        return pd.Series(index=close.index)


def calculate_zhixing_multi_line(close: pd.Series, m1: int = 14, m2: int = 28, m3: int = 57, m4: int = 114) -> pd.Series:
    """
    计算知行多空线
    公式: (MA(CLOSE,M1)+MA(CLOSE,M2)+MA(CLOSE,M3)+MA(CLOSE,M4))/4
    默认参数: M1=14, M2=28, M3=57, M4=114
    """
    try:
        ma1 = close.rolling(window=m1).mean()
        ma2 = close.rolling(window=m2).mean()
        ma3 = close.rolling(window=m3).mean()
        ma4 = close.rolling(window=m4).mean()
        return (ma1 + ma2 + ma3 + ma4) / 4
    except Exception as e:
        logger.error(f"计算知行多空线失败: {e}")
        return pd.Series(index=close.index)


def calculate_oscillator(close: pd.Series, high: pd.Series, low: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
    """
    计算振荡器指标（范围-50到150）
    基于RSI和成交量的复合指标
    """
    try:
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        # 映射到 -50 ~ 150 范围
        oscillator = (rsi / 100) * 200 - 50
        
        # 成交量增强因子
        volume_ma = volume.rolling(window=period).mean()
        volume_ratio = volume / (volume_ma + 1e-10)
        volume_factor = 0.8 + 0.2 * volume_ratio.clip(0.5, 2.0)
        oscillator = oscillator * volume_factor
        
        return oscillator.clip(-50, 150)
    except Exception as e:
        logger.error(f"计算振荡器失败: {e}")
        return pd.Series(index=close.index)


def calculate_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    计算所有技术指标并添加到DataFrame
    Args:
        data: 包含 date, open, high, low, close, volume 的 DataFrame
    Returns:
        添加了所有指标列的 DataFrame
    """
    if data is None or len(data) < 5:  # 至少需要5天数据才能计算一些基本指标
        return None
    
    data = data.copy()
    
    # KDJ (需要至少9天数据)
    if len(data) >= 9:
        k, d, j = calculate_kdj(data['high'], data['low'], data['close'])
        data['kdj_k'] = k
        data['kdj_d'] = d
        data['kdj_j'] = j
    
    # MACD (需要至少26天数据)
    if len(data) >= 26:
        macd, signal, hist = calculate_macd(data['close'])
        data['macd'] = macd
        data['macd_signal'] = signal
        data['macd_hist'] = hist
    
    # BBI (需要至少24天数据)
    if len(data) >= 24:
        data['bbi'] = calculate_bbi(data['close'])
    
    # 知行指标
    data['zhixing_trend'] = calculate_zhixing_trend_line(data['close'])
    
    # 知行多空线 (需要至少114天数据)
    if len(data) >= 114:
        data['zhixing_multi'] = calculate_zhixing_multi_line(data['close'])
    
    # 均线
    if len(data) >= 5:
        data['ma5'] = calculate_sma(data['close'], 5)
    if len(data) >= 10:
        data['ma10'] = calculate_sma(data['close'], 10)
    if len(data) >= 20:
        data['ma20'] = calculate_sma(data['close'], 20)
    if len(data) >= 30:
        data['ma30'] = calculate_sma(data['close'], 30)
    if len(data) >= 60:
        data['ma60'] = calculate_sma(data['close'], 60)
    
    if len(data) >= 13:
        data['ema13'] = calculate_ema(data['close'], 13)
    
    # RSI指标 (需要至少14天数据)
    if len(data) >= 14:
        data['rsi'] = calculate_rsi(data['close'], 14)
    
    # BBI多空指标 (需要至少24天数据)
    if len(data) >= 24:
        data['bbi'] = calculate_bbi(data['close'])
    
    # ====== 买卖信号计算 ======
    # KDJ 金叉死叉 (需要KDJ数据)
    if 'kdj_k' in data.columns and 'kdj_d' in data.columns:
        kdj_diff = data['kdj_k'] - data['kdj_d']
        kdj_golden = (kdj_diff > 0) & (kdj_diff.shift(1) <= 0)  # K从下穿过D = 金叉
        kdj_death = (kdj_diff < 0) & (kdj_diff.shift(1) >= 0)   # K从上穿过D = 死叉
        data['signal_buy_kdj'] = kdj_golden
        data['signal_sell_kdj'] = kdj_death
    
    # MACD 金叉死叉 (需要MACD数据)
    if 'macd' in data.columns and 'macd_signal' in data.columns:
        macd_diff = data['macd'] - data['macd_signal']
        macd_golden = (macd_diff > 0) & (macd_diff.shift(1) <= 0)
        macd_death = (macd_diff < 0) & (macd_diff.shift(1) >= 0)
        data['signal_buy_macd'] = macd_golden
        data['signal_sell_macd'] = macd_death
    
    # 价格突破知行趋势线
    if 'zhixing_trend' in data.columns:
        price_vs_trend = data['close'] - data['zhixing_trend']
        trend_break_up = (price_vs_trend > 0) & (price_vs_trend.shift(1) <= 0)
        trend_break_down = (price_vs_trend < 0) & (price_vs_trend.shift(1) >= 0)
        data['signal_buy_trend'] = trend_break_up
        data['signal_sell_trend'] = trend_break_down
    
    # 综合买卖信号 (任一指标触发即标记)
    data['signal_buy'] = False
    data['signal_sell'] = False
    
    if 'signal_buy_kdj' in data.columns:
        data['signal_buy'] |= data['signal_buy_kdj']
        data['signal_sell'] |= data['signal_sell_kdj']
    if 'signal_buy_macd' in data.columns:
        data['signal_buy'] |= data['signal_buy_macd']
        data['signal_sell'] |= data['signal_sell_macd']
    if 'signal_buy_trend' in data.columns:
        data['signal_buy'] |= data['signal_buy_trend']
        data['signal_sell'] |= data['signal_sell_trend']
    
    return data


def calculate_basic_technical_indicators(current_price: float, historical_data: list = None) -> dict:
    """
    为单个股票计算基本技术指标
    Args:
        current_price: 当前价格
        historical_data: 历史价格数据列表
    Returns:
        包含基本技术指标的字典
    """
    indicators = {
        'current_price': current_price,
        'MA5': None,
        'MA10': None,
        'MA20': None,
        'RSI': None,
        'MACD': None,
        'signal': 'neutral'  # neutral, buy, sell
    }
    
    if historical_data and len(historical_data) >= 20:
        # 转换为pandas Series用于计算
        prices = pd.Series(historical_data)
        
        # 计算移动平均线
        if len(historical_data) >= 5:
            indicators['MA5'] = float(prices.tail(5).mean())
        if len(historical_data) >= 10:
            indicators['MA10'] = float(prices.tail(10).mean())
        if len(historical_data) >= 20:
            indicators['MA20'] = float(prices.tail(20).mean())
        
        # 计算RSI (如果数据足够)
        if len(historical_data) >= 14:
            rsi_series = calculate_rsi(prices, 14)
            indicators['RSI'] = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else None
    
    return indicators