#!/usr/bin/env python3
"""
Meta Ads Intelligence -- Status do Funil F1/F2/F3
Classifica cada campanha/criativo por fase e recomenda movimentos.

*funil           -> status completo do funil
*f1              -> criativos em teste (lab)
*f2              -> criativos na arena
*f3              -> criativos em escala
*mover           -> o que mover hoje (promover / pausar / manter)
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT   = Path(__file__).resolve().parent.parent
SHEETS = ROOT / "data" / "sheets"

TICKET_MEDIO = 184.23
CPA_ALVO     = 92.12
CPA_BOM      = 102.35
CPA_LIMITE   = 122.82
CPA_CORTE    = 153.53

# Palavras-chave nos nomes de campanha para classificar fase
FASE_KEYWORDS = {
    "F3": ["[F3]", "F3 ", "ESCALA", "SCALE", "F3-"],
    "F2": ["[F2]", "F2 ", "ARENA", "VSL", "CBO", "F2-"],
    "F1": ["[F1]", "F1 ", "TESTE", "LAB", "ABO", "F1-", "1-X-1", "1-5-1"],
    "RMKT": ["RMKT", "REMARKETING", "[Q]", "RETARGETING"],
    "F0":  ["F0", "ENGAJAMENTO", "AQUECIMENTO"],
}


def latest_date_label():
    files = sorted(SHEETS.glob("*_manifest.json"), reverse=True)
    if not files:
        print("ERRO: Rode sheets_collector.py primeiro.")
        sys.exit(1)
    return files[0].name[:10]


def classify_campaign(name: str) -> str:
    name_upper = name.upper()
    for fase, keywords in FASE_KEYWORDS.items():
        for kw in keywords:
            if kw.upper() in name_upper:
                return fase
    # Tenta inferir pelo padrao [ADV+] e data
    if "ADV+" in name_upper or "AUTO" in name_upper:
        return "F2/F3"  # Advantage+ tipicamente e F2 ou F3
    return "?"


def load_ads(produto_alias, date_label, since, until):
    path = SHEETS / f"{date_label}_{produto_alias}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[(df["date"] >= pd.Timestamp(since)) & (df["date"] <= pd.Timestamp(until))].copy()
    spend_col = "Spend (Cost, Amount Spent)"
    buy_col   = "Action Omni Purchase"
    imp_col   = "Impressions"
    clk_col   = "Inline Link Clicks"
    freq_col  = None  # frequencia nao disponivel nos sheets, usar campaigns
    for col in [spend_col, buy_col, imp_col, clk_col]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def load_campaigns(date_label, since, until):
    path = ROOT / "data" / "processed" / "campaign_performance.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[(df["date"] >= pd.Timestamp(since)) & (df["date"] <= pd.Timestamp(until))].copy()
    return df[df["spend"] > 0].copy()


def cpa_status(cpa):
    if cpa is None:    return "SEM VENDA", "??"
    if cpa <= CPA_ALVO:   return "ALVO",   "F3"
    if cpa <= CPA_BOM:    return "BOM",    "F2"
    if cpa <= CPA_LIMITE: return "LIMITE", "MONITORAR"
    if cpa <= CPA_CORTE:  return "CORTE",  "PAUSAR"
    return "PAUSAR", "PAUSAR"


def days_since(since_str):
    since = date.fromisoformat(since_str)
    return (date.today() - since).days


def janela_status(since_str):
    d = days_since(since_str)
    if d < 7:
        return f"JANELA ATIVA ({d}/7 dias)", False
    return f"JANELA LIVRE ({d} dias)", True


# ── Display helpers ───────────────────────────────────────────────────────────
def sep(char="-", width=70):
    print(char * width)


def header(title):
    print()
    sep("=")
    print(f"  {title}")
    sep("=")
    print()


def fmt_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ── Modos ─────────────────────────────────────────────────────────────────────
def show_funil(date_label, since, until):
    header("STATUS DO FUNIL F1 / F2 / F3 -- " + since + " a " + until)

    camps = load_campaigns(date_label, since, until)
    if camps.empty:
        print("Sem dados de campanha no periodo.")
        return

    # Agrupa por campanha
    g = camps.groupby("campaign_name").agg(
        gasto=("spend", "sum"),
        vendas=("results", "sum"),
        freq=("frequency", "mean"),
    ).reset_index()
    g["cpa"]  = g.apply(lambda r: round(r["gasto"] / r["vendas"], 2) if r["vendas"] > 0 else None, axis=1)
    g["roas"] = g.apply(lambda r: round((r["vendas"] * TICKET_MEDIO) / r["gasto"], 2) if r["gasto"] > 0 else 0, axis=1)
    g["fase"] = g["campaign_name"].apply(classify_campaign)
    g = g.sort_values("gasto", ascending=False)

    fases_ordem = ["F3", "F2/F3", "F2", "F1", "RMKT", "F0", "?"]
    for fase in fases_ordem:
        subset = g[g["fase"] == fase]
        if subset.empty:
            continue
        fase_label = {
            "F3": "F3 -- ESCALA TOTAL",
            "F2/F3": "F2/F3 -- ADVANTAGE+ (escala)",
            "F2": "F2 -- ARENA VSL",
            "F1": "F1 -- LABORATORIO",
            "RMKT": "REMARKETING (trafego quente)",
            "F0": "F0 -- ENGAJAMENTO",
            "?": "? -- NAO CLASSIFICADO (revisar nome)",
        }.get(fase, fase)

        print(f"  [{fase_label}]")
        sep("-", 70)
        for _, r in subset.iterrows():
            cpa_st, acao = cpa_status(r["cpa"])
            cpa_str = fmt_brl(r["cpa"]) if r["cpa"] else "sem venda"
            freq_str = f"freq {r['freq']:.1f}x" if r["freq"] > 0 else ""
            name = str(r["campaign_name"])[:55]

            # Alertas especificos por fase
            alerts = []
            if fase in ("F3", "F2/F3") and r["freq"] > 2.5:
                alerts.append("ALERTA FREQ")
            if fase == "F2" and r["freq"] > 3.0:
                alerts.append("SATURACAO")
            if r["cpa"] and r["cpa"] > CPA_CORTE:
                alerts.append("PAUSAR")
            if r["roas"] < 1.0 and r["gasto"] > 500:
                alerts.append("ROAS NEGATIVO")

            alert_str = " | ".join(alerts)
            print(
                f"  {name:<55}  {fmt_brl(r['gasto']):>12}  {int(r['vendas']):>3}v"
                f"  CPA {cpa_str:>12}  ROAS {r['roas']:.2f}x"
                + (f"  [{alert_str}]" if alert_str else "")
            )
        print()


def show_mover(date_label, since, until):
    header("O QUE MOVER HOJE -- " + date.today().strftime("%d/%m/%Y"))

    promover_f2 = []
    promover_f3 = []
    pausar      = []
    monitorar   = []

    for produto_alias in ["ads_mda", "ads_lvc", "ads_teus"]:
        produto_nome = produto_alias.replace("ads_", "").upper()
        df = load_ads(produto_alias, date_label, since, until)
        if df.empty:
            continue

        spend_col = "Spend (Cost, Amount Spent)"
        buy_col   = "Action Omni Purchase"
        imp_col   = "Impressions"
        clk_col   = "Inline Link Clicks"

        g = df.groupby("Ad Name").agg(
            gasto=(spend_col, "sum"),
            compras=(buy_col, "sum"),
            impressoes=(imp_col, "sum"),
            cliques=(clk_col, "sum"),
        ).reset_index()
        g = g[g["gasto"] > 20].copy()
        g["cpa"] = g.apply(lambda r: round(r["gasto"] / r["compras"], 2) if r["compras"] > 0 else None, axis=1)
        g["ctr"] = g.apply(lambda r: round(r["cliques"] / r["impressoes"] * 100, 2) if r["impressoes"] > 0 else 0, axis=1)

        for _, r in g.iterrows():
            nome = str(r["Ad Name"])[:60]
            cpa  = r["cpa"]
            gasto = r["gasto"]

            if cpa is None and gasto > TICKET_MEDIO:
                pausar.append((produto_nome, nome, gasto, None, "Sem venda, gasto acima do ticket medio"))
            elif cpa and cpa <= CPA_ALVO:
                promover_f3.append((produto_nome, nome, gasto, cpa, f"CPA {fmt_brl(cpa)} -- nivel ALVO"))
            elif cpa and cpa <= CPA_BOM:
                promover_f2.append((produto_nome, nome, gasto, cpa, f"CPA {fmt_brl(cpa)} -- nivel BOM"))
            elif cpa and cpa <= CPA_LIMITE:
                monitorar.append((produto_nome, nome, gasto, cpa, f"CPA {fmt_brl(cpa)} -- nivel LIMITE"))
            elif cpa and cpa > CPA_CORTE:
                pausar.append((produto_nome, nome, gasto, cpa, f"CPA {fmt_brl(cpa)} -- acima do CORTE"))

    def print_grupo(titulo, lista, icon):
        if not lista:
            return
        print(f"  {icon} {titulo} ({len(lista)})")
        sep("-", 70)
        for produto, nome, gasto, cpa, motivo in sorted(lista, key=lambda x: -(x[2] or 0)):
            cpa_str = fmt_brl(cpa) if cpa else "sem venda"
            print(f"  [{produto}] {nome[:50]:<50}  {fmt_brl(gasto):>10}  {cpa_str}  <- {motivo}")
        print()

    print_grupo("CANDIDATOS F3 -- promover para escala", promover_f3, "[>>>]")
    print_grupo("APROVADOS F2 -- incluir na arena",      promover_f2, "[>>] ")
    print_grupo("PAUSAR -- corte imediato",              pausar,      "[XX] ")
    print_grupo("MONITORAR -- acompanhar mais 1-2 dias", monitorar,   "[!!] ")

    if not any([promover_f2, promover_f3, pausar, monitorar]):
        print("  Nenhuma acao urgente identificada no periodo.")
    print()


def show_vsl(date_label, since, until):
    header("VSL A vs VSL B vs VSL C -- COMPARATIVO")

    for produto_alias in ["ads_mda", "ads_lvc", "ads_teus"]:
        produto_nome = produto_alias.replace("ads_", "").upper()
        df = load_ads(produto_alias, date_label, since, until)
        if df.empty:
            continue

        spend_col = "Spend (Cost, Amount Spent)"
        buy_col   = "Action Omni Purchase"
        imp_col   = "Impressions"
        clk_col   = "Inline Link Clicks"

        df["vsl"] = df["Ad Name"].apply(lambda n: (
            "VSL C" if "VSL C" in str(n).upper() else
            "VSL B" if "VSL B" in str(n).upper() else
            "VSL A" if "VSL A" in str(n).upper() else
            "OUTRO"
        ))

        g = df.groupby("vsl").agg(
            gasto=(spend_col, "sum"),
            compras=(buy_col, "sum"),
            impressoes=(imp_col, "sum"),
            cliques=(clk_col, "sum"),
        ).reset_index()
        g = g[g["gasto"] > 0].copy()
        g["cpa"]  = g.apply(lambda r: round(r["gasto"] / r["compras"], 2) if r["compras"] > 0 else None, axis=1)
        g["ctr"]  = g.apply(lambda r: round(r["cliques"] / r["impressoes"] * 100, 2) if r["impressoes"] > 0 else 0, axis=1)
        g["roas"] = g.apply(lambda r: round((r["compras"] * TICKET_MEDIO) / r["gasto"], 2) if r["gasto"] > 0 else 0, axis=1)
        g = g.sort_values("roas", ascending=False)

        print(f"  {produto_nome}")
        sep("-", 70)
        print(f"  {'VSL':<8} {'Gasto':>12} {'Vendas':>7} {'CPA':>12} {'CTR':>7} {'ROAS':>7}  Status")
        for _, r in g.iterrows():
            cpa_str = fmt_brl(r["cpa"]) if r["cpa"] else "sem venda"
            cpa_st, _ = cpa_status(r["cpa"])
            print(f"  {str(r['vsl']):<8} {fmt_brl(r['gasto']):>12} {int(r['compras']):>7} "
                  f"{cpa_str:>12} {r['ctr']:>6.2f}% {r['roas']:>6.2f}x  [{cpa_st}]")
        print()


def show_checklist():
    header("CHECKLIST DO DIA -- " + date.today().strftime("%A %d/%m/%Y").upper())

    weekday = date.today().weekday()  # 0=seg, 4=sex, 5=sab, 6=dom

    acoes = {
        0: [  # Segunda
            "[1] Alocar 10 criativos novos na F1 (orçamento R$50/conjunto/dia, estrutura ABO 1-X-1)",
            "[2] Verificar criativos ativos na F2 -- algum com CPA acima do CORTE?",
            "[3] Checar janela da F3 -- ajuste de orçamento so apos 7 dias completos",
            "[4] Rodar *status para ver ROAS e CPA de ontem",
            "[5] Verificar reembolsos do fim de semana",
        ],
        1: [  # Terça
            "[1] Monitorar F1 com 1 dia: nao tomar decisao ainda -- so observar CPM",
            "[2] Verificar se criativos novos passaram da fase de aprendizado",
            "[3] Checar *pausar para alertas criticos",
        ],
        2: [  # Quarta
            "[1] CORTE F1: CPA > R$153,53 + zero venda nos ultimos 2 dias = PAUSAR",
            "[2] Verificar budget F2 -- esta dentro da janela de 7 dias?",
            "[3] Checar frequencia em F3 (> 2.5x = alerta antecipado)",
            "[4] Rodar *funil para ver status completo de cada fase",
            "[5] Analisar checkout por produto (*checkout)",
        ],
        3: [  # Quinta
            "[1] Monitorar F1 com 3-4 dias -- janela de leitura, nao mexer em orcamento",
            "[2] Verificar se F2/F3 recentes (< 7 dias) estao em mini-reaprendizado",
            "[3] Checar *criativos para ver ranking atualizado",
        ],
        4: [  # Sexta
            "[1] FECHAR LEITURA F1: identificar aprovados (CPA <= R$102,35)",
            "[2] PROMOVER para F2: criativos aprovados com CPA BOM/ALVO",
            "[3] IDENTIFICAR candidatos F3: CPA <= R$92,12 por multiplos dias consecutivos",
            "[4] Pausar criativos ruins na F2 para abrir espaço aos aprovados da F1",
            "[5] Rodar *comparar para ver semana vs semana",
            "[6] Rodar *report para gerar relatorio semanal completo",
        ],
        5: [  # Sábado
            "[1] Revisao final da semana -- *status e *pl",
            "[2] Confirmar movimentos da sexta (F1->F2, F2->F3)",
            "[3] Analisar reembolsos da semana por criativo (*reembolsos)",
            "[4] Planejar novos criativos F1 para segunda-feira",
        ],
        6: [  # Domingo
            "[1] Revisao semanal -- rodar *comparar",
            "[2] Preparar lista de 10 criativos para alocar na segunda",
            "[3] Checar benchmarks vs semana anterior -- *benchmarks",
        ],
    }

    hoje = acoes.get(weekday, ["[~] Sem checklist especifico para hoje."])
    for acao in hoje:
        print(f"  {acao}")

    print()
    print("  Comandos rapidos para hoje:")
    if weekday in (0,):  # Segunda
        print("    *status | *funil | *f1 | *reembolsos")
    elif weekday in (2,):  # Quarta
        print("    *pausar | *funil | *f1 | *checkout")
    elif weekday in (4, 5):  # Sexta/Sab
        print("    *mover | *comparar | *report | *vsl")
    else:
        print("    *status | *criativos | *pausar")
    print()


def show_reembolsos(date_label, since, until):
    header("ANALISE DE REEMBOLSOS -- " + since + " a " + until)

    path = SHEETS / f"{date_label}_reembolsos.csv"
    if not path.exists():
        print("Sem dados de reembolso.")
        return

    df = pd.read_csv(path)
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce", dayfirst=True)
    df = df[(df["DATA"] >= pd.Timestamp(since)) & (df["DATA"] <= pd.Timestamp(until))].copy()
    df["valor_num"] = (
        df["VALOR REEMBOLSADO"].astype(str)
        .str.replace("R$ ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["valor_num"] = pd.to_numeric(df["valor_num"], errors="coerce").fillna(0)

    if df.empty:
        print("Nenhum reembolso no periodo.")
        return

    total_qtd = len(df)
    total_val = df["valor_num"].sum()
    print(f"  Total: {total_qtd} reembolsos | {fmt_brl(total_val)}")
    print()

    # Por produto
    print("  Por produto:")
    sep("-", 50)
    by_prod = df.groupby("PRODUTO").agg(qtd=("valor_num","count"), valor=("valor_num","sum")).sort_values("valor", ascending=False)
    for prod, row in by_prod.iterrows():
        pct = row["valor"] / total_val * 100
        print(f"  {str(prod)[:45]:<45}  {int(row['qtd']):>3}x  {fmt_brl(row['valor']):>12}  ({pct:.1f}%)")
    print()

    # Por criativo (UTM_CONTENT)
    if "UTM_CONTENT" in df.columns:
        print("  Por criativo (UTM_CONTENT):")
        sep("-", 50)
        by_utm = df[df["UTM_CONTENT"].notna()].groupby("UTM_CONTENT").agg(
            qtd=("valor_num", "count"), valor=("valor_num", "sum")
        ).sort_values("qtd", ascending=False).head(10)
        for utm, row in by_utm.iterrows():
            if str(utm).lower() not in ("nan", "", "organico", "hotmart"):
                print(f"  {str(utm):<35}  {int(row['qtd']):>3}x  {fmt_brl(row['valor']):>12}")
    print()

    # Tendencia diaria
    print("  Tendencia diaria:")
    sep("-", 50)
    by_day = df.groupby("DATA").agg(qtd=("valor_num","count"), valor=("valor_num","sum"))
    avg_day = total_val / max((pd.Timestamp(until) - pd.Timestamp(since)).days + 1, 1)
    print(f"  Media diaria: {fmt_brl(avg_day)} ({total_qtd / max((pd.Timestamp(until) - pd.Timestamp(since)).days + 1, 1):.1f} reembolsos/dia)")
    for d, row in by_day.tail(7).iterrows():
        icon = "[XX]" if row["valor"] > avg_day * 1.5 else "[OK]"
        print(f"  {str(d)[:10]}  {int(row['qtd']):>3}x  {fmt_brl(row['valor']):>12}  {icon}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Status do Funil")
    parser.add_argument("--mode", default="funil",
                        choices=["funil", "mover", "vsl", "checklist", "reembolsos", "f1", "f2", "f3"])
    parser.add_argument("--period", default="week",
                        choices=["today", "yesterday", "week", "month", "last7", "last14", "last30"])
    parser.add_argument("--since")
    parser.add_argument("--until")
    args = parser.parse_args()

    date_label = latest_date_label()
    today = date.today()

    if args.since and args.until:
        since, until = args.since, args.until
    elif args.period == "today":
        since = until = str(today)
    elif args.period == "yesterday":
        since = until = str(today - timedelta(days=1))
    elif args.period == "week":
        since = str(today - timedelta(days=today.weekday()))
        until = str(today)
    elif args.period == "month":
        since = str(today.replace(day=1))
        until = str(today)
    elif args.period == "last14":
        since = str(today - timedelta(days=13))
        until = str(today)
    elif args.period == "last30":
        since = str(today - timedelta(days=29))
        until = str(today)
    else:  # last7
        since = str(today - timedelta(days=6))
        until = str(today)

    if args.mode == "checklist":
        show_checklist()
    elif args.mode in ("funil", "f1", "f2", "f3"):
        show_funil(date_label, since, until)
    elif args.mode == "mover":
        show_mover(date_label, since, until)
    elif args.mode == "vsl":
        show_vsl(date_label, since, until)
    elif args.mode == "reembolsos":
        show_reembolsos(date_label, since, until)


if __name__ == "__main__":
    main()
