# Analyst Rules — Meta Ads Intelligence

> Este arquivo é lido por @analyst ANTES de toda análise.
> As regras aqui definidas SUBSTITUEM todos os defaults do sistema.
> Última atualização: 2026-03-17

---

## 1. Metas da Conta (Account Goals)

**Objetivo primário:** Vendas (Compras) — produto digital

**Receita média real por venda:**
- Produto principal: R$ 173,43
- Order bumps: 4 bumps × ticket médio R$ 36 × taxa de conversão 30% = R$ 10,80
- **Receita média total por venda: R$ 184,23**

**CPA Targets — tabela de referência obrigatória:**

| Label | ROI | Cálculo | CPA | Interpretação |
|-------|-----|---------|-----|---------------|
| CPA ALVO | 2.0x | R$ 184,23 ÷ 2.0 | **R$ 92,12** | Meta ideal — candidato à F3 |
| CPA BOM | 1.8x | R$ 184,23 ÷ 1.8 | **R$ 102,35** | Aprovado para F2 |
| CPA LIMITE | 1.5x | R$ 184,23 ÷ 1.5 | **R$ 122,82** | Máximo tolerável — monitorar |
| CPA CORTE | 1.2x | R$ 184,23 ÷ 1.2 | **R$ 153,53** | Pausar imediatamente se sem venda em 2 dias |

> ⚠️ NUNCA usar o ticket bruto (R$ 197) como base de CPA. Sempre usar R$ 184,23.

**ROAS mínimo aceitável:** 2.0x
**Moeda:** BRL
**Idioma dos relatórios:** Português

---

## 2. Estrutura da Estratégia — Funil F1 → F2 → F3

A conta opera em três fases progressivas. Um criativo só avança quando comprova performance na fase anterior.

```
F1 LABORATÓRIO → Criativos Aprovados → F2 ARENA → Campeões → F3 ESCALA
```

### 🔵 F1 — LABORATÓRIO
- **Estrutura:** ABO — 1 Campanha / X Conjuntos / 1 Criativo por Conjunto (1-X-1)
- **Orçamento:** R$ 50/conjunto/dia
- **Meta:** 10 criativos testados por semana
- **Objetivo:** Testar criativos novos com entrega independente (sem competição interna)
- **Identificação no nome:** campanhas com prefixo `F1`

**Regras de operação F1:**
- Budget FIXO durante os 7 dias — janela de orçamento, não de pausa
- Pausar criativos individualmente NÃO reseta o aprendizado da campanha ABO
- Escala gradual de orçamento dentro da F1 se CPA se aproximar do ALVO antes dos 7 dias

**Regra de corte F1:**
- ⛔ CPA acima de R$ 153,53 + zero venda em 2 dias = PAUSAR imediatamente

**Critério de aprovação para F2:**
- CPA ≤ R$ 102,35 (BOM ou ALVO)
- Pelo menos 1–2 vendas no período de teste
- Performance sustentada por 2 dias consecutivos

---

### 🟠 F2 — ARENA VSL (PRÉ-ESCALA)
- **Estrutura:** CBO — 1 Campanha / 1 Conjunto / X Criativos (1-1-X)
- **Orçamento:** R$ 500 a R$ 1.500/dia
- **Meta:** Manter 3–5 criativos ativos competindo simultaneamente
- **Objetivo:** Pré-escala dos aprovados da F1
- **Identificação no nome:** campanhas com prefixo `F2`

**Regras de operação F2:**
- Campanha CONTÍNUA — criativos ruins pausados, aprovados da F1 preenchem os buracos semanalmente
- Orçamento FIXO por pelo menos 7 dias após qualquer ajuste
- Corte de criativos PERMITIDO a qualquer momento (operação cirúrgica)
- ⚠️ Criativos novos causam 1–2 dias de mini-reaprendizado — não tomar decisão de orçamento nesses dias
- NÃO criar nova F2 a cada semana — a campanha se renova internamente

**Ciclo de renovação F2:**
```
F1 aprova criativos no fim da semana
↓
Criativos ruins na F2 são pausados (CPA acima do limite em 2–4 dias)
↓
Buracos abertos na F2 são preenchidos pelos novos aprovados da F1
↓
A campanha F2 se mantém viva e se renova continuamente
```

**Regra de corte F2:**
- ⛔ CPA acima de R$ 153,53 + zero venda em 2 dias = PAUSAR o criativo

