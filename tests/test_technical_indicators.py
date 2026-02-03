# -*- coding: utf-8 -*-
"""
技术指标计算测试
"""
import pytest
import pandas as pd
import numpy as np

from stock_analysis.core.technical_indicators import (
    calculate_sma,
    calculate_ema,
    calculate_kdj,
    calculate_macd,
    calculate_rsi,
    calculate_bbi,
    calculate_bollinger_bands,
    calculate_all_indicators,
    calculate_basic_technical_indicators,
)


class TestMovingAverages:
    """移动平均线测试"""
    
    def test_calculate_sma_basic(self):
        """测试 SMA 基本计算"""
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        sma = calculate_sma(data, 5)
        
        # 前4个应该是 NaN（窗口不足）
        assert pd.isna(sma.iloc[0])
        assert pd.isna(sma.iloc[3])
        
        # 第5个开始有值
        assert sma.iloc[4] == 3.0  # (1+2+3+4+5)/5 = 3
        assert sma.iloc[9] == 8.0  # (6+7+8+9+10)/5 = 8
    
    def test_calculate_ema_basic(self):
        """测试 EMA 基本计算"""
        data = pd.Series([1, 2, 3, 4, 5])
        ema = calculate_ema(data, 3)
        
        # EMA 应该存在所有值
        assert not pd.isna(ema.iloc[-1])
        # EMA 应该接近但不等于 SMA
        sma = calculate_sma(data, 3)
        assert ema.iloc[-1] != sma.iloc[-1]


class TestKDJ:
    """KDJ 指标测试"""
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        np.random.seed(42)
        n = 30
        return {
            "high": pd.Series(np.random.uniform(10, 15, n)),
            "low": pd.Series(np.random.uniform(8, 10, n)),
            "close": pd.Series(np.random.uniform(9, 14, n)),
        }
    
    def test_calculate_kdj_returns_tuple(self, sample_data):
        """测试 KDJ 返回三个序列"""
        k, d, j = calculate_kdj(
            sample_data["high"],
            sample_data["low"],
            sample_data["close"],
        )
        
        assert isinstance(k, pd.Series)
        assert isinstance(d, pd.Series)
        assert isinstance(j, pd.Series)
        assert len(k) == len(sample_data["close"])
    
    def test_kdj_value_range(self, sample_data):
        """测试 KDJ 值范围"""
        k, d, j = calculate_kdj(
            sample_data["high"],
            sample_data["low"],
            sample_data["close"],
        )
        
        # K 和 D 应该在 0-100 之间（大致）
        # J 可能超出这个范围
        valid_k = k.dropna()
        valid_d = d.dropna()
        
        assert valid_k.min() >= 0
        assert valid_k.max() <= 100
        assert valid_d.min() >= 0
        assert valid_d.max() <= 100


class TestMACD:
    """MACD 指标测试"""
    
    @pytest.fixture
    def price_series(self):
        """创建价格序列"""
        np.random.seed(42)
        return pd.Series(np.random.uniform(10, 20, 50))
    
    def test_calculate_macd_returns_tuple(self, price_series):
        """测试 MACD 返回三个序列"""
        macd, signal, hist = calculate_macd(price_series)
        
        assert isinstance(macd, pd.Series)
        assert isinstance(signal, pd.Series)
        assert isinstance(hist, pd.Series)
        assert len(macd) == len(price_series)
    
    def test_macd_histogram_calculation(self, price_series):
        """测试 MACD 柱状图计算"""
        macd, signal, hist = calculate_macd(price_series)
        
        # 柱状图 = (MACD - Signal) * 2
        expected_hist = (macd - signal) * 2
        pd.testing.assert_series_equal(hist, expected_hist)


class TestRSI:
    """RSI 指标测试"""
    
    def test_calculate_rsi_basic(self):
        """测试 RSI 基本计算"""
        # 持续上涨的价格
        rising_prices = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                   21, 22, 23, 24, 25, 26, 27, 28, 29, 30])
        rsi = calculate_rsi(rising_prices, 14)
        
        # 持续上涨应该接近 100
        assert rsi.iloc[-1] > 90
    
    def test_calculate_rsi_falling(self):
        """测试下跌时的 RSI"""
        # 持续下跌的价格
        falling_prices = pd.Series([30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20,
                                    19, 18, 17, 16, 15, 14, 13, 12, 11, 10])
        rsi = calculate_rsi(falling_prices, 14)
        
        # 持续下跌应该接近 0
        assert rsi.iloc[-1] < 10


