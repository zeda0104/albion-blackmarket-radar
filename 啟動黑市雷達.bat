@echo off
chcp 65001 >nul
title 阿爾比恩 黑市製造利潤計算機
cd /d "%~dp0"

echo 正在檢查 8000 連接埠...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 發現舊程序 (PID: %%a) 仍在背景占用 8000 埠，正在自動清除...
    taskkill /F /PID %%a >nul 2>&1
)

echo 正在啟動黑市製造利潤計算機...
python app.py
pause
