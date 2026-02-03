#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目路径
sys.path.insert(0, '/home/admin/clawd/daily_stock_analysis')
sys.path.insert(0, '/home/admin/clawd/daily_stock_analysis/src')

# 设置环境变量
from src.config import setup_env
setup_env()

def main():
    try:
        from skills.stock_analysis_skill import StockAnalysisSkill
        skill = StockAnalysisSkill()
        
        # 分析中国黄金股票
        result = skill.analyze_stock_with_ai('600916')
        
        print('=' * 80)
        print('中国黄金(600916) 技术分析报告')
        print('=' * 80)
        print(result)
        
    except Exception as e:
        print(f'执行分析时出错: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()