# MASTER AIOS — Meta Ads Intelligence
# Synkra AIOS v2.1 — Configuração Central

> Este arquivo é a fonte de verdade para comportamento de todos os agentes.
> Lido automaticamente pelo @analyst antes de qualquer comando.
> Nenhuma regra daqui pode ser sobrescrita por suposição ou default genérico.

---

## 1. IDENTIDADE DOS AGENTES

### @analyst — Alex
- **Responsabilidade:** Análise, diagnóstico, relatórios, insights
- **Ativa em:** todos os comandos `*` (status, hoje, funil, criativos, pl, report, etc.)
- **Regras:** sempre ler `config/analyst-rules.md` ANTES de qualquer dado
- **Benchmarks:** sempre ler `config/account-benchmarks.md` para comparação
- **Proibido:** inventar números, usar `data/processed/` para faturamento, usar ticket médio como multiplicador de receita

### @dev — Dev
- **Responsabilidade:** Coleta de dados, execução de scripts, pipeline
- **Ativa em:** `*collect`, Etapa 1 do `*workflow`
- **Script primário:** `scripts/sheets_collector.py` (Google Sheets → fonte primária)
- **Script secundário:** `scripts/meta_collector.py` (Meta API → apenas para dados de criativos se necessário)
- **Proibido:** modificar arquivos em `data/raw/` (imutáveis), escrever na Meta API

---

## 2. FONTE DE VERDADE (hierarquia estrita)

```
TIER 1 (primário): data/sheets/{date}_*.csv
  → gasto, faturamento, vendas, checkout, criativos, reembolsos

TIER 2 (secundário): data/processed/
  → usar APENAS ads_*.csv quando sheets não cobrir dados de criativos específicos
  → NUNCA usar para faturamento ou vendas

TIER 3 (imutável): data/raw/
  → raw JSON da Meta API — nunca editar, nunca usar como fonte de análise

EXCLUIR SEMPRE:
  → vendas_acelerador_comercial.csv (serviço %, não receita)
  → vendas_upsell_acelerador.csv (idem)
```

---

## 3. BIBLIOTECA CENTRAL

**Todo script Python deve começar com:**
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from aios_utils import *
```

`scripts/aios_utils.py` contém todos os parsers testados:
- `br_num()` — números BR (R$ 1.234,56 → float)
- `parse_date_vendas()` — datas vendas (DD/MM/YYYY - HH:MM)
- `parse_date_ads()` — datas ads (coluna DATA, YYYY-MM-DD)
- `parse_date_diario()` — datas diario (DD/MM/YYYY)
- `parse_impressoes()` — impressões com ponto como milhar
- `load_diario()` — diario completo com filtro de período
- `load_vendas()` — vendas com STATUS filter + produto exato
- `load_ads()` — ads com DATA col + gasto BR parseado
- `load_reembolsos()` — reembolsos filtrados
- `utm_to_ad_num()` — 'video-ad17' → 17
- `nome_to_ad_num()` — 'AD17 [MDA]...' → 17
- `extract_vsl()` — UTM_CAMPAIGN → 'VSL-A'|'VSL-C'
- `extract_fq()` — '-F-' → 'F' | '-Q-' → 'Q'
- `cpa_status()` — float → '[ALVO]'|'[BOM]'|'[LIMITE]'|'[CORTE]'|'[PAUSAR]'
- `calc_cpa()`, `calc_roas()` — cálculos seguros
- `fmt_brl()`, `fmt_cpa()`, `fmt_roas()` — formatação

**REGRAS DE PARSING (nunca reescrever):**
- Datas vendas: `str[:10]` depois `format='%d/%m/%Y'` (tem hora no campo)
- Datas ads: usar coluna `DATA` (não `date` que é Meta API)
- Gasto ads: string BR (ex: `'1.234,56'`) → usar `br_num()`
- Impressões diario: ponto como milhar (`'45.994'` = 45994) → `parse_impressoes()`
- STATUS vendas: filtrar `APPROVED` + `COMPLETE` (NaN excluído automaticamente)
- Produto principal: match **exato** `==` (não `in`) para evitar order bumps
- Output terminal: sem emoji (Windows cp1252 quebra)
- Scripts longos: escrever em arquivo .py, nunca em `python -c "..."` heredoc

---

## 4. CONSTANTES DE NEGÓCIO

```python
# CPA Targets (ticket médio R$184,23 × margem target)
CPA_ALVO   = 92.12    # 2.0x ROI  — [ALVO]
CPA_BOM    = 102.35   # 1.8x ROI  — [BOM]
CPA_LIMITE = 122.82   # 1.5x ROI  — [LIMITE]
CPA_CORTE  = 153.53   # 1.2x ROI  — [CORTE]
# > CORTE = [PAUSAR]

# TICKET MÉDIO: R$184,23
# → USO EXCLUSIVO: calcular thresholds acima
# → PROIBIDO: multiplicar por vendas para estimar faturamento

# ROAS Benchmarks (fev/26)
ROAS_SAUDAVEL = 1.33
ROAS_ALERTA   = 1.20
ROAS_CRITICO  = 1.15

# Produtos principais (match exato)
PRODUTO_MDA  = 'Mestres do Algoritmo | Profissão Youtuber'
PRODUTO_LVC  = 'Lucrando com Vídeos Curtos'
PRODUTO_TEUS = 'Lucrando com Vídeos Curtos'  # TEUS vende LVC

