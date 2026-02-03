# -*- coding: utf-8 -*-
"""
配置模块
"""
import os
from dotenv import load_dotenv
from typing import List, Optional

# 加载环境变量
load_dotenv()


class Config:
    """配置类"""
    
    # API配置
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    GEMINI_MODEL_FALLBACK = os.getenv("GEMINI_MODEL_FALLBACK", "gemini-2.5-flash")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    GEMINI_REQUEST_DELAY = int(os.getenv("GEMINI_REQUEST_DELAY", "30"))

    # OpenAI兼容API配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

    # 股票配置
    STOCK_LIST = os.getenv("STOCK_LIST", "").split(",")
    if STOCK_LIST == [""]:
        STOCK_LIST = []

    # 通知配置
    FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # 邮件配置
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_RECEIVERS = os.getenv("EMAIL_RECEIVERS", "").split(",")
    if EMAIL_RECEIVERS == [""]:
        EMAIL_RECEIVERS = []

    # 数据库配置
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/stock_analysis.db")

    # 系统配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def log_dir(self):
        return os.getenv("LOG_DIR", "./logs")
    
    @property
    def gemini_api_key(self):
        return os.getenv("GEMINI_API_KEY", "")
    
    @property
    def openai_api_key(self):
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def bocha_api_keys(self):
        keys = os.getenv("BOCHA_API_KEYS", "")
        return [k.strip() for k in keys.split(",")] if keys else []
    
    @property
    def tavily_api_keys(self):
        keys = os.getenv("TAVILY_API_KEYS", "")
        return [k.strip() for k in keys.split(",")] if keys else []
    
    @property
    def serpapi_keys(self):
        keys = os.getenv("SERPAPI_KEYS", "")
        return [k.strip() for k in keys.split(",")] if keys else []
    
    @property
    def webui_enabled(self):
        return os.getenv("WEBUI_ENABLED", "false").lower() == "true"
    
    @property
    def webui_host(self):
        return os.getenv("WEBUI_HOST", "127.0.0.1")
    
    @property
    def webui_port(self):
        return int(os.getenv("WEBUI_PORT", "8080"))
    
    @property
    def single_stock_notify(self):
        return os.getenv("SINGLE_STOCK_NOTIFY", "false").lower() == "true"
    
    @property
    def analysis_delay(self):
        return int(os.getenv("ANALYSIS_DELAY", "0"))
    
    @property
    def dingtalk_stream_enabled(self):
        return os.getenv("DINGTALK_STREAM_ENABLED", "false").lower() == "true"
    
    @property
    def feishu_stream_enabled(self):
        return os.getenv("FEISHU_STREAM_ENABLED", "false").lower() == "true"

    # 定时任务配置
    @property
    def schedule_enabled(self):
        return os.getenv("SCHEDULE_ENABLED", "false").lower() == "true"
    
    @property
    def schedule_time(self):
        return os.getenv("SCHEDULE_TIME", "18:00")
    
    @property
    def market_review_enabled(self):
        return os.getenv("MARKET_REVIEW_ENABLED", "true").lower() == "true"

    def validate(self) -> List[str]:
        """验证配置，返回警告信息列表"""
        warnings = []
        
        if not self.GEMINI_API_KEY and not self.OPENAI_API_KEY:
            warnings.append("警告: 未配置任何AI API Key，将无法使用AI分析功能")
        
        if not self.STOCK_LIST:
            warnings.append("警告: 未配置股票列表")
        
        return warnings


def get_config() -> Config:
    """获取配置实例"""
    return Config()


def setup_env():
    """设置环境"""
    load_dotenv()