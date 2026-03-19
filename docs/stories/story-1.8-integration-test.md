# Story 1.8 — Teste de Integração End-to-End

<!-- Source: Implementation plan -->
<!-- Context: Validation of complete Meta Ads Intelligence pipeline -->

## Status: Draft

## Story

As a @qa agent,
I want to validate the complete meta-ads-intelligence pipeline end-to-end,
so that the user can confidently run daily analysis knowing all components work correctly.

## Pre-Requisites

- [ ] User has `.env` configured with a valid Meta API access token
- [ ] `pip install -r scripts/requirements.txt` completed
- [ ] Stories 1.1 through 1.7 implemented

## Validation Checklist

### Phase 1 — Data Collection

- [ ] `python scripts/meta_collector.py --date-range yesterday` runs without Python errors
- [ ] 4 JSON files created in `data/raw/`:
  - [ ] `data/raw/campaigns/{date}_campaigns.json`
  - [ ] `data/raw/adsets/{date}_adsets.json`
  - [ ] `data/raw/ads/{date}_ads.json`
  - [ ] `data/raw/insights/{date}_insights.json`
- [ ] `data/raw/{date}_manifest.json` exists with `counts` key populated
- [ ] Manifest `counts.campaigns` + `counts.adsets` + `counts.ads` are non-negative integers
- [ ] No unhandled exceptions in collector output

### Phase 2 — Data Processing

- [ ] `python scripts/data_processor.py --date {date}` runs without errors
- [ ] `data/processed/metrics_summary.csv` created with correct columns
- [ ] `data/processed/campaign_performance.csv` created
- [ ] `data/processed/ad_performance.csv` created
- [ ] No NaN values in critical columns: `spend`, `impressions`, `clicks`
- [ ] `roas` column present and calculated as `purchase_value / spend`
- [ ] `result_rate` column present

### Phase 3 — Full Pipeline

- [ ] `*workflow meta-ads-intelligence` initiates all 3 phases
- [ ] Phase 1 completes before Phase 2 starts (sequential dependency respected)
- [ ] @analyst reads `config/analyst-rules.md` before reading any CSV
- [ ] Elicitation menu (1-5) appears before analysis starts
- [ ] `.ai/meta-analysis-{date}.json` created with all required fields
- [ ] `rules_applied` field in JSON is non-empty array

### Phase 4 — Report Validation

- [ ] `docs/reports/{date}-daily-report.md` created
- [ ] No `{{PLACEHOLDER}}` strings remain in the report
- [ ] Section "Regras Aplicadas" is present and lists at least one rule
- [ ] Recommendations section is numbered and non-empty
- [ ] Report renders correctly as Markdown (valid syntax)

### Phase 5 — Idempotency

- [ ] Running the full pipeline a second time on the same date does NOT duplicate rows in CSVs
- [ ] Second run overwrites, not appends, in `data/processed/`
- [ ] Second run generates a new `.ai/meta-analysis-{date}.json` (overwrites)
- [ ] Second run generates a new report (overwrites)

### Phase 6 — Error Handling

- [ ] Invalid token in `.env` → script halts with clear message pointing to `.env`
- [ ] Missing `.env` → script halts with message to copy `.env.example`
- [ ] Missing SDK → script halts with `pip install` instruction
- [ ] Empty account (no campaigns) → scripts complete with warnings, not errors

## Acceptance Criteria

1. All checklist items pass with a real (non-empty) Meta ad account
2. Pipeline runs from zero to report without manual intervention (except elicitation)
3. `rules_applied` in the report reflects what was in `analyst-rules.md`
4. Second run on same day is safe (idempotent)
5. Error messages are actionable (user knows exactly what to fix)

## Notes

- Run with `AIOS_DEBUG=1` if troubleshooting API issues
- Check `data/raw/{date}_manifest.json` for API response counts
- Token must have `ads_read` + `read_insights` + `business_management` permissions
