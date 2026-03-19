---
task: analyzeMetaPerformance()
responsável: Alex (@analyst)
responsavel_type: Agente
atomic_layer: Organism
elicit: true
version: "2.1"
story: meta-ads-intelligence
tags:
  - analysis
  - performance
  - insights
  - sheets-first
---

## Task Definition (AIOS Task Format V2.1)

> **FONTE DE VERDADE: `data/sheets/` — nunca `data/processed/` para faturamento ou vendas.**
> **BIBLIOTECA: usar `scripts/aios_utils.py` para todos os cálculos. Zero aritmética manual.**

```yaml
task: analyzeMetaPerformance()

Entrada:
  - campo: focus
    tipo: integer (1-5)
    origem: User Input (elicited)
    obrigatório: true

  - campo: analyst_rules
    tipo: file
    origem: config/analyst-rules.md     # LER PRIMEIRO — obrigatório
    obrigatório: true

  - campo: account_benchmarks
    tipo: file
    origem: config/account-benchmarks.md
    obrigatório: true

  - campo: diario_mda
    tipo: file
    origem: data/sheets/{date}_diario_mda.csv
    obrigatório: true

  - campo: diario_teus
    tipo: file
    origem: data/sheets/{date}_diario_teus.csv
    obrigatório: true

  - campo: diario_lvc
    tipo: file
    origem: data/sheets/{date}_diario_lvc.csv
    obrigatório: false  # LVC pode estar parado — gasto entra se rodou no período

  - campo: vendas_mda
    tipo: file
    origem: data/sheets/{date}_vendas_mda.csv
    filtro: STATUS IN ('APPROVED','COMPLETE') + PRODUTO == 'Mestres do Algoritmo | Profissão Youtuber'
    obrigatório: true

  - campo: vendas_lvc
    tipo: file
    origem: data/sheets/{date}_vendas_lvc.csv
    filtro: STATUS IN ('APPROVED','COMPLETE') + PRODUTO == 'Lucrando com Vídeos Curtos'
    obrigatório: true

  - campo: vendas_teus
    tipo: file
    origem: data/sheets/{date}_vendas_teus.csv
    filtro: STATUS IN ('APPROVED','COMPLETE') + PRODUTO == 'Lucrando com Vídeos Curtos'
    obrigatório: true

  - campo: reembolsos
    tipo: file
    origem: data/sheets/{date}_reembolsos.csv
    obrigatório: true

  # EXCLUIR SEMPRE:
  # vendas_acelerador_comercial.csv  → serviço com %, NÃO é receita
  # vendas_upsell_acelerador.csv     → idem

Saída:
  - campo: analysis_artifact
    tipo: file (JSON)
    destino: .ai/{date}-analysis.json
    persistido: true
```

---

## Elicitation (obrigatória antes de qualquer leitura)

```
════════════════════════════════════════════════════════════
  Meta Ads Intelligence — @analyst
════════════════════════════════════════════════════════════

  Qual é o foco da análise?

  [1] Visão geral — P&L, CPA, ROAS por produto vs benchmarks
  [2] Funil F1/F2/F3 — status de cada fase, movimentos, janelas
  [3] Produto específico — MDA | LVC | TEUS em detalhe
  [4] Alerta de corte — o que pausar AGORA, sem enrolação
  [5] Análise completa — todos os itens acima

  Responda [1-5] ou Enter para padrão [1]:
════════════════════════════════════════════════════════════
```

---

## STEP 0 — MANDATORY: ler arquivos de configuração ANTES de qualquer dado

```
1. Read: config/analyst-rules.md
2. Read: config/account-benchmarks.md
```

Extrair e registrar em `rules_applied`:
- CPA targets (ALVO / BOM / LIMITE / CORTE)
- ROAS de referência (saudável / alerta / crítico)
- Benchmarks de checkout por produto e VSL
- Regras de funil (F1/F2/F3, janela de 7 dias)
- Rota definitiva de dados (Seção 10)

**LOG obrigatório:**
```
✓ Config carregada:
  CPA: ALVO R$92,12 | BOM R$102,35 | LIMITE R$122,82 | CORTE R$153,53
  ROAS: saudável ≥1.33x | alerta <1.20x | crítico <1.15x
  Checkout LVC VSL B: ≥11% | MDA VSL A: ≥15% | MDA VSL C: ≥21%
  Dados: data/sheets/ (fonte primária)
```

---

## STEP 1 — Carregar e validar dados

Usar `scripts/aios_utils.py`:

