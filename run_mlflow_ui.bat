@echo off
REM Start MLflow UI to view experiments
call venv\Scripts\activate.bat
set PYTHONPATH=%CD%
mlflow ui --backend-store-uri sqlite:///%CD%/mlruns/mlflow.db --host 0.0.0.0 --port 5000