**Critério de promoção para F3:**
- CPA sustentado no nível ALVO (R$ 92,12) por múltiplos dias consecutivos
- Volume de vendas consistente — não apenas CPA isolado

---

### 🟢 F3 — ESCALA TOTAL
- **Estrutura:** CBO — 1 Campanha / 1 Conjunto / X Criativos (1-1-X)
- **Orçamento:** R$ 20.000 a R$ 50.000/mês
- **Meta:** Criativos campeões gerando volume máximo com CPA abaixo do ALVO
- **Cadência:** 1 campanha por mês — renovada com os tops do mês anterior
- **Identificação no nome:** campanhas com prefixo `F3`

**Regras de operação F3:**
- 🔒 Janela de 7 dias para orçamento é RÍGIDA — nenhum ajuste antes de 7 dias completos
- Pausas de criativo são PERMITIDAS a qualquer momento
- ⛔ Criativo com CPA acima de R$ 153,53 por 2 dias consecutivos = PAUSAR o criativo
- Se maioria dos criativos acima do LIMITE = revisar conjunto antes de mexer no orçamento

**Critério de entrada na F3:**
- Foi campeão em pelo menos uma semana de F2
- CPA sustentado no nível BOM ou ALVO por múltiplos dias
- Volume de vendas suficiente para justificar escala elevada

**Critério de saída/pausa da F3:**
- CPA acima de R$ 153,53 por mais de 2 dias consecutivos

---

## 3. Alertas Customizados

| Métrica | Threshold | Ação |
|---------|-----------|------|
| CPA ALVO | ≤ R$ 92,12 | Candidato à F3 |
| CPA BOM | ≤ R$ 102,35 | Aprovado para F2 |
| CPA LIMITE | ≤ R$ 122,82 | Monitorar — máximo tolerável |
| CPA CORTE | > R$ 153,53 + 0 vendas em 2 dias | Pausar imediatamente |
| ROAS mínimo | < 2.0x | Alerta crítico |
| CTR baixo | < 0.5% | Alerta — revisar criativo |
| Frequência | > 3.0x | Alerta — saturação de audiência |
| Frequência F3 | > 2.5x | Alerta antecipado — renovar público |
| Spend sem resultado | > R$ 184,23 sem venda | Avaliar pausa |

---

## 4. Como Classificar Campanhas por Fase

Ao analisar dados, identificar a fase de cada campanha pelo prefixo no nome:

| Prefixo | Fase | Orçamento esperado | Estrutura |
|---------|------|--------------------|-----------|
| `F0` | Engajamento/Aquecimento | Variável | Auxiliar |
| `F1` | Laboratório | ~R$ 50/conjunto/dia | ABO 1-X-1 |
| `F1.5` | Transição/RMKT leve | Variável | Misto |
| `F2` | Arena VSL | R$ 500–1.500/dia | CBO 1-1-X |
| `F3` | Escala Total | R$ 20k–50k/mês | CBO 1-1-X |
| `ASC` | Advantage+ Shopping | Variável | Automático |
| `RMKT` / `[Q]` | Remarketing | Variável | Quente |

> Campanhas com `[F]` no nome = trafego frio. Campanhas com `[Q]` = trafego quente (remarketing).

---

## 5. Processo de Validação Semanal

| Dia | Ação |
|-----|------|
| Segunda | Alocar 10 criativos F1 · Verificar criativos ativos na F2 · Checar janela F3 |
| Quarta | Verificar F1: CPA > R$153,53 + sem venda em 2 dias? Pausar · Checar budget F2 |
| Sexta/Sáb | Fechar leitura F1 · Alocar aprovados (CPA ≤ R$102,35) na F2 · Identificar candidatos à F3 (CPA ≤ R$92,12 por múltiplos dias) |
| Mensal | Compilar campeões das semanas · Montar nova F3 · Encerrar F3 anterior · Ajustar budget com base em ROAS + CPA do mês |

---

## 6. Regras de Análise para @analyst

### Ao analisar campanhas, SEMPRE:

1. **Classificar cada campanha por fase** (F1/F2/F3/RMKT) antes de qualquer julgamento
2. **Usar os CPAs corretos** da tabela da Seção 1 — nunca usar R$ 197 como referência
3. **Considerar a idade da campanha:**
   - F1 com < 3 dias: não tomar decisão de corte ainda — apenas monitorar CPM
   - F1 com 2–3 dias: corte se CPA > R$153,53 + zero venda
   - F1 com 4–7 dias: janela de leitura — observar sem mexer em orçamento
   - F2/F3 recém-ajustadas (< 7 dias do último ajuste): não avaliar orçamento
