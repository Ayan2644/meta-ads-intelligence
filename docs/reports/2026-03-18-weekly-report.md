# Relatório de Performance — Templo do Perpétuo
**Período:** 01/03/2026 a 18/03/2026 (parcial)
**Gerado em:** 2026-03-18 | **Agente:** @analyst
**Fonte primária:** Planilhas Google (gastos + vendas em tempo real) + Meta Ads API

---

## ⚡ Resumo Executivo

| Produto | Gasto | Vendas | CPA | ROAS | IC | Checkout | Status |
|---------|-------|--------|-----|------|----|----------|--------|
| **MDA** | R$ 36.741 | 231 | R$ 159,05 | 1,16x | 1.221 | 18,9% | 🔴 CRÍTICO |
| **LVC** | R$ 15.305 | 133 | R$ 115,08 | 1,60x | 1.009 | 13,2% | 🟡 LIMITE |
| **TEUS** | R$ 9.669 | 57 | R$ 169,64 | 1,09x | 1.223 | 4,7% | 🔴 CRÍTICO |
| **TOTAL** | **R$ 61.715** | **421** | **R$ 146,59** | **1,26x** | **3.453** | **12,2%** | 🔴 ALERTA |

> ⚠️ **ROAS da conta: 1,26x** — abaixo do benchmark saudável (1,33x) e próximo do alerta crítico (< 1,20x).

---

## 💸 P&L Simplificado — Março (1–18)

| Item | Valor |
|------|-------|
| Investimento total (ads) | R$ 61.715 |
| Receita bruta estimada (421 × R$ 184,23) | R$ 77.560 |
| Reembolsos confirmados | - R$ 15.327 |
| **Receita líquida** | **R$ 62.233** |
| **Lucro bruto** | **R$ 518** |
| **Margem** | **0,8%** |

> 🚨 A conta está essencialmente no breakeven. Pausar as campanhas com CPA acima do CORTE é prioridade máxima para recuperar margem.

---

## 🔴 Alertas Críticos — Ação Imediata

### 1. Campanha [10/03/26] ADV+ VSL A [AD17] — PAUSAR AGORA
- **Gasto:** R$ 3.532 | **Vendas:** 10 | **CPA:** R$ 353,20 | **ROAS:** 0,52x
- CPA = 3,8× acima do CORTE (R$ 153,53). Destruição de caixa ativa.
- Janela de 7 dias: cumprida (8 dias desde lançamento)
- **→ PAUSAR IMEDIATAMENTE**

### 2. Campanha [24/02/26] ADV+ VSL A — PAUSAR
- **Gasto:** R$ 11.759 | **Vendas:** 68 | **CPA:** R$ 172,92 | **ROAS:** 1,07x
- Maior campanha da conta com CPA acima do CORTE.
- Janela de 7 dias: cumprida há semanas.
- **→ PAUSAR. Substituir por criativos validados.**

### 3. [21/02/26] ADV+ VSL A [AD188] — PAUSAR
- **Gasto:** R$ 1.858 | **Vendas:** 8 | **CPA:** R$ 232,20 | **ROAS:** 0,79x
- **→ PAUSAR**

### 4. TEUS — Escala Prematura
- Escala de R$ ~150/dia → R$ 1.280/dia sem validação de CPA.
- Checkout rate de **4,7%** (muito abaixo de qualquer benchmark).
- ROAS: 1,09x com 57 vendas e R$ 9.669 investidos.
- **→ Reduzir budget TEUS ao nível de teste até resolver checkout.**

### 5. Reembolsos — 130 em 18 dias (R$ 15.327)
| Produto | Qtd | Valor |
|---------|-----|-------|
| LVC (Lucrando com Vídeos Curtos) | 44 | R$ 7.085 |
| MDA (Mestres do Algoritmo) | 40 | R$ 6.246 |
| Order Bumps (Packs, Ebooks, Grupos) | 45 | R$ 1.655 |
| Acelerador | 1 | R$ 580 |

