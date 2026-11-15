# Arithmetic Operations API — FastAPI + Jenkins + Pytest + Evidently + MLflow

## 1. Project problem statement

Create a Python program that accepts two numbers and performs:

- Addition: `num1 + num2`
- Subtraction: `num1 - num2`
- Multiplication: `num1 * num2`
- Division: `num1 / num2` (division by zero is rejected)

Integrate the program with FastAPI, Jenkins, pytest, Evidently, and MLflow. Git is optional.

## 2. Tools used

| Tool | Purpose in this project |
|---|---|
| Python | Implements the arithmetic calculations |
| FastAPI | Exposes the calculations as HTTP API endpoints |
| Jenkins | Runs the automated build/test/monitoring pipeline |
| pytest | Tests API responses, arithmetic results and error handling |
| Evidently | Compares the distribution of incoming numeric inputs with reference inputs |
| MLflow | Tracks experiments, logs metrics, and manages monitoring artifacts |
| Git (optional) | Tracks source-code changes and can provide Jenkins checkout |

## 3. Folder structure

```text
arithmetic_fastapi_mlops/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_api.py
├── monitoring/
│   └── generate_report.py
├── data/
│   ├── reference_requests.csv
│   └── demo_current_requests.csv
├── logs/
│   └── api_requests.csv       # created automatically after API requests
├── reports/                   # HTML and JSON reports are written here
├── mlruns/                    # MLflow tracking data
│   └── mlflow.db
├── mlflow_tracking.py
├── Jenkinsfile
├── requirements.txt
├── run_api.bat
├── run_tests.bat
├── run_mlflow_ui.bat
├── run_mlflow_tracking.bat
├── run_all_monitoring.bat
└── generate_evidently_report.bat
```

## 4. Requirements

- Windows 10/11 or Linux
- Python 3.10 or newer (Python 3.11 is a good choice for a lab setup)
- Internet connection for the first installation of Python packages
- Jenkins installed and configured for the CI pipeline demonstration

## 5. Setup on Windows (PowerShell)

Open VS Code, open this project folder, then open the integrated terminal (PowerShell).

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can skip activation and use the virtual-environment Python directly:

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 6. Run the FastAPI application

```powershell
python -m uvicorn app.main:app --reload
```

Open these URLs in your browser:

- API home: http://127.0.0.1:8000/
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### API endpoints

All four endpoints use HTTP `POST` and accept JSON containing `num1` and `num2`.

| Operation | URL | Example input | Expected result |
|---|---|---|---|
| Addition | `POST /add` | `{"num1": 10, "num2": 5}` | `15` |
| Subtraction | `POST /subtract` | `{"num1": 10, "num2": 5}` | `5` |
| Multiplication | `POST /multiply` | `{"num1": 10, "num2": 5}` | `50` |
| Division | `POST /divide` | `{"num1": 10, "num2": 5}` | `2` |

Example success response:

```json
{
  "operation": "addition",
  "num1": 10.0,
  "num2": 5.0,
  "result": 15.0
}
```

Division by zero returns HTTP status `400` with a clear error message. Missing or invalid fields are rejected by FastAPI/Pydantic with HTTP status `422`.

## 7. Run pytest

Stop is not required for the API. Open another terminal in the project folder and run:

```powershell
python -m pytest -v
```

The tests check all four calculations, division by zero, missing input, the health endpoint and CSV request logging. Test logs are isolated in a temporary directory so tests do not pollute the real monitoring log.

Expected result: all 8 test cases pass (the parameterized calculation test contributes four cases).

## 8. Generate an Evidently report

Every successful API request is recorded in `logs/api_requests.csv`. Evidently compares the distribution of `num1`, `num2` and `operation` in the reference data with the current request data.

1. Start the API.
2. Open http://127.0.0.1:8000/docs.
3. Execute at least five successful requests across any of the four endpoints.
4. In another terminal, run:

```powershell
python monitoring/generate_report.py
```

The generated reports are:

- `reports/evidently_data_drift_report.html`
- `reports/evidently_data_drift_report.json`

Open the HTML file in a browser.

**Demo behaviour:** If fewer than five real API requests have been recorded, the script uses `data/demo_current_requests.csv` so the report can still be generated immediately. Once at least five real API requests are logged, it uses the actual API log instead. The reference and demo CSVs are small demonstration data, not production traffic.

**Important:** Evidently checks changes in the distribution of API input values; it does not verify whether addition/subtraction/multiplication/division is mathematically correct. pytest checks arithmetic correctness. These tools have different responsibilities.

## 9. MLflow Experiment Tracking

MLflow tracks experiments, logs metrics, and manages artifacts from your API monitoring.

