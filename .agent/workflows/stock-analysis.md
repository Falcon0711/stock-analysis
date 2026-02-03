---
description: 分析 A 股股票，获取技术指标和 AI 投资建议
---

# 股票分析技能

## 何时使用此技能

当用户的请求涉及以下内容时，**必须**使用此技能：

- 🔹 分析任何 A 股股票（如："帮我分析一下茅台"、"600519 怎么样"）
- 🔹 查询股票实时价格、涨跌幅
- 🔹 获取技术指标（KDJ、MACD、BBI、均线等）
- 🔹 需要买卖建议或操作提示
- 🔹 批量分析多只股票

## 常见股票代码

| 股票名称 | 代码 | 说明 |
|----------|------|------|
| 贵州茅台 / 茅台 | 600519 | 白酒龙头 |
| 中国黄金 | 600916 | 黄金珠宝 |
| 平安银行 | 000001 | 银行股 |
| 宁德时代 | 300750 | 新能源龙头 |
| 比亚迪 | 002594 | 新能源车 |
| 招商银行 | 600036 | 银行股 |
| 中国平安 | 601318 | 保险龙头 |
| 腾讯控股 | 00700 | 港股科技 |
| 五粮液 | 000858 | 白酒 |
| 中信证券 | 600030 | 券商龙头 |
| 隆基绿能 | 601012 | 光伏龙头 |
| 紫金矿业 | 601899 | 黄金矿业 |
| 合力科技 | 603917 | 汽配 |

## 执行步骤

### 步骤 1：基础技术分析

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py {股票代码}
```

**示例**：
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py 600519
```

### 步骤 2：AI 增强分析（可选）

如果用户需要更详细的投资建议，使用 `--ai` 参数：

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py {股票代码} --ai
```

**示例**：
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py 600519 --ai
```

### 步骤 3：批量分析（可选）

分析多只股票时，直接列出所有代码：

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py {代码1} {代码2} {代码3}
```

**示例**：
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py 600519 000001 300750
```

### 步骤 4：使用配置的股票列表

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py --list
```

### 步骤 5：输出到文件

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py {股票代码} --ai -o report.txt
```

## Python API 调用

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

## 用户请求示例

| 用户说 | 执行命令 |
|--------|----------|
| "分析茅台" | `python3 run_analysis.py 600519` |
| "帮我分析一下贵州茅台" | `python3 run_analysis.py 600519` |
| "给我 600519 的 AI 分析" | `python3 run_analysis.py 600519 --ai` |
| "我想了解 600519 的投资建议" | `python3 run_analysis.py 600519 --ai` |
| "帮我看看茅台、平安、宁德" | `python3 run_analysis.py 600519 000001 300750` |
| "茅台现在能买吗" | `python3 run_analysis.py 600519 --ai` |

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
| KDJ | K 上穿 D（🟢金叉）| K 下穿 D（🔴死叉）|
| MACD | DIF 上穿 DEA（🟢多头）| DIF 下穿 DEA（🔴空头）|
| BBI | 价格站上 BBI | 价格跌破 BBI |
| 均线 | 多头排列 (MA5>MA10>MA20) | 空头排列 |

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | 运行 `pip install -e .` 安装依赖 |
| AI 分析无输出 | 检查 `.env` 中的 API Key 配置 |
| 网络超时 | 检查网络连接，腾讯数据源需联网 |

## 重要提醒

⚠️ **免责声明**
- 本工具生成的分析报告仅供参考，不构成任何投资建议
- 股市有风险，投资需谨慎
- AI 分析结果可能存在偏差，请结合多方信息综合判断
