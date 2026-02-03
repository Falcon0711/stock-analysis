# ⚠️ 本文件必须严格遵循 stock_analysis_skill.md 模板
# - 震荡股阈值：abs(change_pct) <= 5（非 <=2）
# - 报告结构：含 🤖 AI综合分析: 段落
# - 数据源：仅使用 TencentDataSource.get_realtime()

"""
股票技术分析Skill
提供标准化的个股技术分析报告
"""

import sys
import os
import pandas as pd
import requests
import json
from typing import Dict, Any

# 加载环境变量（关键修复）
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from config.config import setup_env
setup_env()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.core.technical_indicators import calculate_all_indicators
from sources.tencent_data_source import TencentDataSource


class StockAnalysisSkill:
    """股票技术分析技能类"""
    
    def __init__(self):
        self.data_source = TencentDataSource()
    
    def analyze_stock(self, stock_code: str) -> str:
        """
        分析单个股票并返回标准化报告
        
        Args:
            stock_code: 股票代码
            
        Returns:
            格式化的分析报告字符串
        """
        # 获取120天历史K线数据
        kline_data = self.data_source.get_kline_data(stock_code, days=120)
        
        if not kline_data:
            return f"❌ 未能获取到 {stock_code} 的历史数据"
        
        # 将数据转换为pandas DataFrame格式
        df = pd.DataFrame(kline_data)
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # 转换数值列为浮点型
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 计算所有技术指标
        result_df = calculate_all_indicators(df)
        
        if result_df is None:
            return f"❌ {stock_code} 技术指标计算失败"
        
        latest = result_df.iloc[-1]
        
        # 获取实时数据
        realtime_data = self.data_source.get_realtime([stock_code])
        if stock_code not in realtime_data:
            return f"❌ 未能获取到 {stock_code} 的实时数据"
        
        current_data = realtime_data[stock_code]
        
        # 根据涨跌幅判断支撑阻力类型 (遵循模板要求)
        change_pct = current_data['change_pct']
        if abs(change_pct) > 5:  # 明显涨跌
            if change_pct > 0:  # 涨幅较大股票 (涨幅>5%)
                support_type = 'MA5'
                support_value = latest['ma5']
                resistance_type = '当日最高价'
                resistance_value = current_data['high']
            else:  # 跌幅较大股票 (跌幅>5%)
                support_type = 'MA20'
                support_value = latest['ma20']
                resistance_type = '开盘价'
                resistance_value = current_data['open']
        elif abs(change_pct) <= 5:  # 震荡股票 (涨跌幅≤5%)
            support_type = 'MA20'
            support_value = latest['ma20']
            resistance_type = 'MA10'
            resistance_value = latest['ma10']
        else:  # 中等波动
            support_type = 'MA10'
            support_value = latest['ma10']
            resistance_type = 'MA5'
            resistance_value = latest['ma5']
        
        # 构建报告
        report = "=" * 65 + "\n"
        report += f"              {current_data['name']}({stock_code}) 技术分析报告\n"
        report += "=" * 65 + "\n"
        
        # 基本信息
        report += f"📈 基本信息: {current_data['name']} | {current_data['code']}\n"
        report += f"💰 当前价格: {current_data['now']:.2f}元 | 涨跌: {current_data['change']:+.2f} | 涨幅: {current_data['change_pct']:+.2f}%\n"
        
        # 技术指标概览
        report += "\n📊 技术指标概览:\n"
        report += f"  KDJ: K={latest['kdj_k']:.2f}, D={latest['kdj_d']:.2f}, J={latest['kdj_j']:.2f} | 信号: {'🔴死叉' if latest['signal_sell_kdj'] else '🟢金叉'}\n"
        report += f"  MACD: {latest['macd']:.3f}, {latest['macd_signal']:.3f}, {latest['macd_hist']:.3f} | 信号: {'🔴空头' if latest['signal_sell_macd'] else '🟢多头'}\n"
        
        # 添加BBI指标 (如果存在)
        if 'bbi' in latest and latest['bbi'] is not None and not pd.isna(latest['bbi']):
            bbi_value = latest['bbi']
            current_price = current_data['now']
            if current_price > bbi_value:
                bbi_position = '上方'
                bbi_status = '🟢多头'
            else:
                bbi_position = '下方'
                bbi_status = '🔴空头'
            report += f"  BBI: {bbi_value:.2f} | 位置: {bbi_position}\n"
        else:
            report += f"  BBI: N/A | 位置: 🟡未知\n"
        
        report += f"  MA5/10/20/60: {latest['ma5']:.2f}/{latest['ma10']:.2f}/{latest['ma20']:.2f}/{latest['ma60']:.2f}\n"
        report += f"  知行指标: 趋势线={latest['zhixing_trend']:.2f} | 位置: {'上方' if current_data['now'] > latest['zhixing_trend'] else '下方'}, 多空线={latest.get('zhixing_multi', 'N/A'):.2f} | 位置: {'上方' if current_data['now'] > latest.get('zhixing_multi', current_data['now']) else '下方'}\n"
        
        # 支撑阻力
        report += "\n🛡️ 支撑阻力:\n"
        report += f"  近期支撑: {support_type}={support_value:.2f} | 近期阻力: {resistance_type}={resistance_value:.2f}\n"
        
        # 综合信号
        report += "\n🎯 综合信号:\n"
        report += f"  买卖建议: {'🔴卖出' if latest['signal_sell'] else '🟢买入' if latest['signal_buy'] else '🟡观望'}\n"
        report += f"  风险等级: {'🔴高' if abs(current_data['change_pct']) > 5 else '🟡中' if abs(current_data['change_pct']) > 2 else '🟢低'}\n"
        
        report += "\n" + "=" * 65 + "\n"
        
        trend_desc = "上涨" if current_data["change_pct"] > 0 else "下跌" if current_data["change_pct"] < 0 else "震荡"
        action = "关注" if current_data["change_pct"] > 0 else "谨慎" if current_data["change_pct"] < 0 else "观望"
        report += f"💡 提示: 今日{trend_desc} {current_data['change_pct']:+.2f}%，{action}操作\n"
        report += "=" * 65
        
        return report
    
    def analyze_stock_with_ai(self, stock_code: str) -> str:
        """
        分析单个股票并返回包含AI综合分析的报告
        
        Args:
            stock_code: 股票代码
            
        Returns:
            格式化的分析报告字符串（包含AI分析）
        """
        # 首先获取标准技术分析
        standard_report = self.analyze_stock(stock_code)
        
        # 获取实时数据用于AI分析
        realtime_data = self.data_source.get_realtime([stock_code])
        if stock_code not in realtime_data:
            ai_part = "\n🤖 AI综合分析: 暂时无法获取实时数据进行AI分析"
        else:
            # 获取120天历史K线数据
            kline_data = self.data_source.get_kline_data(stock_code, days=120)
            
            if not kline_data:
                ai_part = "\n🤖 AI综合分析: 暂时无法获取历史数据进行AI分析"
            else:
                # 准备DataFrame
                df = pd.DataFrame(kline_data)
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 计算技术指标
                result_df = calculate_all_indicators(df)
                
                if result_df is None:
                    ai_part = "\n🤖 AI综合分析: 技术指标计算失败，无法进行AI分析"
                else:
                    latest = result_df.iloc[-1]
                    
                    # 组织分析数据
                    analysis_data = {
                        'current_data': realtime_data[stock_code],
                        'indicators': latest.to_dict(),
                        'historical_data': kline_data
                    }
                    
                    # 使用项目内置的AI分析器
                    try:
                        import sys
                        import os
                        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        sys.path.append(project_root)
                        
                        # 检查是否配置了DeepSeek API密钥
                        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
                        
                        if deepseek_api_key:
                            from models.core.analyzer import AIAnalyzer
                            # 创建AI分析器
                            ai_analyzer = AIAnalyzer()
                            
                            # 准备完整的分析数据
                            full_analysis_data = {
                                'current_data': analysis_data['current_data'],
                                'indicators': {
                                    'volume': analysis_data['current_data'].get('volume', 0),
                                    'amount': analysis_data['current_data'].get('amount', 0),
                                    'open': analysis_data['current_data'].get('open', 0.0),
                                    'high': analysis_data['current_data'].get('high', 0.0),
                                    'low': analysis_data['current_data'].get('low', 0.0),
                                    'MA5': analysis_data['indicators'].get('ma5', 'N/A'),
                                    'MA10': analysis_data['indicators'].get('ma10', 'N/A'),
                                    'MA20': analysis_data['indicators'].get('ma20', 'N/A'),
                                    'MA60': analysis_data['indicators'].get('ma60', 'N/A'),
                                    'KDJ_K': analysis_data['indicators'].get('kdj_k', 'N/A'),
                                    'KDJ_D': analysis_data['indicators'].get('kdj_d', 'N/A'),
                                    'KDJ_J': analysis_data['indicators'].get('kdj_j', 'N/A'),
                                    'MACD': analysis_data['indicators'].get('macd', 'N/A'),
                                    'MACD_Signal': analysis_data['indicators'].get('macd_signal', 'N/A'),
                                    'MACD_Hist': analysis_data['indicators'].get('macd_hist', 'N/A'),
                                    'BBI': analysis_data['indicators'].get('bbi', 'N/A'),
                                    'Zhixing_Trend': analysis_data['indicators'].get('zhixing_trend', 'N/A'),
                                    'Zhixing_Multi': analysis_data['indicators'].get('zhixing_multi', 'N/A')
                                }
                            }
                            
                            # 使用AI分析器进行详细分析
                            analyzed_result = ai_analyzer.analyze_stock_with_detailed_prompt(stock_code, full_analysis_data)
                            
                            if analyzed_result:
                                ai_analysis = analyzed_result.operation_advice
                                ai_part = f"\n\n🤖 AI综合分析:\n{ai_analysis}"
                            else:
                                ai_part = "\n\n🤖 AI综合分析: DeepSeek分析器返回结果为空"
                        else:
                            ai_part = "\n\n🤖 AI综合分析: 未配置DeepSeek API密钥，无法调用AI分析"
                    except ImportError as e:
                        ai_part = f"\n\n🤖 AI综合分析: 未配置DeepSeek API密钥或无法导入分析器 ({str(e)})"
                    except Exception as e:
                        ai_part = f"\n\n🤖 AI综合分析: 调用AI分析器时发生错误: {str(e)}"
        
        # 将AI分析部分添加到标准报告末尾（在最后的分隔线之前）
        lines = standard_report.split('\n')
        if len(lines) > 2:
            # 在倒数第二行前插入AI分析
            final_lines = lines[:-2]  # 除去最后两行（分隔线和提示）
            final_lines.append(ai_part)
            final_lines.extend(lines[-2:])  # 重新添加最后两行
            
            return '\n'.join(final_lines)
        else:
            return standard_report + ai_part
    
    def analyze_multiple_stocks(self, stock_codes: list) -> Dict[str, str]:
        """
        批量分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            字典，键为股票代码，值为对应的分析报告
        """
        results = {}
        for code in stock_codes:
            results[code] = self.analyze_stock(code)
        return results


