"""
Modelo cuantitativo v1 — Fase de grupos Mundial 2026
======================================================
Variables: Elo puro (sin composite), forma, clasificatorio, lesiones,
           estrella, debutantes, retornos largos.
Sin modificadores de contexto: no altitud, no calor, no viaje, no local.
Método: Bivariate Poisson independiente + Monte Carlo 10k.
Fecha: 2026-06-07
"""

import numpy as np
import pandas as pd
from scipy.stats import poisson

# ============================================================================
# FUERZA BASE — ELO PURO
# ============================================================================

# worldfootballrankings.com 06-Jun-2026 (37 verificados + 11 estimados por OLS)
ELO = {
    "Argentina":1876.12,"Spain":1873.01,"France":1869.43,"England":1827.05,
    "Morocco":1757.29,"Brazil":1765.86,"Portugal":1766.18,"Netherlands":1751.10,
    "Belgium":1742.24,"Croatia":1714.87,"Colombia":1695.99,"Mexico":1687.48,
    "Senegal":1686.41,"Uruguay":1673.07,"USA":1671.23,"Japan":1661.58,
    "Switzerland":1650.06,"Iran":1619.58,"Turkey":1605.73,"Ecuador":1596.48,
    "Austria":1597.40,"South Korea":1591.63,"Australia":1579.34,"Algeria":1571.03,
    "Egypt":1562.37,"Norway":1555.60,"Canada":1559.48,"Ivory Coast":1540.87,
    "Sweden":1509.79,"Czech Republic":1505.74,"Paraguay":1505.35,"Scotland":1503.34,
    "DR Congo":1479.68,"Tunisia":1476.41,"Uzbekistan":1461.21,"Germany":1735.77,
    "New Zealand":1275.60,
    # [ESTIMADO] f(rank) = 1900 - 6.1*rank, R²≈0.91
    "Qatar":1590.18,"South Africa":1534.00,"Bosnia":1582.80,"Ghana":1503.50,
    "Panama":1576.70,"Cape Verde":1473.00,"Saudi Arabia":1552.30,"Iraq":1527.90,
    "Jordan":1485.20,"Haiti":1393.70,"Curacao":1405.90,
}

# Modificadores de forma reciente (cualitativo → escalar)
FORMA = {
    "France":1.04,"Spain":1.02,"Argentina":1.03,"Portugal":1.02,
    "Germany":1.01,"Morocco":1.02,"Netherlands":1.01,"England":1.00,
    "Belgium":1.00,"Croatia":0.97,"Colombia":1.01,"Norway":1.02,
    "Japan":1.02,"Ivory Coast":1.01,"Sweden":1.01,"Turkey":1.01,
    "Brazil":0.96,"Mexico":1.01,"USA":1.01,"Senegal":1.00,
    "Switzerland":1.01,"Bosnia":1.01,"Uruguay":1.00,"Ecuador":1.00,
    "Austria":1.00,"South Korea":1.00,"Australia":1.00,"Algeria":1.00,
    "Czech Republic":1.00,"Paraguay":1.00,"Scotland":0.98,"Iran":0.98,
    "Egypt":0.99,"Canada":1.00,"Ghana":0.99,"Tunisia":0.99,
    "Saudi Arabia":0.98,"Qatar":0.99,"South Africa":1.00,"Panama":1.00,
    "Iraq":1.00,"Jordan":1.00,"Haiti":0.99,"Curacao":0.98,
    "DR Congo":1.00,"Uzbekistan":1.00,"Cape Verde":1.00,"New Zealand":0.98,
}

# Diferencial clasificatorio (goles/partido estimado)
QUAL_DIFF = {
    "Spain":2.5,"France":2.5,"Portugal":2.5,"England":2.2,"Germany":2.0,
    "Netherlands":1.8,"Norway":2.2,"Belgium":1.5,"Switzerland":1.6,
    "Turkey":1.7,"Austria":1.6,"Croatia":1.3,"Czech Republic":1.1,
    "Sweden":1.2,"Scotland":0.9,"Bosnia":0.7,"Morocco":2.1,"Ivory Coast":1.3,
    "Senegal":1.5,"Algeria":1.0,"Egypt":1.0,"DR Congo":0.8,"Ghana":0.7,
    "South Africa":0.8,"Cape Verde":0.9,"Tunisia":0.7,"Japan":2.0,
    "South Korea":1.5,"Iran":1.2,"Australia":1.0,"Saudi Arabia":0.6,
    "Uzbekistan":1.1,"Iraq":0.7,"Jordan":0.5,"Qatar":0.3,"Argentina":1.0,
    "Brazil":0.4,"Colombia":0.6,"Uruguay":0.4,"Ecuador":0.5,"Paraguay":0.1,
    "USA":1.2,"Mexico":1.5,"Canada":1.1,"Panama":0.4,"Haiti":0.3,
    "Curacao":0.5,"New Zealand":0.8,
}

