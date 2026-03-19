---
task: generateMetaReport()
responsável: Alex (@analyst)
responsavel_type: Agente
atomic_layer: Organism
elicit: true
version: "2.1"
story: meta-ads-intelligence
tags:
  - report
  - markdown
  - insights
---

## Task Definition (AIOS Task Format V2.1)

```yaml
task: generateMetaReport()

Entrada:
  - campo: analysis_artifact
    tipo: file (JSON)
    origem: .ai/{date}-analysis.json
    obrigatório: true

  - campo: creatives_artifact
    tipo: file (JSON)
    origem: .ai/{date}-creatives.json
    obrigatório: false  # se existir, incluir no relatório

  - campo: format
    tipo: integer (1-3)
    origem: User Input (elicited)
    default: 1

Saída:
  - campo: report
    tipo: file (Markdown)
    destino: docs/reports/{date}-report.md
    persistido: true
```

---

## Elicitation

```
Qual formato do relatório?

  [1] Completo — executivo + P&L + campanhas + criativos + checklist   ← padrão
  [2] Executivo — resumo e ações prioritárias (1 página)
  [3] Operacional — funil + movimentações (sem P&L detalhado)

Responda [1-3] ou Enter para padrão [1]:
```

---

## Estrutura do Relatório (obrigatória para formato [1])

