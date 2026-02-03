# -*- coding: utf-8 -*-
"""
股票代码工具模块
提供股票代码验证和转换功能
"""
import re
import logging
from typing import Optional, List

from stock_analysis.constants import (
    VALID_SH_PREFIXES,
    VALID_SZ_PREFIXES,
    VALID_BJ_PREFIXES,
    VALID_INDEX_CODES,
)

logger = logging.getLogger(__name__)

# 股票代码正则表达式
STOCK_CODE_PATTERN = re.compile(r"^[0-9]{6}$")
MARKET_CODE_PATTERN = re.compile(r"^(sh|sz|bj)[0-9]{6}$")


def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式是否有效
    
    Args:
        code: 股票代码
        
    Returns:
        是否有效
    """
    if not code:
        return False
    
    code = code.strip().lower()
    
    # 检查是否是带市场前缀的代码
    if MARKET_CODE_PATTERN.match(code):
        return True
    
    # 检查是否是6位数字代码
    if STOCK_CODE_PATTERN.match(code):
        return True
    
    # 检查是否是已知的指数代码
    if code.upper() in VALID_INDEX_CODES:
        return True
    
    return False


def normalize_stock_code(code: str) -> Optional[str]:
    """
    标准化股票代码，返回纯6位数字代码
    
    Args:
        code: 原始股票代码
        
    Returns:
        标准化后的6位代码，无效则返回 None
    """
    if not code:
        return None
    
    code = code.strip()
    
    # 如果已经是带前缀的代码，提取数字部分
    if len(code) == 8 and code[:2].lower() in ("sh", "sz", "bj"):
        return code[2:]
    
    # 如果是6位数字代码
    if STOCK_CODE_PATTERN.match(code):
        return code
    
    # 特殊处理某些代码
    if code.upper() == "1A0001":
        return "000001"
    
    return None


def get_market_prefix(code: str) -> str:
    """
    获取股票代码的市场前缀
    
    Args:
        code: 6位股票代码
        
    Returns:
        市场前缀 (sh/sz/bj)
    """
    if not code:
        return ""
    
    code = normalize_stock_code(code) or code
    
    # 检查是否是已知的指数代码
    if code in VALID_INDEX_CODES:
        return VALID_INDEX_CODES[code]
    
    # 根据首位数字判断市场
    first_char = code[0]
    
    if first_char in VALID_SH_PREFIXES:
        return "sh"
    elif first_char in VALID_BJ_PREFIXES:
        return "bj"
    else:
        return "sz"


def to_tencent_symbol(code: str) -> str:
    """
    将股票代码转换为腾讯格式 (市场前缀+代码)
    
    Args:
        code: 股票代码
        
    Returns:
        腾讯格式的代码 (如 sh600519)
    """
    # 如果已经是腾讯格式
    if len(code) == 8 and code[:2].lower() in ("sh", "sz", "bj"):
        return code.lower()
    
    # 标准化代码
    normalized = normalize_stock_code(code)
    if not normalized:
        logger.warning(f"无法标准化股票代码: {code}")
        return code
    
    # 获取市场前缀
    prefix = get_market_prefix(normalized)
    
    return f"{prefix}{normalized}"


def parse_stock_input(input_str: str) -> List[str]:
    """
    解析用户输入的股票代码字符串
    
    支持格式:
    - 逗号分隔: "600519,000001,002400"
    - 空格分隔: "600519 000001 002400"
    - 混合分隔: "600519, 000001, 002400"
    
    Args:
        input_str: 用户输入的股票代码字符串
        
    Returns:
        有效的股票代码列表
    """
    if not input_str:
        return []
    
    # 使用正则表达式分割
    parts = re.split(r"[,\s]+", input_str.strip())
    
    # 验证并收集有效代码
    valid_codes = []
    for part in parts:
        part = part.strip()
        if part and validate_stock_code(part):
            normalized = normalize_stock_code(part)
            if normalized:
                valid_codes.append(normalized)
            else:
                valid_codes.append(part)
        elif part:
            logger.warning(f"无效的股票代码: {part}")
    
    return valid_codes
