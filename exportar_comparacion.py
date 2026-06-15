"""
Genera comparacion_versiones.html con tablas side-by-side v1/v2/v3/v4.
Ejecutar desde mundial2026/.
"""

import pandas as pd
import html

VERSIONS = ["v1", "v2", "v3", "v4", "v5", "v6"]
GRUPOS = list("ABCDEFGHIJKL")

# ============================================================================
# CARGAR DATOS
# ============================================================================

matches = {}
groups  = {}
for v in VERSIONS:
    try:
        matches[v] = pd.read_csv(f"{v}/pronosticos_fase_grupos.csv")
        groups[v]  = pd.read_csv(f"{v}/clasificacion_grupos.csv")
    except FileNotFoundError:
        print(f"⚠ {v}/ sin CSV — ejecuta {v}/modelo.py primero")

if not matches:
    raise SystemExit("No hay datos. Ejecuta los modelos primero.")

# ============================================================================
# MERGE
# ============================================================================

# Partidos
m = None
for v, df in matches.items():
    sub = df[["P","Local","Visit","G","xG_L","xG_V","Marcador","P(1)","P(X)","P(2)","Conf"]].copy()
    sub.columns = ["P","Local","Visit","G"] + [f"{c}_{v}" for c in ["xG_L","xG_V","Marcador","P(1)","P(X)","P(2)","Conf"]]
    m = sub if m is None else m.merge(sub, on=["P","Local","Visit","G"])

# Calcular cambios de marcador
available_vs = list(matches.keys())
if len(available_vs) >= 2:
    first, last = available_vs[0], available_vs[-1]
    if f"Marcador_{first}" in m.columns and f"Marcador_{last}" in m.columns:
        m["changed"] = m[f"Marcador_{first}"] != m[f"Marcador_{last}"]
    else:
        m["changed"] = False
else:
    m["changed"] = False

# Clasificación
g = None
for v, df in groups.items():
    sub = df[["Grupo","Equipo","Pos","Pts_esp","GF_esp","GC_esp"]].copy()
    sub.columns = ["Grupo","Equipo",f"Pos_{v}",f"Pts_{v}",f"GF_{v}",f"GC_{v}"]
    g = sub if g is None else g.merge(sub, on=["Grupo","Equipo"])

