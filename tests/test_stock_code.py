# -*- coding: utf-8 -*-
"""
股票代码工具测试
"""
import pytest

from stock_analysis.utils.stock_code import (
    validate_stock_code,
    normalize_stock_code,
    get_market_prefix,
    to_tencent_symbol,
    parse_stock_input,
)


class TestValidateStockCode:
    """股票代码验证测试"""
    
    def test_valid_6_digit_codes(self):
        """测试有效的 6 位代码"""
        assert validate_stock_code("600519") is True  # 贵州茅台
        assert validate_stock_code("000001") is True  # 平安银行
        assert validate_stock_code("300750") is True  # 创业板
        assert validate_stock_code("688001") is True  # 科创板
    
    def test_valid_market_prefix_codes(self):
        """测试带市场前缀的代码"""
        assert validate_stock_code("sh600519") is True
        assert validate_stock_code("sz000001") is True
        assert validate_stock_code("bj430001") is True
    
    def test_invalid_codes(self):
        """测试无效代码"""
        assert validate_stock_code("") is False
        assert validate_stock_code("12345") is False  # 5 位
        assert validate_stock_code("1234567") is False  # 7 位
        assert validate_stock_code("abcdef") is False
        assert validate_stock_code(None) is False
    
    def test_index_codes(self):
        """测试指数代码"""
        assert validate_stock_code("000001") is True  # 上证指数
        assert validate_stock_code("399001") is True  # 深证成指


class TestNormalizeStockCode:
    """股票代码标准化测试"""
    
    def test_normalize_6_digit(self):
        """测试 6 位代码标准化"""
        assert normalize_stock_code("600519") == "600519"
        assert normalize_stock_code("000001") == "000001"
    
    def test_normalize_with_prefix(self):
        """测试带前缀代码标准化"""
        assert normalize_stock_code("sh600519") == "600519"
        assert normalize_stock_code("sz000001") == "000001"
        assert normalize_stock_code("SH600519") == "600519"  # 大写
    
    def test_normalize_special_codes(self):
        """测试特殊代码标准化"""
        assert normalize_stock_code("1A0001") == "000001"
    
    def test_normalize_invalid(self):
        """测试无效代码"""
        assert normalize_stock_code("") is None
        assert normalize_stock_code("abc") is None
        assert normalize_stock_code(None) is None


class TestGetMarketPrefix:
    """市场前缀测试"""
    
    def test_shanghai_codes(self):
        """测试上海代码"""
        assert get_market_prefix("600519") == "sh"  # 6 开头
        assert get_market_prefix("500001") == "sh"  # 5 开头
        assert get_market_prefix("900001") == "sh"  # 9 开头
    
    def test_shenzhen_codes(self):
        """测试深圳代码"""
        assert get_market_prefix("000002") == "sz"  # 0 开头 (万科)
        assert get_market_prefix("300750") == "sz"  # 3 开头
    
    def test_beijing_codes(self):
        """测试北京代码"""
        assert get_market_prefix("430001") == "bj"  # 4 开头
        assert get_market_prefix("830001") == "bj"  # 8 开头
    
    def test_index_codes(self):
        """测试指数代码"""
        assert get_market_prefix("000001") == "sh"  # 上证指数
        assert get_market_prefix("399001") == "sz"  # 深证成指


class TestToTencentSymbol:
    """腾讯代码转换测试"""
    
    def test_convert_shanghai(self):
        """测试上海代码转换"""
        assert to_tencent_symbol("600519") == "sh600519"
    
    def test_convert_shenzhen(self):
        """测试深圳代码转换"""
        assert to_tencent_symbol("000002") == "sz000002"  # 万科
    
    def test_already_formatted(self):
        """测试已格式化的代码"""
        assert to_tencent_symbol("sh600519") == "sh600519"
        assert to_tencent_symbol("SZ000001") == "sz000001"


class TestParseStockInput:
    """股票输入解析测试"""
    
    def test_comma_separated(self):
        """测试逗号分隔"""
        result = parse_stock_input("600519,000001,300750")
        assert result == ["600519", "000001", "300750"]
    
    def test_space_separated(self):
        """测试空格分隔"""
        result = parse_stock_input("600519 000001 300750")
        assert result == ["600519", "000001", "300750"]
    
    def test_mixed_separators(self):
        """测试混合分隔符"""
        result = parse_stock_input("600519, 000001,  300750")
        assert result == ["600519", "000001", "300750"]
    
    def test_with_invalid_codes(self):
        """测试包含无效代码"""
        result = parse_stock_input("600519,invalid,000001")
        assert "600519" in result
        assert "000001" in result
        assert "invalid" not in result
    
    def test_empty_input(self):
        """测试空输入"""
        assert parse_stock_input("") == []
        assert parse_stock_input(None) == []
    
    def test_single_code(self):
        """测试单个代码"""
        result = parse_stock_input("600519")
        assert result == ["600519"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
