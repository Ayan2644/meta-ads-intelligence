#!/usr/bin/env python3
"""
Meta Ads Intelligence -- Quick Status Panel
Exibe painel de performance consolidado direto no terminal.

Comandos (*):
    *status          -> hoje/ontem
    *semana          -> semana atual (seg-hoje)
    *pl              -> P&L com reembolsos
    *criativos       -> ranking de criativos
    *pausar          -> alertas de corte urgente

Uso direto:
    python scripts/quick_status.py
    python scripts/quick_status.py --period week
    python scripts/quick_status.py --period month
    python scripts/quick_status.py --since 2026-03-10 --until 2026-03-18
    python scripts/quick_status.py --mode creatives
    python scripts/quick_status.py --mode alerts
    python scripts/quick_status.py --mode pl
"""

import argparse
import sys
import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
SHEETS = ROOT / "data" / "sheets"

TICKET_MEDIO = 184.23
CPA_ALVO    = 92.12
CPA_BOM     = 102.35
CPA_LIMITE  = 122.82
CPA_CORTE   = 153.53

PRODUTOS = {
    "MDA":  {"diario": "diario_mda",  "ads": "ads_mda",  "vendas": "vendas_mda"},
    "LVC":  {"diario": "diario_lvc",  "ads": "ads_lvc",  "vendas": "vendas_lvc"},
    "TEUS": {"diario": "diario_teus", "ads": "ads_teus",  "vendas": "vendas_teus"},
}

BENCH_ROAS_SAUDAVEL = 1.33
BENCH_ROAS_ALERTA   = 1.20
BENCH_ROAS_CRITICO  = 1.15

# ── Cores no terminal ─────────────────────────────────────────────────────────
def c(text, color):
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "cyan": "\033[96m", "bold": "\033[1m",
        "dim": "\033[2m", "reset": "\033[0m",
    }
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7
            )
        except Exception:
            pass
    return f"{colors.get(color,'')}{text}{colors['reset']}"

def roas_color(roas):
    if roas >= BENCH_ROAS_SAUDAVEL: return c(f"{roas:.2f}x", "green")
    if roas >= BENCH_ROAS_ALERTA:   return c(f"{roas:.2f}x", "yellow")
    return c(f"{roas:.2f}x", "red")

def cpa_color(cpa):
    if cpa is None: return c("sem venda", "dim")
    if cpa <= CPA_ALVO:   return c(f"R$ {cpa:.2f}", "green")
    if cpa <= CPA_BOM:    return c(f"R$ {cpa:.2f}", "green")
    if cpa <= CPA_LIMITE: return c(f"R$ {cpa:.2f}", "yellow")
    if cpa <= CPA_CORTE:  return c(f"R$ {cpa:.2f}", "yellow")
    return c(f"R$ {cpa:.2f}", "red")

def cpa_label(cpa):
    if cpa is None:       return c("[SEM VENDA]", "dim")
    if cpa <= CPA_ALVO:   return c("[ALVO-F3]", "green")
    if cpa <= CPA_BOM:    return c("[BOM-F2]", "green")
    if cpa <= CPA_LIMITE: return c("[LIMITE]", "yellow")
    if cpa <= CPA_CORTE:  return c("[CORTE]", "yellow")
    return c("[PAUSAR]", "red")

def status_icon(roas):
    if roas >= BENCH_ROAS_SAUDAVEL: return c("[OK]", "green")
    if roas >= BENCH_ROAS_ALERTA:   return c("[!!]", "yellow")
    return c("[XX]", "red")

# ── Helpers de data ───────────────────────────────────────────────────────────
def latest_sheets_date():
    files = sorted(SHEETS.glob("*_manifest.json"), reverse=True)
    if not files:
        print(c("ERRO: Nenhum dado encontrado em data/sheets/. Rode sheets_collector.py primeiro.", "red"))
        sys.exit(1)
    return files[0].name[:10]  # YYYY-MM-DD

def parse_period(period, since, until):
    today = date.today()
    if since and until:
        return since, until
    if period == "today":
        return str(today), str(today)
    if period == "yesterday":
        d = today - timedelta(days=1)
        return str(d), str(d)
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return str(start), str(today)
    if period == "month":
        return str(today.replace(day=1)), str(today)
    if period == "last7":
        return str(today - timedelta(days=6)), str(today)
    return str(today - timedelta(days=6)), str(today)

