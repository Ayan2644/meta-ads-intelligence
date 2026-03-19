#!/usr/bin/env python3
"""
Meta Ads Intelligence — Data Processor
Reads raw JSON files from data/raw/ and produces normalized CSVs in data/processed/.

Outputs:
  - metrics_summary.csv      — Account-level totals per day
  - campaign_performance.csv — Per-campaign KPIs per day
  - ad_performance.csv       — Per-ad KPIs per day

Usage:
    python scripts/data_processor.py --date 2024-01-15
    python scripts/data_processor.py --date 2024-01-15 --date-since 2024-01-08
"""

import argparse
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run: pip install -r scripts/requirements.txt")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ── Action extraction helpers ─────────────────────────────────────────────────
def extract_action_value(actions: list | None, action_type: str) -> float:
    """Sum all values for a given action_type from the actions list."""
    if not actions:
        return 0.0
    return sum(
        float(a.get("value", 0))
        for a in actions
        if a.get("action_type") == action_type
    )


def extract_primary_action(actions: list | None, primary_types: list[str] | None = None) -> float:
    """Extract the count of the primary conversion action."""
    if not actions:
        return 0.0
    priority = primary_types or ["purchase", "lead", "complete_registration", "contact"]
    for action_type in priority:
        val = extract_action_value(actions, action_type)
        if val > 0:
            return val
    # fallback: sum all link clicks
    return extract_action_value(actions, "link_click")


# ── Safe numeric parsing ─────────────────────────────────────────────────────
def safe_float(value, default=0.0):
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        return int(float(value)) if value else default
    except (ValueError, TypeError):
        return default


# ── Load raw JSON ─────────────────────────────────────────────────────────────
def load_json(path: Path) -> list[dict]:
    if not path.exists():
        print(f"  WARNING: File not found: {path}")
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text or text == "[]":
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        print(f"  WARNING: Could not parse {path}: {e}")
        return []


# ── Normalize insight rows ────────────────────────────────────────────────────
def normalize_insights(insights: list[dict]) -> pd.DataFrame:
    if not insights:
        return pd.DataFrame()

    rows = []
    for row in insights:
        actions = row.get("actions") or []
        action_values = row.get("action_values") or []

        spend = safe_float(row.get("spend"))
        impressions = safe_int(row.get("impressions"))
        clicks = safe_int(row.get("clicks"))
        reach = safe_int(row.get("reach"))
        frequency = safe_float(row.get("frequency"))

        # Derived: CPC, CTR, CPM
        cpc = float(row.get("cpc", 0) or 0) or (spend / clicks if clicks > 0 else 0.0)
        ctr = float(row.get("ctr", 0) or 0) or (clicks / impressions * 100 if impressions > 0 else 0.0)
        cpm = float(row.get("cpm", 0) or 0) or (spend / impressions * 1000 if impressions > 0 else 0.0)

        # Purchase revenue and ROAS
        purchase_value = extract_action_value(action_values, "purchase")
        roas = purchase_value / spend if spend > 0 else 0.0

        # Primary result (purchases > leads > registrations > clicks)
        results = extract_primary_action(actions)
        result_rate = results / impressions if impressions > 0 else 0.0

        checkout_initiations = safe_int(row.get("checkout_initiations", 0))
        checkout_rate = round(results / checkout_initiations * 100, 4) if checkout_initiations > 0 else 0.0

        rows.append({
            "date": row.get("date_start", ""),
            "date_stop": row.get("date_stop", ""),
            "campaign_id": row.get("campaign_id", ""),
            "campaign_name": row.get("campaign_name", ""),
            "adset_id": row.get("adset_id", ""),
            "adset_name": row.get("adset_name", ""),
            "ad_id": row.get("ad_id", ""),
            "ad_name": row.get("ad_name", ""),
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "spend": round(spend, 2),
            "cpc": round(cpc, 4),
            "ctr": round(ctr, 4),
            "cpm": round(cpm, 4),
            "frequency": round(frequency, 2),
            "results": results,
            "result_rate": round(result_rate, 6),
            "purchase_value": round(purchase_value, 2),
            "roas": round(roas, 4),
            "checkout_initiations": checkout_initiations,
            "checkout_rate": checkout_rate,
            "quality_ranking": row.get("quality_ranking", ""),
            "engagement_ranking": row.get("engagement_ranking", ""),
            "conversion_ranking": row.get("conversion_ranking", ""),
        })

    df = pd.DataFrame(rows)

    # Type enforcement
    int_cols = ["impressions", "reach", "clicks"]
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    float_cols = ["spend", "cpc", "ctr", "cpm", "frequency", "results",
                  "result_rate", "purchase_value", "roas"]
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0.0).astype(float)

    return df