4. **Separar análise de frio vs quente:** campanhas `[F]` e campanhas `[Q]/RMKT` têm benchmarks diferentes
5. **Identificar em qual etapa do funil o criativo está** e avaliar se deveria avançar, permanecer ou ser pausado
6. **Frequência em F3 > 2.5x** = alerta antecipado de saturação (mais conservador que o default 3.0x)
7. **Campanhas com zero spend:** ignorar na análise de performance — listar apenas como item de higiene da conta
8. **Campanhas com "Cópia" no nome sem gasto:** listar como candidatas a arquivar

### Ao gerar recomendações, SEMPRE:
- Classificar por prioridade (1 = mais urgente)
- Indicar a fase da campanha (F1/F2/F3)
- Justificar com base nas regras deste arquivo
- Nunca recomendar mudança de orçamento em campanha dentro da janela de 7 dias
- Indicar se a recomendação requer ação imediata ou pode aguardar o checklist semanal

### Campo `rules_applied` no JSON de análise deve incluir:
- `funil-f1-f2-f3`
- `cpa-targets-r184`
- `janela-7-dias-orcamento`
- `frio-vs-quente`
- Qualquer regra específica aplicada

---

## 7. O que Ignorar

- Campanhas com gasto zero: listar apenas como higiene, não analisar performance
- Campanhas com prefixo `F0 - ENGAJAMENTO`: objetivo diferente (engajamento/Manychat), não avaliar por CPA de venda
- Oscilações de CPA nos primeiros 1–2 dias após entrada de novo criativo na F2 (mini-reaprendizado)
- Ajustar alertas de frequência para campanhas de vídeo awareness (F0): usar threshold 5.0x

---

## 8. Formato do Relatório

- **Idioma:** Português brasileiro
- **Moeda:** BRL (R$)
- **Sempre incluir:** classificação por fase (F1/F2/F3), tabela de CPA vs targets, status de cada criativo ativo
- **Sempre incluir:** seção "Movimentações Recomendadas" com ações do checklist semanal
- **Sempre incluir:** nota sobre janela de atribuição e impacto nos dados
- **Tabelas de dados brutos:** sim, incluir para campanhas ativas
- **Ordenar recomendações:** por prioridade (1 = mais urgente)

---

---

## 9. Arquivos de Referência Obrigatórios

| Arquivo | Quando ler |
|---------|------------|
| `config/analyst-rules.md` | SEMPRE — antes de qualquer análise |
| `config/account-benchmarks.md` | SEMPRE — para comparação histórica e benchmarks de checkout/ROAS |

---

## 10. ROTA DEFINITIVA DE DADOS — Fontes por Métrica e Comando

> Esta seção define EXATAMENTE qual arquivo, qual coluna e qual filtro usar para cada métrica.
> Seguir esta rota é obrigatório. Desviar dela causa números errados.

---

### 10.1 — Mapa de Arquivos (Google Sheets → CSV local)

| Aba da Planilha | Arquivo CSV | Uso |
|-----------------|-------------|-----|
| ACOMPANHAMENTO_DIARIO_MDA | `data/sheets/{date}_diario_mda.csv` | Gasto, IC, Cliques, Impressões, Alcance, VPV por dia — MDA |
| ACOMPANHAMENTO_DIARIO_LVC | `data/sheets/{date}_diario_lvc.csv` | Gasto, IC, Cliques, Impressões, Alcance, VPV por dia — LVC |
| ACOMPANHAMENTO_DIARIO_TEUS | `data/sheets/{date}_diario_teus.csv` | Gasto, IC, Cliques, Impressões, Alcance, VPV por dia — TEUS |
| VENDAS_MDA | `data/sheets/{date}_vendas_mda.csv` | Faturamento, vendas, UTM, bumps — produto MDA |
| VENDAS_LVC | `data/sheets/{date}_vendas_lvc.csv` | Faturamento, vendas, UTM, bumps — produto LVC (esteira) |
| VENDAS_TEUS | `data/sheets/{date}_vendas_teus.csv` | Faturamento, vendas, UTM, bumps — campanhas TEUS |
| REEMBOLSOS | `data/sheets/{date}_reembolsos.csv` | Reembolsos por data, produto e UTM |
| ADS_MDA | `data/sheets/{date}_ads_mda.csv` | Performance por criativo — MDA |
| ADS_LVC | `data/sheets/{date}_ads_lvc.csv` | Performance por criativo — LVC |
| ADS_TEUS | `data/sheets/{date}_ads_teus.csv` | Performance por criativo — TEUS |
| VENDAS_ACELERADOR_COMERCIAL | ~~`vendas_acelerador_comercial.csv`~~ | **IGNORAR SEMPRE** — serviço com %, não é receita da operação |
| VENDAS_UPSELL_ACELERADOR | ~~`vendas_upsell_acelerador.csv`~~ | **IGNORAR SEMPRE** — idem |

