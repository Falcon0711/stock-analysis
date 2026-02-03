---
description: 分析 A 股股票，获取技术指标和 AI 投资建议
---

# 股票分析工作流

## 使用场景

当用户请求分析股票、查询技术指标、获取投资建议时使用。

## 执行步骤

### 1. 确定股票代码

常见股票代码对照：
- 贵州茅台 → 600519
- 平安银行 → 000001
- 宁德时代 → 300750
- 招商银行 → 600036
- 比亚迪 → 002594

### 2. 执行分析

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py {股票代码}
```

### 3. AI 增强分析（可选）

如果用户需要更详细的投资建议：

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py {股票代码} --ai
```

### 4. 批量分析（可选）

分析多只股票：

// turbo
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py 600519 000001 300750
```

## 示例

**用户请求**: "分析一下茅台"

**执行**:
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py 600519
```

**用户请求**: "给我茅台的 AI 分析"

**执行**:
```bash
cd /Users/ffmeng/Documents/stock_analysis_project && python3 run_analysis.py 600519 --ai
```
