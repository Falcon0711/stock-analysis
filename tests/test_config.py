# -*- coding: utf-8 -*-
"""
配置模块测试
"""
import pytest
import os
from unittest.mock import patch

from stock_analysis.config import (
    Config,
    AIConfig,
    NotificationConfig,
    ScheduleConfig,
    WebUIConfig,
    get_config,
    get_global_config,
    reload_config,
    _parse_list,
)


class TestParseList:
    """列表解析测试"""
    
    def test_parse_comma_separated(self):
        """测试逗号分隔解析"""
        result = _parse_list("a,b,c")
        assert result == ["a", "b", "c"]
    
    def test_parse_with_spaces(self):
        """测试带空格解析"""
        result = _parse_list("a, b, c")
        assert result == ["a", "b", "c"]
    
    def test_parse_empty_string(self):
        """测试空字符串"""
        result = _parse_list("")
        assert result == []
    
    def test_parse_none(self):
        """测试 None"""
        result = _parse_list(None)
        assert result == []
    
    def test_parse_with_empty_items(self):
        """测试包含空项"""
        result = _parse_list("a,,b,")
        assert result == ["a", "b"]


class TestAIConfig:
    """AI 配置测试"""
    
    def test_default_values(self):
        """测试默认值"""
        config = AIConfig()
        
        assert config.gemini_api_key == ""
        assert config.gemini_model == "gemini-2.5-flash"
        assert config.gemini_temperature == 0.7
        assert config.deepseek_base_url == "https://api.deepseek.com/v1"


class TestConfig:
    """配置类测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = Config()
        
        assert config.stock_list == []
        assert config.max_workers == 3
        assert config.debug is False
    
    def test_backward_compatibility_uppercase(self):
        """测试大写属性向后兼容"""
        config = Config(
            ai=AIConfig(gemini_api_key="test-key"),
            stock_list=["600519"],
        )
        
        # 大写属性应该正常工作
        assert config.GEMINI_API_KEY == "test-key"
        assert config.STOCK_LIST == ["600519"]
    
    def test_validate_no_api_keys(self):
        """测试验证无 API Key"""
        config = Config()
        warnings = config.validate()
        
        assert any("API Key" in w for w in warnings)
    
    def test_validate_no_stock_list(self):
        """测试验证无股票列表"""
        config = Config(
            ai=AIConfig(gemini_api_key="test-key"),
        )
        warnings = config.validate()
        
        assert any("股票列表" in w for w in warnings)
    
    def test_validate_insecure_webhook(self):
        """测试验证不安全的 Webhook"""
        config = Config(
            ai=AIConfig(gemini_api_key="test-key"),
            notification=NotificationConfig(
                feishu_webhook_url="http://insecure.example.com",
            ),
            stock_list=["600519"],
        )
        warnings = config.validate()
        
        assert any("HTTPS" in w for w in warnings)


class TestGetConfig:
    """获取配置测试"""
    
    @patch.dict(os.environ, {
        "GEMINI_API_KEY": "test-gemini-key",
        "STOCK_LIST": "600519,000001",
        "DEBUG": "true",
    })
    def test_load_from_env(self):
        """测试从环境变量加载"""
        config = get_config()
        
        assert config.ai.gemini_api_key == "test-gemini-key"
        assert config.stock_list == ["600519", "000001"]
        assert config.debug is True
    
    @patch.dict(os.environ, {
        "SCHEDULE_ENABLED": "true",
        "SCHEDULE_TIME": "09:30",
    })
    def test_load_schedule_config(self):
        """测试加载定时任务配置"""
        config = get_config()
        
        assert config.schedule.enabled is True
        assert config.schedule.time == "09:30"


class TestGlobalConfig:
    """全局配置测试"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        # 重置全局配置
        reload_config()
        
        config1 = get_global_config()
        config2 = get_global_config()
        
        assert config1 is config2
    
    def test_reload_creates_new(self):
        """测试重新加载创建新实例"""
        config1 = get_global_config()
        config2 = reload_config()
        
        # reload 应该返回新实例
        # 注意：由于是单例，get_global_config 之后会返回新实例
        assert config2 is get_global_config()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
