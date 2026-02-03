# A股智能分析系统 (Stock Analysis)

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个专业的 A 股智能分析系统，集成技术指标计算与多 AI 模型分析能力。

## ✨ 特性

- 📊 **全面的技术指标** - KDJ、MACD、RSI、BBI、布林带、知行指标等
- 🤖 **多 AI 模型支持** - Gemini、OpenAI、DeepSeek
- 📈 **实时数据获取** - 腾讯财经数据源
- 🔔 **多渠道通知** - 飞书、Telegram、钉钉（开发中）
- ⏰ **定时任务** - 支持每日定时分析
- 🎯 **交易策略融入** - 乖离率控制、多头排列检测

## 🚀 快速开始

### 方式一：Docker（推荐）

最简单的使用方式，无需安装 Python 环境：

```bash
# 克隆项目
git clone https://github.com/Falcon0711/stock-analysis.git
cd stock-analysis

# 复制配置文件并填入 API Key
cp .env.example .env
nano .env  # 编辑配置

# 运行分析
docker compose run --rm stock-analysis 600519

# AI 增强分析
docker compose run --rm stock-analysis 600519 --ai

# 批量分析（使用 .env 中的 STOCK_LIST）
docker compose run --rm stock-analysis --list
```

#### Docker 命令说明

```bash
# 构建镜像
docker compose build

# 分析指定股票
docker compose run --rm stock-analysis 600519 000001 300750

# AI 分析并输出到文件
docker compose run --rm stock-analysis 600519 --ai -o /app/reports/report.txt

# 查看帮助
docker compose run --rm stock-analysis --help
```

### 方式二：本地安装

```bash
# 克隆项目
git clone https://github.com/Falcon0711/stock-analysis.git
cd stock-analysis

# 安装依赖
pip install -e .

# 分析股票
python run_analysis.py 600519
```

### 完整安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖（包含开发工具）
pip install -e ".[dev]"
```

### 配置

创建 `.env` 文件：

```bash
# AI API Keys（至少配置一个可使用 AI 分析）
GEMINI_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key

# 股票列表
STOCK_LIST=600519,000001,300750

# 可选配置
DEBUG=false
LOG_LEVEL=INFO
MAX_WORKERS=3
```

### 运行分析

```bash
# 分析单只股票
python run_analysis.py 600519

# 分析多只股票
python run_analysis.py 600519 000001 300750

# 使用 AI 增强分析
python run_analysis.py 600519 --ai

# 使用配置的股票列表
python run_analysis.py --list

# 输出到文件
python run_analysis.py 600519 -o report.txt

# 查看帮助
python run_analysis.py --help
```

## 📊 分析报告示例

```
=================================================================
              贵州茅台(600519) 技术分析报告
=================================================================
📈 基本信息: 贵州茅台 | 600519
💰 当前价格: 1474.92元 | 涨跌: +47.92 | 涨幅: +3.36%

📊 技术指标概览:
  KDJ: K=70.85, D=49.38, J=113.79 | 信号: 🟢金叉
  MACD: 3.517, -7.707, 22.448 | 信号: 🟢多头
  BBI: 1401.17 | 位置: 上方
  MA5/10/20/60: 1412.87/1377.75/1389.25/1406.84
  知行指标: 趋势线=1381.44 | 位置: 上方

🛡️ 支撑阻力:
  近期支撑: MA10=1377.75 | 近期阻力: MA5=1412.87

🎯 综合信号:
  买卖建议: 🟡观望
  风险等级: 🟡中

=================================================================
💡 提示: 今日上涨 +3.36%，关注操作
=================================================================
```

## 📁 项目结构

```
stock_analysis/
├── Dockerfile              # Docker 镜像配置
├── docker-compose.yml      # Docker Compose 配置
├── pyproject.toml          # 项目配置和依赖
├── README.md               # 项目说明
├── run_analysis.py         # 快速分析脚本 ⭐
├── .env.example            # 配置示例
├── src/
│   └── stock_analysis/     # 主包
│       ├── __init__.py
│       ├── __main__.py     # 支持 python -m stock_analysis
│       ├── main.py         # 主程序
│       ├── constants.py    # 常量定义
│       ├── config/         # 配置模块
│       ├── core/           # 核心分析
│       │   ├── analyzer.py             # AI 分析器
│       │   └── technical_indicators.py # 技术指标
│       ├── data_sources/   # 数据源
│       │   └── tencent.py  # 腾讯数据源
│       ├── skills/         # 分析技能 ⭐
│       │   ├── stock_analysis.py
│       │   └── SKILL.md    # 技能说明
│       └── utils/          # 工具函数
├── tests/                  # 测试
└── docs/                   # 文档
```

## 📊 技术指标

| 指标 | 说明 | 默认参数 |
|------|------|----------|
| KDJ | 随机指标 | N=9, M1=3, M2=3 |
| MACD | 异同移动平均线 | Fast=12, Slow=26, Signal=9 |
| RSI | 相对强弱指标 | Period=14 |
| BBI | 多空指标 | 3, 6, 12, 24 |
| 布林带 | 波动率通道 | Period=20, StdDev=2 |
| 知行趋势线 | 短期趋势 | EMA(EMA(C,10),10) |
| 知行多空线 | 中期趋势 | MA14+MA28+MA57+MA114 |

## 🤖 AI 模型

支持以下 AI 模型进行深度分析：

- **DeepSeek** - 高性价比的国产模型（推荐）
- **OpenAI** - GPT 系列模型
- **Gemini** - Google 的大语言模型

优先级：DeepSeek > OpenAI > Gemini

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率报告
pytest --cov=stock_analysis --cov-report=html

# 运行特定测试
pytest tests/test_technical_indicators.py -v
```

## 📝 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 代码格式化
black src tests

# 代码检查
ruff check src tests

# 类型检查
mypy src
```

## 🔄 Python API

```python
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

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。
