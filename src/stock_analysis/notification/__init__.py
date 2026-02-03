# -*- coding: utf-8 -*-
"""
通知服务模块
"""
import logging
from typing import List, Optional

from stock_analysis.core.analyzer import StockResult

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务"""
    
    def __init__(self, config=None):
        """
        初始化通知服务
        
        Args:
            config: 配置对象（可选）
        """
        self.config = config
        self._init_channels()
    
    def _init_channels(self) -> None:
        """初始化通知渠道"""
        # TODO: 根据配置初始化各个通知渠道
        # - 飞书 Webhook
        # - Telegram Bot
        # - 邮件
        # - 钉钉
        pass
    
    def generate_dashboard_report(self, results: List[StockResult]) -> str:
        """
        生成决策仪表盘报告
        
        Args:
            results: 分析结果列表
            
        Returns:
            格式化的报告文本
        """
        if not results:
            return "暂无分析结果"
        
        report_lines = ["# 🚀 个股决策仪表盘\n"]
        
        # 按情绪评分排序
        sorted_results = sorted(results, key=lambda x: x.sentiment_score, reverse=True)
        
        for result in sorted_results:
            emoji = result.get_emoji()
            report_lines.append(f"## {emoji} {result.name} ({result.code})")
            report_lines.append(f"- **当前价格**: {result.current_price:.2f}元")
            report_lines.append(f"- **涨跌幅**: {result.change_percent:+.2f}%")
            report_lines.append(f"- **情绪评分**: {result.sentiment_score:.2f}")
            report_lines.append(f"- **操作建议**: {result.operation_advice}")
            report_lines.append(f"- **趋势预测**: {result.trend_prediction}")
            
            # 技术指标
            tech = result.technical_indicators
            ma5 = tech.get("MA5")
            ma10 = tech.get("MA10")
            ma20 = tech.get("MA20")
            
            if all(v is not None for v in [ma5, ma10, ma20]):
                report_lines.append(
                    f"- **技术指标**: MA5={ma5:.2f}, MA10={ma10:.2f}, MA20={ma20:.2f}"
                )
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def send(self, message: str, channel: str = None) -> bool:
        """
        发送通知
        
        Args:
            message: 消息内容
            channel: 指定通知渠道，为 None 时发送到所有已配置渠道
            
        Returns:
            是否发送成功
        """
        logger.info(f"发送通知: {message[:100]}...")
        
        # TODO: 实际发送到各个渠道
        # 当前仅记录日志
        
        return True
    
    def send_feishu(self, message: str) -> bool:
        """发送飞书通知"""
        if not self.config or not self.config.notification.feishu_webhook_url:
            logger.warning("飞书 Webhook 未配置")
            return False
        
        # TODO: 实现飞书 Webhook 发送
        logger.info(f"发送飞书通知: {message[:50]}...")
        return True
    
    def send_telegram(self, message: str) -> bool:
        """发送 Telegram 通知"""
        if not self.config:
            logger.warning("Telegram 未配置")
            return False
        
        notification_config = self.config.notification
        if not notification_config.telegram_bot_token or not notification_config.telegram_chat_id:
            logger.warning("Telegram Bot Token 或 Chat ID 未配置")
            return False
        
        # TODO: 实现 Telegram 发送
        logger.info(f"发送 Telegram 通知: {message[:50]}...")
        return True
