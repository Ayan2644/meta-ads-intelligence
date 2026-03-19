# Account Benchmarks — Histórico de Performance

> Lido por @analyst como referência comparativa em toda análise.
> Atualizar mensalmente com os dados consolidados do mês anterior.
> Última atualização: 2026-03-17

---

## Como Usar Este Arquivo

- Comparar métricas do período analisado contra os benchmarks abaixo
- Identificar se a conta está acima ou abaixo da performance histórica
- Sinalizar desvios significativos (> 15% acima ou abaixo do benchmark)

---

## Benchmarks — Fevereiro 2026

### Consolidado da Conta

| Métrica | Sem 1 (01–07/02) | Sem 2 (08–14/02) | Sem 3 (15–21/02) | Sem 4 (22–28/02) | Referência |
|---------|------------------|------------------|------------------|------------------|------------|
| Investimento | R$ 35.700 | R$ 48.700 | R$ 45.200 | R$ 36.200 | — |
| Vendas | 499 | 694 | 549 | 510 | — |
| ROAS | 1.34x | 1.33x | 1.15x | 1.16x | — |
| Lucro semana | — | **R$ 15.923** ✅ | R$ 7.497 ❌ | R$ 5.823 ⬇️ | — |

**ROAS de referência:**
- ROAS saudável: **≥ 1.33x**
- ROAS alerta: **< 1.20x**
- ROAS crítico: **< 1.15x**
- Melhor ROAS registrado: **1.34x** (Sem 1 fev/26)

**Volume de referência:**
- Volume saudável/semana: **549–694 vendas**
- Volume mínimo aceitável/semana: **~499 vendas**
- Pico histórico: **694 vendas** (Sem 2 fev/26)

---

### LVC — VSL B (Produto LVC)

| Métrica | Sem 1 | Sem 2 | Sem 3 | Sem 4 | Benchmark |
|---------|-------|-------|-------|-------|-----------|
| Impressões | 718k | 1,07M | 1,03M | 514k | — |
| CPM | R$ 24,45 | R$ 22,88 | — | — | **≤ R$ 25,00** |
| CTR | 0,94% | 0,90% | 0,95% | 1,03% | **≥ 0,90%** |
| Conv. Checkout | 11,32% | 12,23% | 9,96% | 10,55% | **≥ 11%** |
| Vendas vs sem. anterior | — | +74 ✅ | -58 ❌ | -38 ⬇️ | — |

**Benchmarks LVC VSL B:**
- CTR saudável: **≥ 0,90%**
- CTR excelente: **≥ 1,00%**
- Checkout saudável: **≥ 11,00%**
- Checkout alerta: **< 10,00%**
- CPM eficiente: **≤ R$ 25,00**

---

### MDA — VSL A e VSL C (Produto MDA)

| Métrica | Sem 1 | Sem 2 | Sem 3 | Sem 4 | Benchmark |
|---------|-------|-------|-------|-------|-----------|
| Impressões | 419k | 552k | 515k | 629k | — |
| CTR | 0,93% | 0,91% | 0,93% | 0,91% | **≥ 0,90%** |
| Conv. Checkout VSL A | 19,39% | 14,48% | 13,75% | — | **≥ 15%** |
| Conv. Checkout VSL C | 25,95% | 21,59% | 30,53% | 28,57% | **≥ 21%** |
| Lucro semana | — | R$ 4.278 | R$ 6.408 ✅ | R$ 3.505 ⬇️ | — |

**Benchmarks MDA:**
- CTR saudável: **≥ 0,90%**
- Checkout VSL A saudável: **≥ 15%** (queda para < 14% = alerta)
- Checkout VSL C saudável: **≥ 21%** (VSL C consistentemente superior ao VSL A)
- Checkout VSL C excelente: **≥ 28%**
- Lucro semanal MDA saudável: **≥ R$ 5.000**
- Lucro semanal MDA alerta: **< R$ 4.500**

**Observação VSL A vs VSL C:**
VSL C superou VSL A em conversão de checkout em todas as semanas analisadas. VSL C é o criativo dominante para MDA em remarketing e deve ser priorizado na F2/F3.

---

## Insights Estratégicos de Fevereiro

### O que funcionou
- Sem 2 foi a melhor semana: +36% de investimento com ROAS estável (1.33x) e +39% de vendas
- LVC VSL B respondeu bem ao aumento de escala (CPM caiu com mais volume)
- VSL C MDA com checkout acima de 28% em semanas fortes

### Alertas identificados
- Queda de ROAS de 1.33 → 1.15 na Sem 3 foi acompanhada de queda no checkout do LVC VSL B (12,23% → 9,96%) — sinal de saturação de criativo ou audiência
- VSL A MDA mostrou queda consistente de checkout ao longo do mês (19,39% → 13,75%) — criativo em fadiga
- Redução de investimento não melhora ROAS automaticamente (Sem 4: -20% investimento, ROAS quase igual à Sem 3)

### Regra derivada dos dados
> Quando checkout LVC VSL B cair abaixo de 10%, não reduzir budget — investigar fadiga de criativo e renovar F1 com urgência.

---

## Análise a Nível de Criativo — Instruções para @analyst

> ⚠️ IMPORTANTE: Análise de criativo só é possível com CSV exportado a nível de ANÚNCIO (não de campanha).

### Como identificar o nível do export:
- **CSV de campanha:** coluna `ad_name` vazia — métricas agregadas por campanha
- **CSV de anúncio:** coluna `ad_name` preenchida — métricas por criativo individual

### Quando o CSV for a nível de anúncio, @analyst DEVE:
1. Agrupar criativos por fase (F1/F2/F3) via nome da campanha
2. Rankear criativos dentro de cada fase por CPA
3. Identificar criativos candidatos a promoção (CPA ≤ R$ 102,35 na F1)
4. Identificar criativos candidatos a corte (CPA > R$ 153,53 + sem venda em 2 dias)
5. Comparar VSL A vs VSL B vs VSL C dentro do mesmo conjunto
6. Verificar se há criativos na F2/F3 com frequência > 3.0x (sinal de fadiga)

### Nomenclatura esperada dos criativos (padrão da conta):
- `[Vxx]` no nome = versão do criativo (ex: V04, V20, V35)
- `VSL A / VSL B / VSL C` = variação do roteiro
- Criativos sem padrão de nome = dificuldade de rastreio — recomendar padronização

---

## Template para Atualização Mensal

Ao finalizar cada mês, adicionar seção:

```
## Benchmarks — [Mês] [Ano]
### Consolidado
| Métrica | Sem 1 | Sem 2 | Sem 3 | Sem 4 | Referência |
...
### Criativos Campeões do Mês
| Criativo | Fase final | CPA médio | Semanas ativo | Status |
...
### Criativos Pausados
| Criativo | Motivo | CPA no corte | Fase |
...
```

---

*@analyst lê este arquivo como referência comparativa em toda análise.*
*Synkra AIOS — Meta Ads Intelligence · Atualizado em 2026-03-17*
