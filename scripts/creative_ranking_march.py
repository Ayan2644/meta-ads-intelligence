"""
Etapa 4 — Ranking de Criativos — Março 2026
Fonte: data/sheets/2026-03-18_*.csv
"""
import pandas as pd
import re
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sheets')
DATE = '2026-03-18'
ALVO = 92.12; BOM = 102.35; LIMITE = 122.82; CORTE = 153.53

def p(f): return os.path.join(BASE, f'{DATE}_{f}')

def br_num(s):
    """Converte '1.234,56' ou '1234,56' para float."""
    if pd.isna(s): return 0.0
    s = str(s).strip().replace('.', '').replace(',', '.')
    try: return float(s)
    except: return 0.0

def parse_date_br(series):
    """Parseia 'DD/MM/YYYY - HH:MM' ou 'DD/MM/YYYY'."""
    return pd.to_datetime(series.astype(str).str[:10], format='%d/%m/%Y', errors='coerce')

# ─────────────────────────────────────────────────────────────────────────────
# 1. ADS (plataforma) — usar colunas DA PLANILHA: DATA, NOME ADS, GASTO, COMPRAS
# ─────────────────────────────────────────────────────────────────────────────
def load_ads(fname, produto):
    df = pd.read_csv(p(fname))
    df.columns = df.columns.str.strip()
    # Filter March via DATA column (sheet col, YYYY-MM-DD format)
    df = df[df['DATA'].astype(str).str.startswith('2026-03')].copy()
    # Parse numeric
    df['GASTO_N'] = df['GASTO'].apply(br_num)
    df['COMPRAS_N'] = pd.to_numeric(df['COMPRAS'], errors='coerce').fillna(0)
    df['IMPRESSOES_N'] = pd.to_numeric(df.get('IMPRESSÕES', df.get('IMPRESS\u00d5ES', 0)), errors='coerce').fillna(0)
    df['CLIQUES_N'] = pd.to_numeric(df['CLIQUES'], errors='coerce').fillna(0)
    # Aggregate by NOME ADS
    agg = df.groupby('NOME ADS').agg(
        GASTO=('GASTO_N', 'sum'),
        COMPRAS_PLAT=('COMPRAS_N', 'sum'),
        IMPRESSOES=('IMPRESSOES_N', 'sum'),
        CLIQUES=('CLIQUES_N', 'sum'),
        DIAS_ATIVO=('DATA', 'nunique')
    ).reset_index()
    agg['PRODUTO'] = produto
    return agg

ads_mda = load_ads('ads_mda.csv', 'MDA')
ads_teus = load_ads('ads_teus.csv', 'TEUS')

# ads_lvc: verificar se tem dados de março
try:
    ads_lvc_raw = pd.read_csv(p('ads_lvc.csv'))
    ads_lvc_raw.columns = ads_lvc_raw.columns.str.strip()
    if 'DATA' in ads_lvc_raw.columns:
        ads_lvc_march = ads_lvc_raw[ads_lvc_raw['DATA'].astype(str).str.startswith('2026-03')]
        if len(ads_lvc_march) > 0:
            ads_lvc_march = ads_lvc_march.copy()
            ads_lvc_march['GASTO_N'] = ads_lvc_march['GASTO'].apply(br_num)
            ads_lvc_march['COMPRAS_N'] = pd.to_numeric(ads_lvc_march['COMPRAS'], errors='coerce').fillna(0)
            ads_lvc = ads_lvc_march.groupby('NOME ADS').agg(
                GASTO=('GASTO_N', 'sum'),
                COMPRAS_PLAT=('COMPRAS_N', 'sum'),
                DIAS_ATIVO=('DATA', 'nunique')
            ).reset_index()
            ads_lvc['PRODUTO'] = 'LVC'
            ads_lvc['IMPRESSOES'] = 0
            ads_lvc['CLIQUES'] = 0
        else:
            ads_lvc = pd.DataFrame()
    else:
        ads_lvc = pd.DataFrame()
except Exception as e:
    ads_lvc = pd.DataFrame()

