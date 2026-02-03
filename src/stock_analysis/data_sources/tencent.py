# -*- coding: utf-8 -*-
"""
腾讯财经数据源模块
提供 A 股实时行情和历史 K 线数据获取功能
"""
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
import pandas as pd
import numpy as np

from stock_analysis.constants import REQUEST_TIMEOUT, DEFAULT_HISTORY_DAYS
from stock_analysis.utils.stock_code import to_tencent_symbol, normalize_stock_code

logger = logging.getLogger(__name__)


class TencentDataSource:
    """腾讯财经数据源"""
    
    # 腾讯 API 端点
    # 注意: 腾讯财经 API 仅支持 HTTP，这是第三方 API 的限制
    REALTIME_URL = "http://qt.gtimg.cn/q={symbols}"
    KLINE_URL = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    
    def __init__(self):
        """初始化数据源"""
        self._session = requests.Session()
        self._session.headers.update(self._get_headers())
    
    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """获取请求头"""
        return {
            "Referer": "http://gu.qq.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }
    
    def _get_symbol(self, code: str) -> str:
        """
        转换股票代码为腾讯格式
        
        Args:
            code: 股票代码
            
        Returns:
            腾讯格式代码 (如 sh600519)
        """
        return to_tencent_symbol(code)
    
    def get_realtime(self, codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        获取 A 股实时行情
        
        Args:
            codes: 股票代码列表
            
        Returns:
            股票代码到行情数据的映射
        """
        if not codes:
            return {}
        
        try:
            tencent_codes = [self._get_symbol(c) for c in codes]
            codes_str = ",".join(tencent_codes)
            url = self.REALTIME_URL.format(symbols=codes_str)
            
            logger.debug(f"请求实时行情: {url}")
            resp = self._session.get(url, timeout=REQUEST_TIMEOUT)
            resp.encoding = "gbk"
            
            return self._parse_realtime(resp.text, codes)
            
        except requests.Timeout:
            logger.error(f"实时行情请求超时: {codes}")
            return {}
        except requests.RequestException as e:
            logger.error(f"实时行情请求失败: {e}")
            return {}
        except Exception as e:
            logger.exception(f"实时行情获取异常: {e}")
            return {}
    
    def _parse_realtime(self, text: str, original_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        解析腾讯实时行情响应
        
        Args:
            text: 响应文本
            original_codes: 原始股票代码列表
            
        Returns:
            解析后的行情数据
        """
        result = {}
        lines = text.strip().split(" ")
        
        for line in lines:
            if "~" not in line:
                continue
            
            try:
                # 提取代码
                code_match = re.search(r"(?<=_)\w+", line)
                if not code_match:
                    continue
                
                full_code = code_match.group()
                pure_code = full_code[2:] if full_code[:2] in ("sh", "sz", "bj") else full_code
                
                # 解析数据 (腾讯用 ~ 分隔)
                if '="' not in line:
                    continue
                    
                data_part = line.split('="')[1].rstrip('";')
                parts = data_part.split("~")
                
                if len(parts) < 45:
                    logger.warning(f"数据字段不足: {pure_code}, 字段数: {len(parts)}")
                    continue
                
                result[pure_code] = {
                    "name": parts[1],
                    "code": parts[2],
                    "now": self._safe_float(parts[3]),
                    "close": self._safe_float(parts[4]),  # 昨收
                    "open": self._safe_float(parts[5]),
                    "volume": self._safe_float(parts[6]),
                    "high": self._safe_float(parts[33]),
                    "low": self._safe_float(parts[34]),
                    "amount": self._safe_float(parts[37]),
                    "change_pct": self._safe_float(parts[32]),
                    "change": self._safe_float(parts[31]),
                }
                
            except (ValueError, IndexError) as e:
                logger.debug(f"解析行情数据失败: {e}")
                continue
        
        return result
    
    @staticmethod
    def _safe_float(value: str) -> float:
        """
        安全转换字符串为浮点数
        
        Args:
            value: 字符串值
            
        Returns:
            浮点数，转换失败返回 0.0
        """
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def get_kline_data(self, code: str, days: int = DEFAULT_HISTORY_DAYS) -> List[Dict[str, Any]]:
        """
        获取 A 股历史 K 线数据
        
        Args:
            code: 股票代码
            days: 获取天数
            
        Returns:
            K 线数据列表
        """
        try:
            symbol = self._get_symbol(code)
            url = f"{self.KLINE_URL}?param={symbol},day,,,{days},qfq"
            
            logger.debug(f"请求 K 线数据: {url}")
            resp = self._session.get(url, timeout=REQUEST_TIMEOUT)
            resp.encoding = "utf-8"
            
            data = resp.json()
            
            if data.get("code") != 0:
                logger.warning(f"K 线数据获取失败: {code}, {data.get('msg', '未知错误')}")
                return []
            
            if "data" not in data or symbol not in data["data"]:
                logger.warning(f"K 线数据为空: {code}")
                return []
            
            stock_data = data["data"][symbol]
            klines = stock_data.get("qfqday") or stock_data.get("day")
            
            if not klines:
                logger.warning(f"K 线数据为空: {code}")
                return []
            
            return self._parse_klines(klines, code)
            
        except requests.Timeout:
            logger.error(f"K 线数据请求超时: {code}")
            return []
        except requests.RequestException as e:
            logger.error(f"K 线数据请求失败: {code}, {e}")
            return []
        except Exception as e:
            logger.exception(f"K 线数据获取异常: {code}, {e}")
            return []
    
    def _parse_klines(self, klines: List, code: str) -> List[Dict[str, Any]]:
        """
        解析 K 线数据
        
        Args:
            klines: 原始 K 线数据
            code: 股票代码
            
        Returns:
            解析后的 K 线数据列表
        """
        result = []
        
        for item in klines:
            # 跳过非 K 线数据（如分红信息）
            if isinstance(item, dict):
                continue
            
            # 检查是否包含字典类型的元素（分红信息等）
            if any(isinstance(element, dict) for element in item):
                continue
            
            if len(item) < 6:
                continue
            
            try:
                date, open_price, close, high, low, volume = item[:6]
                amount = item[6] if len(item) >= 7 else 0.0
                
                # 验证数据类型
                if any(isinstance(v, dict) for v in [date, open_price, close, high, low, volume]):
                    continue
                
                result.append({
                    "date": str(date),
                    "open": self._safe_float(str(open_price)),
                    "close": self._safe_float(str(close)),
                    "high": self._safe_float(str(high)),
                    "low": self._safe_float(str(low)),
                    "volume": self._safe_float(str(volume)),
                    "amount": self._safe_float(str(amount)) if amount else 0.0,
                })
                
            except (ValueError, TypeError) as e:
                logger.debug(f"解析 K 线数据失败: {code}, {e}")
                continue
        
        return result
    
    def get_history_data(self, code: str, days: int = DEFAULT_HISTORY_DAYS) -> List[Dict[str, Any]]:
        """
        获取历史数据（get_kline_data 的别名）
        
        Args:
            code: 股票代码
            days: 获取天数
            
        Returns:
            历史数据列表
        """
        return self.get_kline_data(code, days)
    
    def close(self):
        """关闭会话"""
        self._session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============ 便捷函数 ============

def analyze_stock_realtime(code: str = "002167") -> Optional[Dict[str, Any]]:
    """
    获取并分析股票实时数据
    
    Args:
        code: 股票代码，默认 002167
        
    Returns:
        股票实时数据，获取失败返回 None
    """
    logger.info(f"正在获取 {code} 的实时数据...")
    
    with TencentDataSource() as source:
        result = source.get_realtime([code])
        
        normalized_code = normalize_stock_code(code) or code
        
        if result and normalized_code in result:
            stock_data = result[normalized_code]
            
            logger.info(f"{stock_data['name']} ({code}) 实时数据:")
            logger.info(f"  当前价格: {stock_data['now']:.2f}")
            logger.info(f"  今日开盘: {stock_data['open']:.2f}")
            logger.info(f"  昨日收盘: {stock_data['close']:.2f}")
            logger.info(f"  今日最高: {stock_data['high']:.2f}")
            logger.info(f"  今日最低: {stock_data['low']:.2f}")
            logger.info(f"  成交量: {stock_data['volume']:,.0f}")
            logger.info(f"  涨跌幅: {stock_data['change_pct']:+.2f}%")
            
            return stock_data
        else:
            logger.warning(f"未能获取到 {code} 的数据")
            return None


def analyze_stock_history(code: str = "002167", days: int = DEFAULT_HISTORY_DAYS) -> Optional[List[Dict[str, Any]]]:
    """
    获取并分析股票历史数据
    
    Args:
        code: 股票代码
        days: 历史天数
        
    Returns:
        历史数据列表，获取失败返回 None
    """
    logger.info(f"正在获取 {code} 过去 {days} 天的历史数据...")
    
    with TencentDataSource() as source:
        history_data = source.get_kline_data(code, days)
        
        if not history_data:
            logger.warning(f"未能获取到 {code} 的历史数据")
            return None
        
        logger.info(f"{code} 历史数据概览:")
        logger.info(f"  数据点数量: {len(history_data)}")
        
        if history_data:
            first_day = history_data[0]
            last_day = history_data[-1]
            
            price_change = last_day["close"] - first_day["close"]
            price_change_pct = (price_change / first_day["close"]) * 100
            
            logger.info(f"  期初价格: {first_day['close']:.2f}")
            logger.info(f"  期末价格: {last_day['close']:.2f}")
            logger.info(f"  期间最高: {max(d['high'] for d in history_data):.2f}")
            logger.info(f"  期间最低: {min(d['low'] for d in history_data):.2f}")
            logger.info(f"  价格变化: {price_change:+.2f} ({price_change_pct:+.2f}%)")
            
            # 计算波动率
            closes = [d["close"] for d in history_data]
            if len(closes) > 1:
                returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
                volatility = np.std(returns) * np.sqrt(252)
                logger.info(f"  年化波动率: {volatility:.2%}")
        
        return history_data


# 为了向后兼容，保留中文函数名的别名（但标记为废弃）
def analyze_stock实时数据(code: str = "002167", date_str: str = None) -> Optional[Dict[str, Any]]:
    """
    [已废弃] 请使用 analyze_stock_realtime
    """
    import warnings
    warnings.warn(
        "analyze_stock实时数据 已废弃，请使用 analyze_stock_realtime",
        DeprecationWarning,
        stacklevel=2
    )
    return analyze_stock_realtime(code)


def analyze_stock历史数据(code: str = "002167", days: int = DEFAULT_HISTORY_DAYS) -> Optional[List[Dict[str, Any]]]:
    """
    [已废弃] 请使用 analyze_stock_history
    """
    import warnings
    warnings.warn(
        "analyze_stock历史数据 已废弃，请使用 analyze_stock_history",
        DeprecationWarning,
        stacklevel=2
    )
    return analyze_stock_history(code, days)


if __name__ == "__main__":
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    # 获取命令行参数
    stock_code = sys.argv[1] if len(sys.argv) > 1 else "002167"
    analyze_stock_realtime(stock_code)