```python
from aios_utils import load_diario, load_vendas, load_reembolsos, br_num, calc_cpa, calc_roas

# Carregar
diario_mda  = load_diario('mda',  year=Y, month=M)
diario_lvc  = load_diario('lvc',  year=Y, month=M)   # pode estar vazio se LVC parou
diario_teus = load_diario('teus', year=Y, month=M)

vendas_mda  = load_vendas('mda',  year=Y, month=M, apenas_principal=True)
vendas_lvc  = load_vendas('lvc',  year=Y, month=M, apenas_principal=True)
vendas_teus = load_vendas('teus', year=Y, month=M, apenas_principal=True)

reembolsos  = load_reembolsos(year=Y, month=M)
```

**Validação crítica antes de prosseguir:**
- `sum(diario_mda.GASTO) > 0` → conta ativa no período
- `len(vendas_mda) > 0` → há vendas para analisar
- `STATUS filter aplicado` → apenas APPROVED + COMPLETE
- `produto == exato` (não 'in') → order bumps excluídos

---

## STEP 2 — Calcular P&L por produto

```python
# POR PRODUTO:
gasto_mda   = diario_mda.GASTO.sum()
fat_mda     = vendas_mda.VALOR_PAGO.sum()
vendas_n_mda = len(vendas_mda)
reemb_mda   = reembolsos[reembolsos.PRODUTO.str.contains('Mestres')].VALOR_REEMBOLSO.sum()
lucro_mda   = fat_mda - gasto_mda

# Idem para LVC e TEUS
# TOTAL = somar os três (gasto LVC entra se rodou no período)
gasto_total  = gasto_mda + gasto_lvc + gasto_teus
fat_total    = fat_mda + fat_lvc + fat_teus
reemb_total  = reembolsos.VALOR_REEMBOLSO.sum()
lucro_liquido = fat_total - gasto_total - reemb_total
roas_total   = calc_roas(fat_total, gasto_total)
```

---

## STEP 3 — Aplicar framework de análise por foco

### FOCO 1 — Visão Geral (P&L + benchmarks)

**Executar:**
1. P&L consolidado (gasto / faturamento / reembolsos / lucro / ROAS) — total + por produto
2. Comparar ROAS vs benchmarks do `account-benchmarks.md`
3. Comparar CPA por produto vs targets (ALVO/BOM/LIMITE/CORTE)
4. Semana a semana dentro do período (identificar tendência)
5. Checkout rate por produto (`IC` do diario / link clicks)

**Verdict obrigatório:**
- `SAUDAVEL` → ROAS ≥ 1.33x + CPA ≤ BOM + sem alertas críticos
- `ATENCAO` → ROAS entre 1.20x e 1.33x OU CPA entre LIMITE e CORTE
- `CRITICO` → ROAS < 1.20x OU CPA > CORTE em mais de um produto

### FOCO 2 — Funil F1/F2/F3

**Executar:**
```python
from aios_utils import load_ads, extract_fq

ads_mda  = load_ads('mda',  year=Y, month=M)
ads_teus = load_ads('teus', year=Y, month=M)
```

Classificar cada campanha por fase via prefixo nome / UTM_CAMPAIGN:
- `[F3]` ou `ESCALA` → F3 (scaling)
- `[F2]` ou `ARENA` ou `VSL` ou `CBO` → F2 (testing at scale)
- `[F1]` ou `TESTE` ou `LAB` ou `ABO` → F1 (lab)
- `[Q]` ou `RMKT` ou `REMARKETING` → RMKT (quente)
- `-F-` → tráfego frio | `-Q-` → tráfego quente

Para cada fase:
- Gasto total, CPA médio, status vs targets
- Criativos candidatos a promoção (CPA ≤ R$102,35 em F1)
- Criativos candidatos a corte (CPA > R$153,53 + sem venda em 2 dias)
- Verificar janela de orçamento (7 dias) antes de recomendar ajuste

### FOCO 3 — Produto específico

Análise isolada do produto selecionado:
- P&L completo com ordem de bumps
- CPA diário (tendência)
- Checkout rate vs benchmark
- Criativos por fase com CPA
- VSL breakdown

### FOCO 4 — Alerta de corte

Lista direta, sem enrolação:
```
PAUSAR AGORA:
1. [NOME AD] — CPA R$XXX (CORTE = R$153,53) + X dias sem venda → Pausar
2. ...

MONITORAR (24h):
1. [NOME AD] — CPA R$XXX (LIMITE) → Se não melhorar amanhã, pausar
```

