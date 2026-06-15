"""
Comparador de versiones v1 / v2 / v3.
Ejecutar desde: mundial2026/
Requiere que cada vX/ ya tenga sus CSVs generados (python vX/modelo.py).
"""

import pandas as pd
import sys

# ============================================================================
# CARGAR LOS TRES DATASETS
# ============================================================================

def load(version):
    try:
        df = pd.read_csv(f"{version}/pronosticos_fase_grupos.csv")
        df["version"] = version
        return df
    except FileNotFoundError:
        print(f"  ⚠ {version}/pronosticos_fase_grupos.csv no encontrado — ejecuta {version}/modelo.py primero")
        return None

v1 = load("v1")
v2 = load("v2")
v3 = load("v3")

dfs = {k:v for k,v in [("v1",v1),("v2",v2),("v3",v3)] if v is not None}
if not dfs:
    sys.exit("No hay CSVs. Ejecuta los tres modelos primero.")

# ============================================================================
# TABLA COMPARATIVA DE xG POR PARTIDO
# ============================================================================

print("\n" + "="*100)
print("COMPARATIVA xG LOCAL por partido (v1 → v2 → v3)")
print("="*100)
merged = None
for ver, df in dfs.items():
    sub = df[["P","Local","Visit","xG_L","xG_V","Marcador","P(1)","P(X)","P(2)"]].copy()
    sub.columns = ["P","Local","Visit"] + [f"{c}_{ver}" for c in ["xG_L","xG_V","Marcador","P(1)","P(X)","P(2)"]]
    merged = sub if merged is None else merged.merge(sub, on=["P","Local","Visit"])

if merged is not None:
    # Mostrar columnas clave en formato compacto
    cols_show = ["P","Local","Visit"]
    for ver in dfs:
        cols_show += [f"xG_L_{ver}", f"xG_V_{ver}", f"Marcador_{ver}"]
    print(merged[cols_show].to_string(index=False))

# ============================================================================
# TABLA COMPARATIVA DE CLASIFICACIÓN POR GRUPO
# ============================================================================

print("\n" + "="*80)
print("COMPARATIVA CLASIFICACIÓN ESPERADA (Pts_esp) POR GRUPO")
print("="*80)

group_dfs = {}
for ver in dfs:
    try:
        gdf = pd.read_csv(f"{ver}/clasificacion_grupos.csv")
        gdf["version"] = ver
        group_dfs[ver] = gdf
    except FileNotFoundError:
        print(f"  ⚠ {ver}/clasificacion_grupos.csv no encontrado")

if group_dfs:
    # Merge por equipo
    gmerged = None
    for ver, gdf in group_dfs.items():
        sub = gdf[["Grupo","Pos","Equipo","Pts_esp"]].copy()
        sub = sub.rename(columns={"Pts_esp": f"Pts_{ver}", "Pos": f"Pos_{ver}"})
        if gmerged is None:
            gmerged = sub
        else:
            gmerged = gmerged.merge(sub.drop(columns="Grupo"), on="Equipo", how="outer")

    if gmerged is not None:
        gmerged = gmerged.sort_values(["Grupo", f"Pts_{list(group_dfs.keys())[-1]}"],
                                       ascending=[True, False])
        pt_cols = ["Grupo","Equipo"] + [f"Pos_{v}" for v in group_dfs] + [f"Pts_{v}" for v in group_dfs]
        print(gmerged[[c for c in pt_cols if c in gmerged.columns]].to_string(index=False))

# ============================================================================
# PARTIDOS CON MAYOR CAMBIO DE xG ENTRE v1 y v3
# ============================================================================

if "v1" in dfs and "v3" in dfs and merged is not None and "xG_L_v1" in merged.columns:
    print("\n" + "="*80)
    print("TOP 10 PARTIDOS CON MAYOR VARIACIÓN DE xG (v1 → v3)")
    print("="*80)
    merged["delta_xGL"] = (merged["xG_L_v3"] - merged["xG_L_v1"]).abs()
    merged["delta_xGV"] = (merged["xG_V_v3"] - merged["xG_V_v1"]).abs()
    merged["delta_total"] = merged["delta_xGL"] + merged["delta_xGV"]
    top_delta = merged.nlargest(10, "delta_total")[
        ["P","Local","Visit","xG_L_v1","xG_L_v3","xG_V_v1","xG_V_v3",
         "Marcador_v1","Marcador_v3","delta_total"]
    ]
    print(top_delta.to_string(index=False))

    # Cambios de pronóstico (marcador diferente)
    if "Marcador_v1" in merged.columns and "Marcador_v3" in merged.columns:
        cambios = merged[merged["Marcador_v1"] != merged["Marcador_v3"]][
            ["P","Local","Visit","Marcador_v1","Marcador_v3","delta_total"]
        ].sort_values("delta_total", ascending=False)
        print(f"\n{'='*80}")
        print(f"MARCADORES QUE CAMBIARON ENTRE v1 y v3 ({len(cambios)} de 72 partidos)")
        print('='*80)
        print(cambios.to_string(index=False))

print("\n✓ Comparación completa")
