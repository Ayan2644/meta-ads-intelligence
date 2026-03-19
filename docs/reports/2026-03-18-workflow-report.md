# Relatório de Performance — Templo do Perpétuo
**Período:** 01/03/2026 → 18/03/2026 (18 dias)
**Gerado em:** 2026-03-18 via *workflow (5 etapas)
**Fonte:** Planilha "Mestres | Todas as Ofertas | Templo do Perpétuo" + Meta Ads API

---

## ETAPA 1–2 — Coleta e Validação ✅

| Fonte | Status | Linhas |
|-------|--------|--------|
| diario_mda | OK | 181 |
| diario_lvc | OK | 124 |
| diario_teus | OK | 71 |
| ads_mda | OK | 4.947 |
| ads_lvc | OK | 3.065 |
| ads_teus | OK | 1.075 |
| vendas_mda | OK | 7.996 |
| vendas_lvc | OK | 3.976 |
| reembolsos | OK | 389 |

---

## ETAPA 3 — Análise de Campanhas

### Consolidado Março (01–18/03)

| Produto | Gasto | Vendas | CPA | ROAS | IC | Checkout | Status |
|---------|-------|--------|-----|------|----|----------|--------|
| **MDA** | R$ 36.741 | 231 | R$ 159,05 | 1,16x | 1.221 | 18,9% | 🔴 CRÍTICO |
| **LVC** | R$ 15.305 | 133 | R$ 115,08 | 1,60x | 1.009 | 13,2% | 🟡 LIMITE |
| **TEUS** | R$ 9.669 | 57 | R$ 169,64 | 1,09x | 1.223 | **4,7%** | 🔴 CRÍTICO |
| **TOTAL** | **R$ 61.716** | **421** | **R$ 146,59** | **1,26x** | **3.453** | 12,2% | 🔴 ALERTA |

> Benchmark ROAS saudável: ≥ 1,33x | Alerta: < 1,20x | Crítico: < 1,15x

### P&L Real (com reembolsos)

| Item | Valor |
|------|-------|
| Receita bruta (421 × R$184,23) | R$ 77.560 |
| Reembolsos | − R$ 15.327 (130 refunds) |
| Receita líquida | R$ 62.233 |
| Investimento | − R$ 61.716 |
| **Lucro líquido** | **R$ 517 (margem 0,8%)** |

> A conta está no breakeven. Pausar campanhas com CPA acima do CORTE é a ação com maior impacto imediato.

### Análise Comparativa Semanal

**Sem 1→2 (01/03→08/03):** Melhor semana — investimento +458%, ROAS 1,30x→1,48x, 33→210 vendas. Lucro R$6.564. ✅

**Sem 2→3 (02/03→15/03):** Virada negativa — investimento −21%, ROAS 1,48x→1,14x, 210→128 vendas. Reembolsos R$6.435. LVC caiu −79 vendas (−83% impressões). Prejuízo R$3.480. ❌

**Sem 3→4 (09/03→18/03, parcial):** Piora — investimento −50%, ROAS 1,14x→0,90x, 128→50 vendas. Prejuízo R$2.362. ❌

> **Padrão identificado:** A conta teve sua melhor semana (Sem 2) e entrou em espiral descendente nas duas semanas seguintes. A queda de LVC (−83% impressões na Sem 3) foi o principal gatilho.

---

## ETAPA 4 — Análise de Criativos

### Candidatos F3 — Promover para Escala (CPA ≤ R$92,12)

| Criativo | Produto | Gasto | Vendas | CPA | CTR | Ação |
|----------|---------|-------|--------|-----|-----|------|
| AD182 — REMARKETING 11 | MDA | R$ 1.722 | 20 | R$ 86,10 | 1,27% | ✅ PROMOVER F3 |
| AD194 — NÃO PERDE TEMPO | MDA | R$ 782 | 10 | R$ 78,24 | 1,38% | ✅ PROMOVER F3 |
| AD69 — EU VOU DESISTIR | MDA | R$ 97 | 2 | R$ 48,64 | 1,55% | ✅ Escalar para validar |
| AD10 — VOCÊ PODE CRIAR | MDA | R$ 187 | 2 | R$ 93,28 | 1,28% | ✅ APROVADO F2 |
| AD11 — EU TINHA UMA MISSÃO | LVC | R$ 86 | 24 | R$ 3,58 | 1,73% | ✅ Top LVC |
| AD10 — PRA QUÊ EU VOU FAZER | LVC | R$ 79 | 29 | R$ 2,72 | 1,23% | ✅ Top LVC |
| AD07 — ESSE TIPO DE VÍDEO | TEUS | R$ 88 | 3 | R$ 29,33 | 1,06% | ✅ Melhor TEUS |

### Pausar Urgente — CPA > R$153,53

