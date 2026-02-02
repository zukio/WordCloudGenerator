@echo off
cd /d "%~dp0"
"venv/Scripts/python.exe" wordcloud/main.py %*
pause