---

### 10.2 — Colunas por Arquivo e Uso Correto

**`diario_*.csv`** — Fonte de gasto e métricas de tráfego agregadas por dia
```
Data            → filtrar por período (formato DD/MM/YYYY)
Gasto           → investimento em anúncios do dia (formato "R$ X.XXX,XX")
Vendas          → conversões rastreadas pelo pixel Meta (subestima — usar como referência, não como verdade)
Cliques no Link → volume de tráfego
Alcance         → pessoas únicas alcançadas
Impressões      → total de exibições
VPV             → visualizações de página de vendas
IC              → Início de Checkout (denominador para taxa de checkout)
Faturamento     → coluna presente em diario_lvc e diario_teus (usar para referência, não como verdade — usar vendas_*.csv)
```

**`vendas_*.csv`** — Fonte de VERDADE para faturamento e contagem de vendas
```
DATA            → data/hora da venda (formato "DD/MM/YYYY - HH:MM")
E-MAIL          → identificador único do comprador
VALOR PAGO      → valor da transação individual (formato "X.XXX,XX" sem R$)
UTM_CAMPAIGN    → campanha que originou a venda
UTM_CONTENT     → criativo específico — cruzar com Ad Name em ads_*.csv
PRODUTO         → nome do produto/oferta comprada
TRANSACTION     → ID único da transação — usar para deduplicação
STATUS          → APPROVED | COMPLETE | REFUNDED | PROTESTED
OFERTA          → código da oferta
```

**`reembolsos.csv`** — Reembolsos registrados por data de ocorrência
```
DATA               → data do reembolso (formato DD/MM/YYYY)
E-MAIL             → comprador reembolsado
VALOR REEMBOLSADO  → valor devolvido
UTM_CONTENT        → criativo do pedido original — cruzar para taxa de reembolso por criativo
PRODUTO            → produto reembolsado
```

**`ads_*.csv`** — Performance por criativo (fonte Meta API + enriquecimento da planilha)
```
Colunas primárias (Meta API):
  date                          → data
  Ad Name                       → nome do criativo na plataforma Meta
  Spend (Cost, Amount Spent)    → gasto do criativo no dia
  Action Omni Purchase          → compras atribuídas pelo pixel
  Impressions                   → impressões
  Inline Link Clicks            → cliques no link
  Action Landing Page View      → visualizações de página de destino (VPV)
  Action 3s Video Views         → views de 3 segundos

Colunas derivadas (planilha):
  NOME ADS    → nome padronizado do criativo
  GASTO       → gasto processado
  COMPRAS     → compras processadas
  IMPRESSÕES  → impressões processadas
  CLIQUES     → cliques processados
  VPG         → visualizações de página de vendas
  VIDEO VIEW  → views de vídeo
  LINK        → URL do criativo
  (colunas "2") → variante / período de comparação
```

---

### 10.3 — Filtros Obrigatórios por Cálculo

| Métrica | Arquivo | Filtro | Coluna | Operação |
|---------|---------|--------|--------|----------|
| **Faturamento bruto** | vendas_*.csv | STATUS IN ('APPROVED','COMPLETE') | VALOR PAGO | SUM |
| **Faturamento principal** | vendas_*.csv | STATUS IN ('APPROVED','COMPLETE') + PRODUTO contém nome do produto principal | VALOR PAGO | SUM |
| **Order bumps** | vendas_*.csv | STATUS IN ('APPROVED','COMPLETE') + PRODUTO NÃO contém produto principal + NÃO contém 'Acelerador' | VALOR PAGO | SUM |
| **Vendas (contagem)** | vendas_*.csv | STATUS IN ('APPROVED','COMPLETE') + PRODUTO = produto principal | — | COUNT |
| **Gasto** | diario_*.csv | data no período + todos os produtos que rodaram | Gasto | SUM |
| **IC (checkout)** | diario_*.csv | data no período | IC | SUM |
| **Taxa de checkout** | diario_*.csv | data no período | Vendas ÷ IC × 100 | CALC |
| **CPA** | — | — | Gasto ÷ Vendas (count) | CALC |
| **ROAS** | — | — | Faturamento bruto ÷ Gasto | CALC |
| **Ticket médio** | vendas_*.csv | STATUS IN ('APPROVED','COMPLETE') | Total Fat ÷ Count(todas as linhas) | CALC |
| **Reembolsos** | reembolsos.csv | data no período | VALOR REEMBOLSADO | SUM |
| **Atribuição UTM** | vendas_*.csv + ads_*.csv | STATUS APPROVED+COMPLETE | UTM_CONTENT = Ad Name | JOIN |

