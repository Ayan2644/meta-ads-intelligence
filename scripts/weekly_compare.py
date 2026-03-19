#!/usr/bin/env python3
"""
Meta Ads Intelligence -- Analise Comparativa Semanal
Compara semanas consecutivas: investimento, ROAS, vendas, lucro, checkout por produto.

Uso:
    python scripts/weekly_compare.py                  # ultimas 2 semanas
    python scripts/weekly_compare.py --weeks 4        # ultimas 4 semanas comparadas
    python scripts/weekly_compare.py --month 2026-02  # todas as semanas de fevereiro
    python scripts/weekly_compare.py --sem-a 2026-03-10 --sem-b 2026-03-17  # custom
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT    = Path(__file__).resolve().parent.parent
SHEETS  = ROOT / "data" / "sheets"

TICKET_MEDIO = 184.23
CPA_CORTE    = 153.53

PRODUTOS = {
    "MDA":  "diario_mda",
    "LVC":  "diario_lvc",
    "TEUS": "diario_teus",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def latest_date_label():
    files = sorted(SHEETS.glob("*_manifest.json"), reverse=True)
    if not files:
        print("ERRO: Rode sheets_collector.py primeiro.")
        sys.exit(1)
    return files[0].name[:10]


def load_diario(produto, date_label):
    alias = PRODUTOS[produto]
    path = SHEETS / f"{date_label}_{alias}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
    df["Gasto"] = (
        df["Gasto"].astype(str)
        .str.replace("R$ ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Gasto"] = pd.to_numeric(df["Gasto"], errors="coerce").fillna(0)
    for col in ["Vendas", "IC", "Cliques no Link", "Alcance", "VPV"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    # Impressoes com pontos de milhar
    if "Impressoes" not in df.columns and "Impressões" in df.columns:
        df["Impressoes"] = (
            df["Impressões"].astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["Impressoes"] = pd.to_numeric(df["Impressoes"], errors="coerce").fillna(0)
    return df


def load_reembolsos(date_label):
    path = SHEETS / f"{date_label}_reembolsos.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce", dayfirst=True)
    df["valor_num"] = (
        df["VALOR REEMBOLSADO"].astype(str)
        .str.replace("R$ ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["valor_num"] = pd.to_numeric(df["valor_num"], errors="coerce").fillna(0)
    return df


def slice_period(df, since, until, date_col="Data"):
    if df.empty or date_col not in df.columns:
        return pd.DataFrame()
    since_ts = pd.Timestamp(since)
    until_ts = pd.Timestamp(until)
    return df[(df[date_col] >= since_ts) & (df[date_col] <= until_ts)].copy()


def calc_week(date_label, since, until, reembolsos_df):
    """Retorna dict com metricas consolidadas + por produto para o periodo."""
    total_gasto  = 0
    total_vendas = 0
    total_ic     = 0
    total_imp    = 0
    total_clk    = 0

    produtos_data = {}

    for produto, alias in PRODUTOS.items():
        df_full = load_diario(produto, date_label)
        if df_full.empty:
            continue
        df = slice_period(df_full, since, until)
        if df.empty:
            continue

        gasto   = df["Gasto"].sum()
        vendas  = int(df["Vendas"].sum())
        ic      = int(df["IC"].sum()) if "IC" in df.columns else 0
        cliques = int(df["Cliques no Link"].sum()) if "Cliques no Link" in df.columns else 0
        impressoes = df["Impressoes"].sum() if "Impressoes" in df.columns else 0

        cpm      = round((gasto / impressoes) * 1000, 2) if impressoes > 0 else 0
        ctr      = round(cliques / impressoes * 100, 2) if impressoes > 0 else 0
        checkout = round(vendas / ic * 100, 1) if ic > 0 else 0

        total_gasto  += gasto
        total_vendas += vendas
        total_ic     += ic
        total_imp    += impressoes
        total_clk    += cliques

        produtos_data[produto] = {
            "gasto": gasto,
            "vendas": vendas,
            "ic": ic,
            "impressoes": impressoes,
            "cpm": cpm,
            "ctr": ctr,
            "checkout": checkout,
            "cliques": cliques,
        }

    reembolsos_periodo = pd.DataFrame()
    if not reembolsos_df.empty:
        reembolsos_periodo = slice_period(reembolsos_df, since, until, date_col="DATA")
    total_reembolsos = reembolsos_periodo["valor_num"].sum() if not reembolsos_periodo.empty else 0
    qtd_reembolsos   = len(reembolsos_periodo)

    receita_bruta = total_vendas * TICKET_MEDIO
    receita_liq   = receita_bruta - total_reembolsos
    lucro         = receita_liq - total_gasto
    roas          = round(receita_bruta / total_gasto, 2) if total_gasto > 0 else 0

    return {
        "since": since,
        "until": until,
        "gasto": total_gasto,
        "vendas": total_vendas,
        "ic": total_ic,
        "impressoes": total_imp,
        "cliques": total_clk,
        "roas": roas,
        "lucro": lucro,
        "reembolsos_valor": total_reembolsos,
        "reembolsos_qtd": qtd_reembolsos,
        "produtos": produtos_data,
    }


def delta_pct(a, b):
    if a == 0:
        return 0
    return round((b - a) / a * 100, 1)


def fmt_pct(val):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"


def status_icon(delta, inverso=False):
    """Retorna emoji baseado no delta. inverso=True para metricas onde queda e boa (ex: CPA)."""
    positivo = delta > 5 if not inverso else delta < -5
    negativo = delta < -5 if not inverso else delta > 5
    if positivo:  return "OK"
    if negativo:  return "XX"
    return "~"


def fmt_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ── Output ────────────────────────────────────────────────────────────────────
def print_comparison(sem_a, sem_b, num_a, num_b):
    since_a = sem_a["since"]
    until_b = sem_b["until"]

    label_a = f"{sem_a['since'][8:10]}/{sem_a['since'][5:7]}"
    label_b = f"{sem_b['until'][8:10]}/{sem_b['until'][5:7]}"
    label_a_full = f"{sem_a['since'][8:10]}/{sem_a['since'][5:7]} a {sem_a['until'][8:10]}/{sem_a['until'][5:7]}"
    label_b_full = f"{sem_b['since'][8:10]}/{sem_b['since'][5:7]} a {sem_b['until'][8:10]}/{sem_b['until'][5:7]}"

    d_inv    = delta_pct(sem_a["gasto"],  sem_b["gasto"])
    d_roas   = delta_pct(sem_a["roas"],   sem_b["roas"])
    d_vendas = delta_pct(sem_a["vendas"], sem_b["vendas"])
    d_lucro  = delta_pct(sem_a["lucro"],  sem_b["lucro"])

    vendas_delta = sem_b["vendas"] - sem_a["vendas"]
    lucro_icon   = "[OK]" if sem_b["lucro"] > sem_a["lucro"] else ("[XX]" if sem_b["lucro"] < 0 else "[!]")

    lines = []
    lines.append("")
    lines.append(f"Sem {num_a} ({label_a_full}) --> Sem {num_b} ({label_b_full})")
    lines.append("")

    # Consolidado
    inv_dir = "Mais" if d_inv >= 0 else "Menos"
    vnd_dir = "saltou" if vendas_delta > 0 else "caiu"
    lines.append("CONSOLIDADO:")
    lines.append(
        f"{inv_dir} investimento {fmt_pct(d_inv)} ({fmt_brl(sem_a['gasto'])} -> {fmt_brl(sem_b['gasto'])}), "
        f"ROAS {sem_a['roas']:.2f}x -> {sem_b['roas']:.2f}x."
    )
    sinal = "+" if vendas_delta >= 0 else ""
    lines.append(
        f"Volume de vendas {vnd_dir} de {sem_a['vendas']} para {sem_b['vendas']} "
        f"({sinal}{vendas_delta} | {fmt_pct(d_vendas)})."
    )
    if sem_b["reembolsos_qtd"] > 0:
        lines.append(
            f"Reembolsos: {sem_b['reembolsos_qtd']} ({fmt_brl(sem_b['reembolsos_valor'])})."
        )
    lucro_txt = "Lucro" if sem_b["lucro"] >= 0 else "Prejuizo"
    lines.append(f"{lucro_txt} da semana: {fmt_brl(sem_b['lucro'])}. [{lucro_icon}]")

    # Por produto
    for produto in ["MDA", "LVC", "TEUS"]:
        pa = sem_a["produtos"].get(produto)
        pb = sem_b["produtos"].get(produto)
        if not pa or not pb:
            if pb:
                lines.append("")
                lines.append(f"{produto} (novo no periodo):")
                lines.append(
                    f"Gasto {fmt_brl(pb['gasto'])} | Vendas {pb['vendas']} | "
                    f"Checkout {pb['checkout']}% | CPA {fmt_brl(pb['gasto']/pb['vendas']) if pb['vendas'] > 0 else 'sem venda'}."
                )
            continue

        d_imp = delta_pct(pa["impressoes"], pb["impressoes"])
        d_cpm = delta_pct(pa["cpm"],        pb["cpm"])
        d_ctr = delta_pct(pa["ctr"],        pb["ctr"])
        d_chk = delta_pct(pa["checkout"],   pb["checkout"])
        d_vnd = pb["vendas"] - pa["vendas"]
        d_gst = delta_pct(pa["gasto"],      pb["gasto"])

        imp_dir = "Maior" if d_imp >= 0 else "Menor"
        vnd_sinal = "+" if d_vnd >= 0 else ""
        vnd_dir2 = "mais" if d_vnd >= 0 else "menos"

        icon_vnd = "[OK]" if d_vnd > 0 else ("[XX]" if d_vnd < -10 else "[!]")
        icon_chk = "[OK]" if d_chk > 5 else ("[XX]" if d_chk < -10 else "[!]")

        lines.append("")
        lines.append(f"{produto}:")

        imp_str = ""
        if pa["impressoes"] > 0 and pb["impressoes"] > 0:
            imp_str = (
                f"{imp_dir} volume de impressoes "
                f"({int(pa['impressoes']/1000)}k -> {int(pb['impressoes']/1000)}k, {fmt_pct(d_imp)})"
            )
            if pa["cpm"] > 0:
                imp_str += f", CPM {fmt_brl(pa['cpm'])} -> {fmt_brl(pb['cpm'])}"
            if pa["ctr"] > 0:
                imp_str += f", CTR {pa['ctr']:.2f}% -> {pb['ctr']:.2f}%"
            imp_str += "."

        chk_str = ""
        if pa["checkout"] > 0 and pb["checkout"] > 0:
            chk_str = f"Checkout {pa['checkout']:.1f}% -> {pb['checkout']:.1f}% [{icon_chk}]. "

        if imp_str:
            lines.append(imp_str)
        if chk_str:
            lines.append(chk_str.strip())

        lines.append(
            f"Resultado: {vnd_sinal}{d_vnd} vendas vs semana anterior "
            f"({pa['vendas']} -> {pb['vendas']}). [{icon_vnd}]"
        )

        if pa["gasto"] > 0 and pb["gasto"] > 0:
            lucro_a = pa["vendas"] * TICKET_MEDIO - pa["gasto"]
            lucro_b = pb["vendas"] * TICKET_MEDIO - pb["gasto"]
            d_lp = delta_pct(lucro_a, lucro_b)
            lucro_icon_p = "[OK]" if lucro_b > lucro_a else "[!]"
            lines.append(
                f"Lucro estimado: {fmt_brl(lucro_a)} -> {fmt_brl(lucro_b)} ({fmt_pct(d_lp)}). [{lucro_icon_p}]"
            )

    lines.append("")
    return "\n".join(lines)


# ── Geracao de semanas ────────────────────────────────────────────────────────
def build_weeks_for_month(month_str):
    """Gera semanas de segunda a domingo para o mes indicado (YYYY-MM)."""
    year, month = int(month_str[:4]), int(month_str[5:7])
    first_day = date(year, month, 1)
    # Encontra a segunda-feira da semana que contem o primeiro dia
    start = first_day - timedelta(days=first_day.weekday())
    weeks = []
    while True:
        end = start + timedelta(days=6)
        # Inclui semana se tem sobreposicao com o mes
        if start.month <= month <= end.month or start.month == month or end.month == month:
            # Limitar ao mes
            sem_start = max(start, first_day)
            import calendar
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            sem_end   = min(end, last_day)
            if sem_start <= sem_end:
                weeks.append((str(sem_start), str(sem_end)))
        start += timedelta(weeks=1)
        if start.month > month and start.year >= year:
            break
    return weeks


def build_weeks_last_n(n):
    """Gera as ultimas N semanas completas (segunda a domingo)."""
    today = date.today()
    # Inicio da semana atual
    current_monday = today - timedelta(days=today.weekday())
    weeks = []
    for i in range(n, 0, -1):
        start = current_monday - timedelta(weeks=i)
        end   = start + timedelta(days=6)
        if end > today:
            end = today
        weeks.append((str(start), str(end)))
    return weeks


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Analise comparativa semanal")
    parser.add_argument("--weeks", type=int, default=2,
                        help="Ultimas N semanas para comparar (default: 2)")
    parser.add_argument("--month", help="Mes especifico: YYYY-MM (ex: 2026-02)")
    parser.add_argument("--sem-a", help="Inicio da semana A: YYYY-MM-DD")
    parser.add_argument("--sem-b", help="Inicio da semana B: YYYY-MM-DD")
    args = parser.parse_args()

    date_label   = latest_date_label()
    reembolsos   = load_reembolsos(date_label)

    # Determinar semanas
    if args.sem_a and args.sem_b:
        d_a = date.fromisoformat(args.sem_a)
        d_b = date.fromisoformat(args.sem_b)
        weeks = [
            (str(d_a), str(d_a + timedelta(days=6))),
            (str(d_b), str(d_b + timedelta(days=6))),
        ]
    elif args.month:
        weeks = build_weeks_for_month(args.month)
    else:
        weeks = build_weeks_last_n(args.weeks + 1)

    if len(weeks) < 2:
        print("Dados insuficientes para comparar (minimo 2 semanas).")
        sys.exit(1)

    # Calcular metricas para cada semana (ignorar semanas sem dados)
    dados = []
    for since, until in weeks:
        w = calc_week(date_label, since, until, reembolsos)
        if w["gasto"] > 0 or w["vendas"] > 0:
            dados.append(w)

    # Gerar comparacoes consecutivas
    mes_label = args.month or f"{date.today().year}-{date.today().month:02d}"
    print()
    print(f"=== ANALISE COMPARATIVA SEMANAL ===")
    if args.month:
        print(f"Mes: {args.month}")
    print()

    for i in range(len(dados) - 1):
        output = print_comparison(dados[i], dados[i + 1], i + 1, i + 2)
        print(output)
        if i < len(dados) - 2:
            print("-" * 60)

    # Resumo geral se mais de 2 semanas
    if len(dados) >= 3:
        print("=" * 60)
        print("RESUMO DO PERIODO")
        print("=" * 60)
        gasto_total  = sum(d["gasto"]  for d in dados)
        vendas_total = sum(d["vendas"] for d in dados)
        lucro_total  = sum(d["lucro"]  for d in dados)
        reem_total   = sum(d["reembolsos_valor"] for d in dados)
        print(f"Investimento total: {fmt_brl(gasto_total)}")
        print(f"Vendas totais:      {vendas_total}")
        print(f"Receita bruta:      {fmt_brl(vendas_total * TICKET_MEDIO)}")
        print(f"Reembolsos:         {fmt_brl(reem_total)}")
        print(f"Lucro total:        {fmt_brl(lucro_total)}")
        if gasto_total > 0:
            margem = lucro_total / gasto_total * 100
            print(f"Margem:             {margem:.1f}%")
        print()


if __name__ == "__main__":
    main()
