# Guia de Importação — Meta Ads Intelligence

## Estrutura de Pastas

```
data/imports/
├── 2026-02/          ← CSVs de fevereiro (4 semanas)
├── 2026-03/          ← CSVs de março (semana atual em diante)
└── GUIA-DE-IMPORTACAO.md
```

---

## Convenção de Nomenclatura

```
sem[N]-[data-inicio]-anuncio.csv
```

Exemplos:
- `sem1-2026-02-01-anuncio.csv`
- `sem2-2026-02-08-anuncio.csv`
- `sem1-2026-03-10-anuncio.csv`

> Sempre exportar a nível de ANÚNCIO (não campanha) para análise de criativo.

---

## Como Exportar do Meta Ads Manager

1. Abrir Gerenciador de Anúncios
2. Clicar em **Anúncios** na coluna da esquerda (3º nível)
3. Selecionar o período da semana desejada
4. Clicar em **Exportar** → **Exportar dados da tabela (CSV)**
5. Salvar na pasta correta com o nome padronizado

---

## Comandos de Importação

### Fevereiro 2026 — 4 semanas

```bash
# Semana 1 — 01 a 07/02
python scripts/data_importer.py --file "data/imports/2026-02/sem1-2026-02-01-anuncio.csv" --date-label 2026-02-01 --also-process

# Semana 2 — 08 a 14/02
python scripts/data_importer.py --file "data/imports/2026-02/sem2-2026-02-08-anuncio.csv" --date-label 2026-02-08 --also-process

# Semana 3 — 15 a 21/02
python scripts/data_importer.py --file "data/imports/2026-02/sem3-2026-02-15-anuncio.csv" --date-label 2026-02-15 --also-process

# Semana 4 — 22 a 28/02
python scripts/data_importer.py --file "data/imports/2026-02/sem4-2026-02-22-anuncio.csv" --date-label 2026-02-22 --also-process
```

### Março 2026

```bash
# Semana 1 — 10 a 16/03 (reimportar a nível de anúncio)
python scripts/data_importer.py --file "data/imports/2026-03/sem1-2026-03-10-anuncio.csv" --date-label 2026-03-10 --also-process

# Semana 2 — 17 a 23/03 (quando disponível)
python scripts/data_importer.py --file "data/imports/2026-03/sem2-2026-03-17-anuncio.csv" --date-label 2026-03-17 --also-process
```

---

## O que acontece após cada import

Os 3 CSVs em `data/processed/` são **cumulativos** — cada import adiciona
as datas novas sem apagar o histórico:

- `metrics_summary.csv` — totais da conta por semana
- `campaign_performance.csv` — performance por campanha por semana
- `ad_performance.csv` — performance por anúncio/criativo por semana ⭐

Após importar todas as semanas, o @analyst consegue:
- Comparar semanas lado a lado
- Ver evolução de cada criativo ao longo das fases F1 → F2 → F3
- Aplicar regras de corte/promoção com base em histórico real

---

## Checklist semanal de importação

Todo início de semana (segunda-feira):

- [ ] Exportar CSV da semana anterior a nível de ANÚNCIO
- [ ] Salvar em `data/imports/YYYY-MM/` com nome padronizado
- [ ] Executar o comando de importação
- [ ] Rodar análise: `*task analyze-meta-performance`

---

*Synkra AIOS — Meta Ads Intelligence · Atualizado em 2026-03-17*
