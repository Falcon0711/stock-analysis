# -*- coding: utf-8 -*-
"""
===================================
A股自选股智能分析系统 - 主入口
===================================

使用方式：
    python -m stock_analysis              # 正常运行
    python -m stock_analysis --debug      # 调试模式
    python -m stock_analysis --dry-run    # 仅获取数据不分析
    python -m stock_analysis --stocks 600519,000001  # 指定股票

交易理念（已融入分析）：
- 严进策略：不追高，乖离率 > 5% 不买入
- 趋势交易：只做 MA5>MA10>MA20 多头排列
- 效率优先：关注筹码集中度好的股票
- 买点偏好：缩量回踩 MA5/MA10 支撑
"""
import os
import sys
import time
import argparse
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Optional

from stock_analysis.config import get_config, Config, setup_env
from stock_analysis.core.pipeline import StockAnalysisPipeline
from stock_analysis.notification import NotificationService
from stock_analysis.core.analyzer import CombinedAnalyzer
from stock_analysis.utils import parse_stock_input
from stock_analysis.constants import (
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_MAX_BYTES,
    DEBUG_LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    DEBUG_LOG_BACKUP_COUNT,
)

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False, log_dir: str = "./logs") -> None:
    """
    配置日志系统
    
    Args:
        debug: 是否启用调试模式
        log_dir: 日志目录
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 日志文件路径
    today_str = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"stock_analysis_{today_str}.log"
    debug_log_file = log_path / f"stock_analysis_debug_{today_str}.log"
    
    # 创建根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 清除现有 handlers
    root_logger.handlers.clear()
    
    # Handler 1: 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    # Handler 2: 常规日志文件
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Handler 3: 调试日志文件
    debug_handler = RotatingFileHandler(
        debug_log_file,
        maxBytes=DEBUG_LOG_MAX_BYTES,
        backupCount=DEBUG_LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(debug_handler)
    
    # 降低第三方库的日志级别
    for lib in ["urllib3", "sqlalchemy", "google", "httpx", "requests"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    logger.info(f"日志系统初始化完成，日志目录: {log_path.absolute()}")


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="A股自选股智能分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m stock_analysis                    # 正常运行
  python -m stock_analysis --debug            # 调试模式
  python -m stock_analysis --dry-run          # 仅获取数据
  python -m stock_analysis --stocks 600519,000001  # 指定股票
  python -m stock_analysis --no-notify        # 不发送通知
        """,
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅获取数据，不进行 AI 分析",
    )
    
    parser.add_argument(
        "--stocks",
        type=str,
        help="指定要分析的股票代码，逗号分隔",
    )
    
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="不发送推送通知",
    )
    
    parser.add_argument(
        "--single-notify",
        action="store_true",
        help="启用单股推送模式",
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="并发线程数",
    )
    
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="启用定时任务模式",
    )
    
    parser.add_argument(
        "--market-review",
        action="store_true",
        help="仅运行大盘复盘分析",
    )
    
    parser.add_argument(
        "--no-market-review",
        action="store_true",
        help="跳过大盘复盘分析",
    )
    
    return parser.parse_args()


def run_full_analysis(
    config: Config,
    args: argparse.Namespace,
    stock_codes: Optional[List[str]] = None,
) -> None:
    """
    执行完整的分析流程
    
    Args:
        config: 配置对象
        args: 命令行参数
        stock_codes: 股票代码列表
    """
    try:
        # 命令行参数覆盖配置
        if getattr(args, "single_notify", False):
            config.notification.single_stock_notify = True
        
        # 创建流水线
        pipeline = StockAnalysisPipeline(
            config=config,
            max_workers=args.workers,
        )
        
        # 运行个股分析
        results = pipeline.run(
            stock_codes=stock_codes,
            dry_run=args.dry_run,
            send_notification=not args.no_notify,
        )
        
        # 输出摘要
        if results:
            logger.info("\n===== 分析结果摘要 =====")
            for r in sorted(results, key=lambda x: x.sentiment_score, reverse=True):
                emoji = r.get_emoji()
                logger.info(
                    f"{emoji} {r.name}({r.code}): {r.operation_advice} | "
                    f"评分 {r.sentiment_score} | {r.trend_prediction}"
                )
        
        logger.info("\n任务执行完成")
        
    except Exception as e:
        logger.exception(f"分析流程执行失败: {e}")


def main() -> int:
    """主入口函数"""
    # 加载环境变量
    setup_env()
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 加载配置
    config = get_config()
    
    # 配置日志
    setup_logging(debug=args.debug, log_dir=config.log_dir)
    
    logger.info("=" * 60)
    logger.info("A股自选股智能分析系统 启动")
    logger.info(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 验证配置
    warnings = config.validate()
    for warning in warnings:
        logger.warning(warning)
    
    # 解析股票列表
    stock_codes = None
    if args.stocks:
        stock_codes = parse_stock_input(args.stocks)
        logger.info(f"使用命令行指定的股票列表: {stock_codes}")
    
    try:
        # 模式1: 定时任务模式
        if args.schedule or config.schedule_enabled:
            logger.info("模式: 定时任务")
            logger.info(f"每日执行时间: {config.schedule_time}")
            
            # TODO: 实现定时任务
            logger.warning("定时任务模式暂未实现")
            return 0
        
        # 模式2: 正常单次运行
        run_full_analysis(config, args, stock_codes)
        
        logger.info("\n程序执行完成")
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n用户中断，程序退出")
        return 130
    except Exception as e:
        logger.exception(f"程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
