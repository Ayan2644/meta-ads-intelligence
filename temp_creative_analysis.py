import sys
import io
import csv
import os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "C:/Users/user/Desktop/AIOS META/meta-ads-intelligence/data/sheets"
ADS_MDA   = os.path.join(BASE, "2026-03-18_ads_mda.csv")
ADS_TEUS  = os.path.join(BASE, "2026-03-18_ads_teus.csv")
VND_MDA   = os.path.join(BASE, "2026-03-18_vendas_mda.csv")
VND_TEUS  = os.path.join(BASE, "2026-03-18_vendas_teus.csv")

PERIODO   = "2026-03"
TICKET    = 184.23
CPA_ALVO  = 92.12
CPA_BOM   = 102.35
CPA_LIMITE= 122.82
CPA_CORTE = 153.53

# ── helpers ────────────────────────────────────────────────────────────────────
def parse_brl(val):
    if val is None: return 0.0
    v = str(val).strip().replace("R$","").replace(" ","")
    if v == "" or v == "-": return 0.0
    v = v.replace(".","").replace(",",".")
    try: return float(v)
    except: return 0.0

def parse_int(val):
    if val is None: return 0
    v = str(val).strip().replace(".","").replace(",","")
    if v == "" or v == "-": return 0
    try: return int(float(v))
    except: return 0

def classify_fase(name):
    n = name.upper()
    if any(x in n for x in ["RMKT","REMARKETING"]): return "RMKT"
    if any(x in n for x in ["[F3]","F3 ","F3]","ESCALA"]): return "F3"
    if any(x in n for x in ["[F2]","F2 ","F2]","CBO"]): return "F2"
    if any(x in n for x in ["[F1]","F1 ","F1]","ABO"]): return "F1"
    return "F2"

def classify_vsl(name):
    n = name.upper()
    if "VSL-C" in n or "VSL C" in n: return "VSL-C"
    if "VSL-A" in n or "VSL A" in n: return "VSL-A"
    if "VSL-B" in n or "VSL B" in n: return "VSL-B"
    return "—"

def classify_trafego(name):
    n = name.upper()
    if any(x in n for x in ["QUENTE","RMKT","REMARKETING"]): return "Q"
    return "F"

def cpa_status(cpa):
    if cpa <= 0: return "—"
    if cpa <= CPA_ALVO:   return "ALVO"
    if cpa <= CPA_BOM:    return "BOM"
    if cpa <= CPA_LIMITE: return "LIMITE"
    if cpa <= CPA_CORTE:  return "CORTE"
    return "PAUSAR"

# ── read ads file ──────────────────────────────────────────────────────────────
def read_ads(filepath, prod_label):
    """Returns dict: nome_ads -> {gasto, compras, impressoes, cliques, vpg}
       Also returns list of 'Ad Name' values (raw Meta column) for UTM matching."""
    agg = defaultdict(lambda: {"gasto":0.0,"compras":0,"impressoes":0,"cliques":0,"vpg":0})
    ad_names = []  # raw Meta 'Ad Name' col values
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        # Raw Meta API columns (cols 0-8)
        try:
            idx_ad_name_raw = headers.index("Ad Name")
        except ValueError:
            idx_ad_name_raw = 1
        # Aggregated block
        try:
            idx_nome = headers.index("NOME ADS")
        except ValueError:
            idx_nome = 10
        idx_data      = idx_nome + 1
        idx_gasto     = idx_nome + 2
        idx_compras   = idx_nome + 3
        idx_impressoes= idx_nome + 4
        idx_cliques   = idx_nome + 5
        idx_vpg       = idx_nome + 6

        for row in reader:
            if len(row) <= idx_vpg:
                continue
            # Collect raw Ad Name
            if len(row) > idx_ad_name_raw:
                raw_an = row[idx_ad_name_raw].strip()
                if raw_an:
                    ad_names.append(raw_an)

            nome = row[idx_nome].strip()
            data = row[idx_data].strip()
            if not nome or not data:
                continue
            if not data.startswith(PERIODO):
                continue
            gasto     = parse_brl(row[idx_gasto])
            compras   = parse_int(row[idx_compras])
            impressoes= parse_int(row[idx_impressoes])
            cliques   = parse_int(row[idx_cliques])
            vpg       = parse_int(row[idx_vpg])
            r = agg[nome]
            r["gasto"]      += gasto
            r["compras"]    += compras
            r["impressoes"] += impressoes
            r["cliques"]    += cliques
            r["vpg"]        += vpg
    return agg, list(set(ad_names))

