# -*- coding: utf-8 -*-
"""
AI 分析模块
支持多种 AI 模型进行股票分析
"""
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple

import requests

from stock_analysis.constants import (
    AI_REQUEST_TIMEOUT,
    CHANGE_PCT_HIGH,
    CHANGE_PCT_MEDIUM,
    SENTIMENT_BULLISH,
    SENTIMENT_NEUTRAL,
)
from stock_analysis.config import get_global_config

logger = logging.getLogger(__name__)

# 尝试导入可选依赖
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.debug("OpenAI SDK 未安装，将无法使用 OpenAI 兼容 API")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.debug("Google Generative AI SDK 未安装，将无法使用 Gemini API")


# ============ 数据类 ============

@dataclass
class StockResult:
    """股票分析结果"""
    code: str
    name: str
    current_price: float
    change_percent: float
    sentiment_score: float
    operation_advice: str
    trend_prediction: str
    technical_indicators: Dict[str, Any]
    additional_info: Dict[str, Any] = field(default_factory=dict)

    def get_emoji(self) -> str:
        """获取对应的情绪表情"""
        if self.sentiment_score >= SENTIMENT_BULLISH:
            return "🟢"
        elif self.sentiment_score >= SENTIMENT_NEUTRAL:
            return "🟡"
        else:
            return "🔴"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "name": self.name,
            "current_price": self.current_price,
            "change_percent": self.change_percent,
            "sentiment_score": self.sentiment_score,
            "operation_advice": self.operation_advice,
            "trend_prediction": self.trend_prediction,
            "technical_indicators": self.technical_indicators,
            "additional_info": self.additional_info,
        }


# ============ 基础分析器接口 ============

class BaseAIAnalyzer(ABC):
    """AI 分析器基类"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查分析器是否可用"""
        pass
    
    @abstractmethod
    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """分析股票"""
        pass
    
    def _build_prompt(self, stock_result: StockResult) -> str:
        """构建分析提示词"""
        return f"""
请对以下股票进行专业分析：

股票信息:
- 代码: {stock_result.code}
- 名称: {stock_result.name}
- 当前价格: {stock_result.current_price}
- 涨跌幅: {stock_result.change_percent}%

技术指标:
{self._format_indicators(stock_result.technical_indicators)}

请从以下几个方面进行分析：
1. 技术面分析
2. 短期趋势预测
3. 操作建议（买入/持有/卖出）
4. 风险提示

要求：分析要专业、客观，给出明确的操作建议。
"""
    
    @staticmethod
    def _format_indicators(indicators: Dict[str, Any]) -> str:
        """格式化技术指标"""
        lines = []
        for key, value in indicators.items():
            if value is not None:
                if isinstance(value, float):
                    if math.isnan(value):
                        continue
                    lines.append(f"- {key}: {value:.2f}")
                else:
                    lines.append(f"- {key}: {value}")
        return "\n".join(lines) if lines else "- 暂无指标数据"


# ============ Gemini 分析器 ============

class GeminiAnalyzer(BaseAIAnalyzer):
    """Gemini 分析器"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model
        self.client = None
        
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(model_name=model)
                logger.info(f"Gemini 分析器初始化成功，模型: {model}")
            except Exception as e:
                logger.error(f"Gemini 分析器初始化失败: {e}")

    def is_available(self) -> bool:
        """检查 Gemini 是否可用"""
        return GENAI_AVAILABLE and self.client is not None

    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用 Gemini 进行分析"""
        if not self.is_available():
            logger.warning("Gemini 不可用，跳过 AI 分析")
            return stock_result

        try:
            prompt = self._build_prompt(stock_result)
            response = self.client.generate_content(prompt)
            
            if response and response.text:
                # 更新分析结果
                stock_result.operation_advice = f"AI分析: {response.text[:300]}..."
                stock_result.trend_prediction = self._extract_trend(response.text)
            
            return stock_result
            
        except Exception as e:
            logger.error(f"Gemini 分析股票 {stock_result.code} 时出错: {e}")
            return stock_result
    
    @staticmethod
    def _extract_trend(text: str) -> str:
        """从 AI 响应中提取趋势预测"""
        # 简单提取，实际应用中可以更复杂
        if "买入" in text or "看涨" in text:
            return "短期看涨"
        elif "卖出" in text or "看跌" in text:
            return "短期看跌"
        else:
            return "震荡整理"


