"""MLflow experiment tracking for API monitoring."""

from __future__ import annotations

import mlflow
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
MLFLOW_DIR = PROJECT_ROOT / "mlruns"
LOG_FILE = PROJECT_ROOT / "logs" / "api_requests.csv"


def setup_mlflow():
    """Initialize MLflow tracking."""
    MLFLOW_DIR.mkdir(exist_ok=True)
    db_path = MLFLOW_DIR / "mlflow.db"
    mlflow.set_tracking_uri(f"sqlite:///{db_path}")
    mlflow.set_experiment("arithmetic_api_monitoring")


def log_api_metrics():
    """Log API metrics to MLflow."""
    setup_mlflow()
    
    if not LOG_FILE.exists():
        print("No API request log found. Start the API and make some requests first.")
        return
    
    # Read API logs
    df = pd.read_csv(LOG_FILE)
    
    if len(df) == 0:
        print("No requests logged yet.")
        return
    
    # Calculate metrics
    total_requests = len(df)
    operations = df['operation'].value_counts().to_dict()
    avg_num1 = df['num1'].mean()
    avg_num2 = df['num2'].mean()
    avg_result = df['result'].mean()
    
    # Start MLflow run
    with mlflow.start_run(run_name="api_monitoring"):
        # Log parameters
        mlflow.log_param("total_requests", total_requests)
        mlflow.log_param("log_file", str(LOG_FILE))
        
        # Log metrics
        mlflow.log_metric("total_requests", total_requests)
        mlflow.log_metric("avg_num1", avg_num1)
        mlflow.log_metric("avg_num2", avg_num2)
        mlflow.log_metric("avg_result", avg_result)
        
        # Log operation counts
        for operation, count in operations.items():
            mlflow.log_metric(f"requests_{operation}", count)
        
        # Log artifacts
        mlflow.log_artifact(str(LOG_FILE), "logs")
        
        # Log dataset stats as a table
        stats_dict = {
            "metric": ["total_requests", "avg_num1", "avg_num2", "avg_result"],
            "value": [total_requests, avg_num1, avg_num2, avg_result]
        }
        stats_df = pd.DataFrame(stats_dict)
        mlflow.log_table(stats_df, artifact_file="api_stats.json")
        
        print(f"✓ Logged metrics for {total_requests} API requests")
        print(f"  - Operations: {operations}")
        print(f"  - Average num1: {avg_num1:.2f}")
        print(f"  - Average num2: {avg_num2:.2f}")
        print(f"  - Average result: {avg_result:.2f}")
        print(f"\nMLflow UI: mlflow ui --backend-store-uri sqlite:///{MLFLOW_DIR / 'mlflow.db'}")


def log_test_results(passed: int, failed: int, total: int):
    """Log pytest test results to MLflow."""
    setup_mlflow()
    
    with mlflow.start_run(run_name="pytest_results"):
        mlflow.log_param("test_framework", "pytest")
        mlflow.log_metric("tests_passed", passed)
        mlflow.log_metric("tests_failed", failed)
        mlflow.log_metric("tests_total", total)
        mlflow.log_metric("pass_rate", (passed / total) * 100 if total > 0 else 0)
        
        print(f"✓ Logged test results: {passed}/{total} passed")


def log_evidently_report():
    """Log Evidently report to MLflow."""
    setup_mlflow()
    
    report_html = PROJECT_ROOT / "reports" / "evidently_data_drift_report.html"
    report_json = PROJECT_ROOT / "reports" / "evidently_data_drift_report.json"
    
    if not report_html.exists():
        print("No Evidently report found. Generate it first with: python monitoring/generate_report.py")
        return
    
    with mlflow.start_run(run_name="evidently_data_drift"):
        mlflow.log_artifact(str(report_html), "evidently_reports")
        mlflow.log_artifact(str(report_json), "evidently_reports")
        
        # Parse JSON report for metrics
        import json
        with open(report_json, 'r') as f:
            report_data = json.load(f)
        
        mlflow.log_param("report_type", "data_drift")
        mlflow.log_param("report_timestamp", report_data.get("timestamp", "unknown"))
        
        print("✓ Logged Evidently report to MLflow")
        print(f"  - HTML report: {report_html.name}")
        print(f"  - JSON report: {report_json.name}")


if __name__ == "__main__":
    print("=" * 60)
    print("MLflow Tracking - Arithmetic API")
    print("=" * 60)
    
    print("\n1. Logging API metrics...")
    log_api_metrics()
    
    print("\n2. Logging Evidently report...")
    log_evidently_report()
    
    print("\n" + "=" * 60)
    print("View all experiments in MLflow UI:")
    db_path = MLFLOW_DIR / "mlflow.db"
    print(f"  mlflow ui --backend-store-uri sqlite:///{db_path}")
    print("=" * 60)
