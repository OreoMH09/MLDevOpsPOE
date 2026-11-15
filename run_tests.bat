@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup first using the README instructions.
    pause
    exit /b 1
)
.venv\Scripts\python -m pytest -v
pause
