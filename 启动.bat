@echo off
chcp 65001 >nul
echo ========================================
echo 足球比赛预测工具 - 启动脚本
echo ========================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请安装Python 3.11+
    pause
    exit /b 1
)

echo 检查依赖包...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo 安装依赖包...
    pip install -r requirements.txt
)

echo.
echo 启动程序...
python main.py

pause
