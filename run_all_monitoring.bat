@echo off
REM Run tests and generate Evidently report
echo ============================================================
echo Running Complete Monitoring Pipeline
echo ============================================================

call venv\Scripts\activate.bat
set PYTHONPATH=%CD%

echo.
echo [1/2] Running pytest tests...
echo ------------------------------------------------------------
pytest tests/ -v

echo.
echo [2/2] Generating Evidently data drift report...
echo ------------------------------------------------------------
python monitoring/generate_report.py

echo.
echo ============================================================
echo Monitoring pipeline completed!
echo ============================================================
echo.
echo To view results:
echo - Evidently report: reports\evidently_data_drift_report.html
echo.
pause
