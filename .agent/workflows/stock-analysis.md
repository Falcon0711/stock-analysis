---
description: 分析 A 股股票，获取技术指标和 AI 投资建议
---

# 股票分析技能

## 使用场景

当用户的请求涉及以下内容时使用此技能：

- 分析任何 A 股股票（如："帮我分析一下茅台"、"600519 怎么样"）
- 查询股票实时价格、涨跌幅
- 获取技术指标（KDJ、MACD、BBI、均线等）
- 需要买卖建议或操作提示
- 批量分析多只股票

## 常见股票代码

| 股票名称 | 代码 |
|----------|------|
| 贵州茅台 | 600519 |
| 平安银行 | 000001 |
| 宁德时代 | 300750 |
| 招商银行 | 600036 |
| 比亚迪 | 002594 |
| 中国平安 | 601318 |

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

## 输出说明

### 基础分析报告包含：
- 📈 基本信息（股票名称、代码、当前价格、涨跌幅）
- 📊 技术指标（KDJ、MACD、BBI、均线、知行指标）
- 🛡️ 支撑阻力位
- 🎯 综合信号（买卖建议、风险等级）
- 💡 操作提示

### AI 增强分析额外包含：
- 🤖 AI 综合分析（技术面分析、趋势预测、操作建议、风险提示）

## 用户请求示例

| 用户说 | 执行命令 |
|--------|----------|
| "分析茅台" | `python3 run_analysis.py 600519` |
| "给我 600519 的 AI 分析" | `python3 run_analysis.py 600519 --ai` |
| "帮我看看茅台、平安、宁德" | `python3 run_analysis.py 600519 000001 300750` |
| "茅台现在能买吗" | `python3 run_analysis.py 600519 --ai` |

## 技术指标解读

| 指标 | 买入信号 | 卖出信号 |
|------|----------|----------|
| KDJ | K 上穿 D（🟢金叉）| K 下穿 D（🔴死叉）|
| MACD | DIF 上穿 DEA（🟢多头）| DIF 下穿 DEA（🔴空头）|
| BBI | 价格站上 BBI | 价格跌破 BBI |
| 均线 | 多头排列 (MA5>MA10>MA20) | 空头排列 |

## 重要提醒

⚠️ 本工具生成的分析报告仅供参考，不构成任何投资建议。股市有风险，投资需谨慎。
