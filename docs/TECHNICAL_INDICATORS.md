# 技术指标模块说明

## 概述
本项目新增了全面的技术指标计算模块，提供专业的股票技术分析功能。

## 模块位置
- **文件**: `src/core/technical_indicators.py`
- **功能**: 计算各类技术指标，支持KDJ、MACD、RSI、均线等多种指标

## 支持的技术指标

### 1. 移动平均线系列
- **SMA (Simple Moving Average)**: 简单移动平均线
- **EMA (Exponential Moving Average)**: 指数移动平均线
- **MA5/MA10/MA20/MA30/MA60**: 不同期限的移动平均线

### 2. 震荡指标
- **KDJ**: 随机指标，包含K、D、J三条线
- **RSI (Relative Strength Index)**: 相对强弱指标
- **OSC (Oscillator)**: 振荡器指标

### 3. 趋势指标
- **MACD (Moving Average Convergence Divergence)**: 指数平滑异同移动平均线
- **BBI (Bull and Bear Index)**: 多空指标
- **知行趋势线**: 短期趋势指标
- **知行多空线**: 多空平衡指标

### 4. 阻力支撑指标
- **布林带 (Bollinger Bands)**: 包含上轨、中轨、下轨

### 5. 买卖信号
- **KDJ金叉死叉**: K线上穿/下穿D线
- **MACD金叉死叉**: MACD线上穿/下穿信号线
- **趋势线突破**: 价格突破趋势线

## 使用方式

### 1. 在分析器中使用
```python
from src.core.technical_indicators import calculate_basic_technical_indicators

# 计算基本技术指标
indicators = calculate_basic_technical_indicators(
    current_price=12.5,
    historical_data=[12.0, 12.1, 12.3, 12.4, 12.5]  # 历史价格数据
)
```

### 2. 计算所有指标
```python
from src.core.technical_indicators import calculate_all_indicators
import pandas as pd

# 输入包含 OHLCV 数据的 DataFrame
data = pd.DataFrame({
    'date': [...],
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
})

# 计算所有技术指标
result = calculate_all_indicators(data)
```

## 集成到现有系统

### 1. 股票分析结果增强
技术指标模块已集成到 `StockResult` 类中，增加了以下字段：
- `MA5`, `MA10`, `MA20`: 移动平均线
- `RSI`: 相对强弱指标
- `signal`: 交易信号 (buy/sell/neutral)

### 2. 自动计算
当分析股票时，系统会：
1. 获取历史价格数据
2. 计算技术指标
3. 生成更全面的分析报告

## 功能特点

### 1. 全面覆盖
- 包含主流技术分析指标
- 支持多种时间周期
- 提供买卖信号判断

### 2. 高效计算
- 基于 Pandas 和 NumPy 优化
- 支持批量计算
- 内存友好

### 3. 灵活扩展
- 模块化设计
- 易于添加新指标
- 支持自定义参数

## 应用场景

### 1. 个股分析
- 提供技术面分析依据
- 辅助判断买卖时机
- 识别支撑阻力位

### 2. 风险控制
- 识别超买超卖状态
- 检测趋势变化
- 提供预警信号

### 3. 投资决策
- 综合技术指标分析
- 量化投资建议
- 减少主观判断误差

## 注意事项

1. **数据质量**: 技术指标准确性依赖于高质量的历史数据
2. **参数设置**: 不同股票可能需要调整指标参数
3. **结合基本面**: 技术分析应结合基本面分析使用
4. **市场环境**: 指标在不同市场环境下表现可能不同

## 未来扩展

- 更多技术指标支持
- 可视化图表生成
- 指标回测功能
- 个性化策略定制

---
*技术指标模块 v1.0*