# ============ OpenAI 兼容分析器 ============

class OpenAICompatibleAnalyzer(BaseAIAnalyzer):
    """OpenAI 兼容分析器（支持 OpenAI、DeepSeek 等）"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "",
        model: str = "gpt-4o-mini"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE and api_key:
            try:
                if base_url:
                    self.client = OpenAI(api_key=api_key, base_url=base_url)
                else:
                    self.client = OpenAI(api_key=api_key)
                logger.info(f"OpenAI 兼容分析器初始化成功，模型: {model}")
            except Exception as e:
                logger.error(f"OpenAI 兼容分析器初始化失败: {e}")

    def is_available(self) -> bool:
        """检查 OpenAI 兼容 API 是否可用"""
        return OPENAI_AVAILABLE and self.client is not None

    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用 OpenAI 兼容 API 进行分析"""
        if not self.is_available():
            logger.warning("OpenAI 兼容 API 不可用，跳过 AI 分析")
            return stock_result

        try:
            prompt = self._build_prompt(stock_result)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                timeout=AI_REQUEST_TIMEOUT,
            )
            
            if response.choices:
                content = response.choices[0].message.content
                stock_result.operation_advice = f"AI分析: {content[:300]}..."
            
            return stock_result
            
        except Exception as e:
            logger.error(f"OpenAI 兼容 API 分析股票 {stock_result.code} 时出错: {e}")
            return stock_result


# ============ DeepSeek 分析器 ============

class DeepSeekAnalyzer(BaseAIAnalyzer):
    """DeepSeek 分析器（使用 requests 直接调用）"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    def is_available(self) -> bool:
        """检查 DeepSeek 是否可用"""
        return bool(self.api_key) and len(self.api_key) > 10

    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用 DeepSeek 进行分析"""
        if not self.is_available():
            logger.warning("DeepSeek 不可用，跳过 AI 分析")
            return stock_result

        try:
            prompt = self._build_prompt(stock_result)
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=AI_REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                return StockResult(
                    code=stock_result.code,
                    name=stock_result.name,
                    current_price=stock_result.current_price,
                    change_percent=stock_result.change_percent,
                    sentiment_score=stock_result.sentiment_score,
                    operation_advice=f"AI分析: {ai_response[:200]}...",
                    trend_prediction=ai_response[200:400] if len(ai_response) > 200 else ai_response,
                    technical_indicators=stock_result.technical_indicators,
                    additional_info=stock_result.additional_info,
                )
            else:
                logger.error(f"DeepSeek API 请求失败: {response.status_code}")
                return stock_result

        except Exception as e:
            logger.error(f"DeepSeek 分析股票 {stock_result.code} 时出错: {e}")
            return stock_result


# ============ 组合分析器 ============