> **7,3 reembolsos/dia em média** — taxa elevada. Investigar concentração por campanha/criativo via UTM_CONTENT na aba REEMBOLSOS.

---

## 📊 Análise por Campanha (MDA)

| Campanha | Tipo | Gasto | Vendas | CPA | ROAS | Janela | Status |
|----------|------|-------|--------|-----|------|--------|--------|
| [13/12/25] RMKT VSL C | Quente | R$ 4.546 | 45 | R$ 101,02 | 1,82x | ✅ Livre | ✅ BOM — MANTER |
| [22/12/25] MIX VSL C | Frio | R$ 4.115 | 34 | R$ 121,02 | 1,52x | ✅ Livre | ⚠️ LIMITE — Monitorar |
| [13/12/25] ADV+ VSL C | Frio | R$ 4.562 | 32 | R$ 142,56 | 1,29x | ✅ Livre | 🟠 CORTE — 2 dias |
| [13/12/25] RMKT VSL A | Quente | R$ 4.680 | 32 | R$ 146,25 | 1,26x | ✅ Livre | 🟠 CORTE — Avaliar substituição por VSL C |
| [24/02/26] ADV+ VSL A | Frio | R$ 11.759 | 68 | R$ 172,92 | 1,07x | ✅ Livre | 🔴 PAUSAR |
| [12/03/26] ADV+ VSL A [ESCALA] | Frio | R$ 3.830 | 23 | R$ 166,51 | 1,11x | ⏳ 6 dias | 🟡 Aguardar janela (19/03) |
| [10/03/26] ADV+ VSL A [AD17] | Frio | R$ 3.532 | 10 | R$ 353,20 | 0,52x | ✅ Livre | 🔴 PAUSAR URGENTE |
| [12/03/26] RMKT VSL C [ESCALA] | Quente | R$ 2.525 | 15 | R$ 168,31 | 1,09x | ⏳ 6 dias | 🟡 Aguardar janela (19/03) |
| [21/02/26] ADV+ VSL A [AD188] | Frio | R$ 1.858 | 8 | R$ 232,20 | 0,79x | ✅ Livre | 🔴 PAUSAR |
| [08/03/26] RMKT VSL C | Quente | R$ 237 | 0 | — | 0x | ✅ Livre | 🔴 PAUSAR |
| [16/03/26] ADV+ VSL A [F2] | Frio | R$ 129 | 0 | — | 0x | ⏳ 2 dias | 🔵 Nova — Aguardar |

---

## 🎨 Análise de Criativos — MDA

### 🏆 Candidatos F3 (CPA ≤ R$ 92,12 — ALVO)

| Criativo | Gasto | Vendas | CPA | CTR | ROAS | Recomendação |
|----------|-------|--------|-----|-----|------|--------------|
| **AD182 — REMARKETING 11** | R$ 1.722 | 20 | R$ **86,10** | 1,27% | 2,14x | ✅ CANDIDATO F3 — volume consistente |
| **AD194 — NÃO PERDE TEMPO** | R$ 782 | 10 | R$ **78,24** | 1,38% | 2,35x | ✅ CANDIDATO F3 — CTR excelente |
| AD69 — EU VOU DESISTIR | R$ 97 | 2 | R$ 48,64 | 1,55% | 3,80x | ⚡ Alto potencial — escalar para validar volume |
| AD46 — OLHA SÓ MEU CANAL V3 | R$ 87 | 1 | R$ 86,68 | 0,92% | 2,12x | Monitorar — volume baixo |
| AD58 — AQUI MEU CANAL | R$ 74 | 1 | R$ 74,49 | 0,43% | 2,48x | Monitorar — CTR abaixo do benchmark (0,43% < 0,90%) |

### ✅ Aprovados F2 (CPA R$ 92,12–102,35 — BOM)

| Criativo | Gasto | Vendas | CPA | CTR | Recomendação |
|----------|-------|--------|-----|-----|--------------|
| AD10 — VOCÊ PODE CRIAR UM CANAL | R$ 187 | 2 | R$ **93,28** | 1,28% | ✅ APROVADO F2 — incluir na próxima rotação |

