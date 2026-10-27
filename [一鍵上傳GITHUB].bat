@echo off
chcp 65001 >nul
title 阿爾比恩黑市雷達 - 一鍵上傳 GitHub

echo ================================================================
echo       ⚔️ 阿爾比恩 黑市製造利潤計算機 - GitHub 上傳工具 ⚔️
echo ================================================================
echo.

git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 系統未安裝 Git，請先前往 https://git-scm.com 下載安裝。
    pause
    exit /b
)

if not exist ".git" (
    echo [1/4] 初始化本機 Git 倉庫...
    git init
    git branch -M main
) else (
    echo [1/4] Git 倉庫已存在，切換至 main 分支...
    git branch -M main
)

git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 請先在 GitHub 上建立一個全新的 Repository (可以是 Private 私有或 Public 公開)。
    echo 請貼上您的 GitHub 儲存庫網址 (例如: https://github.com/您的帳號/albion-radar.git):
    set /p REPO_URL="網址: "
    if "%REPO_URL%"=="" (
        echo [提示] 未輸入網址，取消操作。
        pause
        exit /b
    )
    git remote add origin %REPO_URL%
    echo [2/4] 已綁定遠端儲存庫: %REPO_URL%
) else (
    echo [2/4] 遠端儲存庫已就緒。
)

echo.
echo [3/4] 整理檔案與提交...
git add .
git commit -m "Update Albion Black Market Radar" 2>nul

echo.
echo [4/4] 正在上傳至 GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ================================================================
    echo   🎉 上傳成功！
    echo   現在您可以前往 Render.com 綁定此 GitHub 專案，
    echo   即可享有 24 小時免開電腦、雲端全自動運行的專屬網址！
    echo ================================================================
) else (
    echo.
    echo [提示] 若推送失敗，請確認 GitHub 存取權限 (如 Personal Access Token 或 SSH)。
)

echo.
pause
