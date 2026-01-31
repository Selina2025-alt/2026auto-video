@echo off
chcp 65001 >nul
echo ========================================
echo 批量自动剪辑智能体 - 快速启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未检测到 Node.js，请先安装 Node.js 16+
    pause
    exit /b
)

echo ✓ 环境检查通过
echo.

REM 安装后端依赖
echo [1/3] 检查后端依赖...
cd /d "%~dp0backend"
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul
echo ✓ 后端依赖就绪

REM 安装前端依赖
echo.
echo [2/3] 检查前端依赖...
cd /d "%~dp0"
if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)
echo ✓ 前端依赖就绪

REM 启动服务
echo.
echo [3/3] 启动服务...
call "%~dp0启动服务.bat"
