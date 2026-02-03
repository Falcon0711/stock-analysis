# -*- coding: utf-8 -*-
"""
AI分析器模块 - 为兼容旧版引用而创建
"""
from .core.analyzer import GeminiAnalyzer, CombinedAnalyzer

# 为了向后兼容，提供旧的类名
class StockAnalyzer(CombinedAnalyzer):
    """股票分析器（兼容类）"""
    pass