# ── read vendas file ──────────────────────────────────────────────────────────
def read_vendas(filepath, produto_keyword):
    """Returns dict: utm_content -> count, plus raw rows for sampling."""
    counts = defaultdict(int)
    utm_samples = []
    utm_campaign_counts = defaultdict(int)
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_raw = row.get("DATA","").strip()
            status   = row.get("STATUS","").strip().upper()
            produto  = row.get("PRODUTO","").strip()
            utm      = row.get("UTM_CONTENT","").strip()
            utm_camp = row.get("UTM_CAMPAIGN","").strip()

            # parse date DD/MM/YYYY
            parts = data_raw.split("/")
            if len(parts) == 3:
                date_iso = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            else:
                date_iso = data_raw

            if not date_iso.startswith(PERIODO):
                continue
            if status not in ("APPROVED","COMPLETE","APROVADO","COMPLETO"):
                continue

            # collect UTM_CONTENT samples (first 10 non-empty)
            if utm and len(utm_samples) < 10:
                utm_samples.append((utm, utm_camp))

            # VSL classification from UTM_CAMPAIGN
            if utm_camp:
                utm_campaign_counts[utm_camp] += 1

            if produto_keyword.lower() not in produto.lower():
                continue
            counts[utm] += 1
    return counts, utm_samples, utm_campaign_counts

# ── main ───────────────────────────────────────────────────────────────────────
print("=" * 90)
print("  ANÁLISE DE CRIATIVOS — MARÇO 2026")
print("=" * 90)

# Read data
ads_mda,  ad_names_mda  = read_ads(ADS_MDA,  "MDA")
ads_teus, ad_names_teus = read_ads(ADS_TEUS, "TEUS")
vnd_mda,  utm_samples_mda,  utm_camp_mda  = read_vendas(VND_MDA,  "Mestres do Algoritmo")
vnd_teus, utm_samples_teus, utm_camp_teus = read_vendas(VND_TEUS, "Lucrando com Vídeos Curtos")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — UTM_CONTENT SAMPLE (vendas_mda)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("  SEÇÃO 1 — UTM_CONTENT SAMPLE — vendas_mda.csv (março 2026, até 10 valores)")
print("=" * 90)
print(f"\n  {'UTM_CONTENT':<55}  {'UTM_CAMPAIGN'}")
print("  " + "-" * 85)
for utm_c, utm_camp in utm_samples_mda:
    print(f"  {utm_c:<55}  {utm_camp}")
if not utm_samples_mda:
    print("  (nenhum registro encontrado em março)")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Ad Name column (raw Meta) samples — ads_mda.csv
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("  SEÇÃO 2 — 'Ad Name' (coluna Meta bruta) — ads_mda.csv (10 amostras únicas)")
print("=" * 90)
print()
for an in list(ad_names_mda)[:10]:
    print(f"  {an}")
if not ad_names_mda:
    print("  (nenhum valor encontrado)")

