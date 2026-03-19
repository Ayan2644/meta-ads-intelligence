"""
*status dia {target_date} — Performance de um dia específico
Fonte: data/sheets/ (TIER 1)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aios_utils import *

TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else '2026-03-18'
Y, M, D = [int(x) for x in TARGET_DATE.split('-')]

label = latest_date_label()

# ── Carregar diarios ──────────────────────────────────────────────────────────
def load_diario_day(produto):
    path = sheets_path(f'diario_{produto}', label)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df['DATA_DT'] = parse_date_diario(df['Data'] if 'Data' in df.columns else df.iloc[:, 0])
    df = df[(df['DATA_DT'].dt.year == Y) & (df['DATA_DT'].dt.month == M) & (df['DATA_DT'].dt.day == D)].copy()
    if df.empty:
        return None
    gasto_col = next((c for c in df.columns if 'GASTO' in c.upper()), None)
    vendas_col = next((c for c in df.columns if 'VENDA' in c.upper()), None)
    ic_col = next((c for c in df.columns if c.upper() == 'IC'), None)
    imp_col = next((c for c in df.columns if 'IMPRESS' in c.upper()), None)
    cli_col = next((c for c in df.columns if 'CLIQU' in c.upper() or 'CLICK' in c.upper()), None)
    return {
        'gasto':     br_num(df[gasto_col].iloc[0]) if gasto_col else 0,
        'vendas_d':  int(pd.to_numeric(df[vendas_col].iloc[0], errors='coerce') or 0) if vendas_col else 0,
        'ic':        int(pd.to_numeric(df[ic_col].iloc[0], errors='coerce') or 0) if ic_col else 0,
        'impressoes':parse_impressoes(df[imp_col].iloc[0]) if imp_col else 0,
        'cliques':   int(pd.to_numeric(df[cli_col].iloc[0], errors='coerce') or 0) if cli_col else 0,
    }

d_mda  = load_diario_day('mda')
d_lvc  = load_diario_day('lvc')
d_teus = load_diario_day('teus')

# ── Carregar vendas do dia ────────────────────────────────────────────────────
def load_vendas_day(produto, produto_principal, label=label):
    path = sheets_path(f'vendas_{produto}', label)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df[df['STATUS'].isin(STATUS_VALIDO)].copy()
    df['DATA_DT'] = parse_date_vendas(df['DATA'])
    df = df[(df['DATA_DT'].dt.year == Y) & (df['DATA_DT'].dt.month == M) & (df['DATA_DT'].dt.day == D)].copy()
    prod_col = next((c for c in df.columns if 'PRODUTO' in c.upper()), None)
    if prod_col:
        df_main = df[df[prod_col] == produto_principal]
        df_bump  = df[df[prod_col] != produto_principal]
    else:
        df_main = df
        df_bump  = pd.DataFrame()
    valor_col = next((c for c in df.columns if 'VALOR' in c.upper() and 'PAGO' in c.upper()), None)
    fat_main = df_main[valor_col].apply(br_num).sum() if valor_col and not df_main.empty else 0
    fat_bump = df_bump[valor_col].apply(br_num).sum() if valor_col and not df_bump.empty else 0
    return {
        'vendas': len(df_main),
        'fat_main': fat_main,
        'fat_bump': fat_bump,
        'fat_total': fat_main + fat_bump,
    }

v_mda  = load_vendas_day('mda',  PRODUTOS_PRINCIPAIS['mda'])
v_lvc  = load_vendas_day('lvc',  PRODUTOS_PRINCIPAIS['lvc'])
v_teus = load_vendas_day('teus', PRODUTOS_PRINCIPAIS['teus'])

# ── Calcular totais ───────────────────────────────────────────────────────────
g = {
    'mda':  d_mda['gasto']  if d_mda  else 0,
    'lvc':  d_lvc['gasto']  if d_lvc  else 0,
    'teus': d_teus['gasto'] if d_teus else 0,
}
g['total'] = sum(g.values())

fat = {
    'mda':  v_mda['fat_total'],
    'lvc':  v_lvc['fat_total'],
    'teus': v_teus['fat_total'],
}
fat['total'] = sum(fat.values())

vendas = {
    'mda':  v_mda['vendas'],
    'lvc':  v_lvc['vendas'],
    'teus': v_teus['vendas'],
}
vendas['total'] = sum(vendas.values())

lucro = {k: fat[k] - g[k] for k in ['mda','lvc','teus','total']}
roas  = {k: calc_roas(fat[k], g[k]) for k in ['mda','lvc','teus','total']}
cpa   = {k: calc_cpa(g[k], vendas[k]) for k in ['mda','lvc','teus','total']}

ic_total = (d_mda['ic'] if d_mda else 0) + (d_lvc['ic'] if d_lvc else 0) + (d_teus['ic'] if d_teus else 0)
imp_total = (d_mda['impressoes'] if d_mda else 0) + (d_lvc['impressoes'] if d_lvc else 0) + (d_teus['impressoes'] if d_teus else 0)

# ── Reembolsos do dia ─────────────────────────────────────────────────────────
try:
    reemb = load_reembolsos(year=Y, month=M)
    reemb = reemb[reemb['DATA_DT'].dt.day == D] if not reemb.empty else reemb
    reemb_total = reemb['VALOR_REEMBOLSO'].sum() if not reemb.empty else 0
except:
    reemb_total = 0

lucro_liq = fat['total'] - g['total'] - reemb_total

# ── OUTPUT ────────────────────────────────────────────────────────────────────
def line(w=68): print('-' * w)
def bar(label, val, bench, higher_is_better=True):
    ok = (val >= bench) if higher_is_better else (val <= bench)
    flag = '[OK]' if ok else '[!!]'
    return f'{flag}'

print()
print('=' * 68)
from datetime import date as dt_date
dias_pt = ['segunda-feira','terca-feira','quarta-feira','quinta-feira','sexta-feira','sabado','domingo']
dia_semana = dias_pt[dt_date(Y,M,D).weekday()]
meses_pt = ['','janeiro','fevereiro','marco','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
print(f'  *STATUS -- {D:02d} DE {meses_pt[M].upper()} {Y} ({dia_semana})')
print('=' * 68)

print(f'\n  {"PRODUTO":<10} {"GASTO":>10} {"FAT":>12} {"VENDAS":>7} {"CPA":>8} {"ROAS":>7} {"LUCRO":>12}')
line()
for k, nome in [('mda','MDA'), ('lvc','LVC'), ('teus','TEUS')]:
    cpa_s = fmt_cpa(cpa[k]) if cpa[k] else '  -  '
    roas_s = fmt_roas(roas[k]) if roas[k] else '  -  '
    st = cpa_status(cpa[k]) if cpa[k] else ''
    print(f'  {nome:<10} {fmt_brl(g[k]):>10} {fmt_brl(fat[k]):>12} {vendas[k]:>7} {cpa_s:>8} {roas_s:>7} {fmt_brl(lucro[k]):>12}  {st}')
line()
print(f'  {"TOTAL":<10} {fmt_brl(g["total"]):>10} {fmt_brl(fat["total"]):>12} {vendas["total"]:>7} {fmt_cpa(cpa["total"]) if cpa["total"] else "-":>8} {fmt_roas(roas["total"]) if roas["total"] else "-":>7} {fmt_brl(lucro["total"]):>12}')

print(f'\n  Reembolsos:    {fmt_brl(reemb_total)}')
print(f'  Lucro liquido: {fmt_brl(lucro_liq)}')
print(f'  IC (checkout): {ic_total}  |  Impressoes: {imp_total:,}')

# Benchmarks
print(f'\n  ROAS vs benchmark (>=1,33x): {fmt_roas(roas["total"])} {bar("",roas["total"] if roas["total"] else 0, 1.33)}')
print(f'  CPA total vs CORTE (R$153):  {fmt_cpa(cpa["total"])} {bar("",cpa["total"] if cpa["total"] else 999, CPA_CORTE, higher_is_better=False)}')

# Breakdown faturamento
print(f'\n  FATURAMENTO DETALHADO:')
for k, nome in [('mda','MDA'), ('lvc','LVC'), ('teus','TEUS')]:
    vobj = [v_mda, v_lvc, v_teus][['mda','lvc','teus'].index(k)]
    print(f'  {nome}: principal R${vobj["fat_main"]:,.2f} ({vobj["vendas"]}v) + bumps R${vobj["fat_bump"]:,.2f}')

print()
print('=' * 68)
print()
