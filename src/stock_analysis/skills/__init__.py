# -*- coding: utf-8 -*-
"""
技能模块
提供标准化的股票分析功能
"""
from stock_analysis.skills.stock_analysis import (
    StockAnalysisSkill,
    get_stock_analysis,
    get_stock_analysis_with_ai,
    get_multiple_stock_analysis,
)

__all__ = [
    "StockAnalysisSkill",
    "get_stock_analysis",
    "get_stock_analysis_with_ai",
    "get_multiple_stock_analysis",
]
