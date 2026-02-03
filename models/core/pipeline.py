# -*- coding: utf-8 -*-
"""
股票分析流水线
"""
import logging
import concurrent.futures
from typing import List, Optional
from ..core.analyzer import CombinedAnalyzer, StockResult
from ..notification import NotificationService

logger = logging.getLogger(__name__)


class StockAnalysisPipeline:
    """股票分析流水线"""
    
    def __init__(self, config, max_workers: int = None):
        self.config = config
        self.max_workers = max_workers or config.MAX_WORKERS
        self.analyzer = CombinedAnalyzer()
        self.notifier = NotificationService()
        self.search_service = None  # 初始化搜索服务
        self.logger = logging.getLogger(__name__)
    
    def run(self, stock_codes: Optional[List[str]] = None, 
            dry_run: bool = False, 
            send_notification: bool = True) -> List[StockResult]:
        """运行分析流水线"""
        # 确定要分析的股票代码
        codes_to_analyze = stock_codes or self.config.STOCK_LIST
        
        if not codes_to_analyze:
            self.logger.warning("没有配置要分析的股票代码")
            return []
        
        self.logger.info(f"开始分析 {len(codes_to_analyze)} 只股票: {codes_to_analyze}")
        
        results = []
        
        # 使用线程池并发分析
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有分析任务
            future_to_code = {
                executor.submit(self.analyzer.analyze_single_stock, code): code 
                for code in codes_to_analyze
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result(timeout=30)  # 30秒超时
                    if result:
                        results.append(result)
                        self.logger.info(f"完成分析: {code} ({result.name})")
                    else:
                        self.logger.warning(f"分析失败: {code}")
                except Exception as e:
                    self.logger.error(f"分析 {code} 时发生异常: {e}")
        
        self.logger.info(f"分析完成，成功 {len(results)} 只股票")
        
        # 发送通知（如果不是dry run模式）
        if results and send_notification and not dry_run:
            try:
                dashboard_report = self.notifier.generate_dashboard_report(results)
                self.notifier.send(dashboard_report[:500] + "...")  # 发送预览版本
            except Exception as e:
                self.logger.error(f"发送通知时发生错误: {e}")
        
        return results