### ⚠️ No Limite (CPA R$ 102,35–122,82 — LIMITE)

| Criativo | Gasto | Vendas | CPA | CTR | Status |
|----------|-------|--------|-----|-----|--------|
| AD182 — RMKT 11 (camp. RMKT) | R$ 2.005 | 18 | R$ 111,38 | 1,31% | Monitorar |
| AD150 — CAIO EU LARGO | R$ 2.298 | 19 | R$ 120,92 | 0,64% | ⚠️ CTR abaixo (0,64%) — criativo em fadiga? |
| AD165 — REMARKETING 4 | R$ 1.304 | 12 | R$ 108,63 | 1,08% | Monitorar |
| AD178 — ESSA É A ÚLTIMA CHANCE | R$ 967 | 9 | R$ 107,48 | 1,00% | Monitorar |
| AD169 — REMARKETING 8 — Cópia | R$ 855 | 8 | R$ 106,85 | 0,76% | Nome indica cópia — renomear ou pausar |

### 🔴 Pausar Urgente (CPA > R$ 153,53 ou sem venda)

| Criativo | Gasto | Vendas | CPA | Motivo |
|----------|-------|--------|-----|--------|
| AD17 — FACA DO YOUTUBE [camp. AD17] | R$ 1.766 | 5 | R$ 353,20 | CPA 3,8× acima do CORTE |
| AD45 — EU ACABEI DE CRIAR | R$ 1.576 | 9 | R$ 175,12 | Acima do CORTE |
| AD168 — REMARKETING 7 | R$ 1.407 | 8 | R$ 175,81 | Acima do CORTE |
| AD98 — NO VÍDEO V2 | R$ 989 | 4 | R$ 247,24 | CPA extremo |
| AD100 — NO VÍDEO (camp. 2) | R$ 516 | 2 | R$ 257,92 | CPA extremo |
| AD51 — NO VÍDEO V1 | R$ 256 | 2 | R$ 127,85 | CORTE — monitorar |
| AD170 — RMKT 9 — Cópia | R$ 329 | 1 | R$ 329,46 | Cópia sem padrão + CPA extremo |
| AD99 — NO VÍDEO V3 | R$ 329 | 1 | R$ 328,65 | CPA extremo |
| AD02 — EU ACABEI DE CRIAR (sem venda) | R$ 392 | 0 | — | Gasto acima de R$ 184 sem resultado |

---

## 🆚 VSL A vs VSL C — Análise Comparativa

| VSL | Contexto | CPA médio | ROAS | Veredicto |
|-----|----------|-----------|------|-----------|
| VSL A | Frio (ADV+) | R$ 172,92 | 1,07x | 🔴 Abaixo do mínimo |
| VSL C | Frio (ADV+) | R$ 142,56 | 1,29x | 🟠 No CORTE |
| VSL A | Remarketing | R$ 146,25 | 1,26x | 🟠 No CORTE |
| **VSL C** | **Remarketing** | **R$ 101,02** | **1,82x** | **✅ DOMINANTE** |

> **Confirmado (3ª semana consecutiva):** VSL C supera VSL A em remarketing. Em frio, ambos estão com CPA acima do LIMITE. A conta precisa urgentemente de novos criativos frios com roteiros diferentes.

---

## ⚠️ TEUS — Diagnóstico de Checkout

O problema do TEUS não é o criativo. É o checkout.

| Métrica | TEUS | MDA | LVC |
|---------|------|-----|-----|
| IC (Checkouts iniciados) | 1.223 | 1.221 | 1.009 |
| Vendas | 57 | 231 | 133 |
| **Checkout Rate** | **4,7%** | **18,9%** | **13,2%** |
| Benchmark | — | ≥ 15% (VSL A) | ≥ 11% |

> Com a mesma quantidade de ICs, se o TEUS atingisse 15% de checkout, teria **183 vendas** e CPA de **R$ 52,84** — no nível ALVO. O gargalo está na página de vendas/checkout, não nas campanhas.

