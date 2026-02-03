# 技术指标计算参考文档

## 概述
技术指标计算模块位于 `stock_analysis_project/models/core/technical_indicators.py`，提供了全面的股票技术分析功能。

## 主要技术指标

### 1. 移动平均线系列
- **SMA (Simple Moving Average)**: 简单移动平均线
- **EMA (Exponential Moving Average)**: 指数移动平均线
- **常用周期**: MA5, MA10, MA20, MA30, MA60

### 2. 震荡指标
- **KDJ随机指标**:
  - K线: 快速随机指标
  - D线: 慢速随机指标
  - J线: 三倍K线减二倍D线
- **RSI (Relative Strength Index)**: 14日相对强弱指标
- **OSC (Oscillator)**: 振荡器指标（范围-50到150）

### 3. 趋势指标
- **MACD (Moving Average Convergence Divergence)**:
  - MACD线: 快线与慢线之差
  - 信号线: MACD线的平滑移动平均
  - 柱状图: MACD线与信号线之差
- **BBI (Bull and Bear Index)**: 多空指标 = (MA3 + MA6 + MA12 + MA24) / 4
- **知行趋势线**: EMA(EMA(C,10),10)
- **知行多空线**: (MA(CLOSE,M1)+MA(CLOSE,M2)+MA(CLOSE,M3)+MA(CLOSE,M4))/4

### 4. 阻力支撑指标
- **布林带 (Bollinger Bands)**: 包含上轨、中轨、下轨

### 5. 买卖信号
- **KDJ金叉死叉**: K线上穿/下穿D线
- **MACD金叉死叉**: MACD线上穿/下穿信号线
- **趋势线突破**: 价格突破趋势线

## 主要函数

### `calculate_all_indicators(data: pd.DataFrame) -> pd.DataFrame`
计算所有技术指标并添加到DataFrame中，是最主要的函数。

**输入**: 包含 date, open, high, low, close, volume 的 DataFrame
**输出**: 添加了所有指标列的 DataFrame

### `calculate_basic_technical_indicators(current_price: float, historical_data: list) -> dict`
为单个股票计算基本技术指标。

## 使用方式

### 在股票分析技能中使用
```python
from models.core.technical_indicators import calculate_all_indicators

# 计算技术指标
result_df = calculate_all_indicators(df)
```

### 在主分析流程中使用
技术指标计算已集成到 `StockAnalysisSkill` 类中，在分析股票时自动计算。

## 数据要求

- **最小数据量**: 至少需要5天数据
- **KDJ**: 需要至少9天数据
- **MACD**: 需要至少26天数据
- **BBI**: 需要至少24天数据
- **RSI**: 需要至少14天数据
- **知行多空线**: 需要至少114天数据

## 计算精度
- 所有指标均基于 Pandas 和 NumPy 计算，保证计算精度
- 使用适当的数值稳定性技术防止溢出

## 集成应用
技术指标已集成到以下模块：
- `agents/skills/stock_analysis_skill.py`: 股票分析技能
- `models/core/analyzer.py`: AI分析器
- `models/core/pipeline.py`: 分析流水线

## 注意事项
1. 指标准确性依赖于高质量的历史数据
2. 不同股票可能需要调整指标参数
3. 技术分析应结合基本面分析使用
4. 指标在不同市场环境下表现可能不同