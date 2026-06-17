@echo off
chcp 65001 >nul
cd /d "%~dp0"
"C:\Users\com\AppData\Local\Programs\Python\Python311\python.exe" main.py
if %errorlevel% neq 0 (
    echo.
    echo 오류가 발생했습니다. 위 내용을 캡처해서 알려주세요.
    pause
)