# ============================================================================
# CSS / JS
# ============================================================================

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0f1117; color: #e2e8f0; padding: 24px; }
h1   { font-size: 1.5rem; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
.sub { color: #64748b; font-size: 0.85rem; margin-bottom: 28px; }
h2   { font-size: 1.05rem; font-weight: 600; color: #94a3b8; margin: 32px 0 10px; letter-spacing:.05em; text-transform:uppercase; }
h3   { font-size: 0.9rem; font-weight: 600; color: #7c3aed; margin: 20px 0 6px; }

table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
th    { background: #1e293b; color: #94a3b8; padding: 7px 10px; text-align: left;
        font-weight: 600; border-bottom: 1px solid #334155; white-space: nowrap; }
td    { padding: 6px 10px; border-bottom: 1px solid #1e293b; white-space: nowrap; }
tr:hover td { background: #1e293b; }

.v1  { color: #60a5fa; }   /* azul   */
.v2  { color: #34d399; }   /* verde  */
.v3  { color: #f472b6; }   /* rosa   */
.v4  { color: #fbbf24; }   /* ámbar  */
.v5  { color: #22d3ee; }   /* cian   */
.v6  { color: #a78bfa; }   /* violeta */
.badge-v1 { background:#1e3a5f; color:#60a5fa; border-radius:4px; padding:1px 6px; font-size:.75rem; font-weight:700; }
.badge-v2 { background:#064e3b; color:#34d399; border-radius:4px; padding:1px 6px; font-size:.75rem; font-weight:700; }
.badge-v3 { background:#4c0519; color:#f472b6; border-radius:4px; padding:1px 6px; font-size:.75rem; font-weight:700; }
.badge-v4 { background:#451a03; color:#fbbf24; border-radius:4px; padding:1px 6px; font-size:.75rem; font-weight:700; }
.badge-v5 { background:#083344; color:#22d3ee; border-radius:4px; padding:1px 6px; font-size:.75rem; font-weight:700; }
.badge-v6 { background:#2e1065; color:#a78bfa; border-radius:4px; padding:1px 6px; font-size:.75rem; font-weight:700; }

.changed td { background: #1a1205 !important; }
.changed td.flag { color: #fbbf24; font-weight: 700; }
.pos1  { color: #fbbf24; font-weight: 700; }
.pos2  { color: #94a3b8; }
.pos3  { color: #78716c; }
.pos4  { color: #64748b; }
.hi    { color: #f8fafc; font-weight: 600; }
.muted { color: #475569; }
.delta { color: #fb923c; font-weight: 600; }

.tabs  { display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap; }
.tab   { padding: 5px 14px; border-radius: 6px; border: 1px solid #334155;
         cursor: pointer; font-size: .82rem; color: #94a3b8; background: #1e293b; }
.tab.active { border-color: #7c3aed; color: #c4b5fd; background: #2e1065; }
.panel { display: none; }
.panel.active { display: block; }

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media(max-width:900px){ .grid2 { grid-template-columns: 1fr; } }
"""

JS = """
function showTab(tabId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');
  document.getElementById('panel-' + tabId).classList.add('active');
}
"""

# ============================================================================
# HELPERS
# ============================================================================

def sc(val, cls=""):
    v = html.escape(str(val)) if val is not None else "—"
    return f'<td class="{cls}">{v}</td>'

def marcador_cell(row, v):
    col = f"Marcador_{v}"
    if col not in row.index: return sc("—")
    val = row[col]
    changed = row.get("changed", False)
    cls = "hi" if changed else ""
    return sc(val, cls)

def prob_cell(row, v, which):
    col = f"P({which})_{v}"
    if col not in row.index: return sc("—")
    val = float(row[col])
    pct = f"{val*100:.0f}%"
    cls = "hi" if val >= 0.6 else ("muted" if val < 0.25 else "")
    return f'<td class="{cls}">{pct}</td>'

def xg_cell(row, v, side):
    col = f"xG_{side}_{v}"
    if col not in row.index: return sc("—")
    return sc(f"{float(row[col]):.2f}")

def pts_cell(row, v, pos_v):
    pts_col = f"Pts_{v}"
    pos_col = f"Pos_{v}"
    if pts_col not in row.index: return sc("—")
    pts = float(row[pts_col])
    pos = int(row[pos_col]) if pos_col in row.index else 0
    pos_cls = {1:"pos1",2:"pos2",3:"pos3",4:"pos4"}.get(pos,"")
    return f'<td class="{pos_cls}">{pos}º {pts:.2f}</td>'

# ============================================================================
# SECCIÓN 1: PARTIDOS
# ============================================================================

def build_matches_section():
    rows_html = []
    headers = (
        "<tr>"
        "<th>#</th><th>Local</th><th>Visitante</th><th>G</th>"
    )
    for v in available_vs:
        badge = f'<span class="badge-{v}">{v.upper()}</span>'
        headers += f"<th>{badge} xG L</th><th>{badge} xG V</th><th>{badge} Marcador</th><th>1</th><th>X</th><th>2</th>"
    headers += "<th>Δ</th></tr>"

    for _, row in m.iterrows():
        tr_cls = "changed" if row["changed"] else ""
        flag = "🔄" if row["changed"] else ""
        r = (f'<tr class="{tr_cls}">'
             f'{sc(int(row["P"]))}{sc(row["Local"],"hi")}{sc(row["Visit"])}{sc(row["G"])}')
        for v in available_vs:
            r += xg_cell(row, v, "L")
            r += xg_cell(row, v, "V")
            r += marcador_cell(row, v)
            r += prob_cell(row, v, "1")
            r += prob_cell(row, v, "X")
            r += prob_cell(row, v, "2")
        r += f'<td class="flag">{flag}</td>'
        r += "</tr>"
        rows_html.append(r)

    return f"""
<h2>Partidos — xG y probabilidades por versión</h2>
<p class="sub" style="margin-bottom:12px">🔄 marcador más probable cambió entre {available_vs[0].upper()} y {available_vs[-1].upper()}</p>
<div style="overflow-x:auto">
<table>
<thead>{headers}</thead>
<tbody>{"".join(rows_html)}</tbody>
</table>
</div>
"""

# ============================================================================
# SECCIÓN 2: CLASIFICACIÓN POR GRUPO (tabs)
# ============================================================================

def build_group_section():
    tabs = '<div class="tabs">'
    panels = ""
    for grp in GRUPOS:
        gdata = g[g["Grupo"] == grp] if g is not None else None
        if gdata is None or len(gdata) == 0:
            continue
        gdata = gdata.sort_values(f"Pts_{available_vs[-1]}", ascending=False)
        tabs += f'<button id="tab-{grp}" class="tab" onclick="showTab(\'{grp}\')">{grp}</button>'

        rows_html = []
        for _, row in gdata.iterrows():
            r = f'<tr>{sc(row["Equipo"], "hi")}'
            for v in available_vs:
                r += pts_cell(row, v, f"Pos_{v}")
            r += "</tr>"
            rows_html.append(r)

        header = "<tr><th>Equipo</th>"
        for v in available_vs:
            badge = f'<span class="badge-{v}">{v.upper()}</span>'
            header += f"<th>{badge} Pts</th>"
        header += "</tr>"

        panels += f"""
<div id="panel-{grp}" class="panel">
<table>
<thead>{header}</thead>
<tbody>{"".join(rows_html)}</tbody>
</table>
</div>"""

    tabs += "</div>"
    return f"<h2>Clasificación esperada por grupo</h2>{tabs}{panels}"

# ============================================================================
# SECCIÓN 3: TOP CAMBIOS Y RESUMEN STATS
# ============================================================================

def build_delta_section():
    last = available_vs[-1]   # versión más reciente disponible (v4)
    if len(available_vs) < 2 or "xG_L_v1" not in m.columns or f"xG_L_{last}" not in m.columns:
        return ""
    m2 = m.copy()
    m2["delta"] = ((m2[f"xG_L_{last}"]-m2["xG_L_v1"]).abs() +
                   (m2[f"xG_V_{last}"]-m2["xG_V_v1"]).abs())
    top = m2.nlargest(15, "delta")

    rows_html = []
    for _, row in top.iterrows():
        chg = "🔄" if row["changed"] else ""
        r = (f'<tr><td>{int(row["P"])}</td>'
             f'{sc(row["Local"],"hi")}{sc(row["Visit"])}{sc(row["G"])}'
             f'{xg_cell(row,"v1","L")}{xg_cell(row,"v1","V")}{sc(row.get("Marcador_v1","—"))}'
             f'{xg_cell(row,last,"L")}{xg_cell(row,last,"V")}{sc(row.get(f"Marcador_{last}","—"))}'
             f'<td class="delta">{row["delta"]:.3f}</td>'
             f'<td>{chg}</td></tr>')
        rows_html.append(r)

    changed_count = int(m["changed"].sum())
    stats = f"""
<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:20px">
  <div style="background:#1e293b;border-radius:8px;padding:16px 24px;flex:1;min-width:160px">
    <div style="color:#94a3b8;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em">Marcadores cambiados</div>
    <div style="font-size:2rem;font-weight:700;color:#f472b6">{changed_count}</div>
    <div style="color:#475569;font-size:.8rem">de 72 partidos</div>
  </div>
  <div style="background:#1e293b;border-radius:8px;padding:16px 24px;flex:1;min-width:160px">
    <div style="color:#94a3b8;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em">Sin cambio de marcador</div>
    <div style="font-size:2rem;font-weight:700;color:#34d399">{72-changed_count}</div>
    <div style="color:#475569;font-size:.8rem">consistencia del modelo</div>
  </div>
</div>
"""

    lu = last.upper()
    header = f"<tr><th>#</th><th>Local</th><th>Visit.</th><th>G</th><th>v1 xGL</th><th>v1 xGV</th><th>v1 Marcador</th><th>{lu} xGL</th><th>{lu} xGV</th><th>{lu} Marcador</th><th>Δ xG</th><th></th></tr>"
    return f"""
<h2>Top 15 partidos con mayor variación de xG (v1 → {lu})</h2>
{stats}
<div style="overflow-x:auto">
<table>
<thead>{header}</thead>
<tbody>{"".join(rows_html)}</tbody>
</table>
</div>
"""

# ============================================================================
# SECCIÓN 4: MEJORES TERCEROS
# ============================================================================

def build_terceros_section():
    rows_html = []
    header_parts = "<tr><th>Grupo</th><th>Equipo</th>"
    for v in available_vs:
        badge = f'<span class="badge-{v}">{v.upper()}</span>'
        header_parts += f"<th>{badge} Pts</th><th>{badge} GF</th>"
    header_parts += "</tr>"

    # Merge mejores terceros de cada versión
    t = None
    for v in available_vs:
        try:
            tf = pd.read_csv(f"{v}/mejores_terceros.csv")
            tf = tf[["Grupo","Equipo","Pts_esp","GF_esp"]].rename(
                columns={"Pts_esp":f"Pts_{v}","GF_esp":f"GF_{v}"})
            t = tf if t is None else t.merge(tf, on=["Grupo","Equipo"], how="outer")
        except FileNotFoundError:
            pass

    if t is None:
        return ""

    last_pts = f"Pts_{available_vs[-1]}"
    if last_pts in t.columns:
        t = t.sort_values(last_pts, ascending=False)

    for i, (_, row) in enumerate(t.iterrows()):
        pos_cls = "pos1" if i < 4 else ("pos2" if i < 8 else "pos3")
        r = f'<tr>{sc(row["Grupo"])}<td class="{pos_cls} hi">{html.escape(str(row["Equipo"]))}</td>'
        for v in available_vs:
            pts = row.get(f"Pts_{v}", "—")
            gf  = row.get(f"GF_{v}", "—")
            r += f'<td>{pts:.2f}</td><td class="muted">{gf:.2f}</td>'
        r += "</tr>"
        rows_html.append(r)

    return f"""
<h2>Mejores terceros (ordenados por v3)</h2>
<p class="sub" style="margin-bottom:12px">Los 4 primeros clasifican a octavos de final. Coloreado por posición en v3.</p>
<table>
<thead>{header_parts}</thead>
<tbody>{"".join(rows_html)}</tbody>
</table>
"""

# ============================================================================
# ENSAMBLAR HTML
# ============================================================================

version_info = {
    "v1": "Elo puro · forma · debut · lesiones · estrella (5 vars)",
    "v2": "Elo compuesto (TM+mercado) · altitud · calor · local · viaje · clasificatorio (12 vars)",
    "v3": "42 variables: portero · edad×calor · top-5 ligas · H2H · fatiga club · jet lag · rotación J3 · balón parado · sesgo arbitral...",
    "v4": "+18 vars 🟢: descomposición ATAQUE/DEFENSA (estilo·tempo) · dif. descanso/viaje vs rival · techo→WBGT efectivo · altura · cohesión · momentum · continuidad DT (60 efectivas)",
    "v5": "Total de goles DINÁMICO: el nº de goles escala con el desequilibrio → recupera las goleadas (4-0/5-0) en partidos top-vs-débil. Media 3.0, σ 0.82 (v4 era plana, σ 0.21). Clasificaciones intactas.",
    "v6": "DEFINITIVA — auditada (Opus 4.8): doble conteo de calidad corregido (corr 0.79→0.00, favoritos moderados) · Dixon-Coles (empates 0.19→0.22) · Monte Carlo con desempates FIFA y probabilidad real de clasificar · bugs de integridad corregidos.",
}

legend = '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px">'
for v, desc in version_info.items():
    if v in matches:
        legend += f'<div style="background:#1e293b;border-radius:8px;padding:12px 16px;flex:1;min-width:220px"><span class="badge-{v}">{v.upper()}</span><p style="color:#94a3b8;font-size:.8rem;margin-top:6px">{desc}</p></div>'
legend += "</div>"

body = f"""
<h1>Comparativa de versiones — Modelo Mundial 2026</h1>
<p class="sub">Generado el 2026-06-07 · Ejecuta <code>python exportar_comparacion.py</code> para actualizar</p>
{legend}
{build_matches_section()}
{build_group_section()}
{build_delta_section()}
{build_terceros_section()}
"""

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Comparativa v1/v2/v3 — Mundial 2026</title>
<style>{CSS}</style>
</head>
<body>
{body}
<script>{JS}
// Activate first group tab on load
document.addEventListener('DOMContentLoaded', () => {{
  const firstTab = document.querySelector('.tab');
  if (firstTab) {{
    const id = firstTab.id.replace('tab-', '');
    showTab(id);
  }}
}});
</script>
</body>
</html>"""

out = "comparacion_versiones.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"✓ {out} generado")
