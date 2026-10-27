@echo off
chcp 65001 >nul
title 開放阿爾比恩黑市雷達區網防火牆 (Port 8000)

:: 檢查系統管理員權限
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo 正在請求系統管理員權限以設定 Windows 防火牆...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

    echo ========================================================
    echo   ⚔️ 阿爾比恩黑市雷達 - 區網防火牆設定 ⚔️
    echo ========================================================
    echo.
    echo 正在為 TCP 8000 埠新增 Windows 防火牆入站允許規則...
    netsh advfirewall firewall delete rule name="Albion Radar Port 8000" >nul 2>&1
    netsh advfirewall firewall add rule name="Albion Radar Port 8000" dir=in action=allow protocol=TCP localport=8000 profile=any >nul
    
    if '%errorlevel%' EQU '0' (
        echo.
        echo [OK] 成功新增防火牆允許規則！
        echo.
        echo 現在區網其他裝置（手機、平板、其他筆電/電腦）均可正常連線：
        echo 👉 http://192.168.2.107:8000
        echo.
        echo 若是這台主機本機使用，直接輸入：
        echo 👉 http://localhost:8000
        echo.
    ) else (
        echo.
        echo [ERROR] 新增防火牆失敗，請確認是否具備系統管理員身分。
        echo.
    )

    echo 按任意鍵關閉此視窗...
    pause >nul
