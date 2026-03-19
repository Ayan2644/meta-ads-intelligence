import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aios_utils import *

# br_num
assert br_num('R$ 1.234,56') == 1234.56, f"got {br_num('R$ 1.234,56')}"
assert br_num('1234,56') == 1234.56
assert br_num('0') == 0.0
assert br_num(None) == 0.0
print('[OK] br_num')

# parse_impressoes
assert parse_impressoes('45.994') == 45994
assert parse_impressoes('1.234.567') == 1234567
print('[OK] parse_impressoes')

# load_diario
d = load_diario('mda')
gasto_mda = d['GASTO'].sum()
print(f'[OK] load_diario MDA: {len(d)} dias | Gasto=R${gasto_mda:,.2f}')
assert abs(gasto_mda - 36741.52) < 1, f"Expected ~36741.52, got {gasto_mda}"

# load_vendas
v = load_vendas('mda')
assert len(v) == 326, f"Expected 326 MDA sales, got {len(v)}"
print(f'[OK] load_vendas MDA: {len(v)} vendas | Fat=R${v["VALOR_PAGO"].sum():,.2f}')

# load_ads
a = load_ads('mda')
assert len(a) > 0
gasto_ads = a['GASTO'].sum()
print(f'[OK] load_ads MDA: {len(a)} criativos | Gasto=R${gasto_ads:,.2f}')

# utm_to_ad_num
assert utm_to_ad_num('video-ad17') == 17
assert utm_to_ad_num('video-ad017') == 17
assert utm_to_ad_num(None) is None
print('[OK] utm_to_ad_num')

# nome_to_ad_num
assert nome_to_ad_num('AD17 [MDA] VID VENDA') == 17
assert nome_to_ad_num('AD017 [LVCT] TEST') == 17
print('[OK] nome_to_ad_num')

# cpa_status
assert cpa_status(90) == '[ALVO]'
assert cpa_status(95) == '[BOM]'
assert cpa_status(110) == '[LIMITE]'
assert cpa_status(140) == '[CORTE]'
assert cpa_status(200) == '[PAUSAR]'
assert cpa_status(None) == 'SEM DADOS'
print('[OK] cpa_status')

# extract_vsl
assert extract_vsl('13-12-25-MDA-F-AUTO-VSL-A-197') == 'VSL-A'
assert extract_vsl('13-12-25-MDA-F-AUTO-VSL-C-197') == 'VSL-C'
assert extract_vsl(None) == 'N/A'
print('[OK] extract_vsl')

print()
print('=== TODOS OS TESTES PASSARAM ===')
