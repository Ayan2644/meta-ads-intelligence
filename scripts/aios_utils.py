"""
aios_utils.py — Biblioteca central de parsing e análise do Meta Ads Intelligence
Aprende com erros anteriores para nunca repetir os mesmos problemas.

FIX GLOBAL: força UTF-8 no stdout/stderr do Windows (cp1252 mata qualquer acento ou linha especial)
"""
import sys as _sys
if hasattr(_sys.stdout, 'reconfigure'):
    _sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(_sys.stderr, 'reconfigure'):
    _sys.stderr.reconfigure(encoding='utf-8', errors='replace')
"""

PADRÕES APRENDIDOS:
- Números BR: "R$ 1.234,56" → float (strip R$, replace . by '', , by .)
- Datas diario: DD/MM/YYYY (dayfirst=True)
- Datas vendas: "DD/MM/YYYY - HH:MM" → tomar [:10]
- Datas ads: coluna DATA (YYYY-MM-DD), não a coluna 'date' (Meta API)
- GASTO em ads: string BR sem R$, ex "1.234,56"
- Impressões diario: "45.994" = 45994 (ponto como separador de milhar)
- STATUS válido: apenas APPROVED e COMPLETE
- Produto principal: match EXATO (==), não 'in' (evita order bumps)
- Acelerador: SEMPRE excluído
- Emoji: não usar (Windows cp1252 quebra)
- Verificar dataframe vazio antes de groupby
"""

import os
import re
import glob
import pandas as pd

# ── Constantes ───────────────────────────────────────────────────────────────
SHEETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sheets')

CPA_ALVO   = 92.12
CPA_BOM    = 102.35
CPA_LIMITE = 122.82
CPA_CORTE  = 153.53

STATUS_VALIDO = ['APPROVED', 'COMPLETE']

PRODUTOS_PRINCIPAIS = {
    'mda':  'Mestres do Algoritmo | Profissão Youtuber',
    'lvc':  'Lucrando com Vídeos Curtos',
    'teus': 'Lucrando com Vídeos Curtos',
}

# analyst-rules.md Seção 10.4: MDA usa startswith, LVC/TEUS usam exact match
# MDA pode ter variantes do nome — startswith é mais seguro
def match_produto_principal(produto_serie, produto_key):
    if produto_key == 'mda':
        return produto_serie.str.startswith('Mestres do Algoritmo', na=False)
    else:
        alvo = PRODUTOS_PRINCIPAIS[produto_key]
        return produto_serie == alvo

# ── Data files ───────────────────────────────────────────────────────────────

def latest_date_label(sheets_dir=None):
    """Retorna o date_label mais recente disponível em data/sheets/."""
    d = sheets_dir or SHEETS_DIR
    files = glob.glob(os.path.join(d, '*_diario_mda.csv'))
    if not files:
        return None
    labels = [os.path.basename(f).split('_')[0] for f in files]
    return sorted(labels)[-1]

def sheets_path(alias, date_label=None, sheets_dir=None):
    """Retorna o caminho completo para um arquivo de sheets."""
    d = sheets_dir or SHEETS_DIR
    dt = date_label or latest_date_label(d)
    return os.path.join(d, f'{dt}_{alias}.csv')

# ── Parsing numérico ─────────────────────────────────────────────────────────

def br_num(s):
    """Converte número BR para float. Aceita 'R$ 1.234,56', '1234,56', '1.234', NaN."""
    if pd.isna(s) or s == '' or s == '-':
        return 0.0
    s = str(s).strip()
    s = re.sub(r'R\$\s*', '', s)          # remove R$
    s = s.replace('\xa0', '')              # non-breaking space
    # Detectar formato: se tem vírgula após ponto → BR (1.234,56)
    if re.search(r'\.\d{3},', s):          # 1.234,56
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s and '.' not in s:        # 1234,56
        s = s.replace(',', '.')
    elif '.' in s and ',' not in s:        # pode ser 1.234 (milhar) ou 1.23 (decimal)
        # Se últimos dígitos após ponto forem 3 → milhar; se forem 1 ou 2 → decimal
        after_dot = s.split('.')[-1]
        if len(after_dot) == 3:
            s = s.replace('.', '')          # 1.234 → 1234
        # else deixar como está (1.23 → 1.23)
    try:
        return float(s)
    except ValueError:
        return 0.0