# Status válidos
STATUS_VALIDO = ['APPROVED', 'COMPLETE']
# REFUNDED + PROTESTED = NÃO conta (diferença R$10k+/mês se errar)
```

---

## 5. MAPA DE COMANDOS → AGENTE → SCRIPT

```
*status     → @analyst → quick_status.py --mode status
*hoje       → @analyst → quick_status.py --mode status --period today
*ontem      → @analyst → quick_status.py --mode status --period yesterday
*semana     → @analyst → quick_status.py --mode status --period week
*pausar     → @analyst → quick_status.py --mode alerts
*collect    → @dev     → sheets_collector.py --date-label {hoje}

*funil      → @analyst → funnel_status.py --mode funil
*f1         → @analyst → funnel_status.py --mode f1
*f2         → @analyst → funnel_status.py --mode f2
*f3         → @analyst → funnel_status.py --mode f3
*mover      → @analyst → funnel_status.py --mode mover
*checklist  → @analyst → funnel_status.py --mode checklist

*criativos  → @analyst → quick_status.py --mode creatives
*vsl        → @analyst → funnel_status.py --mode vsl
*reembolsos → @analyst → funnel_status.py --mode reembolsos
*checkout   → @analyst → quick_status.py --mode status (foco IC/checkout)
*fadiga     → @analyst → funnel_status.py --mode fadiga

*pl         → @analyst → quick_status.py --mode pl
*mes        → @analyst → quick_status.py --mode status --period month
*lucro      → @analyst → quick_status.py --mode pl (alias)
*roi [prod] → @analyst → quick_status.py --mode pl --produto {prod}
*budget     → @analyst → funnel_status.py --mode budget

*comparar   → @analyst → weekly_compare.py --weeks 2
*benchmarks → @analyst → (comparar vs account-benchmarks.md)
*tendencia  → @analyst → weekly_compare.py --weeks 4

*report     → @analyst → task: generateMetaReport()
*workflow   → pipeline: meta-ads-intelligence.yaml
*mensal     → @analyst → task: generateMetaReport() --format mensal
```

---

## 6. PROTOCOLO DE EXECUÇÃO DE QUALQUER COMANDO

```
ANTES de qualquer análise (@analyst):
  1. Verificar frescor dos dados (latest_date_label())
     → Se > 1 dia: avisar + oferecer *collect
  2. Ler config/analyst-rules.md
  3. Ler config/account-benchmarks.md
  4. Importar aios_utils
  5. Executar análise com dados reais

DURANTE a análise:
  1. Filtrar STATUS IN ('APPROVED','COMPLETE')
  2. Match exato de produto (==)
  3. Excluir Acelerador
  4. Incluir LVC no faturamento (esteira) mesmo se gasto=0
  5. Incluir gasto LVC no total SE rodou no período

APÓS a análise:
  1. Verificar todos os números vs dados fonte
  2. Gerar insights narrativos (não apenas tabelas)
  3. Classificar por severidade qualquer anomalia
  4. Listar rules_applied
```

---

## 7. PROTOCOLO ANTI-INTERFERÊNCIA

Para garantir que funcionalidades não interfiram entre si:

### Isolamento de dados
- Scripts de análise nunca escrevem em `data/sheets/` (só leitura)
- `data/raw/` é imutável — somente `meta_collector.py` escreve
- `data/processed/` é gerado somente por `data_processor.py`
- `.ai/` é gerado somente por tarefas de análise (artifacts JSON)

### Isolamento de agentes
- @analyst: somente leitura de dados + escrita em `.ai/` e `docs/reports/`
- @dev: somente escrita em `data/` (raw, processed, sheets)
- NUNCA @analyst chama @dev (pipeline unidirecional: coleta → análise)

### Isolamento de cálculos
- Todo cálculo numérico passa por `aios_utils.py`
- Zero aritmética manual em qualquer script
- Scripts novos importam utils; nunca reinventam parsing

### Isolamento de comandos
- Cada comando `*` mapeia para exatamente 1 script/task
- Sem sobreposição de funcionalidade entre comandos
- Período do comando não contamina outros comandos na mesma sessão

---

## 8. QUALIDADE DO OUTPUT — PADRÃO @analyst

Todo output do @analyst deve conter:

**Obrigatório em qualquer resposta de análise:**
- Números precisos (não "~") com fonte identificada
- Comparison vs benchmark (sempre: "X vs benchmark Y")
- Trend direction (subindo/caindo/estável)
- Verdict (SAUDAVEL/ATENCAO/CRITICO)
- Pelo menos 1 insight narrativo com: fato + por que importa + ação

**Proibido:**
- Estimativas sem aviso explícito
- Ticket médio como multiplicador de receita
- Números de períodos diferentes misturados sem aviso
- Análise sem filtro STATUS aplicado
- Relatório sem seção "Regras Aplicadas"

---

## 9. VERSIONAMENTO

```
v1.0 — Inicial (Meta API como fonte primária)
v1.1 — Adicionado suporte Google Sheets
v1.2 — Date ranges ilimitados + data importer
v2.0 — Google Sheets como fonte primária, workflow guiado 5 etapas
v2.1 — aios_utils.py, master.md, tasks alinhadas com sheets-first,
        prompts de insight narrativo, anti-interferência, protocolo de parsing
```

---

*Synkra AIOS — Meta Ads Intelligence Master Config v2.1*
*Atualizar este arquivo sempre que regras de negócio mudarem.*
