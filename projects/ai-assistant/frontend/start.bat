@echo off
echo ========================================
echo   AI 智能文档问答助手
echo ========================================
echo.

echo [1/2] 启动后端服务...
start "Backend" python -m app.main

echo [2/2] 启动前端界面...
timeout /t 3 /nobreak > nul
start "Frontend" python run_frontend.py

echo.
echo ✅ 启动完成！
echo.
echo 📍 后端地址：http://localhost:8000
echo 📍 前端地址：http://localhost:8501
echo.
echo 按任意键退出...
pause > nul