class TestBBI:
    """BBI 指标测试"""
    
    def test_calculate_bbi_basic(self):
        """测试 BBI 基本计算"""
        np.random.seed(42)
        prices = pd.Series(np.random.uniform(10, 20, 30))
        bbi = calculate_bbi(prices)
        
        assert isinstance(bbi, pd.Series)
        assert len(bbi) == len(prices)
        
        # BBI 应该在价格范围内
        valid_bbi = bbi.dropna()
        assert valid_bbi.min() >= prices.min() - 1
        assert valid_bbi.max() <= prices.max() + 1


class TestBollingerBands:
    """布林带测试"""
    
    def test_calculate_bollinger_bands_returns_tuple(self):
        """测试布林带返回三个序列"""
        np.random.seed(42)
        prices = pd.Series(np.random.uniform(10, 20, 30))
        upper, middle, lower = calculate_bollinger_bands(prices)
        
        assert isinstance(upper, pd.Series)
        assert isinstance(middle, pd.Series)
        assert isinstance(lower, pd.Series)
    
    def test_bollinger_bands_order(self):
        """测试布林带上中下轨顺序"""
        np.random.seed(42)
        prices = pd.Series(np.random.uniform(10, 20, 30))
        upper, middle, lower = calculate_bollinger_bands(prices)
        
        # 上轨 > 中轨 > 下轨
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()


class TestAllIndicators:
    """综合指标计算测试"""
    
    @pytest.fixture
    def ohlcv_data(self):
        """创建 OHLCV 数据"""
        np.random.seed(42)
        n = 150  # 足够计算所有指标
        dates = pd.date_range(start="2024-01-01", periods=n, freq="D")
        
        return pd.DataFrame({
            "date": dates,
            "open": np.random.uniform(10, 20, n),
            "high": np.random.uniform(15, 25, n),
            "low": np.random.uniform(8, 15, n),
            "close": np.random.uniform(10, 20, n),
            "volume": np.random.uniform(1000000, 5000000, n),
        })
    
    def test_calculate_all_indicators_adds_columns(self, ohlcv_data):
        """测试计算所有指标后添加的列"""
        result = calculate_all_indicators(ohlcv_data)
        
        assert result is not None
        
        # 检查是否添加了关键指标列
        expected_columns = [
            "kdj_k", "kdj_d", "kdj_j",
            "macd", "macd_signal", "macd_hist",
            "bbi",
            "ma5", "ma10", "ma20",
            "zhixing_trend",
            "signal_buy", "signal_sell",
        ]
        
        for col in expected_columns:
            assert col in result.columns, f"缺少列: {col}"
    
    def test_calculate_all_indicators_with_insufficient_data(self):
        """测试数据不足时的处理"""
        # 只有 3 天数据（少于 MIN_DATA_DAYS // 4 = 5 天）
        small_data = pd.DataFrame({
            "open": [10, 11, 12],
            "high": [11, 12, 13],
            "low": [9, 10, 11],
            "close": [10.5, 11.5, 12.5],
            "volume": [1000, 1100, 1200],
        })
        
        result = calculate_all_indicators(small_data)
        
        # 数据不足时应该返回 None
        assert result is None


class TestBasicTechnicalIndicators:
    """基础技术指标测试"""
    
    def test_calculate_basic_with_insufficient_data(self):
        """测试数据不足时的处理"""
        result = calculate_basic_technical_indicators(
            current_price=15.5,
            historical_data=[10, 11, 12],  # 只有 3 天
        )
        
        assert result["current_price"] == 15.5
        assert result["MA5"] is None
        assert result["signal"] == "neutral"
    
    def test_calculate_basic_with_sufficient_data(self):
        """测试数据充足时的计算"""
        # 创建 25 天的历史数据
        historical = list(range(10, 35))  # 10, 11, ..., 34
        
        result = calculate_basic_technical_indicators(
            current_price=35.0,
            historical_data=historical,
        )
        
        assert result["current_price"] == 35.0
        assert result["MA5"] is not None
        assert result["MA10"] is not None
        assert result["MA20"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