# Lesiones confirmadas
LESIONES_MOD = {
    "Brazil":0.96,"Netherlands":0.97,"Germany":0.99,"Scotland":0.99,
}

# Debutantes y retornos
DEBUTANTS    = {"Curacao","Jordan","Uzbekistan","Cape Verde"}
LONG_ABSENCE = {"Haiti","Iraq","DR Congo"}

# Dependencia de estrella (solo registrada, no modifica xG)
STAR_DEPENDENCY = {
    "Norway":  {"player":"Haaland","factor":0.65},
    "Egypt":   {"player":"Salah",  "factor":0.60},
    "Portugal":{"player":"Ronaldo","factor":0.45},
    "Senegal": {"player":"Mané",   "factor":0.40},
    "Argentina":{"player":"Messi", "factor":0.55},
    "Colombia":{"player":"L.Díaz", "factor":0.45},
}

def effective_strength(team):
    return ELO[team] * LESIONES_MOD.get(team, 1.0)

# ============================================================================
# MODIFICADORES BÁSICOS
# ============================================================================

BASE_LAMBDA = 1.35

def mod_debut(team, match_day):
    if team in DEBUTANTS:
        return {1:0.92, 2:0.96, 3:1.00}.get(match_day, 1.0)
    if team in LONG_ABSENCE:
        return {1:0.96, 2:0.98, 3:1.00}.get(match_day, 1.0)
    return 1.0

def mod_qual(team):
    qdiff = QUAL_DIFF.get(team, 0.5)
    return 1.0 + 0.02*(qdiff - 0.8)

def elo_ratio(ea, eb):
    p = 1/(1+10**(-(ea-eb)/400))
    return (p/(1-p))**0.5

def calc_xg(local, visit, j_l, j_v):
    ea = effective_strength(local)
    eb = effective_strength(visit)
    rl = elo_ratio(ea, eb); rv = elo_ratio(eb, ea)
    xg_l = BASE_LAMBDA*2*rl/(rl+rv)
    xg_v = BASE_LAMBDA*2*rv/(rl+rv)
    xg_l *= FORMA.get(local, 1.0) * mod_debut(local, j_l) * mod_qual(local)
    xg_v *= FORMA.get(visit, 1.0) * mod_debut(visit, j_v) * mod_qual(visit)
    return round(xg_l, 3), round(xg_v, 3)

def poisson_probs(xg_l, xg_v, max_g=8):
    p1=px=p2=0.0; best=(0,0); bp=0.0
    for gl in range(max_g+1):
        for gv in range(max_g+1):
            p = poisson.pmf(gl, xg_l)*poisson.pmf(gv, xg_v)
            if   gl > gv: p1 += p
            elif gl == gv: px += p
            else:           p2 += p
            if p > bp: bp=p; best=(gl,gv)
    return p1, px, p2, best

def confidence_level(local, visit, p1, px, p2):
    gap = abs(effective_strength(local) - effective_strength(visit))
    p_fav = max(p1, p2)
    base = "ALTO" if gap > 200 and p_fav > 0.65 else ("MEDIO" if gap > 100 or p_fav > 0.55 else "BAJO")
    star = max(
        STAR_DEPENDENCY.get(local, {}).get("factor", 0),
        STAR_DEPENDENCY.get(visit,  {}).get("factor", 0),
    )
    if star >= 0.55 and base == "ALTO":   base = "MEDIO*"
    elif star >= 0.40 and base == "MEDIO": base = "BAJO*"
    return base

# ============================================================================
# FIXTURE
# ============================================================================