print("\n  — ads_teus.csv (10 amostras únicas) —")
for an in list(ad_names_teus)[:10]:
    print(f"  {an}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — VSL classification from UTM_CAMPAIGN (vendas_mda março)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("  SEÇÃO 3 — VSL por UTM_CAMPAIGN — vendas_mda março 2026 (todas as vendas aprovadas)")
print("=" * 90)

vsl_a = vsl_b = vsl_c = vsl_other = 0
vsl_a_camps = []
vsl_b_camps = []
vsl_c_camps = []

for camp, cnt in utm_camp_mda.items():
    cu = camp.upper()
    if "VSL-C" in cu or "VSL C" in cu or "VSLC" in cu:
        vsl_c += cnt
        if camp not in vsl_c_camps: vsl_c_camps.append(camp)
    elif "VSL-A" in cu or "VSL A" in cu or "VSLA" in cu:
        vsl_a += cnt
        if camp not in vsl_a_camps: vsl_a_camps.append(camp)
    elif "VSL-B" in cu or "VSL B" in cu or "VSLB" in cu:
        vsl_b += cnt
        if camp not in vsl_b_camps: vsl_b_camps.append(camp)
    else:
        vsl_other += cnt

total_vsl = vsl_a + vsl_b + vsl_c + vsl_other
print(f"\n  VSL-A : {vsl_a:>4} vendas")
for c in vsl_a_camps[:3]: print(f"          ↳ {c}")
print(f"  VSL-B : {vsl_b:>4} vendas")
for c in vsl_b_camps[:3]: print(f"          ↳ {c}")
print(f"  VSL-C : {vsl_c:>4} vendas")
for c in vsl_c_camps[:3]: print(f"          ↳ {c}")
print(f"  Outros: {vsl_other:>4} vendas")
print(f"  TOTAL : {total_vsl:>4} vendas (março 2026, aprovadas)")

print("\n  Top UTM_CAMPAIGN values (all, sorted by count):")
print(f"  {'CAMPAIGN':<60} {'VENDAS':>6}")
print("  " + "-" * 70)
for camp, cnt in sorted(utm_camp_mda.items(), key=lambda x: -x[1])[:20]:
    print(f"  {camp:<60} {cnt:>6}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Build creative records
# ══════════════════════════════════════════════════════════════════════════════
creatives = []

def build_records(ads_dict, vnd_dict, prod_label):
    for nome, d in ads_dict.items():
        if d["gasto"] == 0 and d["compras"] == 0:
            continue
        gasto      = d["gasto"]
        compras    = d["compras"]
        impressoes = d["impressoes"]
        cliques    = d["cliques"]
        vpg        = d["vpg"]

        cpa_pixel  = gasto / compras if compras > 0 else float("inf")
        ctr        = (cliques / impressoes * 100) if impressoes > 0 else 0.0

        vendas_plat = vnd_dict.get(nome, 0)

        # Determine if RMKT via campaign name
        n = nome.upper()
        is_rmkt = any(x in n for x in ["RMKT","REMARKETING"])

        fase     = classify_fase(nome)
        vsl      = classify_vsl(nome)
        trafego  = classify_trafego(nome)
        status   = cpa_status(cpa_pixel)

        creatives.append({
            "nome":      nome,
            "prod":      prod_label,
            "fase":      fase,
            "vsl":       vsl,
            "trafego":   trafego,
            "gasto":     gasto,
            "compras":   compras,
            "cpa_pixel": cpa_pixel,
            "vendas":    vendas_plat,
            "impressoes":impressoes,
            "cliques":   cliques,
            "ctr":       ctr,
            "vpg":       vpg,
            "status":    status,
            "is_rmkt":   is_rmkt,
        })

build_records(ads_mda,  vnd_mda,  "MDA")
build_records(ads_teus, vnd_teus, "TEUS")

# Sort by CPA ascending (inf goes to end)
creatives.sort(key=lambda x: (x["cpa_pixel"] if x["cpa_pixel"] != float("inf") else 9999999))

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FRIO vs RMKT split
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 90)
print("  SEÇÃO 4 — CRIATIVOS FRIO vs RMKT (por UTM_CAMPAIGN / nome do ad)")
print("=" * 90)

frio_creatives = [c for c in creatives if not c["is_rmkt"]]
rmkt_creatives = [c for c in creatives if c["is_rmkt"]]

frio_gasto   = sum(c["gasto"]   for c in frio_creatives)
frio_compras = sum(c["compras"] for c in frio_creatives)
rmkt_gasto   = sum(c["gasto"]   for c in rmkt_creatives)
rmkt_compras = sum(c["compras"] for c in rmkt_creatives)

print(f"\n  FRIO : {len(frio_creatives):>3} criativos | Gasto R${frio_gasto:>8.2f} | Compras {frio_compras:>4} | CPA R${frio_gasto/frio_compras:.2f}" if frio_compras else f"\n  FRIO : {len(frio_creatives):>3} criativos | Gasto R${frio_gasto:>8.2f} | Compras {frio_compras:>4}")
print(f"  RMKT : {len(rmkt_creatives):>3} criativos | Gasto R${rmkt_gasto:>8.2f} | Compras {rmkt_compras:>4} | CPA R${rmkt_gasto/rmkt_compras:.2f}" if rmkt_compras else f"  RMKT : {len(rmkt_creatives):>3} criativos | Gasto R${rmkt_gasto:>8.2f} | Compras {rmkt_compras:>4}")

if rmkt_creatives:
    print(f"\n  Criativos RMKT identificados:")
    for c in rmkt_creatives:
        print(f"    • {c['nome'][:70]}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — FULL RANKED LIST (all 68+)
# ══════════════════════════════════════════════════════════════════════════════
total_gasto   = sum(c["gasto"]   for c in creatives)
total_compras = sum(c["compras"] for c in creatives)
total_vendas  = sum(c["vendas"]  for c in creatives)
total_cpa     = total_gasto / total_compras if total_compras > 0 else 0

print("\n" + "=" * 90)
print(f"  SEÇÃO 5 — RANKING COMPLETO DE TODOS OS {len(creatives)} CRIATIVOS (ordenado por CPA)")
print("=" * 90)
print()
print(f"{'#':>3}  {'NOME (45 chars)':<47} {'PROD':<5} {'FASE':<5} {'GASTO':>9} {'COMP':>5} {'CPA_PX':>9} {'CTR':>6}  {'STATUS':<7}")
print("-" * 105)

for i, c in enumerate(creatives, 1):
    nome_short = c["nome"][:45]
    if c["cpa_pixel"] == float("inf"):
        cpa_str = "   sem vnd"
    else:
        cpa_str = f"R${c['cpa_pixel']:>7.2f}"
    rmkt_tag = " [RMKT]" if c["is_rmkt"] else ""
    print(f"{i:>3}  {nome_short:<47} {c['prod']:<5} {c['fase']:<5} R${c['gasto']:>7.2f} {c['compras']:>5} {cpa_str:>9} {c['ctr']:>5.2f}%  {c['status']:<7}{rmkt_tag}")

print("-" * 105)
print(f"{'TOTAL':<56} R${total_gasto:>7.2f} {total_compras:>5} R${total_cpa:>7.2f}")

# ── VSL Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("  VSL SUMMARY (por nome do ad)")
print("=" * 90)

vsl_agg = defaultdict(lambda: {"gasto":0.0,"compras":0,"vendas":0,"count":0})
for c in creatives:
    v = vsl_agg[c["vsl"]]
    v["gasto"]   += c["gasto"]
    v["compras"] += c["compras"]
    v["vendas"]  += c["vendas"]
    v["count"]   += 1

print(f"\n{'VSL':<8} {'CRIATs':>6} {'GASTO':>10} {'COMP_PX':>8} {'CPA_PX':>9} {'VND_PLT':>8} {'PART%':>6}")
print("-" * 65)

for vsl_name in ["VSL-A","VSL-B","VSL-C","—"]:
    if vsl_name not in vsl_agg:
        continue
    v = vsl_agg[vsl_name]
    cpa = v["gasto"] / v["compras"] if v["compras"] > 0 else 0
    part = v["gasto"] / total_gasto * 100 if total_gasto > 0 else 0
    print(f"{vsl_name:<8} {v['count']:>6} R${v['gasto']:>7.2f} {v['compras']:>8} "
          f"R${cpa:>6.2f} {v['vendas']:>8} {part:>5.1f}%")

# ── F vs Q Summary ────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("  TRÁFEGO FRIO (F) vs QUENTE (Q)")
print("=" * 90)

trf_agg = defaultdict(lambda: {"gasto":0.0,"compras":0,"vendas":0,"count":0})
for c in creatives:
    v = trf_agg[c["trafego"]]
    v["gasto"]   += c["gasto"]
    v["compras"] += c["compras"]
    v["vendas"]  += c["vendas"]
    v["count"]   += 1

print(f"\n{'TRÁFEGO':<10} {'CRIATs':>6} {'GASTO':>10} {'COMP_PX':>8} {'CPA_PX':>9} {'VND_PLT':>8} {'PART%':>6}")
print("-" * 65)

for trf in ["F","Q"]:
    if trf not in trf_agg:
        continue
    v = trf_agg[trf]
    cpa = v["gasto"] / v["compras"] if v["compras"] > 0 else 0
    part = v["gasto"] / total_gasto * 100 if total_gasto > 0 else 0
    label = "Frio (F)" if trf == "F" else "Quente (Q)"
    print(f"{label:<10} {v['count']:>6} R${v['gasto']:>7.2f} {v['compras']:>8} "
          f"R${cpa:>6.2f} {v['vendas']:>8} {part:>5.1f}%")

# ── Status distribution ───────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("  DISTRIBUIÇÃO POR STATUS")
print("=" * 90)

status_agg = defaultdict(lambda: {"count":0,"gasto":0.0,"compras":0})
for c in creatives:
    s = status_agg[c["status"]]
    s["count"]   += 1
    s["gasto"]   += c["gasto"]
    s["compras"] += c["compras"]

print(f"\n{'STATUS':<8} {'CRIATs':>6} {'GASTO':>10} {'COMP_PX':>8}")
print("-" * 40)
for st in ["ALVO","BOM","LIMITE","CORTE","PAUSAR","—"]:
    if st not in status_agg:
        continue
    s = status_agg[st]
    print(f"{st:<8} {s['count']:>6} R${s['gasto']:>7.2f} {s['compras']:>8}")

# ── Per-product totals ────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("  RESUMO POR PRODUTO")
print("=" * 90)

prod_agg = defaultdict(lambda: {"gasto":0.0,"compras":0,"vendas":0})
for c in creatives:
    p = prod_agg[c["prod"]]
    p["gasto"]   += c["gasto"]
    p["compras"] += c["compras"]
    p["vendas"]  += c["vendas"]

print(f"\n{'PROD':<6} {'GASTO':>10} {'COMP_PX':>8} {'CPA_PX':>9} {'VND_PLT':>8}")
print("-" * 50)
for prod in ["MDA","TEUS"]:
    if prod not in prod_agg:
        continue
    p = prod_agg[prod]
    cpa = p["gasto"] / p["compras"] if p["compras"] > 0 else 0
    print(f"{prod:<6} R${p['gasto']:>7.2f} {p['compras']:>8} R${cpa:>6.2f} {p['vendas']:>8}")

print("\n" + "=" * 90)
print(f"  Referências: ALVO ≤ R${CPA_ALVO} | BOM ≤ R${CPA_BOM} | LIMITE ≤ R${CPA_LIMITE} | CORTE ≤ R${CPA_CORTE}")
print("=" * 90)
