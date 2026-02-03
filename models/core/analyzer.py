# -*- coding: utf-8 -*-
"""
AI分析模块 - 支持多种AI模型，包括DeepSeek
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import akshare as ak
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import Config
get_config = lambda: Config()
from .technical_indicators import calculate_basic_technical_indicators

# 尝试导入OpenAI兼容库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("警告: 未安装openai库，将无法使用OpenAI兼容API")

# 尝试导入Google Generative AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("警告: 未安装google-generativeai库，将无法使用Gemini API")

logger = logging.getLogger(__name__)


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
    additional_info: Dict[str, Any] = None

    def get_emoji(self) -> str:
        """获取对应的情绪表情"""
        if self.sentiment_score >= 0.7:
            return "🟢"
        elif self.sentiment_score >= 0.4:
            return "🟡"
        else:
            return "🔴"


class BaseAIAnalyzer:
    """基础AI分析器接口"""
    
    def is_available(self) -> bool:
        """检查AI分析器是否可用"""
        raise NotImplementedError
    
    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """分析股票"""
        raise NotImplementedError


class GeminiAnalyzer(BaseAIAnalyzer):
    """Gemini分析器"""
    
    def __init__(self, api_key: str, model: str = "gemini-3-flash-preview"):
        self.api_key = api_key
        self.model_name = model
        self.logger = logging.getLogger(__name__)
        
        if GENAI_AVAILABLE:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model_name=model)
        else:
            self.client = None

    def is_available(self) -> bool:
        """检查Gemini是否可用"""
        return GENAI_AVAILABLE and self.client is not None

    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用Gemini进行深度分析"""
        if not self.is_available():
            self.logger.warning("Gemini不可用，跳过AI分析")
            return stock_result

        try:
            # 构建分析提示
            prompt = f"""
            请对以下股票进行专业分析：

            股票信息:
            - 代码: {stock_result.code}
            - 名称: {stock_result.name}
            - 当前价格: {stock_result.current_price}
            - 涨跌幅: {stock_result.change_percent}%
            - 情绪评分: {stock_result.sentiment_score}
            - 技术指标: {stock_result.technical_indicators}
            - 其他信息: {stock_result.additional_info}

            请从以下几个方面进行分析：
            1. 技术面分析
            2. 短期趋势预测
            3. 操作建议（买入/持有/卖出）
            4. 风险提示

            要求：分析要专业、客观，给出明确的操作建议。
            """

            response = self.client.generate_content(prompt)
            
            # 注意：这里简化处理，实际应用中可能需要解析AI返回的更复杂结构
            # 目前保持原有评分不变，但可以考虑使用AI返回的信息优化评分
            return stock_result
            
        except Exception as e:
            self.logger.error(f"Gemini分析股票 {stock_result.code} 时出错: {e}")
            return stock_result