class CombinedAnalyzer:
    """组合分析器 - 根据配置选择合适的 AI 分析器"""
    
    def __init__(self, config=None):
        """
        初始化组合分析器
        
        Args:
            config: 配置对象，为 None 时使用全局配置
        """
        self.config = config or get_global_config()
        
        # 初始化各个 AI 分析器
        self.gemini_analyzer: Optional[GeminiAnalyzer] = None
        self.openai_analyzer: Optional[OpenAICompatibleAnalyzer] = None
        self.deepseek_analyzer: Optional[DeepSeekAnalyzer] = None
        
        self._init_analyzers()
    
    def _init_analyzers(self) -> None:
        """初始化 AI 分析器"""
        ai_config = self.config.ai
        
        if ai_config.gemini_api_key:
            self.gemini_analyzer = GeminiAnalyzer(
                api_key=ai_config.gemini_api_key,
                model=ai_config.gemini_model,
            )
            logger.info("Gemini 分析器已配置")
        
        if ai_config.openai_api_key:
            self.openai_analyzer = OpenAICompatibleAnalyzer(
                api_key=ai_config.openai_api_key,
                base_url=ai_config.openai_base_url,
                model=ai_config.openai_model,
            )
            logger.info("OpenAI 兼容分析器已配置")
        
        if ai_config.deepseek_api_key:
            self.deepseek_analyzer = DeepSeekAnalyzer(
                api_key=ai_config.deepseek_api_key,
                base_url=ai_config.deepseek_base_url,
                model=ai_config.deepseek_model,
            )
            logger.info("DeepSeek 分析器已配置")
    
    def get_available_analyzer(self) -> Optional[BaseAIAnalyzer]:
        """获取第一个可用的分析器（优先级：DeepSeek > OpenAI > Gemini）"""
        if self.deepseek_analyzer and self.deepseek_analyzer.is_available():
            return self.deepseek_analyzer
        if self.openai_analyzer and self.openai_analyzer.is_available():
            return self.openai_analyzer
        if self.gemini_analyzer and self.gemini_analyzer.is_available():
            return self.gemini_analyzer
        return None
    
    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用配置的 AI 分析器分析股票"""
        analyzer = self.get_available_analyzer()
        
        if analyzer:
            analyzer_name = analyzer.__class__.__name__
            logger.info(f"使用 {analyzer_name} 分析股票 {stock_result.code}")
            return analyzer.analyze_stock(stock_result)
        else:
            logger.info("未配置可用的 AI 分析器，使用基础分析结果")
            return stock_result

    def analyze_single_stock(self, code: str) -> Optional[StockResult]:
        """
        分析单个股票（整合数据获取和 AI 分析）
        
        Args:
            code: 股票代码
            
        Returns:
            分析结果，失败返回 None
        """
        from stock_analysis.data_sources import TencentDataSource
        from stock_analysis.core.technical_indicators import calculate_basic_technical_indicators
        
        try:
            # 获取实时数据
            with TencentDataSource() as source:
                realtime = source.get_realtime([code])
                
                if not realtime or code not in realtime:
                    logger.error(f"无法获取股票 {code} 的实时数据")
                    return None
                
                stock_data = realtime[code]
                
                # 获取历史数据
                history_data = source.get_kline_data(code, days=30)
                
            # 计算技术指标
            historical_prices = [item["close"] for item in history_data] if history_data else []
            basic_indicators = calculate_basic_technical_indicators(
                current_price=stock_data.get("now", 0.0),
                historical_data=historical_prices,
            )
            
            # 整合技术指标
            technical_indicators = {
                "volume": stock_data.get("volume", 0),
                "amount": stock_data.get("amount", 0),
                "open": stock_data.get("open", 0.0),
                "high": stock_data.get("high", 0.0),
                "low": stock_data.get("low", 0.0),
                **{k: v for k, v in basic_indicators.items() if k != "current_price"},
            }
            
            # 创建 StockResult
            change_pct = stock_data.get("change_pct", 0.0)
            sentiment_score, operation_advice = self._calculate_basic_sentiment(change_pct)
            
            stock_result = StockResult(
                code=code,
                name=stock_data.get("name", ""),
                current_price=stock_data.get("now", 0.0),
                change_percent=change_pct,
                sentiment_score=sentiment_score,
                operation_advice=operation_advice,
                trend_prediction=f"当前涨跌幅{change_pct:+.2f}%",
                technical_indicators=technical_indicators,
            )
            
            # 使用 AI 分析器进行进一步分析
            return self.analyze_stock(stock_result)
            
        except Exception as e:
            logger.exception(f"分析股票 {code} 时出错: {e}")
            return None
    
    @staticmethod
    def _calculate_basic_sentiment(change_pct: float) -> Tuple[float, str]:
        """
        根据涨跌幅计算基础情绪评分
        
        Returns:
            (情绪评分, 操作建议)
        """
        if change_pct > CHANGE_PCT_MEDIUM:
            return 0.8, "谨慎追高"
        elif change_pct > 0:
            return 0.6, "观望"
        elif change_pct > -CHANGE_PCT_MEDIUM:
            return 0.4, "关注机会"
        else:
            return 0.2, "谨慎"


# 为了向后兼容，提供别名
AIAnalyzer = CombinedAnalyzer