### FOCO 5 — Análise completa
Executar focos 1, 2 e 3 (todos os produtos).

---

## STEP 4 — Gerar INSIGHTS NARRATIVOS (obrigatório)

Este passo transforma tabelas em inteligência acionável.
**Não é opcional. Relatórios sem insights narrativos estão incompletos.**

Para cada insight relevante, escrever no formato:
```
[TÍTULO DO INSIGHT]
O que aconteceu: [fato numérico preciso]
Por quê importa: [implicação para o negócio]
Ação sugerida: [o que fazer]
```

**Categorias de insights obrigatórias:**

**A) Motor da semana/mês:**
Qual produto/criativo/VSL está sustentando o resultado?
Qual a concentração de risco?
Ex: "AD182 Remarketing responde por 33 vendas com CPA R$2 — se saturar, 10% do volume some"

**B) Tendência de ROAS:**
ROAS está subindo, estável ou caindo semana a semana?
Qual produto está puxando o movimento?

**C) Anomalias detectadas:**
| Severidade | Tipo | Entidade | Descrição |
|------------|------|----------|-----------|
| ALTO | Concentração de risco | AD07 LVC | 52 vendas, R$8.809 gasto — 1 criativo = 41% do gasto LVC |
| ALTO | CPA muito acima do corte | AD188 MDA | CPA R$316 (corte R$153,53) — R$5.380 desperdiçado |
| MEDIO | Checkout abaixo benchmark | TEUS | IC/checkout não disponível nos dados — verificar |
| BAIXO | Criativo novo sem dados | AD205, AD206 | Gasto mas 0 atribuições UTM — aguardar 2 dias |

**D) Avaliação VSL:**
Qual VSL está ganhando por produto?
VSL C supera VSL A em checkout MDA? (benchmark: sim)

**E) Alerta de fadiga:**
Algum criativo com frequência > 2.5x (F3) ou > 3.0x (F2)?

---

## STEP 5 — Salvar artifact JSON

```json
{
  "date": "YYYY-MM-DD",
  "period": {"since": "...", "until": "..."},
  "analysis_focus": 1,
  "rules_applied": ["..."],
  "verdict": "SAUDAVEL | ATENCAO | CRITICO",
  "pl": {
    "mda": {"gasto": 0, "faturamento": 0, "vendas": 0, "cpa": 0, "roas": 0, "lucro": 0},
    "lvc": {...},
    "teus": {...},
    "total": {"gasto": 0, "faturamento": 0, "reembolsos": 0, "lucro_liquido": 0, "roas": 0}
  },
  "benchmarks_comparison": {
    "roas_status": "saudavel | alerta | critico",
    "checkout_mda_vsla": "...", "checkout_mda_vslc": "...", "checkout_lvc_vslb": "..."
  },
  "anomalies": [
    {"severity": "ALTO | MEDIO | BAIXO", "type": "...", "entity": "...", "description": "...", "action": "..."}
  ],
  "insights": ["narrative insight 1", "narrative insight 2"],
  "recommendations": [
    {"priority": 1, "action": "...", "entity": "...", "reason": "...", "impact": "..."}
  ],
  "campaigns": [],
  "creatives": []
}
```

---

## Post-Conditions

```yaml
post-conditions:
  - .ai/{date}-analysis.json existe e é JSON válido
  - rules_applied não está vazio (analyst-rules.md foi lido)
  - verdict preenchido (SAUDAVEL | ATENCAO | CRITICO)
  - pl.total.roas calculado com dado real (não estimativa)
  - insights array com ≥ 3 itens narrativos
  - recommendations ordenadas por prioridade (1 = mais urgente)
  - NENHUM número inventado — tudo referenciado nos dados
  - STATUS filter aplicado (apenas APPROVED + COMPLETE)
  - Acelerador excluído de todos os cálculos
```

---

## Defaults (substituídos por analyst-rules.md)

| Métrica | Default | Fonte real |
|---------|---------|------------|
| CPA Alvo | R$ 92,12 | analyst-rules.md |
| CPA Corte | R$ 153,53 | analyst-rules.md |
| ROAS saudável | 1.33x | account-benchmarks.md |
| Checkout LVC VSL B | ≥11% | account-benchmarks.md |
| Checkout MDA VSL C | ≥21% | account-benchmarks.md |
| Ticket médio | R$ 184,23 | **SÓ para CPA targets. NUNCA para calcular receita.** |
