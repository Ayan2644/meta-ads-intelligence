# Meta Ads Intelligence

Sistema read-only de coleta, processamento e analise de dados da **Meta Marketing API**. Gera relatorios estruturados com insights, anomalias e recomendacoes acionaveis.

> **Fase atual: Read-Only** — Nenhuma escrita na Meta API. Todas as recomendacoes requerem execucao manual.

## Como funciona

```
Meta API ──> Coleta (JSON) ──> Processamento (CSV) ──> Analise ──> Relatorio (.md)
```

O pipeline tem 3 fases:

| Fase | Script / Task | Output |
|------|--------------|--------|
| 1. Coleta | `meta_collector.py` + `data_processor.py` | JSONs em `data/raw/` + CSVs em `data/processed/` |
| 2. Analise | `analyze-meta-performance` (AIOS task) | `.ai/meta-analysis-{date}.json` |
| 3. Relatorio | `generate-meta-report` (AIOS task) | `docs/reports/{date}-daily-report.md` |

## Setup

### Pre-requisitos

- Python 3.8+
- Conta Meta Business com acesso a Marketing API
- Permissoes: `ads_read`, `read_insights`, `business_management`

### Instalacao

```bash
# 1. Clone o repositorio
git clone https://github.com/KaubyOficial/meta-ads-intelligence.git
cd meta-ads-intelligence

# 2. Instale as dependencias
pip install -r scripts/requirements.txt

# 3. Configure as credenciais
cp .env.example .env
# Edite .env com suas credenciais Meta
```

### Variaveis de ambiente (.env)

```env
META_ACCESS_TOKEN=seu_token_aqui
META_AD_ACCOUNT_ID=act_XXXXXXXXXXXXXXXXX
META_APP_ID=seu_app_id
META_APP_SECRET=seu_app_secret
META_API_VERSION=v19.0
```

## Uso

### Coleta + Processamento

```bash
# Dados de ontem (default)
python scripts/meta_collector.py --date-range yesterday

# Ultimos 7, 30, 90, 365 dias
python scripts/meta_collector.py --date-range last_7d
python scripts/meta_collector.py --date-range last_90d
python scripts/meta_collector.py --date-range last_365d

# Presets de periodo
python scripts/meta_collector.py --date-range this_month
python scripts/meta_collector.py --date-range last_quarter
python scripts/meta_collector.py --date-range this_year

# Range customizado (qualquer periodo)
python scripts/meta_collector.py --since 2025-01-01 --until 2025-06-30
python scripts/meta_collector.py --since 2024-01-01 --until 2024-12-31

# Processar os dados coletados
python scripts/data_processor.py --date 2024-01-15
```

**Presets:** `today` | `yesterday` | `last_7d` | `last_14d` | `last_30d` | `last_60d` | `last_90d` | `last_180d` | `last_365d` | `this_month` | `last_month` | `this_quarter` | `last_quarter` | `this_semester` | `last_semester` | `this_year` | `last_year`

**Custom:** `--since YYYY-MM-DD --until YYYY-MM-DD` (qualquer periodo, sem limitacao)

### Importar dados externos

Importe dados de campanhas de arquivos CSV ou JSON (exportados do Meta Business Manager, planilhas, etc.):

```bash
# Importar CSV
python scripts/data_importer.py --file meus_dados.csv --date-label 2025-01-15

# Importar e ja processar automaticamente
python scripts/data_importer.py --file meus_dados.csv --date-label 2025-01-15 --also-process

# Importar JSON
python scripts/data_importer.py --file export.json --date-label 2025-01-15

# Merge com dados existentes (ao inves de sobrescrever)
python scripts/data_importer.py --file extra.csv --date-label 2025-01-15 --merge

# Mapeamento customizado de colunas
python scripts/data_importer.py --file dados.csv --date-label 2025-01-15 --mapping meu_mapeamento.json
```

O importer reconhece automaticamente colunas do Meta Business Manager (pt-BR e en). Se suas colunas tiverem nomes diferentes, crie um arquivo de mapeamento JSON:

```json
{
  "minha_coluna_gasto": "spend",
  "minha_coluna_impressoes": "impressions",
  "data_inicio": "date_start"
}
```

### Pipeline completo (via AIOS)

```
*workflow meta-ads-intelligence
```

## Estrutura do Projeto

```
meta-ads-intelligence/
├── scripts/
│   ├── meta_collector.py       # Coleta dados da Meta API
│   ├── data_processor.py       # Normaliza JSONs em CSVs
│   ├── data_importer.py        # Importa CSV/JSON externos
│   └── requirements.txt        # Dependencias Python
├── config/
│   └── analyst-rules.md        # Regras customizaveis de analise
├── templates/
│   ├── daily-report-tmpl.md    # Template do relatorio diario
│   └── weekly-summary-tmpl.md  # Template do resumo semanal
├── data/
│   ├── raw/                    # JSONs brutos da API (gitignored)
│   └── processed/              # CSVs normalizados
├── docs/
│   ├── reports/                # Relatorios gerados
│   └── stories/                # Stories de desenvolvimento
├── .ai/                        # Artifacts de analise (gitignored)
├── .aios-core/                 # Tasks e workflows AIOS
│   └── development/
│       ├── tasks/              # Definicoes de tasks
│       └── workflows/          # Definicao do pipeline
└── .env.example                # Template de credenciais
```

## CSVs gerados

| Arquivo | Conteudo |
|---------|----------|
| `metrics_summary.csv` | Totais da conta por dia (spend, ROAS, CTR, CPM) |
| `campaign_performance.csv` | KPIs por campanha por dia |
| `ad_performance.csv` | KPIs por anuncio por dia |

## Regras de Analise

Edite `config/analyst-rules.md` para customizar thresholds:

| Metrica | Default | Descricao |
|---------|---------|-----------|
| ROAS minimo | 2.0 | Abaixo = flag de baixa performance |
| CTR minimo | 0.5% | Abaixo = flag de criativo fraco |
| Frequencia alerta | 3.0 | Acima = fadiga de audiencia |
| Spike de spend | 2x media | Acima = anomalia |

## Stack

- **Python 3.8+** — Scripts de coleta e processamento
- **facebook-business SDK** — Integracao com Meta Marketing API
- **pandas** — Processamento e normalizacao de dados
- **Synkra AIOS** — Orquestracao de agentes para analise e relatorios

## Licenca

Uso privado.

---

*Synkra AIOS — Meta Ads Intelligence v1.0*
