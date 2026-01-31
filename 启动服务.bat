@echo off
chcp 65001 >nul
echo ========================================
echo 批量自动剪辑智能体
echo ========================================
echo.
echo 正在启动服务...
echo.
echo 启动后端服务...
start "后端服务" cmd /c "start_backend.bat"
timeout /t 3 >nul
echo 启动前端服务...
start "前端服务" cmd /c "start_frontend.bat"
echo.
echo ✓ 服务启动完成！
echo.
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
