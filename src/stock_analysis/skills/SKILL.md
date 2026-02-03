---
name: stock_analysis
description: A股智能分析技能 - 获取实时股票数据并进行技术分析和AI增强分析
trigger: 用户询问股票分析、股票代码、A股、技术指标、买卖建议时触发
---

# 股票分析技能

## 何时使用此技能

当用户的请求涉及以下内容时，**必须**使用此技能：

- 🔹 分析任何 A 股股票（如："帮我分析一下茅台"、"600519 怎么样"）
- 🔹 查询股票实时价格、涨跌幅
- 🔹 获取技术指标（KDJ、MACD、BBI、均线等）
- 🔹 需要买卖建议或操作提示
- 🔹 批量分析多只股票

## 快速调用

### 方式一：命令行（推荐）

```bash
# 进入项目目录
cd /Users/ffmeng/Documents/stock_analysis_project

# 基础技术分析
python3 run_analysis.py 600519

# AI 增强分析（包含 DeepSeek AI 分析）
python3 run_analysis.py 600519 --ai

# 分析多只股票
python3 run_analysis.py 600519 000001 300750

# 使用配置的股票列表
python3 run_analysis.py --list

# 输出到文件
python3 run_analysis.py 600519 --ai -o report.txt
```

### 方式二：Python API

```python
import sys
sys.path.insert(0, "/Users/ffmeng/Documents/stock_analysis_project/src")

from stock_analysis.skills import (
    get_stock_analysis,
    get_stock_analysis_with_ai,
    get_multiple_stock_analysis,
)

# 基础技术分析
report = get_stock_analysis("600519")
print(report)

# AI 增强分析
report = get_stock_analysis_with_ai("600519")
print(report)

# 批量分析
reports = get_multiple_stock_analysis(["600519", "000001", "300750"])
for code, report in reports.items():
    print(report)
```

## 常见股票代码

| 股票名称 | 代码 | 说明 |
|----------|------|------|
| 贵州茅台 | 600519 | 白酒龙头 |
| 平安银行 | 000001 | 银行股 |
| 宁德时代 | 300750 | 新能源龙头 |
| 比亚迪 | 002594 | 新能源车 |
| 招商银行 | 600036 | 银行股 |
| 腾讯控股 | 00700 | 港股（需港股代码格式） |

## 输出格式说明

### 基础分析报告包含：

```
📈 基本信息: 股票名称 | 代码
💰 当前价格: xxx元 | 涨跌: +/-xx | 涨幅: +/-x.xx%

📊 技术指标概览:
  KDJ: K=xx, D=xx, J=xx | 信号: 🟢金叉/🔴死叉
  MACD: DIF, DEA, HIST | 信号: 🟢多头/🔴空头
  BBI: xx | 位置: 上方/下方
  MA5/10/20/60: xx/xx/xx/xx
  知行指标: 趋势线=xx | 位置: 上方/下方

🛡️ 支撑阻力:
  近期支撑: MAx=xx | 近期阻力: MAx=xx

🎯 综合信号:
  买卖建议: 🟢买入/🔴卖出/🟡观望
  风险等级: 🔴高/🟡中/🟢低

💡 提示: 操作建议
```

### AI 增强分析额外包含：

```
🤖 AI综合分析:
  - 技术面分析
  - 短期趋势预测
  - 操作建议
  - 风险提示
```

## 用户请求示例及响应

### 示例 1：分析单只股票

**用户**: "帮我分析一下贵州茅台"

**执行**:
```bash
python3 /Users/ffmeng/Documents/stock_analysis_project/run_analysis.py 600519
```

### 示例 2：获取 AI 建议

**用户**: "我想了解 600519 的投资建议"

**执行**:
```bash
python3 /Users/ffmeng/Documents/stock_analysis_project/run_analysis.py 600519 --ai
```

### 示例 3：批量分析

**用户**: "帮我看看茅台、平安、宁德时代"

**执行**:
```bash
python3 /Users/ffmeng/Documents/stock_analysis_project/run_analysis.py 600519 000001 300750
```

### 示例 4：只知道股票名称

**用户**: "分析一下茅台"

**处理逻辑**:
1. 识别"茅台" → 贵州茅台 → 代码 600519
2. 执行分析

## 配置说明

配置文件位置：`/Users/ffmeng/Documents/stock_analysis_project/.env`

```bash
# DeepSeek API（已配置）
DEEPSEEK_API_KEY=sk-xxxxx

# 默认股票列表
STOCK_LIST=600519,000001,300750
```

## 技术指标解读

| 指标 | 买入信号 | 卖出信号 |
|------|----------|----------|
| KDJ | K 上穿 D（金叉）| K 下穿 D（死叉）|
| MACD | DIF 上穿 DEA | DIF 下穿 DEA |
| BBI | 价格站上 BBI | 价格跌破 BBI |
| 均线 | 多头排列 (MA5>MA10>MA20) | 空头排列 |

## 重要提醒

⚠️ **免责声明**
- 本工具生成的分析报告仅供参考，不构成任何投资建议
- 股市有风险，投资需谨慎
- AI 分析结果可能存在偏差，请结合多方信息综合判断

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | 运行 `pip install -e .` 安装依赖 |
| AI 分析无输出 | 检查 `.env` 中的 API Key 配置 |
| 网络超时 | 检查网络连接，腾讯数据源需联网 |