# 便捷函数
def get_stock_analysis(stock_code: str) -> str:
    """
    便捷函数：获取单个股票分析报告
    
    Args:
        stock_code: 股票代码
        
    Returns:
        分析报告字符串
    """
    skill = StockAnalysisSkill()
    return skill.analyze_stock(stock_code)


def get_stock_analysis_with_ai(stock_code: str) -> str:
    """
    便捷函数：获取单个股票分析报告（包含AI综合分析）
    
    Args:
        stock_code: 股票代码
        
    Returns:
        分析报告字符串（包含AI分析）
    """
    skill = StockAnalysisSkill()
    return skill.analyze_stock_with_ai(stock_code)


def get_multiple_stock_analysis(stock_codes: list) -> Dict[str, str]:
    """
    便捷函数：获取多只股票分析报告
    
    Args:
        stock_codes: 股票代码列表
        
    Returns:
        分析报告字典
    """
    skill = StockAnalysisSkill()
    return skill.analyze_multiple_stocks(stock_codes)


def get_multiple_stock_analysis_with_ai(stock_codes: list) -> Dict[str, str]:
    """
    便捷函数：获取多只股票分析报告（包含AI综合分析）
    
    Args:
        stock_codes: 股票代码列表
        
    Returns:
        分析报告字典（包含AI分析）
    """
    skill = StockAnalysisSkill()
    results = {}
    for code in stock_codes:
        results[code] = skill.analyze_stock_with_ai(code)
    return results