---

### 10.4 — Produtos Principais por Arquivo

| Arquivo | Produto Principal | Match correto no campo PRODUTO |
|---------|------------------|-------------------------------|
| vendas_mda.csv | Mestres do Algoritmo | `PRODUTO.startswith("Mestres do Algoritmo")` |
| vendas_lvc.csv | Lucrando com Vídeos Curtos | `PRODUTO == "Lucrando com Vídeos Curtos"` (exato) |
| vendas_teus.csv | Lucrando com Vídeos Curtos | `PRODUTO == "Lucrando com Vídeos Curtos"` (exato) |

> ⚠️ NUNCA usar `"Lucrando com Vídeos Curtos" in PRODUTO` — o bump "PACK EDIÇÃO MILIONÁRIA (Lucrando com Vídeos Curtos)" também contém esse texto e seria classificado incorretamente como produto principal, inflando vendas e fat. principal.
> TEUS é uma estrutura de campanha que vende o produto LVC. A diferença é o UTM_CAMPAIGN que contém "TEUS" no nome.

---

### 10.5 — Regra de STATUS

```
APPROVED  → pagamento confirmado, em processamento  → CONTA no faturamento
COMPLETE  → liquidado/concluído                     → CONTA no faturamento
REFUNDED  → estornado pelo comprador                → NÃO CONTA
PROTESTED → chargeback / disputado                  → NÃO CONTA
```
> Nunca somar VALOR PAGO sem filtrar por STATUS. A diferença pode ser R$ 10.000+/mês.

---

### 10.6 — Regra de Gasto (Investimento)

```
SEMPRE incluir todos os diario_*.csv com gasto > 0 no período analisado.
Mesmo que uma campanha esteja parada HOJE, se ela rodou durante o período, o gasto ENTRA.

Exemplo: LVC parou em ~09/03/2026.
  → Análise de março inteiro: incluir diario_lvc.csv (tem R$ 15.305,40 de 01-09/03)
  → Análise de abril em diante: diario_lvc.csv provavelmente zerado — verificar antes
```

---

### 10.7 — Rota por Comando

| Comando | Gasto | Faturamento | Criativos | Reembolsos |
|---------|-------|-------------|-----------|------------|
| `*status` / `*hoje` / `*ontem` / `*semana` | diario_mda + diario_teus + diario_lvc (se rodou) | vendas_mda + vendas_teus + vendas_lvc | — | reembolsos.csv (período) |
| `*pl` / `*lucro` | todos diarios | todos vendas (APPROVED+COMPLETE) | — | reembolsos.csv |
| `*criativos` | ads_*.csv (GASTO) | vendas_*.csv UTM_CONTENT join ads Ad Name | ads_*.csv (COMPRAS, IMPRESSÕES, CLIQUES) | reembolsos.csv UTM_CONTENT |
| `*funil` / `*f1` / `*f2` / `*f3` / `*mover` | ads_*.csv por campanha | vendas_*.csv por UTM_CAMPAIGN | ads_*.csv | — |
| `*vsl` | ads_*.csv filtrado por VSL no Ad Name | vendas_*.csv UTM_CONTENT | ads_*.csv | reembolsos.csv |
| `*reembolsos` | — | vendas_*.csv (para calcular taxa) | — | reembolsos.csv UTM cruzado |
| `*checkout` | diario_*.csv | vendas_*.csv | — | — |
| `*comparar` | diario_*.csv semanas | vendas_*.csv semanas | — | reembolsos.csv |
| `*benchmarks` | diario_*.csv | vendas_*.csv | ads_*.csv | — |
| `*workflow` | todos | todos | todos | todos |