FIXTURE = [
    (1,"11-Jun","Mexico City","Mexico","South Africa","A",13,1,1),
    (2,"11-Jun","Guadalajara","South Korea","Czech Republic","A",20,1,1),
    (3,"12-Jun","Toronto","Canada","Bosnia","B",15,1,1),
    (4,"12-Jun","Los Angeles","USA","Paraguay","D",18,1,1),
    (5,"13-Jun","Boston","Haiti","Scotland","C",21,1,1),
    (6,"13-Jun","Vancouver","Australia","Turkey","D",21,1,1),
    (7,"13-Jun","New York","Brazil","Morocco","C",18,1,1),
    (8,"13-Jun","San Francisco","Qatar","Switzerland","B",12,1,1),
    (9,"14-Jun","Philadelphia","Ivory Coast","Ecuador","E",19,1,1),
    (10,"14-Jun","Houston","Germany","Curacao","E",12,1,1),
    (11,"14-Jun","Dallas","Netherlands","Japan","F",15,1,1),
    (12,"14-Jun","Monterrey","Sweden","Tunisia","F",20,1,1),
    (13,"15-Jun","Miami","Saudi Arabia","Uruguay","H",18,1,1),
    (14,"15-Jun","Atlanta","Spain","Cape Verde","H",12,1,1),
    (15,"15-Jun","Los Angeles","Iran","New Zealand","G",18,1,1),
    (16,"15-Jun","Seattle","Belgium","Egypt","G",12,1,1),
    (17,"16-Jun","New York","France","Senegal","I",15,1,1),
    (18,"16-Jun","Boston","Iraq","Norway","I",18,1,1),
    (19,"16-Jun","Kansas City","Argentina","Algeria","J",20,1,1),
    (20,"16-Jun","San Francisco","Austria","Jordan","J",21,1,1),
    (21,"17-Jun","Toronto","Ghana","Panama","L",19,1,1),
    (22,"17-Jun","Dallas","England","Croatia","L",15,1,1),
    (23,"17-Jun","Houston","Portugal","DR Congo","K",12,1,1),
    (24,"17-Jun","Mexico City","Uzbekistan","Colombia","K",20,1,1),
    (25,"18-Jun","Atlanta","Czech Republic","South Africa","A",12,2,2),
    (26,"18-Jun","Los Angeles","Switzerland","Bosnia","B",12,2,2),
    (27,"18-Jun","Vancouver","Canada","Qatar","B",18,2,2),
    (28,"18-Jun","Guadalajara","Mexico","South Korea","A",19,2,2),
    (29,"19-Jun","Philadelphia","Brazil","Haiti","C",21,2,2),
    (30,"19-Jun","Boston","Scotland","Morocco","C",18,2,2),
    (31,"19-Jun","San Francisco","Turkey","Paraguay","D",20,2,2),
    (32,"19-Jun","Seattle","USA","Australia","D",12,2,2),
    (33,"20-Jun","Toronto","Germany","Ivory Coast","E",16,2,2),
    (34,"20-Jun","Kansas City","Ecuador","Curacao","E",19,2,2),
    (35,"20-Jun","Houston","Netherlands","Sweden","F",12,2,2),
    (36,"20-Jun","Monterrey","Tunisia","Japan","F",22,2,2),
    (37,"21-Jun","Miami","Uruguay","Cape Verde","H",18,2,2),
    (38,"21-Jun","Atlanta","Spain","Saudi Arabia","H",12,2,2),
    (39,"21-Jun","Los Angeles","Belgium","Iran","G",12,2,2),
    (40,"21-Jun","Vancouver","New Zealand","Egypt","G",18,2,2),
    (41,"22-Jun","New York","Norway","Senegal","I",20,2,2),
    (42,"22-Jun","Philadelphia","France","Iraq","I",17,2,2),
    (43,"22-Jun","Dallas","Argentina","Austria","J",20,2,2),
    (44,"22-Jun","San Francisco","Jordan","Algeria","J",20,2,2),
    (45,"23-Jun","Boston","England","Ghana","L",16,2,2),
    (46,"23-Jun","Toronto","Panama","Croatia","L",19,2,2),
    (47,"23-Jun","Houston","Portugal","Uzbekistan","K",12,2,2),
    (48,"23-Jun","Guadalajara","Colombia","DR Congo","K",20,2,2),
    (49,"24-Jun","Miami","Scotland","Brazil","C",18,3,3),
    (50,"24-Jun","Atlanta","Morocco","Haiti","C",18,3,3),
    (51,"24-Jun","Vancouver","Switzerland","Canada","B",12,3,3),
    (52,"24-Jun","Seattle","Bosnia","Qatar","B",12,3,3),
    (53,"24-Jun","Mexico City","Czech Republic","Mexico","A",19,3,3),
    (54,"24-Jun","Monterrey","South Africa","South Korea","A",19,3,3),
    (55,"25-Jun","Philadelphia","Curacao","Ivory Coast","E",16,3,3),
    (56,"25-Jun","New York","Ecuador","Germany","E",16,3,3),
    (57,"25-Jun","Dallas","Japan","Sweden","F",18,3,3),
    (58,"25-Jun","Kansas City","Tunisia","Netherlands","F",18,3,3),
    (59,"25-Jun","Los Angeles","Turkey","USA","D",19,3,3),
    (60,"25-Jun","San Francisco","Paraguay","Australia","D",19,3,3),
    (61,"26-Jun","Boston","Norway","France","I",15,3,3),
    (62,"26-Jun","Toronto","Senegal","Iraq","I",15,3,3),
    (63,"26-Jun","Seattle","Egypt","Iran","G",20,3,3),
    (64,"26-Jun","Vancouver","New Zealand","Belgium","G",20,3,3),
    (65,"26-Jun","Houston","Cape Verde","Saudi Arabia","H",19,3,3),
    (66,"26-Jun","Guadalajara","Uruguay","Spain","H",18,3,3),
    (67,"27-Jun","New York","Panama","England","L",17,3,3),
    (68,"27-Jun","Philadelphia","Croatia","Ghana","L",17,3,3),
    (69,"27-Jun","Kansas City","Algeria","Austria","J",21,3,3),
    (70,"27-Jun","Dallas","Jordan","Argentina","J",21,3,3),
    (71,"27-Jun","Miami","Colombia","Portugal","K",19,3,3),
    (72,"27-Jun","Atlanta","DR Congo","Uzbekistan","K",19,3,3),
]

