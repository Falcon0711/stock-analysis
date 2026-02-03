# coding:utf8
"""
使用腾讯财经数据源进行股票分析
"""
import re
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import requests

class TencentDataSource:
    """腾讯财经数据源"""
    
    def __init__(self):
        self._session = requests.Session()

    def _get_headers(self) -> dict:
        return {
            "Referer": "http://gu.qq.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _get_symbol(self, code: str) -> str:
        """转换A股代码为腾讯格式"""
        if code.startswith(("sh", "sz", "bj")):
            return code
        # 处理上证指数特殊代码
        if code == "1A0001":
            return "sh000001"
        # 特殊处理指数代码
        if code in ["000001", "000300"]:
            return "sh" + code
        if code in ["399001", "399006", "399005"]:
            return "sz" + code
        if code.startswith(("5", "6", "9")):
            return "sh" + code
        elif code.startswith(("4", "8")):
            return "bj" + code
        else:
            return "sz" + code

    def get_realtime(self, codes: list) -> dict:
        """获取A股实时行情"""
        try:
            tencent_codes = [self._get_symbol(c) for c in codes]
            codes_str = ",".join(tencent_codes)
            url = f"http://qt.gtimg.cn/q={codes_str}"
            resp = self._session.get(url, headers=self._get_headers(), timeout=10)
            resp.encoding = 'gbk'
            return self._parse_realtime(resp.text, codes)
        except Exception as e:
            print(f"[腾讯] 实时行情获取失败: {e}")
            return {}

    def _parse_realtime(self, text: str, original_codes: list) -> dict:
        """解析腾讯实时行情"""
        result = {}
        lines = text.strip().split(' ')
        for line in lines:
            if '~' not in line:
                continue
            try:
                # 提取代码
                code_match = re.compile(r"(?<=_)\w+").search(line)
                if not code_match:
                    continue
                full_code = code_match.group()
                pure_code = full_code[2:] if full_code[:2] in ('sh', 'sz', 'bj') else full_code

                # 解析数据 (腾讯用~分隔)
                data_part = line.split('="')[1].rstrip('";') if '="' in line else ""
                parts = data_part.split('~')
                if len(parts) < 45:
                    continue

                def safe_float(s):
                    try:
                        return float(s) if s else 0.0
                    except (ValueError, TypeError):
                        return 0.0

                result[pure_code] = {
                    'name': parts[1],
                    'code': parts[2],
                    'now': safe_float(parts[3]),
                    'close': safe_float(parts[4]),  # 昨收
                    'open': safe_float(parts[5]),
                    'volume': safe_float(parts[6]),
                    'high': safe_float(parts[33]),
                    'low': safe_float(parts[34]),
                    'amount': safe_float(parts[37]),
                    'change_pct': safe_float(parts[32]),
                    'change': safe_float(parts[31]),
                }
            except (ValueError, IndexError, KeyError):
                continue
        return result

    def get_kline_data(self, code: str, days: int = 30) -> list:
        """
        获取A股历史K线数据
        :param code: 股票代码
        :param days: 获取天数
        :return: K线数据列表
        """
        try:
            symbol = self._get_symbol(code)
            # 使用正确的腾讯K线API端点
            url = f"http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={symbol},day,,,{days},qfq"
            resp = self._session.get(url, headers=self._get_headers(), timeout=10)
            resp.encoding = 'utf-8'
            
            data = resp.json()
            if data['code'] == 0 and 'data' in data and symbol in data['data']:
                stock_data = data['data'][symbol]
                klines = stock_data.get('qfqday', stock_data.get('day'))  # 优先使用前复权数据
                
                if klines:
                    result = []
                    for item in klines:
                        # 检查是否是正常的K线数据（包含价格信息）而不是分红信息
                        if isinstance(item, dict):
                            # 跳过分红等非K线数据
                            continue
                        # 检查是否包含字典类型的元素（分红信息等）
                        has_dict_element = any(isinstance(element, dict) for element in item)
                        if has_dict_element:
                            continue
                        if len(item) >= 6:
                            date, open_price, close, high, low, volume = item[:6]
                            # 如果数据不足6个元素，补充默认值
                            if len(item) < 7:
                                amount = 0.0  # 成交额可能不存在
                            else:
                                amount = item[6]
                            
                            # 检查是否有字典类型的值
                            if not all(not isinstance(v, dict) for v in [date, open_price, close, high, low, volume]):
                                continue
                            
                            result.append({
                                'date': str(date),
                                'open': float(str(open_price)) if str(open_price) != '' and str(open_price) != 'None' else 0.0,
                                'close': float(str(close)) if str(close) != '' and str(close) != 'None' else 0.0,
                                'high': float(str(high)) if str(high) != '' and str(high) != 'None' else 0.0,
                                'low': float(str(low)) if str(low) != '' and str(low) != 'None' else 0.0,
                                'volume': float(str(volume)) if str(volume) != '' and str(volume) != 'None' else 0.0,
                                'amount': float(str(amount)) if str(amount) != '' and str(amount) != 'None' and amount is not None else 0.0
                            })
                    return result
                else:
                    print(f"[腾讯] {code} K线数据为空")
                    return []
            else:
                print(f"[腾讯] {code} K线数据获取失败: {data.get('msg', '未知错误')}")
                return []
        except Exception as e:
            print(f"[腾讯] K线数据获取异常: {e}")
            return []

    def get_history_data(self, code: str, days: int = 30) -> list:
        """
        获取历史数据
        :param code: 股票代码
        :param days: 获取天数
        :return: 历史数据列表
        """
        return self.get_kline_data(code, days)

# 获取指定股票的实时数据
def analyze_stock实时数据(code='002167', date_str='2026-01-30'):
    """
    使用腾讯财经数据源分析股票
    """
    print(f"正在使用腾讯财经数据源分析 {code} ...")
    
    # 创建腾讯数据源实例
    tencent_source = TencentDataSource()
    
    try:
        # 获取实时数据
        result = tencent_source.get_realtime([code])
        
        if result and code in result:
            stock_data = result[code]
            
            print(f"{stock_data['name']} ({code}) 实时数据:")
            print(f"当前价格: {stock_data['now']:.2f}")
            print(f"今日开盘: {stock_data['open']:.2f}")
            print(f"昨日收盘: {stock_data['close']:.2f}")
            print(f"今日最高: {stock_data['high']:.2f}")
            print(f"今日最低: {stock_data['low']:.2f}")
            print(f"成交量: {stock_data['volume']:,.0f}")
            print(f"成交额: {stock_data['amount']:,.0f}")
            print(f"涨跌幅: {stock_data['change_pct']:+.2f}%")
            print(f"涨跌额: {stock_data['change']:+.2f}")
            
            # 提供简要分析
            if stock_data['change_pct'] > 0:
                trend = "上涨"
            elif stock_data['change_pct'] < 0:
                trend = "下跌"
            else:
                trend = "平盘"
            
            print(f"\n简要分析: 今日{trend} {abs(stock_data['change_pct']):.2f}%")
            
            if stock_data['change_pct'] < -3:
                print("风险提示: 当日跌幅较大，请注意风险")
            elif stock_data['change_pct'] > 3:
                print("注意: 当日涨幅较大，谨防回调")
            
            return stock_data
        else:
            print(f"未能获取到 {code} 的数据")
            return None
            
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None

# 分析股票历史数据
def analyze_stock历史数据(code='002167', days=30):
    """
    使用腾讯财经数据源分析股票历史数据
    """
    print(f"正在使用腾讯财经数据源分析 {code} 过去 {days} 天的历史数据...")
    
    # 创建腾讯数据源实例
    tencent_source = TencentDataSource()
    
    try:
        # 获取历史数据
        history_data = tencent_source.get_history_data(code, days)
        
        if history_data:
            print(f"\n{code} 过去 {days} 天历史数据概览:")
            print(f"数据点数量: {len(history_data)}")
            
            if len(history_data) > 0:
                first_day = history_data[0]
                last_day = history_data[-1]
                
                print(f"期初价格: {first_day['close']:.2f}")
                print(f"期末价格: {last_day['close']:.2f}")
                print(f"期间最高: {max(data['high'] for data in history_data):.2f}")
                print(f"期间最低: {min(data['low'] for data in history_data):.2f}")
                
                price_change = last_day['close'] - first_day['close']
                price_change_pct = (price_change / first_day['close']) * 100
                print(f"价格变化: {price_change:+.2f} ({price_change_pct:+.2f}%)")
                
                avg_volume = sum(data['volume'] for data in history_data) / len(history_data)
                print(f"平均成交量: {avg_volume:,.0f}")
                
                # 计算波动率
                import numpy as np
                closes = [data['close'] for data in history_data]
                if len(closes) > 1:
                    returns = [((closes[i] - closes[i-1]) / closes[i-1]) for i in range(1, len(closes))]
                    volatility = np.std(returns) * np.sqrt(252) if returns else 0
                    print(f"年化波动率: {volatility:.2%}")
                
                # 显示最近几天的详细数据
                print(f"\n最近5个交易日详情:")
                for data in history_data[-5:]:
                    print(f"{data['date']}: 开{data['open']:.2f}, 收{data['close']:.2f}, "
                          f"高{data['high']:.2f}, 低{data['low']:.2f}, 量{data['volume']:,.0f}")
                
                # 简单趋势判断
                recent_close = [data['close'] for data in history_data[-5:]]
                if len(recent_close) >= 3:
                    if recent_close[-1] > recent_close[-2] > recent_close[-3]:
                        trend = "近期呈上升趋势"
                    elif recent_close[-1] < recent_close[-2] < recent_close[-3]:
                        trend = "近期呈下降趋势"
                    else:
                        trend = "近期震荡调整"
                    print(f"\n趋势判断: {trend}")
                
            return history_data
        else:
            print(f"未能获取到 {code} 过去 {days} 天的历史数据")
            return None
            
    except Exception as e:
        print(f"获取历史数据时出错: {e}")
        return None

# 执行分析
if __name__ == "__main__":
    import sys
    # 如果命令行传入了参数，则使用传入的股票代码，否则默认使用002167
    stock_code = sys.argv[1] if len(sys.argv) > 1 else '002167'
    analyze_stock实时数据(stock_code)