### Log metrics to MLflow

After generating some API traffic and the Evidently report, run:

```powershell
python mlflow_tracking.py
```

This script:
- Logs API request metrics (total requests, operation counts, averages)
- Logs the Evidently HTML and JSON reports as artifacts
- Creates experiments in the MLflow tracking database

### View MLflow UI

Start the MLflow UI to explore logged experiments:

```powershell
.\run_mlflow_ui.bat
```

Or manually:

```powershell
mlflow ui --backend-store-uri sqlite:///mlruns/mlflow.db --host 0.0.0.0 --port 5000
```

Then open http://localhost:5000 in your browser.

### Run complete monitoring pipeline

Execute tests, generate Evidently reports, and log to MLflow in one command:

```powershell
.\run_all_monitoring.bat
```

This automated script:
1. Runs pytest tests
2. Generates Evidently data drift report
3. Logs all metrics and artifacts to MLflow

**MLflow Features:**
- **Experiments:** Organize runs by experiment name (`arithmetic_api_monitoring`)
- **Metrics:** Track API usage patterns, operation distributions, and averages
- **Artifacts:** Store Evidently reports and API logs for each run
- **Comparison:** Compare metrics across multiple runs in the UI

## 10. Jenkins integration

## 10. Jenkins integration

The included `Jenkinsfile` has three stages:

1. Install Dependencies — creates a Python virtual environment and installs `requirements.txt`.
2. Run Pytest — executes the automated test suite. A test failure fails the pipeline.
3. Generate Evidently Report — creates the HTML and JSON monitoring report.

The Jenkinsfile supports Windows agents (`bat`) and Linux agents (`sh`). Ensure the Jenkins agent has Python 3 installed and can access the internet to install packages.

### Run with Jenkins and Git (optional)

1. Put this project folder in a Git repository and push it to a Git provider, if using Git.
2. In Jenkins, create a **Pipeline** job.
3. Under Pipeline Definition, select **Pipeline script from SCM**, choose Git, and enter the repository URL and branch.
4. Ensure the repository root contains `Jenkinsfile`.
5. Save and select **Build Now**.
6. Open the build's **Console Output** and verify the stages.
7. After the build, find the archived Evidently HTML/JSON report under the build's archived artifacts (if report generation succeeded).

### Git is not being used

For a lab demonstration without Git, create a Jenkins **Freestyle project** and configure the project folder as the job's workspace/source directory. Add these Windows build steps in order:

```bat
py -3 -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\python -m pytest -v
set PYTHONPATH=%CD%
venv\Scripts\python monitoring\generate_report.py
venv\Scripts\python mlflow_tracking.py
```

Run the job and inspect **Console Output**. Jenkins must have permission to write to the workspace. For a repeatable Pipeline job, SCM checkout is generally more convenient.

## 11. What to explain in the practical viva

- **FastAPI:** Converts Python functions into HTTP API endpoints. `/docs` provides interactive Swagger documentation.
- **Jenkins:** Automates the sequence of installing dependencies, running tests and generating a monitoring report.
- **pytest:** Runs automated assertions to confirm that the API returns the expected arithmetic results and handles errors.
- **Evidently:** Compares reference inputs with current API inputs and generates a data-drift report.
- **MLflow:** Tracks experiments, logs metrics (request counts, averages), and stores artifacts (Evidently reports, logs). Provides a UI for comparing runs.
- **Git (optional):** Tracks code changes and can be used by Jenkins to fetch the project source.

## 12. Quick command summary

```powershell
# Install dependencies
pip install -r requirements.txt

# Start FastAPI
python -m uvicorn app.main:app --reload
# Or use the batch file
.\run_api.bat

# Run tests
python -m pytest -v
# Or use the batch file
.\run_tests.bat

# Generate Evidently report
python monitoring/generate_report.py
# Or use the batch file
.\generate_evidently_report.bat

# Log metrics to MLflow
python mlflow_tracking.py
# Or use the batch file
.\run_mlflow_tracking.bat

# Start MLflow UI
.\run_mlflow_ui.bat

# Run complete monitoring pipeline (pytest + Evidently + MLflow)
.\run_all_monitoring.bat
```

## 13. Batch Files Reference

| Batch File | Purpose |
|---|---|
| `run_api.bat` | Start the FastAPI server |
| `run_tests.bat` | Run pytest test suite |
| `generate_evidently_report.bat` | Generate Evidently data drift report |
| `run_mlflow_ui.bat` | Start MLflow UI on http://localhost:5000 |
| `run_mlflow_tracking.bat` | Log metrics and artifacts to MLflow |
| `run_all_monitoring.bat` | Complete pipeline: pytest → Evidently → MLflow |
