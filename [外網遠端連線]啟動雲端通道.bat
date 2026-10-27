@echo off
chcp 65001 >nul
title 阿爾比恩黑市雷達 - 雲端外網通道 (Cloudflare Tunnel)
cd /d "%~dp0"

echo ===================================================================
echo   🌐 阿爾比恩黑市雷達 - 外部網路 / 手機4G遠端訪問通道
echo ===================================================================
echo.
echo [說明]
echo 本工具透過 Cloudflare 官方安全加密通道，為本機 8000 埠建立專屬外網網址。
echo  ✓ 免費、安全加密 (HTTPS)
echo  ✓ 免路由器開 Port、免固定 IP、穿透任何網路與防火牆
echo  ✓ 手機 4G/5G、公司/學校 Wi-Fi、咖啡廳均可直接連線進入
echo.

if not exist "cloudflared.exe" (
    echo 正在下載 Cloudflare 官方連線元件 (僅首次需要)...
    curl.exe -L -o cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    if not exist "cloudflared.exe" (
        echo [錯誤] 下載失敗，請檢查網路連線。
        pause
        exit /b
    )
)

echo ===================================================================
echo 正在建立全球安全加密隧道，請稍候 3~5 秒...
echo 看到下方的 [ https://xxxx.trycloudflare.com ] 網址後：
echo 👉 直接複製該網址貼到手機或外網電腦瀏覽器即可直接使用！
echo ===================================================================
echo.

cloudflared.exe tunnel --url http://localhost:8000
pause
