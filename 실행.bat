@echo off
chcp 65001 >nul
set PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%
cd /d "%~dp0"
python main.py