ads_all = pd.concat([ads_mda, ads_teus] + ([ads_lvc] if len(ads_lvc) > 0 else []), ignore_index=True)
print(f"ADS março: MDA={len(ads_mda)}, TEUS={len(ads_teus)}, LVC={len(ads_lvc) if len(ads_lvc)>0 else 0} criativos")
print(f"Total ads únicos: {len(ads_all)}")
print(f"Gasto total ads: R$ {ads_all['GASTO'].sum():,.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. VENDAS (pixel/UTM) — fonte de verdade para CPA real
# ─────────────────────────────────────────────────────────────────────────────
def load_vendas(fname, produto_principal, produto_label):
    df = pd.read_csv(p(fname))
    df.columns = df.columns.str.strip()
    # Filter STATUS
    df = df[df['STATUS'].isin(['APPROVED', 'COMPLETE'])].copy()
    # Filter March (date format: DD/MM/YYYY - HH:MM)
    df['DATA_dt'] = parse_date_br(df['DATA'])
    df = df[(df['DATA_dt'].dt.year == 2026) & (df['DATA_dt'].dt.month == 3)].copy()
    # Filter produto principal (exact match)
    df = df[df['PRODUTO'] == produto_principal].copy()
    df['_label'] = produto_label
    return df

vend_mda  = load_vendas('vendas_mda.csv',  'Mestres do Algoritmo | Profissão Youtuber', 'MDA')
vend_lvc  = load_vendas('vendas_lvc.csv',  'Lucrando com Vídeos Curtos', 'LVC')
vend_teus = load_vendas('vendas_teus.csv', 'Lucrando com Vídeos Curtos', 'TEUS')

print(f"\nVendas pixel março (principais): MDA={len(vend_mda)}, LVC={len(vend_lvc)}, TEUS={len(vend_teus)}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. UTM attribution: video-adN → AD_NUM, VSL from UTM_CAMPAIGN
# ─────────────────────────────────────────────────────────────────────────────
def extract_ad_num_utm(utm):
    if pd.isna(utm): return None
    m = re.search(r'video-ad(\d+)', str(utm), re.I)
    if m: return int(m.group(1))
    m = re.search(r'ad[\-_]?(\d+)$', str(utm), re.I)
    if m: return int(m.group(1))
    return None

def extract_vsl(camp):
    if pd.isna(camp): return 'N/A'
    s = str(camp).upper()
    if 'VSL-C' in s: return 'VSL-C'
    if 'VSL-B' in s: return 'VSL-B'
    if 'VSL-A' in s: return 'VSL-A'
    return 'N/A'

def extract_fq(camp):
    """F = tráfego frio, Q = tráfego quente/remarketing."""
    if pd.isna(camp): return '?'
    s = str(camp).upper()
    if '-Q-' in s or 'RMKT' in s or 'REMARKETING' in s or 'QUENTE' in s: return 'Q'
    if '-F-' in s or 'FRIO' in s or 'FROID' in s: return 'F'
    return '?'

def build_pixel_agg(df, label):
    if df.empty: return pd.DataFrame()
    rows = []
    for _, r in df.iterrows():
        ad_num = extract_ad_num_utm(r.get('UTM_CONTENT'))
        vsl = extract_vsl(r.get('UTM_CAMPAIGN'))
        fq = extract_fq(r.get('UTM_CAMPAIGN'))
        val = br_num(r.get('VALOR PAGO', 0))
        rows.append({'AD_NUM': ad_num, 'VSL': vsl, 'FQ': fq, 'VALOR': val, 'LABEL': label})
    pix = pd.DataFrame(rows)
    return pix.groupby(['AD_NUM', 'VSL', 'FQ', 'LABEL']).agg(
        VENDAS_PIX=('VALOR', 'count'),
        FAT_PIX=('VALOR', 'sum')
    ).reset_index()

pix_mda  = build_pixel_agg(vend_mda,  'MDA')
pix_lvc  = build_pixel_agg(vend_lvc,  'LVC')
pix_teus = build_pixel_agg(vend_teus, 'TEUS')
pix_all  = pd.concat([pix_mda, pix_lvc, pix_teus], ignore_index=True)

print(f"Pixel agg: MDA={len(pix_mda)}, LVC={len(pix_lvc)}, TEUS={len(pix_teus)} combos ad/vsl")

# Resolve por AD_NUM + LABEL (modo dominante de VSL/FQ)
if not pix_all.empty:
    pix_by_ad = pix_all.groupby(['AD_NUM', 'LABEL']).agg(
        VENDAS_PIX=('VENDAS_PIX', 'sum'),
        FAT_PIX=('FAT_PIX', 'sum'),
        VSL=('VSL', lambda x: x.value_counts().index[0]),
        FQ=('FQ', lambda x: x.value_counts().index[0])
    ).reset_index()
else:
    pix_by_ad = pd.DataFrame(columns=['AD_NUM', 'LABEL', 'VENDAS_PIX', 'FAT_PIX', 'VSL', 'FQ'])

# ─────────────────────────────────────────────────────────────────────────────
# 4. Extrair AD_NUM de NOME ADS (ex: "AD17 [MDA]..." → 17)
# ─────────────────────────────────────────────────────────────────────────────
def extract_ad_num_nome(nome):
    if pd.isna(nome): return None
    m = re.match(r'AD(\d+)\s', str(nome), re.I)
    if m: return int(m.group(1))
    return None

ads_all['AD_NUM'] = ads_all['NOME ADS'].apply(extract_ad_num_nome)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Merge ads × pixel
# ─────────────────────────────────────────────────────────────────────────────
merged = ads_all.merge(
    pix_by_ad,
    left_on=['AD_NUM', 'PRODUTO'],
    right_on=['AD_NUM', 'LABEL'],
    how='left'
)

# CPA plataforma
merged['CPA_PLAT'] = merged.apply(
    lambda r: round(r['GASTO'] / r['COMPRAS_PLAT'], 2) if r['COMPRAS_PLAT'] > 0 else None, axis=1)

# CPA pixel
merged['CPA_PIX'] = merged.apply(
    lambda r: round(r['GASTO'] / r['VENDAS_PIX'], 2)
    if pd.notna(r.get('VENDAS_PIX')) and r.get('VENDAS_PIX', 0) > 0 else None, axis=1)

# ROAS pixel
merged['ROAS_PIX'] = merged.apply(
    lambda r: round(r['FAT_PIX'] / r['GASTO'], 2)
    if pd.notna(r.get('FAT_PIX')) and r.get('FAT_PIX', 0) > 0 and r['GASTO'] > 0 else None, axis=1)

# Status CPA (referência = pixel; fallback = plataforma)
def status_cpa(r):
    cpa = r.get('CPA_PIX')
    if pd.isna(cpa) or cpa is None:
        cpa = r.get('CPA_PLAT')
    if pd.isna(cpa) or cpa is None: return 'SEM DADOS'
    if cpa <= ALVO:   return '[ALVO]'
    if cpa <= BOM:    return '[BOM]'
    if cpa <= LIMITE: return '[LIMITE]'
    if cpa <= CORTE:  return '[CORTE]'
    return '[PAUSAR]'

merged['STATUS'] = merged.apply(status_cpa, axis=1)

# Preencher VSL/FQ de não atribuídos
merged['VSL'] = merged['VSL'].fillna('N/A')
merged['FQ']  = merged['FQ'].fillna('?')

# Sort por CPA_PIX asc (nulos por último), depois CPA_PLAT
merged['_sort'] = merged['CPA_PIX'].fillna(merged['CPA_PLAT'].fillna(9999))
merged = merged.sort_values('_sort').drop(columns='_sort')

# ─────────────────────────────────────────────────────────────────────────────
# 6. OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
pd.set_option('display.max_rows', 300)
pd.set_option('display.width', 250)
pd.set_option('display.max_colwidth', 55)

COLS = ['NOME ADS', 'PRODUTO', 'VSL', 'FQ', 'GASTO', 'COMPRAS_PLAT', 'CPA_PLAT',
        'VENDAS_PIX', 'CPA_PIX', 'ROAS_PIX', 'STATUS']

print("\n" + "="*130)
print("ETAPA 4 — RANKING COMPLETO DE CRIATIVOS — MARÇO 2026")
print("Ordenado por CPA Pixel asc (menor = melhor). Pixel = UTM attribution. Plataforma = Meta API.")
print("="*130)

def fmt(df, cols):
    d = df[[c for c in cols if c in df.columns]].copy()
    for c in ['GASTO', 'FAT_PIX']:
        if c in d.columns:
            d[c] = d[c].apply(lambda x: f'R${x:,.0f}' if pd.notna(x) else '-')
    for c in ['CPA_PLAT', 'CPA_PIX']:
        if c in d.columns:
            d[c] = d[c].apply(lambda x: f'R${x:.0f}' if pd.notna(x) else '-')
    for c in ['ROAS_PIX']:
        if c in d.columns:
            d[c] = d[c].apply(lambda x: f'{x:.2f}x' if pd.notna(x) else '-')
    for c in ['COMPRAS_PLAT', 'VENDAS_PIX']:
        if c in d.columns:
            d[c] = d[c].apply(lambda x: f'{int(x)}' if pd.notna(x) and x > 0 else '-')
    return d

print(fmt(merged, COLS).to_string(index=False))

# ── Resumo por STATUS ─────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RESUMO POR STATUS (CPA pixel ou plataforma)")
print("="*60)
status_summary = merged.groupby('STATUS').agg(
    Criativos=('NOME ADS', 'count'),
    Gasto=('GASTO', 'sum'),
    Compras_Plat=('COMPRAS_PLAT', 'sum'),
    Vendas_Pix=('VENDAS_PIX', lambda x: x.fillna(0).sum())
).reset_index()
status_summary['Gasto'] = status_summary['Gasto'].apply(lambda x: f'R${x:,.0f}')
print(status_summary.to_string(index=False))

# ── VSL breakdown ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("VSL BREAKDOWN — PIXEL (principais)")
print("="*60)
vsl_df = merged[merged['VSL'] != 'N/A'].copy()
if not vsl_df.empty:
    vsl_sum = vsl_df.groupby(['PRODUTO', 'VSL']).agg(
        Criativos=('NOME ADS', 'count'),
        Gasto=('GASTO', 'sum'),
        Vendas_Pix=('VENDAS_PIX', lambda x: x.fillna(0).sum()),
        Fat_Pix=('FAT_PIX', lambda x: x.fillna(0).sum())
    ).reset_index()
    vsl_sum['CPA'] = vsl_sum.apply(
        lambda r: f'R${r["Gasto"]/r["Vendas_Pix"]:.0f}' if r['Vendas_Pix'] > 0 else '-', axis=1)
    vsl_sum['ROAS'] = vsl_sum.apply(
        lambda r: f'{r["Fat_Pix"]/r["Gasto"]:.2f}x' if r['Gasto'] > 0 else '-', axis=1)
    vsl_sum['Gasto'] = vsl_sum['Gasto'].apply(lambda x: f'R${x:,.0f}')
    vsl_sum['Vendas_Pix'] = vsl_sum['Vendas_Pix'].apply(lambda x: f'{int(x)}')
    vsl_sum['Fat_Pix'] = vsl_sum['Fat_Pix'].apply(lambda x: f'R${x:,.0f}')
    print(vsl_sum[['PRODUTO', 'VSL', 'Criativos', 'Gasto', 'Vendas_Pix', 'Fat_Pix', 'CPA', 'ROAS']].to_string(index=False))

# ── Top 10 / Bottom 10 ───────────────────────────────────────────────────────
with_cpa = merged[merged['CPA_PIX'].notna()].copy()
print(f"\n{'='*70}")
print(f"TOP 10 CRIATIVOS — MENOR CPA PIXEL ({len(with_cpa)} com atribuição)")
print("="*70)
print(fmt(with_cpa.head(10), COLS).to_string(index=False))

print(f"\n{'='*70}")
print(f"BOTTOM 10 — MAIOR CPA PIXEL (candidatos a pausa)")
print("="*70)
print(fmt(with_cpa.tail(10), COLS).to_string(index=False))

print(f"\n{'='*70}")
print(f"SEM ATRIBUIÇÃO PIXEL — gasto mas 0 vendas UTM ({len(merged[merged['CPA_PIX'].isna()])} criativos)")
print("="*70)
no_pix = merged[merged['CPA_PIX'].isna()].copy()
print(fmt(no_pix, ['NOME ADS', 'PRODUTO', 'VSL', 'FQ', 'GASTO', 'COMPRAS_PLAT', 'CPA_PLAT', 'STATUS']).to_string(index=False))

print("\nScript concluído.")
