# -*- coding: utf-8 -*-
"""
stock_analysis 包
A股智能分析系统
"""
from stock_analysis.core.analyzer import CombinedAnalyzer, StockResult
from stock_analysis.core.technical_indicators import calculate_all_indicators
from stock_analysis.data_sources.tencent import TencentDataSource

__version__ = "1.0.0"
__all__ = [
    "CombinedAnalyzer",
    "StockResult",
    "TencentDataSource",
    "calculate_all_indicators",
]