| Criativo | Produto | Gasto | Vendas | CPA | Motivo |
|----------|---------|-------|--------|-----|--------|
| AD17 — FACA DO YOUTUBE [camp. AD17] | MDA | R$ 1.766 | 5 | R$ 353,20 | 3,8× acima do CORTE |
| AD45 — EU ACABEI DE CRIAR | MDA | R$ 1.576 | 9 | R$ 175,12 | Acima do CORTE |
| AD168 — REMARKETING 7 | MDA | R$ 1.407 | 8 | R$ 175,81 | Acima do CORTE |
| AD98 — NO VÍDEO V2 | MDA | R$ 989 | 4 | R$ 247,24 | CPA extremo |
| AD02 — EU ACABEI DE CRIAR | MDA | R$ 392 | 0 | sem venda | > R$184 sem resultado |

### Análise de Reembolsos por Criativo (UTM_CONTENT)

| Criativo | Reembolsos | Valor | Alerta |
|----------|------------|-------|--------|
| **video-ad07** | **26x** | **R$ 3.368** | 🔴 Maior volume — cruzar com vendas |
| video-ad188 | 8x | R$ 677 | ⚠️ Monitorar |
| video-ad10 | 6x | R$ 618 | ⚠️ Monitorar |
| video-ad168 | 6x | R$ 477 | ⚠️ Monitorar |
| video-ad182 | 3x | R$ 520 | Observar |

> **video-ad07** é o criativo com mais reembolsos (26x, R$3.368). Verificar se taxa de reembolso justifica o CPA aparente.

### Diagnóstico TEUS — Checkout 4,7%

| | TEUS | MDA | LVC | Benchmark |
|--|------|-----|-----|-----------|
| IC (checkouts iniciados) | 1.223 | 1.221 | 1.009 | — |
| Vendas | 57 | 231 | 133 | — |
| **Checkout rate** | **4,7%** | 18,9% | 13,2% | ≥ 11% |

> Com 1.223 ICs, se o TEUS atingisse 15% de checkout teria **183 vendas** e CPA de **R$52,84** — nível ALVO.
> **O problema do TEUS não é o criativo — é a página de vendas/checkout.**

---

## ETAPA 5 — Movimentações Recomendadas

### 🔴 Ação Imediata (hoje, 18/03)

| Pri | Ação | Alvo | Impacto estimado |
|-----|------|------|-----------------|
| 1 | PAUSAR campanha | [10/03/26] ADV+ VSL A [AD17] | Libera R$3.500/semana — CPA R$353 |
| 1 | PAUSAR campanha | [24/02/26] ADV+ VSL A | Libera R$11.700/semana — CPA R$173 |
| 1 | PAUSAR campanha | [21/02/26] ADV+ VSL A [AD188] | Libera R$1.900/semana — ROAS negativo |
| 1 | PAUSAR criativo | AD45, AD168, AD98 | CPA > CORTE |
| 1 | REDUZIR budget | TEUS | Checkout 4,7% — escala inviável |

### 🟡 Esta Semana

| Pri | Ação | Detalhe |
|-----|------|---------|
| 2 | PROMOVER F3 | AD182 (CPA R$86) + AD194 (CPA R$78) — CPA sustentado no ALVO |
| 2 | INCLUIR F2 | AD10 — VOCÊ PODE CRIAR (CPA R$93, CTR 1,28%) |
| 3 | INVESTIGAR | video-ad07 — 26 reembolsos em março. Calcular taxa de reembolso real |
| 3 | AVALIAR RMKT | Substituir VSL A por VSL C no remarketing (CPA R$146 vs R$101) |
| 4 | DIAGNOSTICAR | Checkout TEUS — landing page, oferta, preço, prova social |
| 4 | REAVALIAR | Campanhas de 12/03 completam janela de 7 dias em 19/03 |

### Checklist Semanal

- [ ] Pausar 3 campanhas com CPA acima do CORTE
- [ ] Pausar criativos AD45, AD168, AD98 individualmente
- [ ] Mover AD182 e AD194 para F3
- [ ] Adicionar AD10 na rotação F2
- [ ] Filtrar reembolsos por video-ad07 na planilha — calcular taxa real
- [ ] Verificar landing page do TEUS (checkout 4,7%)
- [ ] Em 19/03: reavaliar campanhas de 12/03 (fim da janela)
- [ ] Planejar 10 criativos F1 com roteiro diferente (VSL A em fadiga)

---

## Benchmarks vs Fevereiro/2026

| Métrica | Março (atual) | Fev benchmark | Status |
|---------|--------------|---------------|--------|
| ROAS conta | 1,26x | 1,33x (saudável) | 🔴 Abaixo |
| Checkout MDA | 18,9% | ≥ 15% (VSL A) | ✅ OK |
| Checkout LVC | 13,2% | ≥ 11% | ✅ OK |
| Checkout TEUS | 4,7% | — | 🔴 Crítico |
| Reembolsos/dia | 7,2 | — | ⚠️ Alto |

---

*Synkra AIOS — Meta Ads Intelligence | *workflow | 2026-03-18*
*Scripts: quick_status.py + funnel_status.py + weekly_compare.py*
*Fonte: Planilha "Mestres | Todas as Ofertas | Templo do Perpétuo"*
