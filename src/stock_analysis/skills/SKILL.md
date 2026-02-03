# 股票分析技能说明

## 功能描述

使用 stock_analysis 项目进行 A 股智能分析，整合了腾讯财经数据源和多种 AI 分析能力（DeepSeek、OpenAI、Gemini）。

## 触发条件

- 当用户要求进行股票分析时
- 当用户询问特定股票的实时数据或历史数据时
- 当用户需要 AI 驱动的股票分析时
- 当用户提及任何股票代码或股票名称时
- 当用户要求查看股票走势、K 线、技术分析等时

## 分析模式

### 1. 基础技术分析

```python
from stock_analysis.skills import get_stock_analysis

# 分析单只股票
report = get_stock_analysis("600519")
print(report)
```

输出包含：
- 📈 基本信息（名称、代码、当前价格、涨跌幅）
- 📊 技术指标（KDJ、MACD、BBI、均线、知行指标）
- 🛡️ 支撑阻力位
- 🎯 综合信号（买卖建议、风险等级）
- 💡 操作提示

### 2. AI 增强分析

```python
from stock_analysis.skills import get_stock_analysis_with_ai

# 分析单只股票（包含 AI 分析）
report = get_stock_analysis_with_ai("600519")
print(report)
```

额外输出：
- 🤖 AI 综合分析（需要配置 API 密钥）

### 3. 批量分析

```python
from stock_analysis.skills import get_multiple_stock_analysis

# 分析多只股票
reports = get_multiple_stock_analysis(["600519", "000001", "300750"])
for code, report in reports.items():
    print(report)

# 批量 AI 分析
reports = get_multiple_stock_analysis(["600519", "000001"], with_ai=True)
```

## 快速使用

```bash
# 安装项目
pip install -e .

# 分析单只股票
python run_analysis.py 600519

# 分析多只股票
python run_analysis.py 600519 000001 300750

# 包含 AI 分析
python run_analysis.py 600519 --ai

# 使用配置的股票列表
python run_analysis.py --list

# 输出到文件
python run_analysis.py 600519 -o report.txt
```

## 配置

在项目根目录创建 `.env` 文件：

```bash
# 股票列表
STOCK_LIST=600519,000001,300750

# AI API 密钥（选择其一即可）
DEEPSEEK_API_KEY=your-deepseek-key    # 推荐
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
```

## 技术指标说明

| 指标 | 说明 | 信号 |
|------|------|------|
| KDJ | 随机指标 | K 上穿 D 为金叉（买入），下穿为死叉（卖出） |
| MACD | 异同移动平均线 | DIF 上穿 DEA 为多头，下穿为空头 |
| BBI | 多空指标 | 价格在 BBI 上方为多头，下方为空头 |
| 知行指标 | 自定义趋势指标 | 价格在趋势线上方为看涨 |

## 重要提醒

- ⚠️ 股票分析报告仅供参考，不构成投资建议
- ⚠️ 股市有风险，投资需谨慎
- ⚠️ AI 分析结果依赖于模型能力，可能存在偏差

## 依赖

- stock_analysis 主包
- 腾讯数据源模块（tencent.py）
- AI 分析器（可选，需要 API 密钥）
