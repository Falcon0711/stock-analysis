# -*- coding: utf-8 -*-
"""
大盘复盘分析模块
"""
import logging
from datetime import datetime
from typing import Optional

from src.notification import NotificationService
from src.core.analyzer import CombinedAnalyzer
from tencent_data_source import analyze_stock实时数据


def run_market_review(notifier: Optional[NotificationService] = None, 
                     analyzer: Optional[CombinedAnalyzer] = None, 
                     search_service = None, 
                     send_notification: bool = True):
    """
    运行大盘复盘分析
    """
    logger = logging.getLogger(__name__)
    logger.info("执行大盘复盘分析...")
    
    # 获取当前时间
    now = datetime.now()
    
    # 获取主要指数数据
    # 根据测试结果，以下代码是准确的指数数据
    major_indices = {
        '上证指数': '000001',
        '深证成指': '399001',
        '创业板指': '399006',
        '沪深300': '399300'
    }
    
    indices_data = {}
    for name, code in major_indices.items():
        try:
            data = analyze_stock实时数据(code)
            if data:
                indices_data[name] = data
        except Exception as e:
            logger.warning(f"获取{name}({code})数据失败: {e}")
    
    # 尝试获取科创50指数 - 根据您提供的信息，科创50代码可能是1B0688
    # 但由于当前数据源限制，可能无法获取到正确的科创50数据
    try:
        data = analyze_stock实时数据('1B0688')
        if data and '科创' in data.get('name', ''):
            indices_data['科创50'] = data
            logger.info("成功获取科创50指数数据")
        else:
            # 再次尝试一些可能的代码
            alternative_codes = ['000688', '931643', '931644']  # 尝试几个可能的代码
            for alt_code in alternative_codes:
                try:
                    alt_data = analyze_stock实时数据(alt_code)
                    if alt_data and '科创' in alt_data.get('name', ''):
                        indices_data['科创50'] = alt_data
                        logger.info(f"通过替代代码 {alt_code} 获取科创50指数数据")
                        break
                except:
                    continue
            else:
                logger.info("当前数据源中未找到科创50指数数据")
    except Exception as e:
        logger.warning(f"获取科创50数据失败: {e}")
    
    # 构建大盘复盘报告
    report = f"""# 📈 A股大盘复盘报告
**日期**: {now.strftime('%Y年%m月%d日 %H:%M')}

## 📊 主要指数表现"""
    
    for name, data in indices_data.items():
        price = data.get('now', 0)
        change_pct = data.get('change_pct', 0)
        change_amount = data.get('change_amount', 0)
        volume = data.get('volume', 0)
        
        # 根据涨跌幅确定颜色
        if change_pct > 0:
            emoji = "🟢"
        elif change_pct < 0:
            emoji = "🔴"
        else:
            emoji = "🟡"
        
        report += f"""
- {emoji} **{name}**: {price:.2f} ({change_pct:+.2f}% / {change_amount:+.2f})"""

    # 获取市场概况数据
    total_volume = sum([data.get('volume', 0) for data in indices_data.values()])
    report += f"""
    
## 🔄 市场概况
- 今日两市成交量: {total_volume:,}手
- 涨跌家数比: 数据获取中
- 北向资金: 数据获取中

## 🔥 热点板块
- 领涨板块: 数据获取中
- 领跌板块: 数据获取中
"""
    
    # 使用AI分析器进行市场分析
    if analyzer:
        try:
            ai_analysis_prompt = f"""
请对当前A股市场情况进行专业分析：

主要指数表现:
"""
            for name, data in indices_data.items():
                price = data.get('now', 0)
                change_pct = data.get('change_pct', 0)
                change_amount = data.get('change_amount', 0)
                ai_analysis_prompt += f"- {name}: {price:.2f}, 涨跌幅 {change_pct:+.2f}% ({change_amount:+.2f})\n"
            
            ai_analysis_prompt += f"""
市场概况:
- 两市总成交量: {total_volume:,}手

请提供:
1. 市场情绪判断
2. 技术面分析
3. 主力资金可能流向
4. 短期走势预测
5. 风险提示
6. 投资建议
"""
            
            # 创建一个虚拟的StockResult来进行分析
            from src.core.analyzer import StockResult
            virtual_result = StockResult(
                code="MARKET_OVERVIEW",
                name="A股市场概览",
                current_price=0,
                change_percent=0,
                sentiment_score=0.5,
                operation_advice="等待AI分析",
                trend_prediction="等待AI分析",
                technical_indicators={},
                additional_info={"ai_analysis_prompt": ai_analysis_prompt}
            )
            
            analyzed_result = analyzer.analyze_stock(virtual_result)
            
            if analyzed_result:
                report += f"""
## 💡 AI市场分析
{analyzed_result.operation_advice}

**趋势预测**: {analyzed_result.trend_prediction}
"""
            else:
                report += f"""
## 💡 市场分析
- 市场情绪: 待AI分析
- 技术面分析: 待AI分析
- 短期预测: 待AI分析
"""
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            report += f"""
## 💡 市场分析
- 市场情绪: 待AI分析
- 技术面分析: 待AI分析
- 短期预测: 待AI分析
"""
    else:
        report += f"""
## 💡 市场分析
- 市场情绪: 待AI分析
- 技术面分析: 待AI分析
- 短期预测: 待AI分析
"""
    
    report += f"""
## ⚠️ 风险提示
- 市场波动风险
- 政策变化风险
- 国际环境影响

---
*本报告基于腾讯财经实时数据生成于 {now.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    logger.info("大盘复盘分析完成")
    
    # 发送通知
    if notifier and send_notification:
        try:
            notifier.send("大盘复盘分析已完成")
        except Exception as e:
            logger.error(f"发送大盘复盘通知失败: {e}")
    
    return report