def parse_impressoes(s):
    """Impressões diario vêm como '45.994' (ponto = milhar). Converter para int."""
    if pd.isna(s) or s == '' or s == '-':
        return 0
    s = str(s).strip().replace('.', '').replace(',', '')
    try:
        return int(float(s))
    except ValueError:
        return 0

# ── Parsing de datas ─────────────────────────────────────────────────────────

def parse_date_diario(series):
    """Datas de diario_*.csv: DD/MM/YYYY."""
    return pd.to_datetime(series.astype(str).str.strip(), dayfirst=True, errors='coerce')

def parse_date_vendas(series):
    """Datas de vendas_*.csv: 'DD/MM/YYYY - HH:MM' ou 'DD/MM/YYYY'."""
    clean = series.astype(str).str[:10].str.strip()
    return pd.to_datetime(clean, format='%d/%m/%Y', errors='coerce')

def parse_date_ads(series):
    """Datas de ads_*.csv coluna DATA: YYYY-MM-DD."""
    return pd.to_datetime(series.astype(str).str.strip(), errors='coerce')

def is_march_2026(dt_series):
    return (dt_series.dt.year == 2026) & (dt_series.dt.month == 3)

def filter_period(df, date_col, year, month):
    """Filtra DataFrame por ano/mês usando a coluna já parseada."""
    mask = (df[date_col].dt.year == year) & (df[date_col].dt.month == month)
    return df[mask].copy()

# ── Loaders ─────────────────────────────────────────────────────────────────

def load_diario(produto, date_label=None, year=2026, month=3):
    """
    Carrega diario_{produto}.csv.
    Colunas garantidas na saída: DATA_DT, GASTO, VENDAS, IC, IMPRESSOES, CLIQUES
    """
    path = sheets_path(f'diario_{produto}', date_label)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    df['DATA_DT'] = parse_date_diario(df['Data'] if 'Data' in df.columns else df.iloc[:, 0])
    df = filter_period(df, 'DATA_DT', year, month)

    # Mapear colunas com nomes variáveis
    col = lambda *kws: next((c for c in df.columns for k in kws if k.upper() in c.upper()), None)

    df['GASTO']     = df[col('GASTO', 'GASTO')].apply(br_num) if col('GASTO') else 0.0
    df['VENDAS']    = pd.to_numeric(df[col('VENDAS', 'VENDA')], errors='coerce').fillna(0) if col('VENDAS', 'VENDA') else 0
    df['IC']        = pd.to_numeric(df[col('IC')], errors='coerce').fillna(0) if col('IC') else 0
    df['IMPRESSOES'] = df[col('IMPRES', 'IMPRESS')].apply(parse_impressoes) if col('IMPRES', 'IMPRESS') else 0
    df['CLIQUES']   = pd.to_numeric(df[col('CLIQU', 'CLICK')], errors='coerce').fillna(0) if col('CLIQU', 'CLICK') else 0

    return df[['DATA_DT', 'GASTO', 'VENDAS', 'IC', 'IMPRESSOES', 'CLIQUES']].copy()


