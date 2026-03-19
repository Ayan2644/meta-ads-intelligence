---
task: fetchMetaData()
responsável: Dev (@dev)
responsavel_type: Agente
atomic_layer: Organism
elicit: false
version: "2.1"
story: meta-ads-intelligence
tags:
  - data-collection
  - sheets-first
  - automation
---

## Task Definition (AIOS Task Format V2.1)

> **FONTE PRIMÁRIA: Google Sheets (scripts/sheets_collector.py)**
> **FONTE SECUNDÁRIA: Meta API (scripts/meta_collector.py) — opcional**
> Ordem obrigatória: Sheets PRIMEIRO, Meta API só se necessário.

```yaml
task: fetchMetaData()

Entrada:
  - campo: date_label
    tipo: string (YYYY-MM-DD)
    origem: User Input ou hoje
    default: today
    obrigatório: true

  - campo: since
    tipo: string (YYYY-MM-DD)
    origem: User Input
    obrigatório: false

  - campo: until
    tipo: string (YYYY-MM-DD)
    origem: User Input
    obrigatório: false

Saída:
  - campo: sheets_csvs
    tipo: files (12 CSVs)
    destino: data/sheets/{date_label}_*.csv
    persistido: true

  - campo: manifest
    tipo: file
    destino: data/sheets/{date_label}_manifest.json
    persistido: true
```

---

## Pre-Conditions

```yaml
pre-conditions:
  - config/google-credentials.json existe
    blocker: true
    error: "Credenciais Google ausentes — verificar config/google-credentials.json"

  - Python 3.8+ disponível
    blocker: true

  - gspread instalado
    blocker: true
    check: python -c "import gspread"
    error: "pip install -r scripts/requirements.txt"

  - pandas instalado
    blocker: true
    check: python -c "import pandas"
```

---

## Execution Steps

### Step 1 — Coletar Google Sheets (OBRIGATÓRIO)

```bash
python scripts/sheets_collector.py --date-label {date_label}
```

**Output esperado (12/12 abas):**
```
[1/12] VENDAS_MDA        → {date_label}_vendas_mda.csv        (X linhas)
[2/12] VENDAS_LVC        → {date_label}_vendas_lvc.csv        (X linhas)
[3/12] VENDAS_TEUS       → {date_label}_vendas_teus.csv       (X linhas)
[4/12] ACOMP_DIARIO_MDA  → {date_label}_diario_mda.csv        (X linhas)
[5/12] ACOMP_DIARIO_LVC  → {date_label}_diario_lvc.csv        (X linhas)
[6/12] ACOMP_DIARIO_TEUS → {date_label}_diario_teus.csv       (X linhas)
[7/12] ADS_MDA           → {date_label}_ads_mda.csv           (X linhas)
[8/12] ADS_LVC           → {date_label}_ads_lvc.csv           (X linhas)
[9/12] ADS_TEUS          → {date_label}_ads_teus.csv          (X linhas)
[10/12] REEMBOLSOS       → {date_label}_reembolsos.csv        (X linhas)
[11/12] VENDAS_ACEL_COM  → {date_label}_vendas_acelerador_comercial.csv (ignorar)
[12/12] VENDAS_UPSELL    → {date_label}_vendas_upsell_acelerador.csv    (ignorar)

Manifest: data/sheets/{date_label}_manifest.json
```

**SE FALHAR:**
```
Erro credenciais: verificar config/google-credentials.json e compartilhamento da planilha
Erro rede: tentar novamente
Erro aba ausente: reportar ao usuário qual aba está faltando
```

### Step 2 — Validar arquivos críticos

```python
from aios_utils import latest_date_label, sheets_path
import os

date = '{date_label}'
criticos = ['diario_mda', 'diario_teus', 'vendas_mda', 'vendas_lvc', 'vendas_teus', 'reembolsos']

for alias in criticos:
    path = sheets_path(alias, date)
    if not os.path.exists(path):
        print(f"ERRO: {path} ausente")
    else:
        import pandas as pd
        df = pd.read_csv(path)
        print(f"OK: {alias} — {len(df)} linhas")
```

### Step 3 — (Opcional) Coletar Meta API

Executar APENAS se análise de criativos exigir dados que não estão nas planilhas:

```bash
python scripts/meta_collector.py --date-range {range}
python scripts/data_processor.py --date {date_label}
```

**Output:**
- `data/raw/` → JSONs brutos (imutáveis)
- `data/processed/` → CSVs normalizados (usar APENAS para ads_*.csv quando sheets não cobrir)

### Step 4 — Confirmar coleta

```
════════════════════════════════════════════
  Coleta concluída: {date_label}
════════════════════════════════════════════
  Google Sheets: 12/12 abas coletadas
  Arquivos criticos: OK
  Tamanho total: {N} linhas

  Pronto para análise:
  → *workflow | *status | *funil | *report
════════════════════════════════════════════
```

---

## Post-Conditions

```yaml
post-conditions:
  - 12 CSVs em data/sheets/{date_label}_*.csv
  - manifest.json criado com contagem de linhas
  - diario_mda, vendas_mda, reembolsos presentes e não vazios
  - LVC pode ter linhas reduzidas (parou ~09/03/2026) — isso é esperado
```

---

## Mapeamento Planilha → Arquivo

| Aba Google Sheets | Arquivo CSV | Uso |
|-------------------|-------------|-----|
| VENDAS_MDA | vendas_mda.csv | Faturamento MDA real |
| VENDAS_LVC | vendas_lvc.csv | Faturamento LVC (esteira) |
| VENDAS_TEUS | vendas_teus.csv | Faturamento TEUS |
| ACOMPANHAMENTO_DIARIO_MDA | diario_mda.csv | Gasto MDA por dia |
| ACOMPANHAMENTO_DIARIO_LVC | diario_lvc.csv | Gasto LVC (histórico) |
| ACOMPANHAMENTO_DIARIO_TEUS | diario_teus.csv | Gasto TEUS por dia |
| ADS_MDA | ads_mda.csv | Criativos MDA |
| ADS_LVC | ads_lvc.csv | Criativos LVC |
| ADS_TEUS | ads_teus.csv | Criativos TEUS |
| REEMBOLSOS | reembolsos.csv | Reembolsos por produto |
| VENDAS_ACELERADOR_COMERCIAL | vendas_acelerador_comercial.csv | **IGNORAR** |
| VENDAS_UPSELL_ACELERADOR | vendas_upsell_acelerador.csv | **IGNORAR** |

---

## Performance

```yaml
duration_expected: 10-20s (Google Sheets API)
custo: zero (Google Sheets API gratuita)
```
