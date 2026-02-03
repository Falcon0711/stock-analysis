# -*- coding: utf-8 -*-
"""
股票分析流水线模块
"""
import logging
import concurrent.futures
from typing import List, Optional

from stock_analysis.core.analyzer import CombinedAnalyzer, StockResult
from stock_analysis.notification import NotificationService
from stock_analysis.constants import DEFAULT_MAX_WORKERS, TASK_TIMEOUT

logger = logging.getLogger(__name__)


class StockAnalysisPipeline:
    """股票分析流水线"""
    
    def __init__(self, config, max_workers: int = None):
        """
        初始化流水线
        
        Args:
            config: 配置对象
            max_workers: 最大并发数，为 None 时使用配置值
        """
        self.config = config
        self.max_workers = max_workers or getattr(config, "max_workers", DEFAULT_MAX_WORKERS)
        self.analyzer = CombinedAnalyzer(config)
        self.notifier = NotificationService(config)
        self.search_service = None  # 搜索服务（可选）
    
    def run(
        self,
        stock_codes: Optional[List[str]] = None,
        dry_run: bool = False,
        send_notification: bool = True,
    ) -> List[StockResult]:
        """
        运行分析流水线
        
        Args:
            stock_codes: 要分析的股票代码列表，为 None 时使用配置中的列表
            dry_run: 是否只获取数据不进行 AI 分析
            send_notification: 是否发送通知
            
        Returns:
            分析结果列表
        """
        codes_to_analyze = stock_codes or self.config.stock_list
        
        if not codes_to_analyze:
            logger.warning("没有配置要分析的股票代码")
            return []
        
        logger.info(f"开始分析 {len(codes_to_analyze)} 只股票: {codes_to_analyze}")
        
        results = []
        
        # 使用线程池并发分析
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_code = {
                executor.submit(self.analyzer.analyze_single_stock, code): code
                for code in codes_to_analyze
            }
            
            for future in concurrent.futures.as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result(timeout=TASK_TIMEOUT)
                    if result:
                        results.append(result)
                        logger.info(f"完成分析: {code} ({result.name})")
                    else:
                        logger.warning(f"分析失败: {code}")
                except concurrent.futures.TimeoutError:
                    logger.error(f"分析 {code} 超时")
                except Exception as e:
                    logger.error(f"分析 {code} 时发生异常: {e}")
        
        logger.info(f"分析完成，成功 {len(results)} 只股票")
        
        # 发送通知
        if results and send_notification and not dry_run:
            self._send_notification(results)
        
        return results
    
    def _send_notification(self, results: List[StockResult]) -> None:
        """发送分析结果通知"""
        try:
            dashboard_report = self.notifier.generate_dashboard_report(results)
            # 发送预览版本（限制长度）
            preview = dashboard_report[:500] + "..." if len(dashboard_report) > 500 else dashboard_report
            self.notifier.send(preview)
        except Exception as e:
            logger.error(f"发送通知时发生错误: {e}")
