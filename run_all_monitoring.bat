@echo off
REM Run tests, generate Evidently report, and log to MLflow
echo ============================================================
echo Running Complete Monitoring Pipeline
echo ============================================================

call venv\Scripts\activate.bat
set PYTHONPATH=%CD%

echo.
echo [1/3] Running pytest tests...
echo ------------------------------------------------------------
pytest tests/ -v

echo.
echo [2/3] Generating Evidently data drift report...
echo ------------------------------------------------------------
python monitoring/generate_report.py

echo.
echo [3/3] Logging metrics to MLflow...
echo ------------------------------------------------------------
python mlflow_tracking.py

echo.
echo ============================================================
echo Monitoring pipeline completed!
echo ============================================================
echo.
echo To view results:
echo - Evidently report: reports\evidently_data_drift_report.html
echo - MLflow UI: run run_mlflow_ui.bat
echo.
pause
