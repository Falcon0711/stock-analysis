#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股智能分析系统 - 快速分析脚本

使用方式：
    python run_analysis.py 600519           # 分析单只股票
    python run_analysis.py 600519 000001    # 分析多只股票
    python run_analysis.py 600519 --ai      # 包含 AI 分析
    python run_analysis.py --list           # 使用配置的股票列表
"""
import sys
import os
import argparse
import logging
from datetime import datetime

# 添加 src 到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


def setup_logging(debug: bool = False) -> None:
    """配置日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # 降低第三方库日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="A股智能分析系统 - 快速分析脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_analysis.py 600519                # 分析贵州茅台
  python run_analysis.py 600519 000001 300750  # 分析多只股票
  python run_analysis.py 600519 --ai           # 包含 AI 分析
  python run_analysis.py --list                # 使用配置的股票列表
  python run_analysis.py --list --ai           # 配置列表 + AI 分析
        """,
    )
    
    parser.add_argument(
        "stocks",
        nargs="*",
        help="股票代码，可以指定多个",
    )
    
    parser.add_argument(
        "--ai",
        action="store_true",
        help="启用 AI 增强分析",
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        dest="use_config_list",
        help="使用配置文件中的股票列表",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式",
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="输出到文件（可选）",
    )
    
    return parser.parse_args()


def main() -> int:
    """主函数"""
    args = parse_args()
    setup_logging(args.debug)
    
    logger = logging.getLogger(__name__)
    
    # 加载环境变量
    from stock_analysis.config import setup_env, get_config
    setup_env()
    
    config = get_config()
    
    # 确定要分析的股票列表
    stock_codes = []
    
    if args.use_config_list:
        stock_codes = config.stock_list
        if not stock_codes:
            logger.error("配置中没有股票列表，请设置 STOCK_LIST 环境变量")
            return 1
        logger.info(f"使用配置的股票列表: {stock_codes}")
    elif args.stocks:
        stock_codes = args.stocks
    else:
        # 默认分析一只股票作为示例
        stock_codes = ["600519"]  # 贵州茅台
        logger.info("未指定股票代码，使用默认: 600519 (贵州茅台)")
    
    # 导入分析技能
    from stock_analysis.skills import StockAnalysisSkill
    
    skill = StockAnalysisSkill()
    
    logger.info("=" * 60)
    logger.info(f"A股智能分析系统 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"分析模式: {'AI 增强分析' if args.ai else '基础技术分析'}")
    logger.info(f"分析股票: {', '.join(stock_codes)}")
    logger.info("=" * 60)
    
    results = []
    
    for code in stock_codes:
        logger.info(f"\n正在分析 {code}...")
        
        try:
            if args.ai:
                report = skill.analyze_stock_with_ai(code)
            else:
                report = skill.analyze_stock(code)
            
            results.append(report)
            print("\n" + report + "\n")
            
        except Exception as e:
            logger.error(f"分析 {code} 时发生错误: {e}")
            results.append(f"❌ {code} 分析失败: {e}")
    
    # 输出到文件（如果指定）
    if args.output:
        output_content = "\n\n".join(results)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"# A股分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(output_content)
        logger.info(f"报告已保存到: {args.output}")
    
    logger.info("\n分析完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
