#!/usr/bin/env python3
"""
Meta Ads Intelligence — Data Importer
Imports external CSV or JSON files into the pipeline (data/raw/insights/).
Normalizes column names to match the Meta API schema so data_processor.py
can handle imported data the same way as API-collected data.

Usage:
    python scripts/data_importer.py --file export.csv --date-label 2025-01-15
    python scripts/data_importer.py --file export.json --date-label 2025-01-15
    python scripts/data_importer.py --file export.csv --date-label 2025-01-15 --mapping my_mapping.json
    python scripts/data_importer.py --file export.csv --date-label 2025-01-15 --also-process

Supported formats: CSV (.csv), JSON (.json)
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run: pip install -r scripts/requirements.txt")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


# ── Column auto-detection map ────────────────────────────────────────────────
# Maps common source column names (from Meta Business Manager exports,
# Google Sheets, etc.) to the internal schema used by data_processor.py.
COLUMN_MAP = {
    # Campaign
    "Campaign ID": "campaign_id",
    "Campaign id": "campaign_id",
    "campaign id": "campaign_id",
    "ID da campanha": "campaign_id",
    "Campaign Name": "campaign_name",
    "Campaign name": "campaign_name",
    "campaign name": "campaign_name",
    "Nome da campanha": "campaign_name",
    # Ad Set
    "Ad Set ID": "adset_id",
    "Ad set ID": "adset_id",
    "Ad Set id": "adset_id",
    "ad set id": "adset_id",
    "ID do conjunto de anúncios": "adset_id",
    "ID do conjunto de anuncios": "adset_id",
    "Ad Set Name": "adset_name",
    "Ad set name": "adset_name",
    "ad set name": "adset_name",
    "Nome do conjunto de anúncios": "adset_name",
    "Nome do conjunto de anuncios": "adset_name",
    # Ad
    "Ad ID": "ad_id",
    "Ad id": "ad_id",
    "ad id": "ad_id",
    "ID do anúncio": "ad_id",
    "ID do anuncio": "ad_id",
    "Ad Name": "ad_name",
    "Ad name": "ad_name",
    "ad name": "ad_name",
    "Nome do anúncio": "ad_name",
    "Nome do anuncio": "ad_name",
    # Metrics
    "Impressions": "impressions",
    "Impressões": "impressions",
    "Impressoes": "impressions",
    "Término dos relatórios": "date_stop",
    "Reach": "reach",
    "Alcance": "reach",
    "Clicks (all)": "clicks",
    "Clicks (All)": "clicks",
    "Link Clicks": "clicks",
    "Link clicks": "clicks",
    "Clicks": "clicks",
    "Cliques": "clicks",
    "Cliques no link": "clicks",
    "Amount Spent (BRL)": "spend",
    "Amount spent (BRL)": "spend",
    "Amount Spent": "spend",
    "Amount spent": "spend",
    "Spend": "spend",
    "Valor gasto": "spend",
    "Valor usado": "spend",
    "Valor usado (BRL)": "spend",
    "Custo": "spend",
    "CPC (All)": "cpc",
    "CPC (all)": "cpc",
    "CPC": "cpc",
    "CPC (custo por clique no link) (BRL)": "cpc",
    "CTR (All)": "ctr",
    "CTR (all)": "ctr",
    "CTR": "ctr",
    "CTR (taxa de cliques no link)": "ctr",
    "CPM": "cpm",
    "CPM (custo por 1.000 impressões) (BRL)": "cpm",
    "Frequency": "frequency",
    "Frequência": "frequency",
    "Frequencia": "frequency",
    # Dates
    "Reporting starts": "date_start",
    "Reporting Starts": "date_start",
    "Day": "date_start",
    "Date": "date_start",
    "Data": "date_start",
    "Início dos relatórios": "date_start",
    "Inicio dos relatorios": "date_start",
    "Reporting ends": "date_stop",
    "Reporting Ends": "date_stop",
    "Fim dos relatórios": "date_stop",
    "Fim dos relatorios": "date_stop",
    # Campaign / AdSet IDs (PT-BR variants from Meta export)
    "Identificação da campanha": "campaign_id",
    "Identificação do conjunto de anúncios": "adset_id",
    "Identificacao da campanha": "campaign_id",
    "Identificacao do conjunto de anuncios": "adset_id",
    # Revenue
    "Purchase ROAS": "roas",
    "ROAS": "roas",
    "Results": "results",
    "Resultados": "results",
    "Purchase Value": "purchase_value",
    "Purchase value": "purchase_value",
    "Valor de compra": "purchase_value",
    "Conversion Value": "purchase_value",
    # Checkout funnel
    "Finalizações de compra iniciadas": "checkout_initiations",
    "Finalizacoes de compra iniciadas": "checkout_initiations",
    "Finalizações de compra iniciadas no site": "checkout_initiations",
    "Checkout Initiated": "checkout_initiations",
    # Quality rankings
    "Classificação de qualidade": "quality_ranking",
    "Classificacao de qualidade": "quality_ranking",
    "Quality Ranking": "quality_ranking",
    "Classificação da taxa de engajamento": "engagement_ranking",
    "Classificacao da taxa de engajamento": "engagement_ranking",
    "Engagement Rate Ranking": "engagement_ranking",
    "Classificação da taxa de conversão": "conversion_ranking",
    "Classificacao da taxa de conversao": "conversion_ranking",
    "Conversion Rate Ranking": "conversion_ranking",
}

# Fields expected by data_processor.py's normalize_insights()
REQUIRED_FIELDS = ["date_start"]
OPTIONAL_FIELDS = [
    "date_stop", "campaign_id", "campaign_name",
    "adset_id", "adset_name", "ad_id", "ad_name",
    "impressions", "reach", "clicks", "spend",
    "cpc", "ctr", "cpm", "frequency",
    "actions", "action_values",
    "results", "purchase_value", "roas",
    "checkout_initiations",
    "quality_ranking", "engagement_ranking", "conversion_ranking",
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def _parse_number(value):
    """Parse numbers that may use comma as decimal separator (BRL format)."""
    if pd.isna(value) or value == "" or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    # "1.234,56" → "1234.56" (Brazilian/European format)
    if "," in s and "." in s:
        if s.rindex(",") > s.rindex("."):
            s = s.replace(".", "").replace(",", ".")
        # else normal "1,234.56" format
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    # Remove currency symbols
    s = s.replace("R$", "").replace("$", "").replace("€", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_date(value) -> str:
    """Try to parse a date value into YYYY-MM-DD format."""
    if pd.isna(value) or value == "" or value is None:
        return ""
    s = str(value).strip()
    # Already ISO format
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s
    # Try pandas auto-detection
    try:
        # Try DD/MM/YYYY first (common in BR)
        parsed = pd.to_datetime(s, dayfirst=True)
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        try:
            parsed = pd.to_datetime(s)
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return s


def load_external_file(file_path: Path) -> pd.DataFrame:
    """Load CSV or JSON file into a DataFrame."""
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        # Try UTF-8 first, fall back to latin-1 (common for Meta exports in BR)
        try:
            return pd.read_csv(file_path, dtype=str)
        except UnicodeDecodeError:
            return pd.read_csv(file_path, dtype=str, encoding="latin-1")
    elif suffix == ".json":
        text = file_path.read_text(encoding="utf-8")
        data = json.loads(text)
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict) and "data" in data:
            return pd.DataFrame(data["data"])
        else:
            print(f"ERROR: JSON must be an array or have a 'data' key.")
            sys.exit(1)
    else:
        print(f"ERROR: Unsupported file format: '{suffix}'. Use .csv or .json")
        sys.exit(1)


def apply_column_mapping(df: pd.DataFrame, custom_mapping: dict | None = None) -> pd.DataFrame:
    """Rename columns using auto-detection map + optional custom mapping."""
    # Build final mapping: auto-detect first, custom overrides
    mapping = {}
    for src_col in df.columns:
        # Check exact match in COLUMN_MAP
        if src_col in COLUMN_MAP:
            mapping[src_col] = COLUMN_MAP[src_col]
        # Check if already in target format
        elif src_col in OPTIONAL_FIELDS or src_col in REQUIRED_FIELDS:
            pass  # keep as-is
        # Check case-insensitive match
        else:
            for map_key, map_val in COLUMN_MAP.items():
                if src_col.lower().strip() == map_key.lower().strip():
                    mapping[src_col] = map_val
                    break

    # Apply custom mapping (overrides everything)
    if custom_mapping:
        for src, dst in custom_mapping.items():
            if src in df.columns:
                mapping[src] = dst

    if mapping:
        # If multiple source columns map to the same target, keep only the first
        seen_targets = {}
        drop_cols = []
        for src, dst in mapping.items():
            if dst in seen_targets:
                drop_cols.append(src)
            else:
                seen_targets[dst] = src
        if drop_cols:
            df = df.drop(columns=drop_cols, errors="ignore")
            mapping = {k: v for k, v in mapping.items() if k not in drop_cols}
        df = df.rename(columns=mapping)

    return df


def normalize_to_raw_insights(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to the raw insights JSON format expected by data_processor.py."""
    rows = []
    for _, row in df.iterrows():
        entry = {
            "date_start": _parse_date(row.get("date_start", "")),
            "date_stop": _parse_date(row.get("date_stop", row.get("date_start", ""))),
            "campaign_id": str(row.get("campaign_id", "")),
            "campaign_name": str(row.get("campaign_name", "")),
            "adset_id": str(row.get("adset_id", "")),
            "adset_name": str(row.get("adset_name", "")),
            "ad_id": str(row.get("ad_id", "")),
            "ad_name": str(row.get("ad_name", "")),
            "impressions": str(int(_parse_number(row.get("impressions", 0)))),
            "reach": str(int(_parse_number(row.get("reach", 0)))),
            "clicks": str(int(_parse_number(row.get("clicks", 0)))),
            "spend": str(round(_parse_number(row.get("spend", 0)), 2)),
            "cpc": str(round(_parse_number(row.get("cpc", 0)), 4)),
            "ctr": str(round(_parse_number(row.get("ctr", 0)), 4)),
            "cpm": str(round(_parse_number(row.get("cpm", 0)), 4)),
            "frequency": str(round(_parse_number(row.get("frequency", 0)), 2)),
            "actions": [],
            "action_values": [],
            "checkout_initiations": str(int(_parse_number(row.get("checkout_initiations", 0)))),
            "quality_ranking": str(row.get("quality_ranking", "")),
            "engagement_ranking": str(row.get("engagement_ranking", "")),
            "conversion_ranking": str(row.get("conversion_ranking", "")),
        }

        # If purchase_value or results are present, inject them into actions/action_values
        purchase_val = _parse_number(row.get("purchase_value", 0))
        results_val = _parse_number(row.get("results", 0))

        if results_val > 0:
            entry["actions"] = [{"action_type": "purchase", "value": str(results_val)}]
        if purchase_val > 0:
            entry["action_values"] = [{"action_type": "purchase", "value": str(purchase_val)}]

        rows.append(entry)

    return rows