# ── Load previous period for delta calculation ────────────────────────────────
def load_previous_period(target_date: str, days_back: int = 7) -> pd.DataFrame:
    d = date.fromisoformat(target_date)
    prev_date = str(d - timedelta(days=days_back))
    insights_file = RAW_DIR / "insights" / f"{prev_date}_insights.json"
    prev_insights = load_json(insights_file)
    if not prev_insights:
        return pd.DataFrame()
    return normalize_insights(prev_insights)


def compute_delta(current: float, previous: float) -> float | None:
    if previous == 0 or (isinstance(previous, float) and math.isnan(previous)):
        return None
    if isinstance(current, float) and math.isnan(current):
        return None
    return round((current - previous) / previous * 100, 2)


# ── Generate CSVs ─────────────────────────────────────────────────────────────
def generate_metrics_summary(df: pd.DataFrame, prev_df: pd.DataFrame, date_label: str) -> pd.DataFrame:
    """One row per day — account-level totals."""
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby("date").agg(
        total_spend=("spend", "sum"),
        total_impressions=("impressions", "sum"),
        total_clicks=("clicks", "sum"),
        total_reach=("reach", "sum"),
        total_results=("results", "sum"),
        total_purchase_value=("purchase_value", "sum"),
        campaigns_active=("campaign_id", "nunique"),
        adsets_active=("adset_id", "nunique"),
        ads_active=("ad_id", "nunique"),
    ).reset_index()

    agg["avg_ctr"] = (agg["total_clicks"] / agg["total_impressions"].replace(0, float("nan")) * 100).round(4)
    agg["avg_cpc"] = (agg["total_spend"] / agg["total_clicks"].replace(0, float("nan"))).round(4)
    agg["avg_cpm"] = (agg["total_spend"] / agg["total_impressions"].replace(0, float("nan")) * 1000).round(4)
    agg["roas"] = (agg["total_purchase_value"] / agg["total_spend"].replace(0, float("nan"))).round(4)
    agg["avg_ctr"] = agg["avg_ctr"].fillna(0)
    agg["avg_cpc"] = agg["avg_cpc"].fillna(0)
    agg["avg_cpm"] = agg["avg_cpm"].fillna(0)
    agg["roas"] = agg["roas"].fillna(0)

    # Delta vs previous period
    if not prev_df.empty:
        prev_agg = prev_df.groupby("date").agg(
            total_spend=("spend", "sum"),
            total_results=("results", "sum"),
            total_purchase_value=("purchase_value", "sum"),
        ).reset_index()
        if not prev_agg.empty:
            prev_row = prev_agg.iloc[0]
            agg["delta_spend_pct"] = agg["total_spend"].apply(
                lambda x: compute_delta(x, prev_row["total_spend"])
            )
            agg["delta_results_pct"] = agg["total_results"].apply(
                lambda x: compute_delta(x, prev_row["total_results"])
            )
            agg["delta_roas_pct"] = agg["roas"].apply(
                lambda x: compute_delta(x, prev_agg.iloc[0]["total_purchase_value"] / max(prev_row["total_spend"], 0.01))
            )

    return agg


