@echo off
chcp 65001 >nul
echo ========================================
echo 批量自动剪辑智能体 - 前端服务
echo ========================================
echo.
echo 正在启动前端服务...
echo 服务地址: http://localhost:5173
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

call npm run dev

pause