```markdown
# Meta Ads Intelligence — Relatório {período}

**Conta:** Templo do Perpétuo
**Período:** {since} a {until}
**Gerado em:** {date}
**Verdict:** {SAUDAVEL | ATENCAO | CRITICO}

---

## ⚡ ALERTAS CRÍTICOS

> Só aparece se houver itens [ALTO] nos anomalies. Destacar no topo com ação imediata.

| # | Entidade | Problema | CPA/Status | Ação Imediata |
|---|----------|----------|------------|---------------|
| 1 | AD188 [MDA] ELE TA GANHANDO | CPA R$316 (Corte R$153) | [PAUSAR] | Pausar hoje |

---

## Resumo Executivo

| KPI | Valor | Benchmark | Status |
|-----|-------|-----------|--------|
| Investimento | R$ X | — | — |
| Vendas | X | 499–694/sem | {acima/abaixo} |
| Faturamento bruto | R$ X | — | — |
| Reembolsos | R$ X (X%) | — | {ok/alto} |
| Lucro líquido | R$ X | — | — |
| ROAS | X.XXx | ≥ 1.33x | {status} |
| CPA médio | R$ X | ≤ R$ 102,35 | {status} |

**Veredicto:** {uma frase narrativa do estado geral}

---

## P&L por Produto

| Produto | Gasto | Faturamento | Vendas | CPA | ROAS | Lucro | Status |
|---------|-------|-------------|--------|-----|------|-------|--------|
| MDA | R$X | R$X | X | R$X | X.Xx | R$X | {status} |
| LVC | R$X | R$X | X | R$X | X.Xx | R$X | {status} |
| TEUS | R$X | R$X | X | R$X | X.Xx | R$X | {status} |
| **TOTAL** | **R$X** | **R$X** | **X** | **R$X** | **X.Xx** | **R$X** | **{verdict}** |

> Reembolsos deduzidos: R$X (detalhado abaixo)

---

## Insights — O que os dados dizem

> Esta seção é obrigatória. Análise narrativa — não apenas tabelas.
> Mínimo 4 insights. Máximo 8. Cada um com fato + por que importa + ação.

### 1. [MOTOR DO PERÍODO]
**O que aconteceu:** [produto/criativo X respondeu por Y% do resultado]
**Por quê importa:** [concentração de risco ou oportunidade de escala]
**Ação:** [reforçar, diversificar, ou monitorar]

### 2. [TENDÊNCIA DE ROAS]
**O que aconteceu:** ROAS foi de X.Xx (sem 1) → X.Xx (sem 2) → X.Xx (sem 3)
**Por quê importa:** [subindo = escalar | caindo = investigar fadiga]
**Ação:** [ajuste de budget, renovação de criativos, ou manter curso]

### 3. [VSL VENCEDOR]
**O que aconteceu:** VSL-{X} com CPA R$X vs VSL-{Y} R$X no período
**Por quê importa:** [qual roteiro escalar agora]
**Ação:** [direcionar verba para VSL vencedor]

### 4. [ANOMALIA PRINCIPAL]
**O que aconteceu:** [descrição numérica precisa]
**Por quê importa:** [impacto no P&L se não corrigido]
**Ação:** [corretiva imediata]

---

## Análise Semana a Semana

| Semana | Gasto | Vendas | ROAS | CPA | Lucro | Tendência |
|--------|-------|--------|------|-----|-------|-----------|
| Sem 1 | R$X | X | X.Xx | R$X | R$X | — |
| Sem 2 | R$X | X | X.Xx | R$X | R$X | {+/-} vs Sem1 |
| Sem 3 | R$X | X | X.Xx | R$X | R$X | {+/-} vs Sem2 |

---

## Campanhas por Fase

| Fase | Campanha | Produto | Gasto | CPA | Status | Ação |
|------|----------|---------|-------|-----|--------|------|
| F3 | ... | MDA | R$X | R$X | [BOM] | Manter |
| F2 | ... | TEUS | R$X | R$X | [LIMITE] | Monitorar |
| F1 | ... | MDA | R$X | R$X | [ALVO] | → F2 |
| RMKT | ... | MDA | R$X | R$X | [ALVO] | Escalar |

---

## Ranking de Criativos

| Criativo | Produto | VSL | Gasto | CPA Pixel | Status | Ação |
|---------|---------|-----|-------|-----------|--------|------|
| AD182 Remarketing 11 | MDA | VSL-A | R$62 | R$2 | [ALVO] | → F3 |
| ... | | | | | | |

> CPA Pixel = atribuição UTM (vendas_*.csv UTM_CONTENT → ads_*.csv NOME ADS)

---

## VSL A vs VSL B vs VSL C

| Produto | VSL | Criativos | Gasto | Vendas | CPA | ROAS | Verdict |
|---------|-----|-----------|-------|--------|-----|------|---------|
| MDA | VSL-A | X | R$X | X | R$X | X.Xx | {status} |
| MDA | VSL-C | X | R$X | X | R$X | X.Xx | {status} |
| LVC | VSL-B | X | R$X | X | R$X | X.Xx | {status} |
| TEUS | VSL-A | X | R$X | X | R$X | X.Xx | {status} |

---

## Reembolsos

| Produto | Qtd | Valor | % do faturamento | Criativo com mais reembolso |
|---------|-----|-------|-----------------|----------------------------|
| MDA | X | R$X | X% | AD... (UTM) |
| LVC | X | R$X | X% | — |
| TEUS | X | R$X | X% | — |

---

## Movimentações Recomendadas

> Ordenadas por impacto. Executar na ordem. Todas requerem aprovação humana.

### 1. [AÇÃO MAIS URGENTE]
- **Entidade:** [nome do ad/campanha]
- **Ação:** PAUSAR | PROMOVER F1→F2 | PROMOVER F2→F3 | ESCALAR BUDGET | CRIAR VARIAÇÃO
- **Por quê:** [razão com dado numérico]
- **Impacto esperado:** [o que muda se executar]

### 2. ...

---

## Checklist da Semana

> Baseado no dia atual e fase do mês.

**Segunda-feira (planejamento):**
- [ ] Verificar CPAs da semana anterior
- [ ] Decidir criativos F1 para esta semana
- [ ] Conferir budget disponível por produto

**Quarta-feira (meio de semana):**
- [ ] Cortar criativos F1 com CPA > R$153,53 + sem venda em 48h
- [ ] Confirmar se F2 está dentro da janela de 7 dias
- [ ] Checar checkout rates

**Sexta-feira (fechamento):**
- [ ] Consolidar P&L da semana
- [ ] Mover candidatos F1→F2 aprovados
- [ ] Planejar criativos novos para semana seguinte

---

## Anomalias Detectadas

| Severidade | Tipo | Entidade | Métrica | Valor | Threshold | Ação Imediata |
|------------|------|----------|---------|-------|-----------|---------------|

---

## Regras Aplicadas

> Seção obrigatória — nunca omitir.

- CPA targets: ALVO R$92,12 | BOM R$102,35 | LIMITE R$122,82 | CORTE R$153,53
- ROAS benchmark: saudável ≥1.33x | alerta <1.20x | crítico <1.15x
- STATUS filter: apenas APPROVED + COMPLETE (excluídos REFUNDED, PROTESTED)
- Produto principal: match exato (exclui order bumps automaticamente)
- Acelerador: excluído de todos os cálculos
- Fonte: data/sheets/ (Google Sheets — fonte primária)
- {outras regras aplicadas da sessão}

---

## Referência de Dados

| Arquivo | Uso |
|---------|-----|
| data/sheets/{date}_diario_mda.csv | Gasto MDA |
| data/sheets/{date}_diario_lvc.csv | Gasto LVC |
| data/sheets/{date}_diario_teus.csv | Gasto TEUS |
| data/sheets/{date}_vendas_mda.csv | Faturamento MDA (APPROVED+COMPLETE) |
| data/sheets/{date}_vendas_lvc.csv | Faturamento LVC (esteira) |
| data/sheets/{date}_vendas_teus.csv | Faturamento TEUS |
| data/sheets/{date}_reembolsos.csv | Reembolsos discriminados |
| data/sheets/{date}_ads_mda.csv | Criativos MDA |
| data/sheets/{date}_ads_teus.csv | Criativos TEUS |

---

*Gerado pelo Meta Ads Intelligence — Synkra AIOS v2.1*
*Fase: Read-Only — Todas as recomendações requerem execução manual*
```

---

## Post-Conditions

```yaml
post-conditions:
  - docs/reports/{date}-report.md criado
  - Seção "ALERTAS CRÍTICOS" presente SE houver anomalias ALTO
  - Seção "Regras Aplicadas" presente e não vazia
  - Seção "Insights" com ≥ 4 insights narrativos (não apenas tabelas)
  - Zero placeholders {{}} não preenchidos
  - Todos os números referenciados nos dados (sem estimativas)
  - STATUS filter documentado nas regras aplicadas
  - Acelerador explicitamente excluído
```
