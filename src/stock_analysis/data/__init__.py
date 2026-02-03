# -*- coding: utf-8 -*-
"""
股票代码映射模块
提供股票名称到代码的查询功能
"""
import json
import os
from typing import Optional

# 加载股票代码映射
_STOCK_CODES_FILE = os.path.join(os.path.dirname(__file__), "stock_codes.json")
_stock_map: dict = {}


def _load_stock_codes() -> dict:
    """加载股票代码映射表"""
    global _stock_map
    if not _stock_map:
        try:
            with open(_STOCK_CODES_FILE, "r", encoding="utf-8") as f:
                _stock_map = json.load(f)
        except FileNotFoundError:
            _stock_map = {}
    return _stock_map


def get_stock_code(name_or_code: str) -> Optional[str]:
    """
    根据股票名称或代码获取标准股票代码
    
    Args:
        name_or_code: 股票名称或代码
        
    Returns:
        股票代码，如果找不到返回 None
        
    Examples:
        >>> get_stock_code("贵州茅台")
        '600519'
        >>> get_stock_code("茅台")
        '600519'
        >>> get_stock_code("600519")
        '600519'
        >>> get_stock_code("中国黄金")
        '600916'
    """
    name_or_code = name_or_code.strip()
    
    # 如果本身就是6位数字代码，直接返回
    if name_or_code.isdigit() and len(name_or_code) == 6:
        return name_or_code
    
    # 港股代码（5位）
    if name_or_code.isdigit() and len(name_or_code) == 5:
        return name_or_code
    
    # 从映射表查找
    stock_map = _load_stock_codes()
    
    # 精确匹配
    if name_or_code in stock_map:
        return stock_map[name_or_code]
    
    # 模糊匹配（包含关系）
    for name, code in stock_map.items():
        if name_or_code in name or name in name_or_code:
            return code
    
    return None


def search_stocks(keyword: str) -> list:
    """
    搜索股票
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        匹配的 (名称, 代码) 列表
    """
    stock_map = _load_stock_codes()
    results = []
    
    for name, code in stock_map.items():
        if keyword in name or keyword in code:
            results.append((name, code))
    
    return results


def get_all_stocks() -> dict:
    """获取所有股票映射"""
    return _load_stock_codes().copy()