class OpenAICompatibleAnalyzer(BaseAIAnalyzer):
    """OpenAI兼容分析器"""
    
    def __init__(self, api_key: str, base_url: str = "", model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        if OPENAI_AVAILABLE:
            # 如果提供了base_url，则为OpenAI兼容API（如DeepSeek）
            if base_url:
                self.client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    def is_available(self) -> bool:
        """检查OpenAI兼容API是否可用"""
        return OPENAI_AVAILABLE and self.client is not None

    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用OpenAI兼容API进行分析"""
        if not self.is_available():
            self.logger.warning("OpenAI兼容API不可用，跳过AI分析")
            return stock_result

        try:
            # 构建分析提示
            prompt = f"""
            请对以下股票进行专业分析：

            股票信息:
            - 代码: {stock_result.code}
            - 名称: {stock_result.name}
            - 当前价格: {stock_result.current_price}
            - 涨跌幅: {stock_result.change_percent}%
            - 情绪评分: {stock_result.sentiment_score}
            - 技术指标: {stock_result.technical_indicators}
            - 其他信息: {stock_result.additional_info}

            请从以下几个方面进行分析：
            1. 技术面分析
            2. 短期趋势预测
            3. 操作建议（买入/持有/卖出）
            4. 风险提示

            要求：分析要专业、客观，给出明确的操作建议。
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 同样简化处理，保持原有评分不变
            return stock_result
            
        except Exception as e:
            self.logger.error(f"OpenAI兼容API分析股票 {stock_result.code} 时出错: {e}")
            return stock_result


class DeepSeekAnalyzer:
    """DeepSeek分析器 - 使用requests直接调用API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1", model: str = "deepseek-chat"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def is_available(self) -> bool:
        """检查DeepSeek是否可用"""
        # 只要API密钥存在且格式正确就认为可用
        return self.api_key and len(self.api_key) > 10

    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用DeepSeek进行深度分析"""
        if not self.is_available():
            self.logger.warning("DeepSeek不可用，跳过AI分析")
            return stock_result

        try:
            # 构建分析提示
            prompt = f"""
            请对以下股票进行专业分析：

            股票信息:
            - 代码: {stock_result.code}
            - 名称: {stock_result.name}
            - 当前价格: {stock_result.current_price}
            - 涨跌幅: {stock_result.change_percent}%

            技术指标:
            - 成交量: {stock_result.technical_indicators.get('volume', 'N/A')}
            - 成交额: {stock_result.technical_indicators.get('amount', 'N/A')}
            - 开盘价: {stock_result.technical_indicators.get('open', 'N/A')}
            - 最高价: {stock_result.technical_indicators.get('high', 'N/A')}
            - 最低价: {stock_result.technical_indicators.get('low', 'N/A')}

            请从以下几个方面进行分析：
            1. 技术面分析
            2. 短期趋势预测
            3. 操作建议（买入/持有/卖出）
            4. 风险提示

            要求：分析要专业、客观，给出明确的操作建议。
            """

            import requests
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60  # 增加超时时间到60秒
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # 解析AI响应并更新股票结果
                # 这里可以更精细地解析AI响应，但为了简化，我们更新操作建议
                updated_result = StockResult(
                    code=stock_result.code,
                    name=stock_result.name,
                    current_price=stock_result.current_price,
                    change_percent=stock_result.change_percent,
                    sentiment_score=stock_result.sentiment_score,
                    operation_advice=f"AI分析: {ai_response[:200]}...",
                    trend_prediction=f"AI趋势预测: {ai_response[200:400] if len(ai_response) > 200 else ai_response}",
                    technical_indicators=stock_result.technical_indicators,
                    additional_info=stock_result.additional_info
                )
                
                self.logger.info(f"DeepSeek分析完成: {stock_result.code}")
                return updated_result
            else:
                self.logger.error(f"DeepSeek API 请求失败: {response.status_code} - {response.text}")
                return stock_result

        except Exception as e:
            self.logger.error(f"DeepSeek分析股票 {stock_result.code} 时出错: {e}")
            return stock_result


class AIAnalyzer:
    """
    AI股票分析器
    用于基于技术指标进行综合AI分析
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个AI分析器
        self.gemini_analyzer = None
        self.openai_analyzer = None
        self.deepseek_analyzer = None
        
        # 验证配置
        self.logger.info(f"Gemini API Key 配置: {bool(self.config.GEMINI_API_KEY)}")
        self.logger.info(f"OpenAI API Key 配置: {bool(self.config.OPENAI_API_KEY)}")
        self.logger.info(f"DeepSeek API Key 配置: {bool(self.config.DEEPSEEK_API_KEY)}")
        
        if self.config.GEMINI_API_KEY:
            self.gemini_analyzer = GeminiAnalyzer(
                api_key=self.config.GEMINI_API_KEY,
                model=self.config.GEMINI_MODEL
            )
        
        if self.config.OPENAI_API_KEY:
            self.openai_analyzer = OpenAICompatibleAnalyzer(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_BASE_URL,
                model=self.config.OPENAI_MODEL
            )
        
        if self.config.DEEPSEEK_API_KEY:
            self.logger.info("初始化 DeepSeek 分析器...")
            self.deepseek_analyzer = DeepSeekAnalyzer(
                api_key=self.config.DEEPSEEK_API_KEY,
                base_url=self.config.DEEPSEEK_BASE_URL,
                model=self.config.DEEPSEEK_MODEL
            )
            self.logger.info(f"DeepSeek 分析器已创建: {self.deepseek_analyzer is not None}")

    def _build_analysis_prompt(self, stock_code: str, analysis_data: Dict[str, Any]) -> str:
        """
        构建AI分析提示词
        """
        import math
        
        def safe_format(value, format_str='.2f'):
            """安全格式化数值，处理NaN和None"""
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return 'N/A'
            try:
                if format_str == '.2f':
                    return f'{float(value):.2f}'
                elif format_str == '.3f':
                    return f'{float(value):.3f}'
                else:
                    return str(value)
            except (ValueError, TypeError):
                return 'N/A'
        
        current_data = analysis_data.get('current_data', {})
        indicator_data = analysis_data.get('indicators', {})
        
        prompt = f"""
请基于以下股票的技术指标数据进行综合分析：

股票代码: {stock_code}
股票名称: {current_data.get('name', '未知')}
当前价格: {safe_format(current_data.get('now', 0), '.2f')}元
涨跌幅: {safe_format(current_data.get('change_pct', 0), '+.2f')}%

技术指标数据:
- KDJ: K={safe_format(indicator_data.get('kdj_k', 'N/A'), '.2f')}, D={safe_format(indicator_data.get('kdj_d', 'N/A'), '.2f')}, J={safe_format(indicator_data.get('kdj_j', 'N/A'), '.2f')}
- MACD: {safe_format(indicator_data.get('macd', 'N/A'), '.3f')}, {safe_format(indicator_data.get('macd_signal', 'N/A'), '.3f')}, {safe_format(indicator_data.get('macd_hist', 'N/A'), '.3f')}
- BBI: {safe_format(indicator_data.get('bbi', 'N/A'), '.2f')}
- MA5/10/20/60: {safe_format(indicator_data.get('ma5', 'N/A'), '.2f')}/{safe_format(indicator_data.get('ma10', 'N/A'), '.2f')}/{safe_format(indicator_data.get('ma20', 'N/A'), '.2f')}/{safe_format(indicator_data.get('ma60', 'N/A'), '.2f')}
- 知行趋势线: {safe_format(indicator_data.get('zhixing_trend', 'N/A'), '.2f')}
- 知行多空线: {safe_format(indicator_data.get('zhixing_multi', 'N/A'), '.2f')}

请从以下几个方面进行分析：
1. 技术面分析：基于各项技术指标给出评价
2. 短期趋势：对未来1-3个交易日的趋势预测
3. 中期趋势：对未来1-4周的趋势预测
4. 关键价位：指出重要的支撑位和阻力位
5. 操作建议：给出具体的操作建议（买入、持有、卖出）
6. 风险提示：指出主要风险因素

请用简洁明了的语言进行分析，避免模糊表述，给出具体的观点。
"""
        return prompt
    
    def analyze_stock_with_detailed_prompt(self, stock_code: str, analysis_data: Dict[str, Any]) -> Optional[StockResult]:
        """
        使用AI分析单个股票（使用详细提示词）
        
        Args:
            stock_code: 股票代码
            analysis_data: 分析数据
            
        Returns:
            StockResult对象或None
        """
        try:
            # 构建AI提示词
            prompt = self._build_analysis_prompt(stock_code, analysis_data)
            
            # 使用配置的AI分析器进行分析
            # 优先级：DeepSeek > OpenAI > Gemini
            if self.deepseek_analyzer and self.deepseek_analyzer.is_available():
                self.logger.info(f"使用DeepSeek进行详细分析: {stock_code}")
                
                # 创建临时StockResult用于传递技术指标
                temp_result = StockResult(
                    code=stock_code,
                    name=analysis_data.get('current_data', {}).get('name', ''),
                    current_price=analysis_data.get('current_data', {}).get('now', 0.0),
                    change_percent=analysis_data.get('current_data', {}).get('change_pct', 0.0),
                    sentiment_score=0.5,
                    operation_advice="待AI分析",
                    trend_prediction="待AI分析",
                    technical_indicators=analysis_data.get('indicators', {}),
                    additional_info={}
                )
                
                detailed_analysis = self.deepseek_analyzer.analyze_stock(temp_result)
                
                if detailed_analysis:
                    return detailed_analysis
            elif self.openai_analyzer and self.openai_analyzer.is_available():
                self.logger.info(f"使用OpenAI兼容API进行详细分析: {stock_code}")
                # 类似处理...
            elif self.gemini_analyzer and self.gemini_analyzer.is_available():
                self.logger.info(f"使用Gemini进行详细分析: {stock_code}")
                # 类似处理...
            
            # 如果没有配置任何AI分析器，返回原始数据
            current_data = analysis_data.get('current_data', {})
            indicators = analysis_data.get('indicators', {})
            
            return StockResult(
                code=stock_code,
                name=current_data.get('name', ''),
                current_price=current_data.get('now', 0.0),
                change_percent=current_data.get('change_pct', 0.0),
                sentiment_score=0.5,
                operation_advice="AI分析不可用",
                trend_prediction="AI分析不可用",
                technical_indicators=indicators,
                additional_info={}
            )
            
        except Exception as e:
            self.logger.error(f"详细AI分析股票 {stock_code} 时出错: {e}")
            return None


class CombinedAnalyzer:
    """组合分析器 - 根据配置选择合适的AI分析器"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个AI分析器
        self.gemini_analyzer = None
        self.openai_analyzer = None
        self.deepseek_analyzer = None
        
        # 验证配置
        self.logger.info(f"Gemini API Key 配置: {bool(self.config.GEMINI_API_KEY)}")
        self.logger.info(f"OpenAI API Key 配置: {bool(self.config.OPENAI_API_KEY)}")
        self.logger.info(f"DeepSeek API Key 配置: {bool(self.config.DEEPSEEK_API_KEY)}")
        
        if self.config.GEMINI_API_KEY:
            self.gemini_analyzer = GeminiAnalyzer(
                api_key=self.config.GEMINI_API_KEY,
                model=self.config.GEMINI_MODEL
            )
        
        if self.config.OPENAI_API_KEY:
            self.openai_analyzer = OpenAICompatibleAnalyzer(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_BASE_URL,
                model=self.config.OPENAI_MODEL
            )
        
        if self.config.DEEPSEEK_API_KEY:
            self.logger.info("初始化 DeepSeek 分析器...")
            self.deepseek_analyzer = DeepSeekAnalyzer(
                api_key=self.config.DEEPSEEK_API_KEY,
                base_url=self.config.DEEPSEEK_BASE_URL,
                model=self.config.DEEPSEEK_MODEL
            )
            self.logger.info(f"DeepSeek 分析器已创建: {self.deepseek_analyzer is not None}")
    
    def analyze_stock(self, stock_result: StockResult) -> Optional[StockResult]:
        """使用配置的AI分析器分析股票"""
        # 优先级：DeepSeek > OpenAI > Gemini
        if self.deepseek_analyzer and self.deepseek_analyzer.is_available():
            self.logger.info(f"使用DeepSeek分析股票 {stock_result.code}")
            return self.deepseek_analyzer.analyze_stock(stock_result)
        elif self.openai_analyzer and self.openai_analyzer.is_available():
            self.logger.info(f"使用OpenAI兼容API分析股票 {stock_result.code}")
            return self.openai_analyzer.analyze_stock(stock_result)
        elif self.gemini_analyzer and self.gemini_analyzer.is_available():
            self.logger.info(f"使用Gemini分析股票 {stock_result.code}")
            return self.gemini_analyzer.analyze_stock(stock_result)
        else:
            self.logger.info(f"未配置或不可用的AI分析器，跳过AI分析，使用基础分析结果")
            return stock_result

    def analyze_single_stock(self, code: str) -> Optional[StockResult]:
        """分析单个股票（整合数据获取和AI分析）"""
        try:
            # 使用腾讯数据源获取实时数据
            import importlib.util
            import sys
            import os
            
            # 动态导入tencent_data_source模块
            tencent_module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tencent_data_source.py')
            spec = importlib.util.spec_from_file_location("tencent_data_source", tencent_module_path)
            tencent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tencent_module)
            analyze_stock实时数据 = tencent_module.analyze_stock实时数据
            stock_data = analyze_stock实时数据(code)
            
            if stock_data:
                # 获取历史数据用于技术指标计算
                # 动态导入腾讯数据源实例以获取历史数据
                tencent_source = tencent_module.TencentDataSource()
                history_data = tencent_source.get_history_data(code, days=30)  # 获取30天历史数据
                
                # 使用技术指标模块计算基本技术指标
                historical_prices = [item['close'] for item in history_data] if history_data else []
                basic_indicators = calculate_basic_technical_indicators(
                    current_price=stock_data.get('now', 0.0),
                    historical_data=historical_prices
                )
                
                # 整合技术指标
                technical_indicators = {
                    'volume': stock_data.get('volume', 0),
                    'amount': stock_data.get('amount', 0),
                    'open': stock_data.get('open', 0.0),
                    'high': stock_data.get('high', 0.0),
                    'low': stock_data.get('low', 0.0),
                    'MA5': basic_indicators.get('MA5'),
                    'MA10': basic_indicators.get('MA10'),
                    'MA20': basic_indicators.get('MA20'),
                    'RSI': basic_indicators.get('RSI'),
                    'signal': basic_indicators.get('signal', 'neutral')
                }
                
                # 创建StockResult对象
                stock_result = StockResult(
                    code=code,
                    name=stock_data.get('name', ''),
                    current_price=stock_data.get('now', 0.0),
                    change_percent=stock_data.get('change_pct', 0.0),
                    sentiment_score=0.5,  # 初始情绪分数
                    operation_advice="待分析",  # 待AI分析后更新
                    trend_prediction="待分析",  # 待AI分析后更新
                    technical_indicators=technical_indicators,
                    additional_info={}
                )
                
                # 更新情绪分数和操作建议（基于基础指标）
                if stock_result.change_percent > 3:
                    stock_result.sentiment_score = 0.8
                    stock_result.operation_advice = "谨慎追高"
                elif stock_result.change_percent > 0:
                    stock_result.sentiment_score = 0.6
                    stock_result.operation_advice = "观望"
                elif stock_result.change_percent > -3:
                    stock_result.sentiment_score = 0.4
                    stock_result.operation_advice = "关注机会"
                else:
                    stock_result.sentiment_score = 0.2
                    stock_result.operation_advice = "谨慎"
                
                stock_result.trend_prediction = f"当前涨跌幅{stock_result.change_percent:+.2f}%"
                
                # 使用AI分析器进一步分析
                return self.analyze_stock(stock_result)
            else:
                self.logger.error(f"无法获取股票 {code} 的数据")
                return None
                
        except Exception as e:
            self.logger.error(f"分析股票 {code} 时出错: {e}")
            return None