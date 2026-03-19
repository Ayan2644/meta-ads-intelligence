# Meta Ads Intelligence Report — {{DATE}}

**Conta:** {{ACCOUNT_ID}}
**Período:** {{DATE_SINCE}} a {{DATE_UNTIL}}
**Análise gerada por:** @analyst
**Foco:** {{ANALYSIS_FOCUS_LABEL}}

---

## Resumo Executivo

| KPI | Hoje | Variação (7d) |
|-----|------|---------------|
| Spend Total | {{TOTAL_SPEND}} | {{DELTA_SPEND}} |
| Resultados | {{TOTAL_RESULTS}} | {{DELTA_RESULTS}} |
| ROAS | {{ROAS}} | {{DELTA_ROAS}} |
| CTR Médio | {{AVG_CTR}}% | — |
| CPM Médio | {{AVG_CPM}} | — |
| CPC Médio | {{AVG_CPC}} | — |
| Impressões | {{TOTAL_IMPRESSIONS}} | — |
| Cliques | {{TOTAL_CLICKS}} | — |

**Veredicto da conta:** {{VERDICT}}

---

## Principais Insights

{{NARRATIVE_INSIGHTS}}

---

## Top Campanhas

| Campanha | Spend | ROAS | Resultados | CTR | Status |
|----------|-------|------|------------|-----|--------|
{{TOP_CAMPAIGNS_TABLE}}

---

## Campanhas Críticas — Atenção Necessária

| Campanha | Spend | ROAS | CTR | Problema | Ação Recomendada |
|----------|-------|------|-----|----------|------------------|
{{BOTTOM_CAMPAIGNS_TABLE}}

---

## Anomalias Detectadas

{{ANOMALIES_SECTION}}

---

## Análise de Criativos

| Anúncio | Campanha | CTR | CPC | Frequência | ROAS | Verdict |
|---------|----------|-----|-----|------------|------|---------|
{{ADS_TABLE}}

---

## Recomendações

> Ordenadas por impacto estimado (1 = mais urgente)

{{RECOMMENDATIONS_LIST}}

---

## Regras Aplicadas

> Regras definidas em `config/analyst-rules.md` que foram utilizadas nesta análise:

{{RULES_APPLIED_LIST}}

---

## Referência de Dados

| Arquivo | Conteúdo |
|---------|----------|
| `data/processed/metrics_summary.csv` | Totais da conta por dia |
| `data/processed/campaign_performance.csv` | KPIs por campanha |
| `data/processed/ad_performance.csv` | KPIs por anúncio |
| `.ai/meta-analysis-{{DATE}}.json` | Artifact de análise completo |

---

*Gerado pelo Meta Ads Intelligence System — Synkra AIOS*
*Fase: Read-Only — Todas as recomendações requerem revisão humana antes de execução*
