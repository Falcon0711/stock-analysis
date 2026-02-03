# -*- coding: utf-8 -*-
"""
股票分析技能模块
提供标准化的个股技术分析报告，支持基础分析和 AI 增强分析
"""
import logging
from typing import Dict, Any, Optional

import pandas as pd

from stock_analysis.data_sources import TencentDataSource
from stock_analysis.core.technical_indicators import calculate_all_indicators
from stock_analysis.constants import CHANGE_PCT_HIGH, CHANGE_PCT_MEDIUM

logger = logging.getLogger(__name__)


class StockAnalysisSkill:
    """
    股票技术分析技能类
    
    提供两种分析模式：
    1. 基础技术分析 (analyze_stock)
    2. AI 增强分析 (analyze_stock_with_ai)
    """
    
    def __init__(self):
        self.data_source = TencentDataSource()
    
    def _fetch_data_and_calculate(self, stock_code: str):
        """获取数据并计算技术指标"""
        # 获取 120 天历史 K 线数据
        kline_data = self.data_source.get_kline_data(stock_code, days=120)
        
        if not kline_data:
            return None, None, f"❌ 未能获取到 {stock_code} 的历史数据"
        
        # 转换为 DataFrame
        df = pd.DataFrame(kline_data)
        df = df[["date", "open", "high", "low", "close", "volume"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        
        # 转换数值列
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # 计算技术指标
        result_df = calculate_all_indicators(df)
        
        if result_df is None:
            return None, None, f"❌ {stock_code} 技术指标计算失败"
        
        latest = result_df.iloc[-1]
        
        # 获取实时数据
        realtime_data = self.data_source.get_realtime([stock_code])
        if stock_code not in realtime_data:
            return None, None, f"❌ 未能获取到 {stock_code} 的实时数据"
        
        current_data = realtime_data[stock_code]
        
        return current_data, latest, None

    def analyze_stock(self, stock_code: str) -> str:
        """
        分析单个股票并返回标准化技术分析报告
        """
        current_data, latest, error = self._fetch_data_and_calculate(stock_code)
        if error:
            return error
            
        # 确定支撑阻力
        change_pct = current_data["change_pct"]
        support, resistance = self._get_support_resistance(change_pct, latest, current_data)
        
        # 构建报告
        return self._build_report(stock_code, current_data, latest, support, resistance)
    
    def analyze_stock_with_ai(self, stock_code: str) -> str:
        """
        分析单个股票并返回包含 AI 综合分析的报告
        """
        # 1. 获取基础数据和分析结果
        current_data, latest, error = self._fetch_data_and_calculate(stock_code)
        if error:
            return error
            
        # 2. 生成基础报告
        change_pct = current_data["change_pct"]
        support, resistance = self._get_support_resistance(change_pct, latest, current_data)
        standard_report = self._build_report(stock_code, current_data, latest, support, resistance)
        
        # 3. 准备 AI 分析所需的数据，直接使用已获取的数据
        try:
            from stock_analysis.core.analyzer import CombinedAnalyzer, StockResult
            from stock_analysis.config import get_global_config
            
            config = get_global_config()
            
            # 检查是否配置了 AI API
            has_ai = (config.ai.deepseek_api_key or 
                     config.ai.openai_api_key or 
                     config.ai.gemini_api_key)
            
            if not has_ai:
                ai_analysis = "\n🤖 AI综合分析: 未配置AI API密钥，请设置 DEEPSEEK_API_KEY、OPENAI_API_KEY 或 GEMINI_API_KEY"
            else:
                # 构造传递给 AI 的数据对象
                technical_indicators = {
                    "volume": current_data.get("volume", 0),
                    "amount": current_data.get("amount", 0),
                    "open": current_data.get("open", 0.0),
                    "high": current_data.get("high", 0.0),
                    "low": current_data.get("low", 0.0),
                    # 添加关键技术指标
                    "KDJ_K": latest.get('kdj_k'),
                    "KDJ_D": latest.get('kdj_d'),
                    "KDJ_J": latest.get('kdj_j'),
                    "MACD": latest.get('macd'),
                    "MACD_Signal": latest.get('macd_signal'),
                    "MACD_Hist": latest.get('macd_hist'),
                    "RSI": latest.get('rsi_14'),
                    "BBI": latest.get('bbi'),
                    "MA5": latest.get('ma5'),
                    "MA10": latest.get('ma10'),
                    "MA20": latest.get('ma20'),
                    "MA60": latest.get('ma60'),
                }
                
                # 预先计算情感得分
                sentiment_score, operation_advice = CombinedAnalyzer._calculate_basic_sentiment(change_pct)
                
                stock_result = StockResult(
                    code=stock_code,
                    name=current_data.get("name", ""),
                    current_price=current_data.get("now", 0.0),
                    change_percent=change_pct,
                    sentiment_score=sentiment_score,
                    operation_advice=operation_advice,
                    trend_prediction=f"当前涨跌幅{change_pct:+.2f}%",
                    technical_indicators=technical_indicators,
                )
                
                # 初始化分析器并进行 AI 分析
                analyzer = CombinedAnalyzer(config)
                result = analyzer.analyze_stock(stock_result)
                
                if result and result.operation_advice:
                    # 检查是否只返回了默认建议（即 AI 分析失败）
                    if result.operation_advice.startswith("AI分析:"):
                        ai_analysis = f"\n\n🤖 AI综合分析:\n{result.operation_advice}"
                    else:
                        # 如果没有 AI 前缀，可能是分析失败回退到了基础建议
                        ai_analysis = f"\n\n🤖 AI综合分析: (AI服务响应异常，显示基础建议)\n{result.operation_advice}"
                else:
                    ai_analysis = "\n\n🤖 AI综合分析: AI 分析未返回结果"

        except Exception as e:
            logger.error(f"AI 分析过程出错: {e}")
            ai_analysis = f"\n\n🤖 AI综合分析: 分析过程出错 ({e})"
        
        # 4. 组合报告
        return standard_report + "\n" + ai_analysis
    
    def _get_support_resistance(
        self,
        change_pct: float,
        latest: pd.Series,
        current_data: dict
    ) -> tuple:
        """
        根据涨跌幅确定支撑阻力位
        
        Returns:
            ((支撑类型, 支撑值), (阻力类型, 阻力值))
        """
        if abs(change_pct) > CHANGE_PCT_HIGH:
            if change_pct > 0:  # 大涨
                return ("MA5", latest["ma5"]), ("当日最高价", current_data["high"])
            else:  # 大跌
                return ("MA20", latest["ma20"]), ("开盘价", current_data["open"])
        elif abs(change_pct) <= CHANGE_PCT_MEDIUM:  # 震荡
            return ("MA20", latest["ma20"]), ("MA10", latest["ma10"])
        else:  # 中等波动
            return ("MA10", latest["ma10"]), ("MA5", latest["ma5"])
    
    def _build_report(
        self,
        stock_code: str,
        current_data: dict,
        latest: pd.Series,
        support: tuple,
        resistance: tuple,
    ) -> str:
        """构建技术分析报告"""
        support_type, support_value = support
        resistance_type, resistance_value = resistance
        
        report = "=" * 65 + "\n"
        report += f"              {current_data['name']}({stock_code}) 技术分析报告\n"
        report += "=" * 65 + "\n"
        
        # 基本信息
        report += f"📈 基本信息: {current_data['name']} | {current_data['code']}\n"
        report += f"💰 当前价格: {current_data['now']:.2f}元 | 涨跌: {current_data['change']:+.2f} | 涨幅: {current_data['change_pct']:+.2f}%\n"
        
        # 技术指标
        report += "\n📊 技术指标概览:\n"
        
        # KDJ
        kdj_signal = "🔴死叉" if latest.get("signal_sell_kdj", False) else "🟢金叉"
        report += f"  KDJ: K={latest['kdj_k']:.2f}, D={latest['kdj_d']:.2f}, J={latest['kdj_j']:.2f} | 信号: {kdj_signal}\n"
        
        # MACD
        macd_signal = "🔴空头" if latest.get("signal_sell_macd", False) else "🟢多头"
        report += f"  MACD: {latest['macd']:.3f}, {latest['macd_signal']:.3f}, {latest['macd_hist']:.3f} | 信号: {macd_signal}\n"
        
        # BBI
        if "bbi" in latest and pd.notna(latest["bbi"]):
            bbi_position = "上方" if current_data["now"] > latest["bbi"] else "下方"
            report += f"  BBI: {latest['bbi']:.2f} | 位置: {bbi_position}\n"
        else:
            report += "  BBI: N/A\n"
        
        # 均线
        ma60_value = latest.get("ma60", 0)
        ma60_str = f"{ma60_value:.2f}" if pd.notna(ma60_value) else "N/A"
        report += f"  MA5/10/20/60: {latest['ma5']:.2f}/{latest['ma10']:.2f}/{latest['ma20']:.2f}/{ma60_str}\n"
        
        # 知行指标
        trend_pos = "上方" if current_data["now"] > latest["zhixing_trend"] else "下方"
        zhixing_multi = latest.get("zhixing_multi")
        if pd.notna(zhixing_multi):
            multi_pos = "上方" if current_data["now"] > zhixing_multi else "下方"
            report += f"  知行指标: 趋势线={latest['zhixing_trend']:.2f} | 位置: {trend_pos}, 多空线={zhixing_multi:.2f} | 位置: {multi_pos}\n"
        else:
            report += f"  知行指标: 趋势线={latest['zhixing_trend']:.2f} | 位置: {trend_pos}\n"
        
        # 支撑阻力
        report += "\n🛡️ 支撑阻力:\n"
        report += f"  近期支撑: {support_type}={support_value:.2f} | 近期阻力: {resistance_type}={resistance_value:.2f}\n"
        
        # 综合信号
        report += "\n🎯 综合信号:\n"
        
        if latest.get("signal_sell", False):
            signal = "🔴卖出"
        elif latest.get("signal_buy", False):
            signal = "🟢买入"
        else:
            signal = "🟡观望"
        report += f"  买卖建议: {signal}\n"
        
        change_pct = current_data["change_pct"]
        if abs(change_pct) > CHANGE_PCT_HIGH:
            risk = "🔴高"
        elif abs(change_pct) > CHANGE_PCT_MEDIUM:
            risk = "🟡中"
        else:
            risk = "🟢低"
        report += f"  风险等级: {risk}\n"
        
        report += "\n" + "=" * 65 + "\n"
        
        trend_desc = "上涨" if change_pct > 0 else "下跌" if change_pct < 0 else "震荡"
        action = "关注" if change_pct > 0 else "谨慎" if change_pct < 0 else "观望"
        report += f"💡 提示: 今日{trend_desc} {change_pct:+.2f}%，{action}操作\n"
        report += "=" * 65
        
        return report
    
    def analyze_multiple_stocks(self, stock_codes: list, with_ai: bool = False) -> Dict[str, str]:
        """
        批量分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            with_ai: 是否包含 AI 分析
            
        Returns:
            股票代码到分析报告的映射
        """
        results = {}
        for code in stock_codes:
            if with_ai:
                results[code] = self.analyze_stock_with_ai(code)
            else:
                results[code] = self.analyze_stock(code)
        return results


# ============ 便捷函数 ============

def get_stock_analysis(stock_code: str) -> str:
    """获取单个股票分析报告"""
    skill = StockAnalysisSkill()
    return skill.analyze_stock(stock_code)


def get_stock_analysis_with_ai(stock_code: str) -> str:
    """获取单个股票分析报告（包含 AI 分析）"""
    skill = StockAnalysisSkill()
    return skill.analyze_stock_with_ai(stock_code)


def get_multiple_stock_analysis(stock_codes: list, with_ai: bool = False) -> Dict[str, str]:
    """获取多只股票分析报告"""
    skill = StockAnalysisSkill()
    return skill.analyze_multiple_stocks(stock_codes, with_ai=with_ai)
