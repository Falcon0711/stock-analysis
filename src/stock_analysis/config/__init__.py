# -*- coding: utf-8 -*-
"""
配置模块
统一管理所有配置项
"""
import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_env() -> None:
    """加载环境变量"""
    # 尝试多个可能的 .env 文件位置
    possible_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent.parent / ".env",
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path)
            logger.debug(f"Loaded .env from {env_path}")
            return
    
    # 即使没有找到 .env 也尝试加载（可能已经设置了环境变量）
    load_dotenv()


@dataclass
class AIConfig:
    """AI 模型配置"""
    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_model_fallback: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.7
    gemini_request_delay: int = 30
    
    # OpenAI 兼容 API
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    
    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    deepseek_temperature: float = 0.7


@dataclass
class NotificationConfig:
    """通知配置"""
    feishu_webhook_url: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    dingtalk_stream_enabled: bool = False
    feishu_stream_enabled: bool = False
    single_stock_notify: bool = False


@dataclass
class ScheduleConfig:
    """定时任务配置"""
    enabled: bool = False
    time: str = "18:00"
    market_review_enabled: bool = True


@dataclass
class WebUIConfig:
    """WebUI 配置"""
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass
class Config:
    """应用配置"""
    # 子配置
    ai: AIConfig = field(default_factory=AIConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    webui: WebUIConfig = field(default_factory=WebUIConfig)
    
    # 股票配置
    stock_list: List[str] = field(default_factory=list)
    
    # 搜索 API keys
    bocha_api_keys: List[str] = field(default_factory=list)
    tavily_api_keys: List[str] = field(default_factory=list)
    serpapi_keys: List[str] = field(default_factory=list)
    
    # 系统配置
    log_level: str = "INFO"
    log_dir: str = "./logs"
    database_path: str = "./data/stock_analysis.db"
    max_workers: int = 3
    debug: bool = False
    analysis_delay: int = 0
    
    # 兼容性属性 (大写，用于旧代码兼容)
    @property
    def GEMINI_API_KEY(self) -> str:
        return self.ai.gemini_api_key
    
    @property
    def GEMINI_MODEL(self) -> str:
        return self.ai.gemini_model
    
    @property
    def GEMINI_MODEL_FALLBACK(self) -> str:
        return self.ai.gemini_model_fallback
    
    @property
    def GEMINI_TEMPERATURE(self) -> float:
        return self.ai.gemini_temperature
    
    @property
    def GEMINI_REQUEST_DELAY(self) -> int:
        return self.ai.gemini_request_delay
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.ai.openai_api_key
    
    @property
    def OPENAI_BASE_URL(self) -> str:
        return self.ai.openai_base_url
    
    @property
    def OPENAI_MODEL(self) -> str:
        return self.ai.openai_model
    
    @property
    def OPENAI_TEMPERATURE(self) -> float:
        return self.ai.openai_temperature
    
    @property
    def DEEPSEEK_API_KEY(self) -> str:
        return self.ai.deepseek_api_key
    
    @property
    def DEEPSEEK_BASE_URL(self) -> str:
        return self.ai.deepseek_base_url
    
    @property
    def DEEPSEEK_MODEL(self) -> str:
        return self.ai.deepseek_model
    
    @property
    def DEEPSEEK_TEMPERATURE(self) -> float:
        return self.ai.deepseek_temperature
    
    @property
    def STOCK_LIST(self) -> List[str]:
        return self.stock_list
    
    @property
    def FEISHU_WEBHOOK_URL(self) -> str:
        return self.notification.feishu_webhook_url
    
    @property
    def TELEGRAM_BOT_TOKEN(self) -> str:
        return self.notification.telegram_bot_token
    
    @property
    def TELEGRAM_CHAT_ID(self) -> str:
        return self.notification.telegram_chat_id
    
    @property
    def DATABASE_PATH(self) -> str:
        return self.database_path
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.log_level
    
    @property
    def MAX_WORKERS(self) -> int:
        return self.max_workers
    
    @property
    def DEBUG(self) -> bool:
        return self.debug
    
    # 新式属性（小写，用于新代码）
    @property
    def gemini_api_key(self) -> str:
        return self.ai.gemini_api_key
    
    @property
    def openai_api_key(self) -> str:
        return self.ai.openai_api_key
    
    @property
    def webui_enabled(self) -> bool:
        return self.webui.enabled
    
    @property
    def webui_host(self) -> str:
        return self.webui.host
    
    @property
    def webui_port(self) -> int:
        return self.webui.port
    
    @property
    def single_stock_notify(self) -> bool:
        return self.notification.single_stock_notify
    
    @single_stock_notify.setter
    def single_stock_notify(self, value: bool) -> None:
        self.notification.single_stock_notify = value
    
    @property
    def dingtalk_stream_enabled(self) -> bool:
        return self.notification.dingtalk_stream_enabled
    
    @property
    def feishu_stream_enabled(self) -> bool:
        return self.notification.feishu_stream_enabled
    
    @property
    def schedule_enabled(self) -> bool:
        return self.schedule.enabled
    
    @property
    def schedule_time(self) -> str:
        return self.schedule.time
    
    @property
    def market_review_enabled(self) -> bool:
        return self.schedule.market_review_enabled
    
    def validate(self) -> List[str]:
        """验证配置，返回警告信息列表"""
        warnings = []
        
        if not self.ai.gemini_api_key and not self.ai.openai_api_key and not self.ai.deepseek_api_key:
            warnings.append("警告: 未配置任何AI API Key，将无法使用AI分析功能")
        
        if not self.stock_list:
            warnings.append("警告: 未配置股票列表")
        
        if self.notification.feishu_webhook_url and not self.notification.feishu_webhook_url.startswith("https://"):
            warnings.append("警告: 飞书 Webhook URL 应使用 HTTPS")
        
        return warnings


def _parse_list(value: str) -> List[str]:
    """解析逗号分隔的字符串为列表"""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def get_config() -> Config:
    """从环境变量获取配置"""
    setup_env()
    
    return Config(
        ai=AIConfig(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            gemini_model_fallback=os.getenv("GEMINI_MODEL_FALLBACK", "gemini-2.0-flash"),
            gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            gemini_request_delay=int(os.getenv("GEMINI_REQUEST_DELAY", "30")),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            deepseek_temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
        ),
        notification=NotificationConfig(
            feishu_webhook_url=os.getenv("FEISHU_WEBHOOK_URL", ""),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            dingtalk_stream_enabled=os.getenv("DINGTALK_STREAM_ENABLED", "false").lower() == "true",
            feishu_stream_enabled=os.getenv("FEISHU_STREAM_ENABLED", "false").lower() == "true",
            single_stock_notify=os.getenv("SINGLE_STOCK_NOTIFY", "false").lower() == "true",
        ),
        schedule=ScheduleConfig(
            enabled=os.getenv("SCHEDULE_ENABLED", "false").lower() == "true",
            time=os.getenv("SCHEDULE_TIME", "18:00"),
            market_review_enabled=os.getenv("MARKET_REVIEW_ENABLED", "true").lower() == "true",
        ),
        webui=WebUIConfig(
            enabled=os.getenv("WEBUI_ENABLED", "false").lower() == "true",
            host=os.getenv("WEBUI_HOST", "127.0.0.1"),
            port=int(os.getenv("WEBUI_PORT", "8080")),
        ),
        stock_list=_parse_list(os.getenv("STOCK_LIST", "")),
        bocha_api_keys=_parse_list(os.getenv("BOCHA_API_KEYS", "")),
        tavily_api_keys=_parse_list(os.getenv("TAVILY_API_KEYS", "")),
        serpapi_keys=_parse_list(os.getenv("SERPAPI_KEYS", "")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_dir=os.getenv("LOG_DIR", "./logs"),
        database_path=os.getenv("DATABASE_PATH", "./data/stock_analysis.db"),
        max_workers=int(os.getenv("MAX_WORKERS", "3")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        analysis_delay=int(os.getenv("ANALYSIS_DELAY", "0")),
    )


# 全局配置实例
_config: Optional[Config] = None


def get_global_config() -> Config:
    """获取全局配置实例（单例模式）"""
    global _config
    if _config is None:
        _config = get_config()
    return _config


def reload_config() -> Config:
    """重新加载配置"""
    global _config
    _config = get_config()
    return _config