def load_vendas(produto, date_label=None, year=2026, month=3,
                apenas_principal=True, incluir_bumps=False):
    """
    Carrega vendas_{produto}.csv.
    Aplica filtros: STATUS válido, período, produto principal (se apenas_principal=True).
    Retorna DataFrame com colunas: DATA_DT, VALOR_PAGO, PRODUTO, STATUS, UTM_CONTENT, UTM_CAMPAIGN
    """
    path = sheets_path(f'vendas_{produto}', date_label)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # Data
    data_col = next((c for c in df.columns if 'DATA' in c.upper() or 'DATE' in c.upper()), df.columns[0])
    df['DATA_DT'] = parse_date_vendas(df[data_col])
    df = filter_period(df, 'DATA_DT', year, month)

    # STATUS — excluir sem status e status inválidos
    if 'STATUS' in df.columns:
        df = df[df['STATUS'].isin(STATUS_VALIDO)].copy()
    else:
        # Se não tem coluna STATUS, não filtrar (dado legado)
        pass

    # analyst-rules.md Seção 10.4: MDA=startswith | LVC/TEUS=exact
    if apenas_principal and 'PRODUTO' in df.columns:
        mask = match_produto_principal(df['PRODUTO'], produto.lower())
        df = df[mask].copy()

    # Normalizar colunas de saída
    valor_col = next((c for c in df.columns if 'VALOR' in c.upper() and 'PAGO' in c.upper()), None)
    if valor_col:
        df['VALOR_PAGO'] = df[valor_col].apply(br_num)
    else:
        df['VALOR_PAGO'] = 0.0

    for col_out, keywords in [('UTM_CONTENT', ['UTM_CONTENT', 'UTM CONTENT']),
                               ('UTM_CAMPAIGN', ['UTM_CAMPAIGN', 'UTM CAMPAIGN']),
                               ('PRODUTO', ['PRODUTO', 'PRODUCT']),
                               ('STATUS', ['STATUS'])]:
        src = next((c for c in df.columns for k in keywords if c.upper() == k.upper()), None)
        if src and src != col_out:
            df[col_out] = df[src]
        elif src is None:
            df[col_out] = None

    keep = ['DATA_DT', 'VALOR_PAGO', 'PRODUTO', 'STATUS', 'UTM_CONTENT', 'UTM_CAMPAIGN']
    return df[[c for c in keep if c in df.columns]].copy()


def load_ads(produto, date_label=None, year=2026, month=3):
    """
    Carrega ads_{produto}.csv.
    USA coluna DATA (planilha), não 'date' (Meta API).
    Agrega por NOME ADS: GASTO, COMPRAS, IMPRESSOES, CLIQUES, DIAS_ATIVO
    """
    path = sheets_path(f'ads_{produto}', date_label)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # Usar coluna DATA da planilha (YYYY-MM-DD), não 'date' da Meta API
    df['DATA_DT'] = parse_date_ads(df['DATA'])
    df = filter_period(df, 'DATA_DT', year, month)

    if df.empty:
        return pd.DataFrame(columns=['NOME ADS', 'PRODUTO', 'GASTO', 'COMPRAS', 'IMPRESSOES', 'CLIQUES', 'DIAS_ATIVO'])

    df['GASTO_N']     = df['GASTO'].apply(br_num)
    df['COMPRAS_N']   = pd.to_numeric(df['COMPRAS'], errors='coerce').fillna(0)
    # Impressões podem estar em várias colunas e formatos
    imp_col = next((c for c in df.columns if 'IMPRESS' in c.upper() and '2' not in c), None)
    df['IMPRESSOES_N'] = df[imp_col].apply(parse_impressoes) if imp_col else 0
    cli_col = next((c for c in df.columns if 'CLIQU' in c.upper() and '2' not in c), None)
    df['CLIQUES_N']   = pd.to_numeric(df[cli_col], errors='coerce').fillna(0) if cli_col else 0

    agg = df.groupby('NOME ADS').agg(
        GASTO=('GASTO_N', 'sum'),
        COMPRAS=('COMPRAS_N', 'sum'),
        IMPRESSOES=('IMPRESSOES_N', 'sum'),
        CLIQUES=('CLIQUES_N', 'sum'),
        DIAS_ATIVO=('DATA_DT', 'nunique')
    ).reset_index()
    agg['PRODUTO'] = produto.upper()
    return agg


def load_reembolsos(date_label=None, year=2026, month=3):
    """Carrega reembolsos.csv filtrado por período."""
    path = sheets_path('reembolsos', date_label)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    data_col = next((c for c in df.columns if 'DATA' in c.upper()), df.columns[0])
    df['DATA_DT'] = parse_date_vendas(df[data_col])
    df = filter_period(df, 'DATA_DT', year, month)
    valor_col = next((c for c in df.columns if 'VALOR' in c.upper()), None)
    if valor_col:
        df['VALOR_REEMBOLSO'] = df[valor_col].apply(br_num)
    return df

# ── UTM attribution ─────────────────────────────────────────────────────────

