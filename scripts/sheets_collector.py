#!/usr/bin/env python3
"""
Meta Ads Intelligence — Google Sheets Collector
Reads sales and performance data from Google Sheets (READ-ONLY).
Never writes or modifies any data in the spreadsheet.

Usage:
    python scripts/sheets_collector.py
    python scripts/sheets_collector.py --date-label 2026-03-17
    python scripts/sheets_collector.py --sheets vendas_mda ads_mda
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("ERROR: gspread not installed.")
    print("Run: python -m pip install gspread google-auth")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed.")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "config" / "google-credentials.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "sheets"

SPREADSHEET_ID = "1_3pCHweiFK1aksrDA4KbUvmrJtzeEQwTqad3Cvdyd4I"

# Abas a coletar e seus apelidos internos
SHEETS_CONFIG = {
    "VENDAS_UPSELL_ACELERADOR":      "vendas_upsell_acelerador",
    "VENDAS_MDA":                    "vendas_mda",
    "ACOMPANHAMENTO_DIARIO_MDA":     "diario_mda",
    "ADS_MDA":                       "ads_mda",
    "VENDAS_LVC":                    "vendas_lvc",
    "ACOMPANHAMENTO_DIARIO_LVC":     "diario_lvc",
    "ADS_LVC":                       "ads_lvc",
    "VENDAS_TEUS":                   "vendas_teus",
    "ACOMPANHAMENTO_DIARIO_TEUS":    "diario_teus",
    "ADS_TEUS":                      "ads_teus",
    "REEMBOLSOS":                    "reembolsos",
    "VENDAS_ACELERADOR_COMERCIAL":   "vendas_acelerador_comercial",
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


# ── Auth ──────────────────────────────────────────────────────────────────────
def get_client() -> gspread.Client:
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        print("Save your Google Service Account JSON as:")
        print(f"  {CREDENTIALS_FILE}")
        sys.exit(1)

    creds = Credentials.from_service_account_file(str(CREDENTIALS_FILE), scopes=SCOPES)
    return gspread.authorize(creds)


# ── Collect ───────────────────────────────────────────────────────────────────
def collect_sheet(spreadsheet, sheet_name: str) -> pd.DataFrame:
    try:
        ws = spreadsheet.worksheet(sheet_name)
        data = ws.get_all_values()
        if not data or len(data) < 2:
            print(f"  WARNING: {sheet_name} is empty or has no data rows")
            return pd.DataFrame()
        headers = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=headers)
        # Remove completely empty rows
        df = df.replace("", None).dropna(how="all")
        print(f"  -> {sheet_name}: {len(df)} rows, {len(df.columns)} cols")
        return df
    except gspread.exceptions.WorksheetNotFound:
        print(f"  WARNING: Sheet '{sheet_name}' not found in spreadsheet")
        return pd.DataFrame()
    except Exception as e:
        print(f"  ERROR reading {sheet_name}: {e}")
        return pd.DataFrame()


# ── Save ──────────────────────────────────────────────────────────────────────
def save_sheet(df: pd.DataFrame, alias: str, date_label: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{date_label}_{alias}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    return path


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Meta Ads Intelligence — Google Sheets Collector (READ-ONLY)"
    )
    parser.add_argument(
        "--date-label",
        default=str(date.today()),
        help="Date label for output files (YYYY-MM-DD). Default: today",
    )
    parser.add_argument(
        "--sheets",
        nargs="*",
        help="Sheet names to collect (default: all configured sheets)",
    )
    args = parser.parse_args()

    date_label = args.date_label
    sheets_to_collect = args.sheets or list(SHEETS_CONFIG.keys())

    print(f"\n{'='*60}")
    print(f"Google Sheets Collector -- READ ONLY")
    print(f"Spreadsheet: {SPREADSHEET_ID}")
    print(f"Date label:  {date_label}")
    print(f"Sheets:      {', '.join(sheets_to_collect)}")
    print(f"{'='*60}\n")

    client = get_client()

    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        print(f"Connected: '{spreadsheet.title}'\n")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERROR: Spreadsheet not found or not shared with service account.")
        print(f"Share the sheet with: (check your credentials file for client_email)")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR connecting to spreadsheet: {e}")
        sys.exit(1)

    print("Collecting sheets...")
    results = {}
    for sheet_name in sheets_to_collect:
        alias = SHEETS_CONFIG.get(sheet_name, sheet_name.lower().replace(" ", "_"))
        df = collect_sheet(spreadsheet, sheet_name)
        if not df.empty:
            path = save_sheet(df, alias, date_label)
            results[sheet_name] = {
                "alias": alias,
                "rows": len(df),
                "cols": len(df.columns),
                "file": str(path.relative_to(PROJECT_ROOT)),
                "columns": df.columns.tolist(),
            }

    # Save manifest
    manifest = {
        "date_label": date_label,
        "spreadsheet_id": SPREADSHEET_ID,
        "collected_at": str(date.today()),
        "sheets": results,
    }
    manifest_path = OUTPUT_DIR / f"{date_label}_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"Collection complete!")
    print(f"  Sheets collected: {len(results)}/{len(sheets_to_collect)}")
    print(f"  Output dir: data/sheets/")
    print(f"  Manifest: {manifest_path.relative_to(PROJECT_ROOT)}")
    print(f"{'='*60}\n")

    # Print column summary for mapping
    print("Column summary (for data mapping):")
    for sheet_name, info in results.items():
        print(f"\n  [{info['alias']}] {info['rows']} rows")
        print(f"  Columns: {', '.join(info['columns'][:10])}", end="")
        if len(info['columns']) > 10:
            print(f" ... (+{len(info['columns'])-10} more)")
        else:
            print()


if __name__ == "__main__":
    main()