**→ Pausar escala TEUS. Diagnosticar checkout: oferta, preço, urgência, prova social.**

---

## 📅 LVC — Performance Semanal (dados disponíveis até 09/03)

| Período | Gasto | Vendas | CPA | ROAS | Checkout | Status |
|---------|-------|--------|-----|------|----------|--------|
| Mar 1–9 | R$ 15.305 | 133 | R$ 115,08 | 1,60x | 13,2% | 🟡 LIMITE |
| Benchmark fev | — | 549–694/sem | — | ≥ 1,33x | ≥ 11% | — |

> LVC é o produto mais saudável da conta neste período. ROAS 1,60x acima do benchmark. Checkout 13,2% dentro do saudável. Monitorar CPA para não cruzar o LIMITE.

---

## 📋 Movimentações Recomendadas

### 🔴 Ações Imediatas (hoje)

| Prioridade | Ação | Campanha/Criativo | Justificativa |
|-----------|------|-------------------|---------------|
| 1 | **PAUSAR** campanha | [10/03/26] ADV+ VSL A [AD17] | CPA R$353 — ROAS 0,52x — destruição de caixa |
| 1 | **PAUSAR** campanha | [24/02/26] ADV+ VSL A | CPA R$173 — maior campanha da conta no PAUSAR |
| 1 | **PAUSAR** campanha | [21/02/26] ADV+ VSL A [AD188] | CPA R$232 — ROAS negativo |
| 1 | **PAUSAR** criativo | AD17 na camp. [AD17] | CPA R$353 |
| 1 | **PAUSAR** criativo | AD45 — EU ACABEI DE CRIAR | CPA R$175 |
| 1 | **PAUSAR** criativo | AD168 — REMARKETING 7 | CPA R$176 |
| 1 | **Reduzir budget** | TEUS | Checkout 4,7% — escala inviável |

### 🟡 Ações Desta Semana

| Prioridade | Ação | Detalhe |
|-----------|------|---------|
| 2 | Promover para F3 | AD182 REMARKETING 11 (CPA R$86,10 — volume consistente) |
| 2 | Promover para F3 | AD194 NÃO PERDE TEMPO (CPA R$78,24 — CTR 1,38%) |
| 2 | Incluir na F2 | AD10 VOCÊ PODE CRIAR (CPA R$93,28 — aprovado) |
| 3 | Avaliar RMKT VSL A | [13/12/25] RMKT VSL A com CPA R$146 — considerar substituição por VSL C |
| 3 | Investigar reembolsos | Cruzar REEMBOLSOS com UTM_CONTENT para identificar criativo/campanha |
| 4 | Diagnosticar checkout TEUS | Página de vendas, oferta, preço — checkout 4,7% é o gargalo real |
| 5 | Reavaliar janelas em 19/03 | Campanhas de 12/03 completam 7 dias |

### 🟢 Checklist Semanal

- [ ] Pausar campanhas priorizadas acima
- [ ] Mover AD182 e AD194 para F3
- [ ] Adicionar AD10 na rotação F2
- [ ] Acessar aba REEMBOLSOS → filtrar por UTM_CONTENT → identificar criativos com alta taxa de reembolso
- [ ] Verificar checkout TEUS na landing page
- [ ] Em 19/03: reavaliar campanhas de 12/03 (final da janela de 7 dias)
- [ ] Novos 10 criativos F1 para semana que vem (roteiro diferente de VSL A — está saturando)

---

## 📌 Nota sobre Atribuição

Os dados de vendas das planilhas (fonte primária) são captados diretamente da plataforma, sem erros de atribuição do Pixel. O CPA calculado aqui usa esses dados como verdade. As discrepâncias com o relatório nativo do Meta (que usa atribuição de 7 dias click / 1 dia view) são esperadas e não devem ser usadas para tomar decisões sem cruzar com a planilha.

---

*Synkra AIOS — Meta Ads Intelligence | @analyst | 2026-03-18*
*Fontes: Planilha "Mestres | Todas as Ofertas | Templo do Perpétuo" + Meta Ads API*
