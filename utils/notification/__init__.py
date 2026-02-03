# -*- coding: utf-8 -*-
"""
通知服务模块
"""
import logging
from typing import List
from ..core.analyzer import StockResult

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_dashboard_report(self, results: List[StockResult]) -> str:
        """生成决策仪表盘报告"""
        report_lines = []
        report_lines.append("# 🚀 个股决策仪表盘\n")
        
        for result in sorted(results, key=lambda x: x.sentiment_score, reverse=True):
            emoji = result.get_emoji()
            report_lines.append(f"## {emoji} {result.name} ({result.code})")
            report_lines.append(f"- **当前价格**: {result.current_price:.2f}元")
            report_lines.append(f"- **涨跌幅**: {result.change_percent:+.2f}%")
            report_lines.append(f"- **情绪评分**: {result.sentiment_score:.2f}")
            report_lines.append(f"- **操作建议**: {result.operation_advice}")
            report_lines.append(f"- **趋势预测**: {result.trend_prediction}")
            
            # 技术指标
            tech = result.technical_indicators
            if 'MA5' in tech:
                report_lines.append(f"- **技术指标**: MA5={tech['MA5']:.2f}, MA10={tech['MA10']:.2f}, MA20={tech['MA20']:.2f}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def send(self, message: str):
        """发送通知（这里简化为日志记录）"""
        self.logger.info(f"通知发送: {message}")
        # 在实际实现中，这里会集成飞书、Telegram、邮件等通知渠道