def utm_to_ad_num(utm_content):
    """'video-ad17' → 17. 'video-ad017' → 17. None/NaN → None."""
    if pd.isna(utm_content) or not utm_content:
        return None
    m = re.search(r'video-ad0*(\d+)', str(utm_content), re.I)
    if m:
        return int(m.group(1))
    m = re.search(r'ad[\-_]?0*(\d+)$', str(utm_content), re.I)
    if m:
        return int(m.group(1))
    return None

def nome_to_ad_num(nome_ads):
    """'AD17 [MDA]...' → 17. 'AD017 [LVCT]...' → 17."""
    if pd.isna(nome_ads):
        return None
    m = re.match(r'AD0*(\d+)\s', str(nome_ads), re.I)
    return int(m.group(1)) if m else None

def extract_vsl(utm_campaign):
    """'...-VSL-C-...' → 'VSL-C'. Sem match → 'N/A'."""
    if pd.isna(utm_campaign):
        return 'N/A'
    s = str(utm_campaign).upper()
    for v in ['VSL-C', 'VSL-B', 'VSL-A']:
        if v.replace('-', '') in s.replace('-', ''):
            return v
    return 'N/A'

def extract_fq(utm_campaign):
    """'-F-' → 'F' (frio). '-Q-' ou RMKT → 'Q' (quente)."""
    if pd.isna(utm_campaign):
        return '?'
    s = str(utm_campaign).upper()
    if any(k in s for k in ['-Q-', 'RMKT', 'REMARKETING', 'QUENTE']):
        return 'Q'
    if any(k in s for k in ['-F-', 'FRIO']):
        return 'F'
    return '?'

# ── CPA / Status ─────────────────────────────────────────────────────────────

def cpa_status(cpa):
    """Retorna status textual para o CPA (sem emoji — compatível com Windows cp1252)."""
    if pd.isna(cpa) or cpa is None:
        return 'SEM DADOS'
    if cpa <= CPA_ALVO:   return '[ALVO]'
    if cpa <= CPA_BOM:    return '[BOM]'
    if cpa <= CPA_LIMITE: return '[LIMITE]'
    if cpa <= CPA_CORTE:  return '[CORTE]'
    return '[PAUSAR]'

def calc_cpa(gasto, vendas):
    return round(gasto / vendas, 2) if vendas and vendas > 0 else None

def calc_roas(faturamento, gasto):
    return round(faturamento / gasto, 2) if gasto and gasto > 0 else None

# ── Formatação ───────────────────────────────────────────────────────────────

def fmt_brl(v, decimals=0):
    if pd.isna(v) or v is None: return '-'
    return f'R${v:,.{decimals}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_cpa(v):
    if pd.isna(v) or v is None: return '-'
    return f'R${v:.0f}'

def fmt_roas(v):
    if pd.isna(v) or v is None: return '-'
    return f'{v:.2f}x'

def fmt_int(v):
    if pd.isna(v) or v is None: return '-'
    return str(int(v))

# ── Validação de dados ────────────────────────────────────────────────────────

def check_data_freshness(max_days_old=1, date_label=None):
    """
    Verifica se os dados de sheets estão atualizados.
    Retorna (ok: bool, label: str, msg: str).
    """
    from datetime import datetime, timedelta
    label = date_label or latest_date_label()
    if not label:
        return False, None, "Nenhum arquivo encontrado em data/sheets/"
    try:
        dt = datetime.strptime(label, '%Y-%m-%d')
        delta = (datetime.today() - dt).days
        if delta > max_days_old:
            return False, label, f"Dados com {delta} dia(s) de atraso (ultimo: {label}). Rode *collect para atualizar."
        return True, label, f"Dados atualizados: {label}"
    except ValueError:
        return True, label, f"Label: {label}"

def safe_groupby(df, by, agg):
    """groupby seguro — retorna DataFrame vazio se df estiver vazio."""
    if df is None or df.empty:
        return pd.DataFrame()
    return df.groupby(by).agg(agg).reset_index()

# ── Report helpers ────────────────────────────────────────────────────────────

def print_section(title, width=80):
    print('\n' + '=' * width)
    print(title)
    print('=' * width)

def print_table(df, cols=None, max_col_width=50):
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', max_col_width)
    show = df[cols] if cols else df
    print(show.to_string(index=False))
