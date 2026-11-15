"""Generate an Evidently data-drift report for API request inputs.

The report compares the distribution of num1, num2 and operation in a
reference dataset with observed API traffic. If fewer than five real API
requests have been logged, a bundled demo comparison file is used so that
the report can still be demonstrated during a lab session.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_requests.csv"
DEMO_CURRENT_FILE = PROJECT_ROOT / "data" / "demo_current_requests.csv"
LIVE_LOG_FILE = PROJECT_ROOT / "logs" / "api_requests.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
FEATURE_COLUMNS = ["num1", "num2", "operation"]
MIN_LIVE_ROWS = 5


def load_monitoring_data() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Load baseline and current input data, selecting live logs when ready."""
    reference = pd.read_csv(REFERENCE_FILE)
    reference = reference[FEATURE_COLUMNS].copy()

    source = "bundled demo current-data file"
    if LIVE_LOG_FILE.exists():
        try:
            live = pd.read_csv(LIVE_LOG_FILE)
            if len(live) >= MIN_LIVE_ROWS:
                current = live[FEATURE_COLUMNS].copy()
                source = f"live API log ({len(current)} requests)"
            else:
                current = pd.read_csv(DEMO_CURRENT_FILE)[FEATURE_COLUMNS].copy()
        except (ValueError, KeyError, pd.errors.EmptyDataError):
            current = pd.read_csv(DEMO_CURRENT_FILE)[FEATURE_COLUMNS].copy()
    else:
        current = pd.read_csv(DEMO_CURRENT_FILE)[FEATURE_COLUMNS].copy()

    if len(reference) < 5 or len(current) < 5:
        raise ValueError("Evidently needs at least five rows in both datasets for this demo.")

    return reference, current, source


def main() -> None:
    reference, current, source = load_monitoring_data()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = Report(
        [
            DataDriftPreset(drift_share=0.5),
        ]
    )
    snapshot = report.run(current_data=current, reference_data=reference)

    html_path = REPORT_DIR / "evidently_data_drift_report.html"
    json_path = REPORT_DIR / "evidently_data_drift_report.json"
    snapshot.save_html(str(html_path))
    snapshot.save_json(str(json_path))

    print("Evidently report generated successfully.")
    print(f"Reference rows: {len(reference)}")
    print(f"Current rows:   {len(current)}")
    print(f"Current data source: {source}")
    print(f"HTML report: {html_path}")
    print(f"JSON report: {json_path}")
    print("Open the HTML report in a browser to inspect the drift results.")


if __name__ == "__main__":
    main()