---

### 10.8 — O que NUNCA usar como fonte

| Fonte proibida | Por quê |
|----------------|---------|
| `data/processed/campaign_performance.csv` | Dados da Meta API — subestimam vendas (janela de atribuição) |
| `data/processed/ad_performance.csv` | Idem — usar apenas como complemento de ads_*.csv se necessário |
| Coluna `Vendas` do `diario_*.csv` | Pixel Meta subestima conversões — usar só para taxa de checkout (IC÷Vendas) |
| Coluna `Faturamento` do `diario_lvc/teus.csv` | Dado agregado menos preciso — sempre preferir vendas_*.csv |
| `vendas_acelerador_comercial.csv` | Serviço com %, fora da operação |
| `vendas_upsell_acelerador.csv` | Idem |
| Ticket médio R$ 184,23 como multiplicador | Apenas para CPA targets — nunca para calcular receita real |

---

## 11. Protocolo de Precisão Numérica — TOLERÂNCIA ZERO A ERROS

> ⛔ Erros aritméticos em análises diárias se acumulam em distorções graves nas análises macro (semanal/mensal).
> Todo número publicado deve ser verificado antes de apresentar.

### Regras obrigatórias de cálculo:

1. **Faturamento real:** somar VALOR PAGO de cada linha das vendas_*.csv individualmente. Nunca estimar, nunca multiplicar por ticket médio.
2. **Ticket médio R$ 184,23:** uso exclusivo para cálculo de metas de CPA (tabela Seção 1). Proibido usá-lo como multiplicador de receita.
3. **Verificação obrigatória:** após somar qualquer série de valores, refazer a soma antes de publicar. Se houver dúvida, somar uma terceira vez.
4. **Sem arredondamentos não declarados:** se arredondar, indicar explicitamente. Apresentar valores com centavos quando os dados os contêm.
5. **Campanhas ativas (março/2026):** MDA + TEUS. LVC **sem investimento em anúncios**, mas faz parte da esteira — receitas LVC (orgânico, assinatura, remarketing residual) **CONTAM no faturamento total**. Gasto de anúncios = apenas MDA + TEUS.
6. **Acelerador Comercial (vendas_acelerador_comercial.csv / vendas_upsell_acelerador.csv):** **EXCLUIR COMPLETAMENTE** de todas as análises — faturamento, P&L, ROAS, CPA. É um serviço com estrutura de % sobre resultado, não pertence à operação de anúncios. Ignorar esses arquivos em todos os cálculos.
6. **Transparência de dados ausentes:** se algum arquivo estiver desatualizado ou vazio, declarar explicitamente antes de apresentar qualquer número parcial. Nunca apresentar parcial como total.
7. **Reembolsos:** sempre deduzir do faturamento bruto ao calcular faturamento líquido e resultado. Buscar grep "DD/MM/YYYY" no reembolsos.csv antes de fechar qualquer P&L.
8. **Conferência cruzada:** gasto do diário_*.csv vs vendas da vendas_*.csv devem ser lidos de fontes separadas e cruzados — nunca inferir um a partir do outro.

### Status válidos para faturamento:
- **APPROVED** = pago, em processamento → CONTA
- **COMPLETE** = liquidado → CONTA
- **REFUNDED** = estornado → NÃO CONTA
- **PROTESTED** = chargeback/disputado → NÃO CONTA
- Sempre filtrar STATUS IN ('APPROVED','COMPLETE') ao somar vendas_*.csv

### Gasto: incluir TODOS os produtos que rodaram no período
- Mesmo que LVC esteja parado hoje, se rodou em parte do período analisado, o gasto ENTRA.
- Sempre ler diario_mda + diario_teus + diario_lvc e somar todos com gasto > 0 no período.

### Checklist antes de publicar qualquer número:
- [ ] Faturamento: filtrei por STATUS=APPROVED ou COMPLETE?
- [ ] Gasto: incluí todos os diários com gasto no período (MDA+TEUS+LVC se aplicável)?
- [ ] Dupla contagem: verifiquei transaction IDs duplicados entre TEUS e LVC?
- [ ] Dados ausentes: declarei claramente o que está faltando?
- [ ] Soma final: usei script Python, não aritmética manual?

---

*@analyst lê este arquivo antes de toda análise — alterações têm efeito imediato na próxima execução.*
*Synkra AIOS — Meta Ads Intelligence · Atualizado em 2026-03-18*
