# -*- coding: utf-8 -*-
"""
A股智能分析系统 - 完整主程序

使用方式：
    python -m stock_analysis                       # 使用配置的股票列表
    python -m stock_analysis --stocks 600519,000001 # 指定股票
    python -m stock_analysis --debug               # 调试模式
"""
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import List, Optional

from stock_analysis.config import get_config, Config, setup_env
from stock_analysis.skills import StockAnalysisSkill
from stock_analysis.utils import parse_stock_input
from stock_analysis.constants import (
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
)

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False, log_dir: str = "./logs") -> None:
    """配置日志系统"""
    level = logging.DEBUG if debug else logging.INFO
    
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    today_str = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"stock_analysis_{today_str}.log"
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    # 文件输出
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # 降低第三方库日志级别
    for lib in ["urllib3", "sqlalchemy", "google", "httpx", "requests"]:
        logging.getLogger(lib).setLevel(logging.WARNING)


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="A股智能分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("--debug", action="store_true", help="调试模式")
    parser.add_argument("--stocks", type=str, help="股票代码，逗号分隔")
    parser.add_argument("--ai", action="store_true", help="AI 增强分析")
    parser.add_argument("--output", "-o", type=str, help="输出文件")
    
    return parser.parse_args()


def run_analysis(
    stock_codes: List[str],
    with_ai: bool = False,
    output_file: Optional[str] = None,
) -> int:
    """
    执行股票分析
    
    Args:
        stock_codes: 股票代码列表
        with_ai: 是否使用 AI 分析
        output_file: 输出文件路径
    """
    if not stock_codes:
        logger.warning("没有配置要分析的股票代码")
        return 1
    
    logger.info(f"开始分析 {len(stock_codes)} 只股票: {stock_codes}")
    
    skill = StockAnalysisSkill()
    results = []
    
    for code in stock_codes:
        logger.info(f"正在分析 {code}...")
        try:
            report = skill.analyze_stock_with_ai(code) if with_ai else skill.analyze_stock(code)
            results.append(report)
            print("\n" + report + "\n")
        except Exception as e:
            logger.error(f"分析 {code} 失败: {e}")
            results.append(f"❌ {code} 分析失败: {e}")
    
    # 输出到文件
    if output_file and results:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# A股分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n\n".join(results))
        logger.info(f"报告已保存到: {output_file}")
    
    logger.info(f"分析完成，共 {len(results)} 只股票")
    return 0


def main() -> int:
    """主入口"""
    setup_env()
    args = parse_arguments()
    config = get_config()
    
    setup_logging(debug=args.debug, log_dir=config.log_dir)
    
    logger.info("=" * 60)
    logger.info("A股智能分析系统 启动")
    logger.info(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 验证配置
    warnings = config.validate()
    for warning in warnings:
        logger.warning(warning)
    
    # 解析股票列表
    stock_codes = parse_stock_input(args.stocks) if args.stocks else config.stock_list
    
    if not stock_codes:
        stock_codes = ["600519"]  # 默认
        logger.info("使用默认股票: 600519")
    
    try:
        return run_analysis(
            stock_codes=stock_codes,
            with_ai=args.ai,
            output_file=args.output,
        )
    except KeyboardInterrupt:
        logger.info("\n用户中断")
        return 130
    except Exception as e:
        logger.exception(f"执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
