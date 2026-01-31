@echo off
chcp 65001 >nul
echo ========================================
echo 批量自动剪辑智能体 - 后端服务
echo ========================================
echo.
echo 正在启动后端服务...
echo 服务地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

cd /d "%~dp0backend"
python start.py

pause