def generate_campaign_performance(df: pd.DataFrame, prev_df: pd.DataFrame) -> pd.DataFrame:
    """One row per campaign per day."""
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby(["date", "campaign_id", "campaign_name"]).agg(
        spend=("spend", "sum"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        reach=("reach", "sum"),
        results=("results", "sum"),
        purchase_value=("purchase_value", "sum"),
        adsets_count=("adset_id", "nunique"),
        ads_count=("ad_id", "nunique"),
        checkout_initiations=("checkout_initiations", "sum"),
    ).reset_index()
    agg["checkout_rate"] = (agg["results"] / agg["checkout_initiations"].replace(0, float("nan")) * 100).round(4).fillna(0)

    agg["ctr"] = (agg["clicks"] / agg["impressions"].replace(0, float("nan")) * 100).round(4).fillna(0)
    agg["cpc"] = (agg["spend"] / agg["clicks"].replace(0, float("nan"))).round(4).fillna(0)
    agg["cpm"] = (agg["spend"] / agg["impressions"].replace(0, float("nan")) * 1000).round(4).fillna(0)
    agg["roas"] = (agg["purchase_value"] / agg["spend"].replace(0, float("nan"))).round(4).fillna(0)
    agg["result_rate"] = (agg["results"] / agg["impressions"].replace(0, float("nan"))).round(6).fillna(0)

    # Delta vs previous period (by campaign)
    if not prev_df.empty:
        prev_agg = prev_df.groupby("campaign_id").agg(
            prev_spend=("spend", "sum"),
            prev_results=("results", "sum"),
            prev_roas=("roas", "mean"),
        ).reset_index()
        agg = agg.merge(prev_agg, on="campaign_id", how="left")
        agg["delta_spend_pct"] = agg.apply(
            lambda r: compute_delta(r["spend"], r.get("prev_spend", 0) or 0), axis=1
        )
        agg["delta_results_pct"] = agg.apply(
            lambda r: compute_delta(r["results"], r.get("prev_results", 0) or 0), axis=1
        )
        agg.drop(columns=["prev_spend", "prev_results", "prev_roas"], errors="ignore", inplace=True)

    return agg


def generate_ad_performance(df: pd.DataFrame, prev_df: pd.DataFrame) -> pd.DataFrame:
    """One row per ad per day."""
    if df.empty:
        return pd.DataFrame()

    # Already at ad level from insights, just clean up
    ad_cols = [
        "date", "campaign_id", "campaign_name", "adset_id", "adset_name",
        "ad_id", "ad_name", "impressions", "reach", "clicks", "spend",
        "cpc", "ctr", "cpm", "frequency", "results", "result_rate",
        "purchase_value", "roas",
        "checkout_initiations", "checkout_rate",
        "quality_ranking", "engagement_ranking", "conversion_ranking",
    ]
    existing_cols = [c for c in ad_cols if c in df.columns]
    agg = df[existing_cols].copy()

    # Delta vs previous period (by ad)
    if not prev_df.empty and "ad_id" in prev_df.columns:
        prev_agg = prev_df.groupby("ad_id").agg(
            prev_spend=("spend", "sum"),
            prev_results=("results", "sum"),
        ).reset_index()
        agg = agg.merge(prev_agg, on="ad_id", how="left")
        agg["delta_spend_pct"] = agg.apply(
            lambda r: compute_delta(r["spend"], r.get("prev_spend", 0) or 0), axis=1
        )
        agg["delta_results_pct"] = agg.apply(
            lambda r: compute_delta(r["results"], r.get("prev_results", 0) or 0), axis=1
        )
        agg.drop(columns=["prev_spend", "prev_results"], errors="ignore", inplace=True)

    return agg


# ── Save CSV (idempotent) ─────────────────────────────────────────────────────
def save_csv(df: pd.DataFrame, path: Path, name: str) -> bool:
    if df.empty:
        print(f"  WARNING: {name} is empty — skipping CSV write")
        return False
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # If existing file has other dates, keep them and overwrite only current dates
    if path.exists():
        existing = pd.read_csv(path, dtype=str)
        if "date" in existing.columns and "date" in df.columns:
            current_dates = df["date"].unique().tolist()
            replaced_count = existing[existing["date"].isin(current_dates)].shape[0]
            if replaced_count > 0:
                print(f"  INFO: Replacing {replaced_count} existing rows for dates: {current_dates}")
            existing = existing[~existing["date"].isin(current_dates)]
            df = pd.concat([existing, df.astype(str)], ignore_index=True)
        # else full overwrite

    df.to_csv(path, index=False)
    print(f"  -> {name}: {len(df)} rows -> {path.name}")
    return True


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Meta Ads Intelligence — Data Processor")
    parser.add_argument(
        "--date",
        required=True,
        help="Primary date to process (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-since",
        default=None,
        help="Start date if processing a range (YYYY-MM-DD). Defaults to --date.",
    )
    args = parser.parse_args()

    try:
        target_date = args.date
        date.fromisoformat(target_date)
    except ValueError:
        print(f"ERROR: Invalid date format: '{args.date}'. Use YYYY-MM-DD.")
        sys.exit(1)

    date_since = args.date_since or target_date
    if args.date_since:
        try:
            date.fromisoformat(args.date_since)
        except ValueError:
            print(f"ERROR: Invalid --date-since format: '{args.date_since}'. Use YYYY-MM-DD.")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Meta Ads Processor — {date_since} to {target_date}")
    print(f"{'='*60}\n")

    # ── Load raw insights ──────────────────────────────────────────────────────
    insights_file = RAW_DIR / "insights" / f"{date_since}_insights.json"
    print(f"Loading insights from: {insights_file}")
    raw_insights = load_json(insights_file)

    if not raw_insights:
        print("  No insight data found. Run meta_collector.py first.")
        print("  Creating empty placeholder CSVs...")

    df = normalize_insights(raw_insights)
    prev_df = load_previous_period(date_since, days_back=7)

    if not prev_df.empty:
        print(f"  Found previous period data for delta calculations")
    else:
        print(f"  No previous period data found — delta columns will be empty")

    print("\nGenerating CSVs...")

    # ── Metrics summary ────────────────────────────────────────────────────────
    summary_df = generate_metrics_summary(df, prev_df, date_since)
    save_csv(summary_df, PROCESSED_DIR / "metrics_summary.csv", "metrics_summary")

    # ── Campaign performance ───────────────────────────────────────────────────
    campaign_df = generate_campaign_performance(df, prev_df)
    save_csv(campaign_df, PROCESSED_DIR / "campaign_performance.csv", "campaign_performance")

    # ── Ad performance ────────────────────────────────────────────────────────
    ad_df = generate_ad_performance(df, prev_df)
    save_csv(ad_df, PROCESSED_DIR / "ad_performance.csv", "ad_performance")

    # ── Validation ────────────────────────────────────────────────────────────
    issues = []
    for csv_name in ["metrics_summary.csv", "campaign_performance.csv", "ad_performance.csv"]:
        csv_path = PROCESSED_DIR / csv_name
        if csv_path.exists():
            check_df = pd.read_csv(csv_path)
            critical_cols = {"spend", "impressions", "clicks"} & set(check_df.columns)
            for col in critical_cols:
                nan_count = check_df[col].isna().sum()
                if nan_count > 0:
                    issues.append(f"{csv_name}:{col} has {nan_count} NaN values")

    print(f"\n{'='*60}")
    print("Processing complete!")
    if issues:
        print("\nValidation issues:")
        for issue in issues:
            print(f"  WARN: {issue}")
    else:
        print("  OK: All CSVs validated (no NaN in critical fields)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