def _json_serializer(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Meta Ads Intelligence — Data Importer",
        epilog="Import external CSV/JSON files into the pipeline for analysis.",
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to the CSV or JSON file to import",
    )
    parser.add_argument(
        "--date-label", required=True,
        help="Date label for the output file (YYYY-MM-DD). Used as the filename key.",
    )
    parser.add_argument(
        "--mapping", default=None,
        help="Path to a JSON file with custom column name mappings ({\"source\": \"target\"})",
    )
    parser.add_argument(
        "--merge", action="store_true",
        help="Merge with existing data for this date instead of overwriting",
    )
    parser.add_argument(
        "--also-process", action="store_true",
        help="Automatically run data_processor.py after import",
    )
    args = parser.parse_args()

    # ── Validate inputs ──────────────────────────────────────────────────────
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    try:
        date.fromisoformat(args.date_label)
    except ValueError:
        print(f"ERROR: Invalid --date-label format: '{args.date_label}'. Use YYYY-MM-DD.")
        sys.exit(1)

    custom_mapping = None
    if args.mapping:
        mapping_path = Path(args.mapping).resolve()
        if not mapping_path.exists():
            print(f"ERROR: Mapping file not found: {mapping_path}")
            sys.exit(1)
        custom_mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    date_label = args.date_label

    print(f"\n{'='*60}")
    print(f"Meta Ads Importer — {file_path.name}")
    print(f"Date label: {date_label}")
    print(f"{'='*60}\n")

    # ── Load file ────────────────────────────────────────────────────────────
    print(f"Loading {file_path.suffix} file...")
    df = load_external_file(file_path)
    print(f"  -> {len(df)} rows, {len(df.columns)} columns")
    print(f"  Columns found: {', '.join(df.columns.tolist())}")

    # ── Map columns ──────────────────────────────────────────────────────────
    print("\nMapping columns...")
    df = apply_column_mapping(df, custom_mapping)
    mapped_cols = [c for c in df.columns if c in REQUIRED_FIELDS + OPTIONAL_FIELDS]
    unmapped_cols = [c for c in df.columns if c not in REQUIRED_FIELDS + OPTIONAL_FIELDS]
    print(f"  Mapped:   {', '.join(mapped_cols)}")
    if unmapped_cols:
        print(f"  Ignored:  {', '.join(unmapped_cols)}")

    # ── Remove summary/total rows ────────────────────────────────────────────
    # Meta Ads Manager CSV exports include a summary row (first data row)
    # where entity name columns (ad_name, adset_name, campaign_name) are
    # empty but metric columns (spend, impressions) have aggregated values.
    # Including this row double-counts all metrics.
    entity_cols = [c for c in ["ad_name", "adset_name", "campaign_name"] if c in df.columns]
    if entity_cols:
        metric_cols = [c for c in ["spend", "impressions"] if c in df.columns]
        all_entities_empty = df[entity_cols].apply(
            lambda col: col.isna() | (col.astype(str).str.strip() == ""), axis=0
        ).all(axis=1)
        has_metrics = pd.Series(False, index=df.index)
        for mc in metric_cols:
            has_metrics = has_metrics | (df[mc].apply(_parse_number) > 0)
        summary_mask = all_entities_empty & has_metrics
        n_removed = summary_mask.sum()
        if n_removed > 0:
            df = df[~summary_mask].reset_index(drop=True)
            print(f"  Removed {n_removed} summary/total row(s)")

    # ── Validate required fields ─────────────────────────────────────────────
    missing_required = [f for f in REQUIRED_FIELDS if f not in df.columns]
    if missing_required:
        print(f"\nERROR: Missing required columns after mapping: {', '.join(missing_required)}")
        print(f"  Your columns: {', '.join(df.columns.tolist())}")
        print(f"  Tip: Use --mapping to provide custom column name mappings")
        sys.exit(1)

    # ── Normalize to raw insights format ─────────────────────────────────────
    print("\nNormalizing to raw insights format...")
    insights = normalize_to_raw_insights(df)
    print(f"  -> {len(insights)} insight rows generated")

    # ── Handle merge ─────────────────────────────────────────────────────────
    insights_file = RAW_DIR / "insights" / f"{date_label}_insights.json"
    insights_file.parent.mkdir(parents=True, exist_ok=True)

    if args.merge and insights_file.exists():
        existing_text = insights_file.read_text(encoding="utf-8").strip()
        if existing_text and existing_text != "[]":
            existing = json.loads(existing_text)
            print(f"  Merging with {len(existing)} existing rows")
            insights = existing + insights

    # ── Write insights JSON ──────────────────────────────────────────────────
    insights_file.write_text(
        json.dumps(insights, indent=2, default=_json_serializer),
        encoding="utf-8",
    )
    print(f"  -> Saved: {insights_file.relative_to(PROJECT_ROOT)}")

    # ── Write stub files for campaigns/adsets/ads if missing ─────────────────
    for entity in ["campaigns", "adsets", "ads"]:
        entity_file = RAW_DIR / entity / f"{date_label}_{entity}.json"
        entity_file.parent.mkdir(parents=True, exist_ok=True)
        if not entity_file.exists():
            entity_file.write_text("[]", encoding="utf-8")
            print(f"  -> Created stub: {entity_file.relative_to(PROJECT_ROOT)}")

    # ── Write manifest ───────────────────────────────────────────────────────
    manifest = {
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "import",
        "source_file": str(file_path),
        "date_label": date_label,
        "counts": {
            "insights_rows": len(insights),
        },
        "files": {
            "insights": str(insights_file.relative_to(PROJECT_ROOT)),
        },
        "warnings": [],
    }
    manifest_file = RAW_DIR / f"{date_label}_manifest.json"
    manifest_file.write_text(
        json.dumps(manifest, indent=2, default=_json_serializer),
        encoding="utf-8",
    )

    print(f"\n{'='*60}")
    print("Import complete!")
    print(f"  Insight rows: {len(insights)}")
    print(f"  Output: {insights_file.relative_to(PROJECT_ROOT)}")
    print(f"  Manifest: {manifest_file.relative_to(PROJECT_ROOT)}")
    print(f"{'='*60}\n")

    # ── Auto-process ─────────────────────────────────────────────────────────
    if args.also_process:
        print("Running data_processor.py...")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "data_processor.py"),
             "--date", date_label, "--date-since", date_label],
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            print("WARNING: data_processor.py returned non-zero exit code")
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
