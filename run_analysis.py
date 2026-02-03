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
    for lib in ["urllib3", "requests", "google", "httpx"]:
        logging.getLogger(lib).setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="A股智能分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_analysis.py 600519                # 分析贵州茅台
  python run_analysis.py 600519 000001 300750  # 分析多只股票
  python run_analysis.py 600519 --ai           # 包含 AI 分析
  python run_analysis.py --list                # 使用配置的股票列表
        """,
    )
    
    parser.add_argument("stocks", nargs="*", help="股票代码，可以指定多个")
    parser.add_argument("--ai", action="store_true", help="启用 AI 增强分析")
    parser.add_argument("--list", action="store_true", dest="use_config_list", help="使用配置中的股票列表")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("-o", "--output", type=str, help="输出到文件")
    
    return parser.parse_args()


def main() -> int:
    """主函数"""
    args = parse_args()
    setup_logging(args.debug)
    
    logger = logging.getLogger(__name__)
    
    # 加载环境变量和配置
    from stock_analysis.config import setup_env, get_config
    setup_env()
    config = get_config()
    
    # 确定要分析的股票列表
    raw_inputs = []
    if args.use_config_list:
        raw_inputs = config.stock_list
        if not raw_inputs:
            logger.error("配置中没有股票列表，请设置 STOCK_LIST 环境变量")
            return 1
    elif args.stocks:
        raw_inputs = args.stocks
    else:
        raw_inputs = ["600519"]  # 默认：贵州茅台
        logger.info("未指定股票代码，使用默认: 600519 (贵州茅台)")
    
    # 解析股票代码（支持中文名称）
    from stock_analysis.data import get_stock_code
    stock_codes = []
    
    for item in raw_inputs:
        # 如果是 6 位数字，直接使用
        if item.isdigit() and len(item) == 6:
            stock_codes.append(item)
        else:
            # 尝试通过名称查找
            code = get_stock_code(item)
            if code:
                logger.info(f"解析股票名称: '{item}' -> {code}")
                stock_codes.append(code)
            else:
                logger.warning(f"无法识别股票: '{item}'，已跳过")
    
    if not stock_codes:
        logger.error("没有有效的股票代码，请检查输入")
        return 1
    
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
            report = skill.analyze_stock_with_ai(code) if args.ai else skill.analyze_stock(code)
            results.append(report)
            print("\n" + report + "\n")
        except Exception as e:
            logger.error(f"分析 {code} 时发生错误: {e}")
            results.append(f"❌ {code} 分析失败: {e}")
    
    # 输出到文件
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"# A股分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n\n".join(results))
        logger.info(f"报告已保存到: {args.output}")
    
    logger.info("\n分析完成！")
    return 0


if __name__ == "__main__":
    sys.exit(main())
