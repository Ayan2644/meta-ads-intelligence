"""
*pausar / *alerts — O que pausar AGORA. Sem enrolação.
Fonte: data/sheets/ | Regras: analyst-rules.md
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aios_utils import *
from datetime import date as dtdate

label = latest_date_label()
Y, M = 2026, 3
hoje = dtdate(Y, M, 18)

# ── Carregar ads (plataforma) — com range de datas ────────────────────────────
def get_ads_all():
    rows = []
    ranges = {}
    for produto in ['mda', 'teus']:
        try:
            path = sheets_path(f'ads_{produto}', label)
            raw = pd.read_csv(path)
            raw.columns = raw.columns.str.strip()
            raw['DATA_DT'] = parse_date_ads(raw['DATA'])
            raw = filter_period(raw, 'DATA_DT', Y, M)
            if not raw.empty:
                ranges[produto] = (raw['DATA_DT'].min(), raw['DATA_DT'].max())
            df = load_ads(produto, label, Y, M)
            df['PRODUTO'] = produto.upper()
            rows.append(df)
        except:
            pass
    combined = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    # Calcular periodo global
    all_min = min((v[0] for v in ranges.values()), default=None)
    all_max = max((v[1] for v in ranges.values()), default=None)
    return combined, all_min, all_max

# ── Carregar vendas pixel por ad — com campanha e datas ───────────────────────
def get_pixel_by_ad():
    rows = []
    for produto in ['mda', 'teus']:
        try:
            v = load_vendas(produto, label, Y, M, apenas_principal=True)
            if v.empty:
                continue
            v['AD_NUM'] = v['UTM_CONTENT'].apply(utm_to_ad_num)
            v = v[v['AD_NUM'].notna()].copy()
            if v.empty:
                continue

            # Agregar por AD_NUM
            grp = v.groupby('AD_NUM').agg(
                VENDAS_PIX=('VALOR_PAGO', 'count'),
                FAT_PIX=('VALOR_PAGO', 'sum'),
                PRIMEIRA_VENDA=('DATA_DT', 'min'),
                ULTIMA_VENDA=('DATA_DT', 'max'),
            ).reset_index()

            # Campanha mais frequente por ad (para identificar no Meta)
            camp_mode = (
                v.dropna(subset=['UTM_CAMPAIGN'])
                .groupby('AD_NUM')['UTM_CAMPAIGN']
                .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else '')
                .reset_index()
                .rename(columns={'UTM_CAMPAIGN': 'CAMPANHA'})
            )
            grp = grp.merge(camp_mode, on='AD_NUM', how='left')
            grp['PRODUTO'] = produto.upper()
            rows.append(grp)
        except:
            pass
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()

ads, periodo_min, periodo_max = get_ads_all()
pixel = get_pixel_by_ad()

if ads.empty:
    print("Sem dados de ads disponiveis.")
    sys.exit(0)

# Formatar periodo
def fmt_date(d):
    return d.strftime('%d/%m') if d is not None and pd.notna(d) else '?'

periodo_str = f'{fmt_date(periodo_min)} a {fmt_date(periodo_max)}'

# Extrair ad_num do NOME ADS
ads['AD_NUM'] = ads['NOME ADS'].apply(nome_to_ad_num)

# Merge ads + pixel
if not pixel.empty:
    merged = ads.merge(pixel, on=['AD_NUM', 'PRODUTO'], how='left')
else:
    merged = ads.copy()
    for c in ['VENDAS_PIX', 'FAT_PIX', 'PRIMEIRA_VENDA', 'ULTIMA_VENDA', 'CAMPANHA']:
        merged[c] = None

merged['VENDAS_PIX'] = pd.to_numeric(merged.get('VENDAS_PIX', 0), errors='coerce').fillna(0)
merged['CPA_PLAT'] = merged.apply(lambda r: calc_cpa(r['GASTO'], r['COMPRAS']), axis=1)
merged['CPA_PIX']  = merged.apply(lambda r: calc_cpa(r['GASTO'], r['VENDAS_PIX']), axis=1)

# Referência CPA: pixel se disponível, else plataforma
merged['CPA_REF'] = merged.apply(
    lambda r: r['CPA_PIX'] if pd.notna(r.get('CPA_PIX')) and r.get('VENDAS_PIX', 0) > 0
              else r['CPA_PLAT'], axis=1)

# Dias sem venda (pixel)
merged['DIAS_SEM_VENDA'] = merged['ULTIMA_VENDA'].apply(
    lambda d: (hoje - d.date()).days if pd.notna(d) else 99)

# ── Classificar alertas ────────────────────────────────────────────────────────
def classificar(r):
    cpa   = r['CPA_REF']
    dias  = r.get('DIAS_SEM_VENDA', 99)
    gasto = r['GASTO']
    vendas = r['VENDAS_PIX']

    if pd.isna(cpa):
        if gasto > 200 and vendas == 0:
            return 'PAUSAR', 'Gasto alto sem nenhuma venda atribuida'
        return 'MONITORAR', 'Sem dados suficientes'

    if cpa > CPA_CORTE and dias >= 2:
        return 'PAUSAR AGORA', f'CPA {fmt_cpa(cpa)} + {dias}d sem venda'
    if cpa > CPA_CORTE:
        return 'ALERTA', f'CPA {fmt_cpa(cpa)} -- se amanha sem venda PAUSAR'
    if cpa > CPA_LIMITE:
        return 'MONITORAR', f'CPA {fmt_cpa(cpa)} no limite'
    return 'OK', fmt_cpa(cpa)

merged[['ALERTA', 'MOTIVO']] = merged.apply(
    lambda r: pd.Series(classificar(r)), axis=1)

# ── Separar por urgência ───────────────────────────────────────────────────────
pausar    = merged[merged['ALERTA'] == 'PAUSAR AGORA'].sort_values('CPA_REF', ascending=False)
alerta    = merged[merged['ALERTA'] == 'ALERTA'].sort_values('CPA_REF', ascending=False)
monitorar = merged[merged['ALERTA'].isin(['MONITORAR', 'PAUSAR'])].sort_values('GASTO', ascending=False)
ok_count  = len(merged[merged['ALERTA'] == 'OK'])

# Colunas principais — inclui CAMPANHA e periodo no header
COLS_FULL = ['NOME ADS', 'PRODUTO', 'CAMPANHA', 'GASTO', 'VENDAS_PIX', 'CPA_REF',
             'PRIMEIRA_VENDA', 'ULTIMA_VENDA', 'DIAS_SEM_VENDA', 'MOTIVO']

def fmt_campanha(c):
    if pd.isna(c) or not c:
        return '-'
    s = str(c)
    # Extrair parte relevante: produto-fq-vsl-fase
    # ex: "MDA-F-VSL-C-AD17-2026-03" → mostrar os primeiros segmentos significativos
    parts = s.split('-')
    # Pegar os 5 primeiros segmentos (ex: MDA-F-VSL-C-AD17)
    return '-'.join(parts[:5]) if len(parts) >= 5 else s[:40]

def show(df, cols=None):
    use_cols = cols or COLS_FULL
    d = df[[c for c in use_cols if c in df.columns]].copy()

    if 'GASTO' in d.columns:
        d['GASTO'] = d['GASTO'].apply(fmt_brl)
    if 'VENDAS_PIX' in d.columns:
        d['VENDAS_PIX'] = d['VENDAS_PIX'].apply(fmt_int)
    if 'COMPRAS' in d.columns:
        d['COMPRAS'] = d['COMPRAS'].apply(lambda x: fmt_int(x) if pd.notna(x) else '-')
    if 'CPA_REF' in d.columns:
        d['CPA_REF'] = d['CPA_REF'].apply(lambda x: fmt_cpa(x) if pd.notna(x) else '-')
    if 'CPA_PLAT' in d.columns:
        d['CPA_PLAT'] = d['CPA_PLAT'].apply(lambda x: fmt_cpa(x) if pd.notna(x) else '-')
    if 'DIAS_SEM_VENDA' in d.columns:
        d['DIAS_SEM_VENDA'] = d['DIAS_SEM_VENDA'].apply(
            lambda x: f'{int(x)}d' if pd.notna(x) and x < 90 else '-')
    if 'PRIMEIRA_VENDA' in d.columns:
        d['PRIMEIRA_VENDA'] = d['PRIMEIRA_VENDA'].apply(
            lambda x: x.strftime('%d/%m') if pd.notna(x) else '-')
    if 'ULTIMA_VENDA' in d.columns:
        d['ULTIMA_VENDA'] = d['ULTIMA_VENDA'].apply(
            lambda x: x.strftime('%d/%m') if pd.notna(x) else '-')
    if 'CAMPANHA' in d.columns:
        d['CAMPANHA'] = d['CAMPANHA'].apply(fmt_campanha)

    pd.set_option('display.max_colwidth', 52)
    pd.set_option('display.width', 260)
    print(d.to_string(index=False))

# ── OUTPUT ─────────────────────────────────────────────────────────────────────
print()
print('=' * 80)
print(f'  *ALERTS -- ACOES URGENTES -- {hoje.strftime("%d/%m/%Y")}')
print(f'  Periodo analisado: {periodo_str} | Corte: CPA > R${CPA_CORTE:.0f} + 2d sem venda')
print(f'  Fonte: data/sheets/{label}_ads_*.csv + vendas_*.csv')
print('=' * 80)

if not pausar.empty:
    print(f'\n[PAUSAR AGORA] -- {len(pausar)} criativo(s)')
    print('-' * 80)
    show(pausar)
    print(f'\n  Gasto acumulado nesses criativos: {fmt_brl(pausar["GASTO"].sum())}')
else:
    print('\n[PAUSAR AGORA] -- Nenhum criativo no corte imediato.')

if not alerta.empty:
    print(f'\n[ALERTA -- AMANHA PAUSAR] -- {len(alerta)} criativo(s)')
    print('-' * 80)
    show(alerta)

if not monitorar.empty:
    sem_dados = monitorar[monitorar['ALERTA'] == 'PAUSAR']
    limite    = monitorar[monitorar['ALERTA'] == 'MONITORAR']
    if not sem_dados.empty:
        print(f'\n[GASTO SEM ATRIBUICAO] -- {len(sem_dados)} criativo(s) com gasto e 0 vendas pixel')
        print('-' * 80)
        show(sem_dados, ['NOME ADS', 'PRODUTO', 'CAMPANHA', 'GASTO', 'COMPRAS', 'CPA_REF', 'MOTIVO'])
    if not limite.empty:
        print(f'\n[MONITORAR -- CPA no LIMITE] -- {len(limite)} criativo(s)')
        print('-' * 80)
        show(limite, ['NOME ADS', 'PRODUTO', 'CAMPANHA', 'GASTO', 'VENDAS_PIX', 'CPA_REF',
                      'PRIMEIRA_VENDA', 'ULTIMA_VENDA', 'MOTIVO'])

print(f'\n[OK] -- {ok_count} criativos dentro dos targets')
print()
print('=' * 80)
total_ads  = len(merged)
gasto_ok   = merged[merged['ALERTA'] == 'OK']['GASTO'].sum()
gasto_risco = merged[merged['ALERTA'].isin(['PAUSAR AGORA', 'ALERTA'])]['GASTO'].sum()
print(f'  Total analisado: {total_ads} criativos | Gasto OK: {fmt_brl(gasto_ok)} | Em risco: {fmt_brl(gasto_risco)}')
print(f'  CPA calculado sobre gasto de {periodo_str} (acumulado do mes)')
print('=' * 80)
print()
