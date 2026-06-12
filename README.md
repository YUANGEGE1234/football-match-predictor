# 足球比赛预测工具 - Football Match Predictor

基于 Rotowire.com 数据源，结合天气、历史战绩、球员状态、裁判、赔率等多种因素，使用AI大模型进行足球比赛预测的商业级分析工具。

## 功能特点

### 数据采集
- 从 Rotowire.com 实时获取比赛信息
- 支持多个联赛：世界杯、英超、西甲、德甲、意甲、法甲、欧冠、MLS等
- 获取完整的首发阵容（球员全名、位置）
- 伤病/停赛信息
- 多平台赔率对比（DraftKings、FanDuel、BetMGM、PointsBet）
- 天气信息（温度、风速、降雨概率）

### 信息分析
- 48支国家队教练详细信息
- 裁判执法风格分析
- 赔率隐含概率计算
- 天气对比赛的影响评估

### AI预测
- 双模型分析系统：
  - 归纳模型：整理和归纳比赛信息
  - 分析模型：深度分析并给出预测
- 专业的7部分分析提示词：
  1. 阵容与战术分析
  2. 教练因素分析
  3. 关键球员分析
  4. 裁判与环境因素
  5. 数据与概率分析
  6. 风险评估
  7. 最终预测（胜负概率、比分预测）
- API调用失败自动重试（最多3次）

### 界面特点
- 清晰的GUI界面
- 实时进度显示
- 多平台赔率对比表格
- 详细的比赛信息展示

## 快速开始

### 方法一：使用EXE（推荐）

1. 下载 `足球比赛预测工具.exe`
2. 双击运行
3. 填入AI模型配置
4. 选择比赛开始分析

### 方法二：Python运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方法三：自行打包

```bash
# 安装打包工具
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --name "足球比赛预测工具" main.py
```

## 配置说明

### 推荐AI API中转站

如果你无法直接访问OpenAI API，推荐使用以下中转站：

**新源AI中转站**: https://xinyuanai666.com

- 支持OpenAI兼容接口
- 稳定快速
- 注册即可使用

### 归纳模型配置
- **API地址**: 推荐使用 https://xinyuanai666.com 或 https://api.openai.com
- **API密钥**: 在中转站获取的API密钥
- **模型**: 推荐使用 gpt-3.5-turbo 或同等模型

### 分析模型配置
- **API地址**: 推荐使用 https://xinyuanai666.com 或 https://api.openai.com
- **API密钥**: 在中转站获取的API密钥
- **模型**: 推荐使用 gpt-4 或更强大的模型

### 天气API（可选）
- 免费获取：https://openweathermap.org/api

## 数据来源

- **比赛信息**: [Rotowire.com](https://www.rotowire.com/soccer/lineups.php)
- **赔率数据**: DraftKings, FanDuel, BetMGM, PointsBet
- **天气数据**: OpenWeatherMap API
- **AI分析**: 支持OpenAI兼容接口的大模型

## 项目结构

```
football_predictor/
├── main.py                 # 主程序入口
├── config.py              # 配置管理
├── requirements.txt       # 依赖列表
├── .gitignore            # Git忽略文件
├── README.md             # 项目说明
├── scraper/
│   ├── __init__.py
│   └── rotowire.py       # Rotowire爬虫模块
├── analyzer/
│   ├── __init__.py
│   └── ai_analyzer.py    # AI分析模块
├── gui/
│   ├── __init__.py
│   └── main_window.py    # GUI界面
└── weather/
    ├── __init__.py
    └── weather_service.py # 天气服务
```

## 技术栈

- Python 3.11+
- Tkinter (GUI)
- BeautifulSoup4 (网页解析)
- Requests (HTTP请求)
- PyInstaller (程序打包)

## 免责声明

本工具仅供学习和研究使用。预测结果仅供参考，不构成任何投注建议。请理性对待体育赛事预测。

## 许可证

MIT License

## 作者

MiMoCode - Xiaomi MiMo Team