# ============================================================================
# EJECUTAR PARTIDOS
# ============================================================================

results = []
for row in FIXTURE:
    mid,fecha,venue,local,visit,grupo,hora,j_l,j_v = row
    xg_l, xg_v = calc_xg(local, visit, j_l, j_v)
    p1,px,p2,sc = poisson_probs(xg_l, xg_v)
    conf = confidence_level(local, visit, p1, px, p2)
    ea, eb = effective_strength(local), effective_strength(visit)
    facs = []
    if abs(ea-eb) > 150:
        fav = local if ea > eb else visit
        facs.append(f"Elo gap {abs(ea-eb):.0f}→{fav}")
    if local in DEBUTANTS:  facs.append(f"Debut {local}")
    if visit in DEBUTANTS:  facs.append(f"Debut {visit}")
    for t in [local, visit]:
        dep = STAR_DEPENDENCY.get(t)
        if dep: facs.append(f"Dep.★ {dep['player']}")
    if not facs: facs.append("Equilibrado")
    results.append({
        "P":mid,"Fecha":fecha,"Sede":venue,"H":hora,
        "Local":local,"Visit":visit,"G":grupo,
        "xG_L":xg_l,"xG_V":xg_v,
        "Marcador":f"{sc[0]}-{sc[1]}",
        "P(1)":round(p1,3),"P(X)":round(px,3),"P(2)":round(p2,3),
        "Conf":conf,"Factores":" | ".join(facs[:4]),
    })

df = pd.DataFrame(results)

# ============================================================================
# MONTE CARLO
# ============================================================================

def simulate_group(g_matches, n=10_000):
    teams = list({m["Local"] for m in g_matches}|{m["Visit"] for m in g_matches})
    pts={t:0.0 for t in teams}; gf={t:0.0 for t in teams}; gc={t:0.0 for t in teams}
    for _ in range(n):
        p={t:0 for t in teams}; f={t:0 for t in teams}; c={t:0 for t in teams}
        for m in g_matches:
            l,v = m["Local"],m["Visit"]
            gl=np.random.poisson(m["xG_L"]); gv=np.random.poisson(m["xG_V"])
            f[l]+=gl; c[l]+=gv; f[v]+=gv; c[v]+=gl
            if gl>gv: p[l]+=3
            elif gl==gv: p[l]+=1; p[v]+=1
            else: p[v]+=3
        for t in teams:
            pts[t]+=p[t]; gf[t]+=f[t]; gc[t]+=c[t]
    rows=[{"Equipo":t,"Pts_esp":round(pts[t]/n,2),
           "GF_esp":round(gf[t]/n,2),"GC_esp":round(gc[t]/n,2)} for t in teams]
    return pd.DataFrame(rows).sort_values("Pts_esp",ascending=False).reset_index(drop=True)

grupos={}
for r in results: grupos.setdefault(r["G"],[]).append(r)

print("="*65)
print("PRONÓSTICO MUNDIAL 2026 v1 — Elo + forma + debut + lesiones")
print("="*65)
group_dfs=[]
for g in sorted(grupos):
    sim=simulate_group(grupos[g])
    sim["Grupo"]=g; sim["Pos"]=range(1,len(sim)+1)
    group_dfs.append(sim)
    print(f"\nGRUPO {g}")
    print(sim[["Pos","Equipo","Pts_esp","GF_esp","GC_esp"]].to_string(index=False))

group_df=pd.concat(group_dfs,ignore_index=True)
terceros=group_df[group_df["Pos"]==3].sort_values("Pts_esp",ascending=False)
print("\n--- MEJORES TERCEROS ---")
print(terceros[["Grupo","Equipo","Pts_esp","GF_esp"]].to_string(index=False))

df.to_csv("pronosticos_fase_grupos.csv",index=False)
group_df.to_csv("clasificacion_grupos.csv",index=False)
terceros.to_csv("mejores_terceros.csv",index=False)
print("\n✓ CSV guardados en v1/")
