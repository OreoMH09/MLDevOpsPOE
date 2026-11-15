@echo off
REM Log API metrics and Evidently reports to MLflow
call venv\Scripts\activate.bat
set PYTHONPATH=%CD%
python mlflow_tracking.py
pause