# ── Leitura de dados ──────────────────────────────────────────────────────────
def load_diario(produto_key, date_label, since, until):
    alias = PRODUTOS[produto_key]["diario"]
    path = SHEETS / f"{date_label}_{alias}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
    df = df[(df["Data"] >= since) & (df["Data"] <= until)].copy()
    # Limpar colunas monetarias
    for col in ["Gasto", "Faturamento"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace("R$ ", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["Vendas", "IC", "Cliques no Link", "Alcance", "Impressoes", "Impressoes", "VPV"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    # Alias de coluna de impressoes
    if "Impressões" in df.columns:
        df["Impressões"] = pd.to_numeric(
            df["Impressões"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
            errors="coerce"
        ).fillna(0)
    return df

def load_ads(produto_key, date_label, since, until):
    alias = PRODUTOS[produto_key]["ads"]
    path = SHEETS / f"{date_label}_{alias}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[(df["date"] >= since) & (df["date"] <= until)].copy()
    spend_col = "Spend (Cost, Amount Spent)"
    buy_col   = "Action Omni Purchase"
    imp_col   = "Impressions"
    clk_col   = "Inline Link Clicks"
    for col in [spend_col, buy_col, imp_col, clk_col]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def load_reembolsos(date_label, since, until):
    path = SHEETS / f"{date_label}_reembolsos.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce", dayfirst=True)
    df = df[(df["DATA"] >= since) & (df["DATA"] <= until)].copy()
    df["valor_num"] = (
        df["VALOR REEMBOLSADO"].astype(str)
        .str.replace("R$ ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["valor_num"] = pd.to_numeric(df["valor_num"], errors="coerce").fillna(0)
    return df

# ── Calculos por produto ──────────────────────────────────────────────────────
def calc_produto(produto_key, date_label, since, until):
    df = load_diario(produto_key, date_label, since, until)
    if df.empty:
        return None
    gasto  = df["Gasto"].sum()
    vendas = int(df["Vendas"].sum())
    ic     = int(df["IC"].sum()) if "IC" in df.columns else 0
    cliques = int(df["Cliques no Link"].sum()) if "Cliques no Link" in df.columns else 0
    cpa    = round(gasto / vendas, 2) if vendas > 0 else None
    roas   = round((vendas * TICKET_MEDIO) / gasto, 2) if gasto > 0 else 0.0
    checkout = round(vendas / ic * 100, 1) if ic > 0 else 0.0
    return {
        "produto": produto_key,
        "gasto": gasto,
        "vendas": vendas,
        "ic": ic,
        "cliques": cliques,
        "cpa": cpa,
        "roas": roas,
        "checkout": checkout,
        "receita_bruta": round(vendas * TICKET_MEDIO, 2),
    }

# ── Modos de exibicao ─────────────────────────────────────────────────────────
def show_status(resultados, reembolsos_df, period_label):
    print()
    print(c("=" * 65, "bold"))
    print(c(f"  META ADS INTELLIGENCE -- STATUS", "bold") + c(f"  [{period_label}]", "cyan"))
    print(c("=" * 65, "bold"))
    print()

    total_gasto  = 0
    total_vendas = 0
    total_ic     = 0

    for r in resultados:
        if not r: continue
        total_gasto  += r["gasto"]
        total_vendas += r["vendas"]
        total_ic     += r["ic"]

        icon = status_icon(r["roas"])
        gasto_fmt = f"R$ {r['gasto']:,.2f}"
        linha = (f"  {icon}  {c(r['produto'], 'bold'):<6}  "
                 f"Gasto: {c(gasto_fmt, 'cyan')}  |  "
                 f"Vendas: {c(str(r['vendas']), 'bold')}  |  "
                 f"CPA: {cpa_color(r['cpa'])}  |  "
                 f"ROAS: {roas_color(r['roas'])}")
        print(linha)
        if r["ic"] > 0:
            chk_color = "green" if r["checkout"] >= 11 else ("yellow" if r["checkout"] >= 8 else "red")
            checkout_fmt = f"{r['checkout']}%"
            print(f"         IC: {r['ic']}  |  Checkout: {c(checkout_fmt, chk_color)}  |  "
                  f"Cliques: {r['cliques']}")
        print()

    # Reembolsos
    qtd_r  = len(reembolsos_df)
    val_r  = reembolsos_df["valor_num"].sum() if not reembolsos_df.empty else 0
    receita_bruta = total_vendas * TICKET_MEDIO
    receita_liq   = receita_bruta - val_r
    lucro         = receita_liq - total_gasto

    print(c("  " + "-" * 61, "dim"))
    print(f"  {c('TOTAL', 'bold')}        "
          f"Gasto: {c(f'R$ {total_gasto:,.2f}', 'cyan')}  |  "
          f"Vendas: {c(str(total_vendas), 'bold')}  |  "
          f"ROAS: {roas_color(round((total_vendas * TICKET_MEDIO) / total_gasto, 2) if total_gasto > 0 else 0)}")
    print()
    lucro_color = "green" if lucro > 0 else "red"
    print(f"  {'Receita bruta':<18} R$ {receita_bruta:>10,.2f}")
    print(f"  {'Reembolsos':<18} {c(f'- R$ {val_r:>8,.2f}  ({qtd_r} refunds)', 'yellow')}")
    print(f"  {'Receita liquida':<18} R$ {receita_liq:>10,.2f}")
    print(f"  {'Investimento':<18} - R$ {total_gasto:>8,.2f}")
    print(f"  {c('Lucro bruto', 'bold'):<27} {c(f'R$ {lucro:>10,.2f}', lucro_color)}")
    print()
    print(c("=" * 65, "dim"))
    print()

def show_creatives(date_label, since, until, top_n=10):
    print()
    print(c("=" * 70, "bold"))
    print(c("  RANKING DE CRIATIVOS", "bold"))
    print(c("=" * 70, "bold"))

    for produto_key in PRODUTOS:
        df = load_ads(produto_key, date_label, since, until)
        if df.empty:
            continue

        spend_col = "Spend (Cost, Amount Spent)"
        buy_col   = "Action Omni Purchase"
        clk_col   = "Inline Link Clicks"
        imp_col   = "Impressions"

        g = df.groupby("Ad Name").agg(
            gasto=(spend_col, "sum"),
            compras=(buy_col, "sum"),
            cliques=(clk_col, "sum"),
            impressoes=(imp_col, "sum"),
        ).reset_index()
        g = g[g["gasto"] > 10].copy()
        g["cpa"]  = g.apply(lambda r: round(r["gasto"] / r["compras"], 2) if r["compras"] > 0 else None, axis=1)
        g["ctr"]  = g.apply(lambda r: round(r["cliques"] / r["impressoes"] * 100, 2) if r["impressoes"] > 0 else 0, axis=1)
        g["roas"] = g.apply(lambda r: round((r["compras"] * TICKET_MEDIO) / r["gasto"], 2) if r["gasto"] > 0 else 0, axis=1)
        g = g.sort_values("gasto", ascending=False).head(top_n)

        print()
        print(f"  {c(produto_key, 'bold')} — top {min(top_n, len(g))} por gasto")
        print(c(f"  {'Ad Name':<45} {'Gasto':>8} {'Vnd':>4} {'CPA':>12} {'CTR':>6} {'Status'}", "dim"))
        print(c("  " + "-" * 85, "dim"))
        for _, r in g.iterrows():
            name = str(r["Ad Name"])[:44]
            cpa_str = f"R$ {r['cpa']:.2f}" if r["cpa"] else "sem venda"
            print(f"  {name:<45} R${r['gasto']:>7,.0f} {int(r['compras']):>4}  "
                  f"{cpa_color(r['cpa']):>12}  {r['ctr']:.2f}%  {cpa_label(r['cpa'])}")
    print()
    print(c("=" * 70, "dim"))
    print()

def show_alerts(resultados, date_label, since, until):
    print()
    print(c("=" * 65, "bold"))
    print(c("  ALERTAS -- ACOES URGENTES", "bold"))
    print(c("=" * 65, "bold"))
    print()

    alertas = []

    for r in resultados:
        if not r: continue
        cpa = r["cpa"]
        if cpa and cpa > CPA_CORTE:
            alertas.append((1, r["produto"], f"CPA R$ {cpa:.2f} -- acima do CORTE (R$ {CPA_CORTE})", "red"))
        elif r["roas"] > 0 and r["roas"] < BENCH_ROAS_ALERTA:
            alertas.append((2, r["produto"], f"ROAS {r['roas']:.2f}x -- abaixo do benchmark ({BENCH_ROAS_ALERTA}x)", "yellow"))
        if r["checkout"] > 0 and r["checkout"] < 8:
            alertas.append((1, r["produto"], f"Checkout {r['checkout']}% -- critico (< 8%)", "red"))

    # Criativos urgentes
    for produto_key in PRODUTOS:
        df = load_ads(produto_key, date_label, since, until)
        if df.empty:
            continue
        spend_col = "Spend (Cost, Amount Spent)"
        buy_col   = "Action Omni Purchase"
        g = df.groupby("Ad Name").agg(
            gasto=(spend_col, "sum"),
            compras=(buy_col, "sum"),
        ).reset_index()
        g = g[g["gasto"] > 50].copy()
        g["cpa"] = g.apply(lambda r: round(r["gasto"] / r["compras"], 2) if r["compras"] > 0 else None, axis=1)
        urgentes = g[(g["cpa"].notna()) & (g["cpa"] > CPA_CORTE)].sort_values("cpa", ascending=False)
        sem_venda = g[(g["cpa"].isna()) & (g["gasto"] > TICKET_MEDIO)]
        for _, row in urgentes.head(5).iterrows():
            name = str(row["Ad Name"])[:50]
            alertas.append((1, produto_key, f"PAUSAR {name} -- CPA R$ {row['cpa']:.2f}", "red"))
        for _, row in sem_venda.head(3).iterrows():
            name = str(row["Ad Name"])[:50]
            alertas.append((2, produto_key, f"SEM VENDA -- {name} -- R$ {row['gasto']:.0f} gastos", "yellow"))

    if not alertas:
        print(c("  Nenhum alerta critico no periodo.", "green"))
    else:
        for prio, produto, msg, color in sorted(alertas, key=lambda x: x[0]):
            icon = c("[XX]", "red") if prio == 1 else c("[!!]", "yellow")
            print(f"  {icon} [{c(produto, 'bold')}] {c(msg, color)}")
    print()
    print(c("=" * 65, "dim"))
    print()

def show_pl(resultados, reembolsos_df, period_label):
    print()
    print(c("=" * 55, "bold"))
    print(c(f"  P&L -- {period_label}", "bold"))
    print(c("=" * 55, "bold"))
    print()

    total_gasto   = 0
    total_receita = 0

    for r in resultados:
        if not r: continue
        receita = r["vendas"] * TICKET_MEDIO
        lucro   = receita - r["gasto"]
        lc      = "green" if lucro >= 0 else "red"
        print(f"  {c(r['produto'], 'bold'):<8}  "
              f"Gasto: R$ {r['gasto']:>9,.2f}  |  "
              f"Receita: R$ {receita:>9,.2f}  |  "
              f"Lucro: {c(f'R$ {lucro:>8,.2f}', lc)}")
        total_gasto   += r["gasto"]
        total_receita += receita

    # Reembolsos por produto
    if not reembolsos_df.empty:
        print()
        print(c("  Reembolsos por produto:", "dim"))
        by_prod = reembolsos_df.groupby("PRODUTO").agg(
            qtd=("valor_num", "count"),
            valor=("valor_num", "sum")
        ).sort_values("valor", ascending=False)
        for prod, row in by_prod.iterrows():
            print(f"    {str(prod)[:45]:<45}  {int(row['qtd']):>3}x  R$ {row['valor']:>8,.2f}")

    total_reembolsos = reembolsos_df["valor_num"].sum() if not reembolsos_df.empty else 0
    receita_liq = total_receita - total_reembolsos
    lucro_liq   = receita_liq - total_gasto
    lc = "green" if lucro_liq >= 0 else "red"

    print()
    print(c("  " + "-" * 51, "dim"))
    print(f"  {'Receita bruta':<20} R$ {total_receita:>10,.2f}")
    print(f"  {'Reembolsos':<20} {c(f'- R$ {total_reembolsos:>8,.2f}', 'yellow')}  "
          f"({len(reembolsos_df)} refunds)")
    print(f"  {'Receita liquida':<20} R$ {receita_liq:>10,.2f}")
    print(f"  {'Investimento total':<20} - R$ {total_gasto:>8,.2f}")
    print(f"  {c('LUCRO LIQUIDO', 'bold'):<29} {c(f'R$ {lucro_liq:>10,.2f}', lc)}")
    margem = lucro_liq / total_gasto * 100 if total_gasto > 0 else 0
    print(f"  {'Margem':<20} {c(f'{margem:.1f}%', lc)}")
    print()
    print(c("=" * 55, "dim"))
    print()

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Meta Ads -- Quick Status")
    parser.add_argument("--period", default="week",
                        choices=["today", "yesterday", "week", "month", "last7"],
                        help="Periodo de analise")
    parser.add_argument("--since", help="Data inicio YYYY-MM-DD")
    parser.add_argument("--until", help="Data fim YYYY-MM-DD")
    parser.add_argument("--mode", default="status",
                        choices=["status", "creatives", "alerts", "pl", "all"],
                        help="Modo de exibicao")
    args = parser.parse_args()

    date_label = latest_sheets_date()
    since_str, until_str = parse_period(args.period, args.since, args.until)
    since = pd.Timestamp(since_str)
    until = pd.Timestamp(until_str)
    period_label = f"{since_str} a {until_str}"

    resultados   = [calc_produto(k, date_label, since, until) for k in PRODUTOS]
    reembolsos   = load_reembolsos(date_label, since, until)

    mode = args.mode
    if mode in ("status", "all"):
        show_status(resultados, reembolsos, period_label)
    if mode in ("creatives", "all"):
        show_creatives(date_label, since, until)
    if mode in ("alerts", "all"):
        show_alerts(resultados, date_label, since, until)
    if mode in ("pl", "all"):
        show_pl(resultados, reembolsos, period_label)


if __name__ == "__main__":
    main()
