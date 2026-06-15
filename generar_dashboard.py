"""
Genera dashboard_mundial.html — dashboard standalone (un solo archivo) con los
resultados del modelo v6 DEFINITIVA, con estética de broadcast deportivo:
campo de fútbol de césped, emblema de trofeo, tipografía condensada, datos del torneo.

Datos embebidos → portable, se abre desde móvil u ordenador sin servidor.
Banderas: flagcdn.com · Tipografía: Google Fonts (requieren internet al abrir).
Nota: el emblema es un diseño propio (no el logo oficial FIFA, que tiene copyright).
Ejecutar desde mundial2026/.
"""

import pandas as pd
import json

# ============================================================================
# 1 — EQUIPOS: nombre ES + código ISO para banderas (flagcdn)
# ============================================================================
TEAMS = {
    "Argentina":("Argentina","ar"), "Spain":("España","es"), "France":("Francia","fr"),
    "England":("Inglaterra","gb-eng"), "Morocco":("Marruecos","ma"), "Brazil":("Brasil","br"),
    "Portugal":("Portugal","pt"), "Netherlands":("Países Bajos","nl"), "Belgium":("Bélgica","be"),
    "Croatia":("Croacia","hr"), "Colombia":("Colombia","co"), "Mexico":("México","mx"),
    "Senegal":("Senegal","sn"), "Uruguay":("Uruguay","uy"), "USA":("EE. UU.","us"),
    "Japan":("Japón","jp"), "Switzerland":("Suiza","ch"), "Iran":("Irán","ir"),
    "Turkey":("Turquía","tr"), "Ecuador":("Ecuador","ec"), "Austria":("Austria","at"),
    "South Korea":("Corea del Sur","kr"), "Australia":("Australia","au"), "Algeria":("Argelia","dz"),
    "Egypt":("Egipto","eg"), "Norway":("Noruega","no"), "Canada":("Canadá","ca"),
    "Ivory Coast":("Costa de Marfil","ci"), "Sweden":("Suecia","se"), "Czech Republic":("Chequia","cz"),
    "Paraguay":("Paraguay","py"), "Scotland":("Escocia","gb-sct"), "DR Congo":("RD Congo","cd"),
    "Tunisia":("Túnez","tn"), "Uzbekistan":("Uzbekistán","uz"), "Germany":("Alemania","de"),
    "New Zealand":("Nueva Zelanda","nz"), "Qatar":("Catar","qa"), "South Africa":("Sudáfrica","za"),
    "Bosnia":("Bosnia","ba"), "Ghana":("Ghana","gh"), "Panama":("Panamá","pa"),
    "Cape Verde":("Cabo Verde","cv"), "Saudi Arabia":("Arabia Saudí","sa"), "Iraq":("Irak","iq"),
    "Jordan":("Jordania","jo"), "Haiti":("Haití","ht"), "Curacao":("Curazao","cw"),
}
SEDES_ES = {
    "Mexico City":"Ciudad de México","Guadalajara":"Guadalajara","Monterrey":"Monterrey",
    "Atlanta":"Atlanta","Kansas City":"Kansas City","Dallas":"Dallas","Houston":"Houston",
    "Los Angeles":"Los Ángeles","San Francisco":"San Francisco","Seattle":"Seattle",
    "Vancouver":"Vancouver","Toronto":"Toronto","Boston":"Boston","Philadelphia":"Filadelfia",
    "New York":"Nueva York","Miami":"Miami",
}
def es_name(en): return TEAMS.get(en,(en,"un"))[0]
def code(en):    return TEAMS.get(en,(en,"un"))[1]

def traducir_factores(factores):
    out = factores
    for en,(es,_) in sorted(TEAMS.items(), key=lambda x:-len(x[0])):
        out = out.replace(en, es)
    return out

# ============================================================================
# 2 — CARGAR DATOS v6
# ============================================================================
pron = pd.read_csv("v6/pronosticos_fase_grupos.csv")
clas = pd.read_csv("v6/clasificacion_grupos.csv")
terc = pd.read_csv("v6/mejores_terceros.csv")

def jornada(pid): return 1 if pid<=24 else (2 if pid<=48 else 3)
terc_sorted = terc.sort_values("Pts_esp", ascending=False).reset_index(drop=True)
terceros_pasan = set(terc_sorted.iloc[:8]["Equipo"])

matches, total_goles = [], 0
for _, r in pron.iterrows():
    gl, gv = map(int, str(r["Marcador"]).split("-")); total_goles += gl+gv
    dia, mes = str(r["Fecha"]).split("-")
    matches.append({
        "id": int(r["P"]), "j": jornada(int(r["P"])),
        "fecha": f"{int(dia)} {mes.lower()}", "sede": SEDES_ES.get(r["Sede"], r["Sede"]), "hora": int(r["H"]),
        "local": es_name(r["Local"]), "localCode": code(r["Local"]),
        "visit": es_name(r["Visit"]), "visitCode": code(r["Visit"]),
        "grupo": r["G"], "marcador": r["Marcador"],
        "p1": round(float(r["P(1)"])*100), "px": round(float(r["P(X)"])*100), "p2": round(float(r["P(2)"])*100),
        "xgL": float(r["xG_L"]), "xgV": float(r["xG_V"]),
        "conf": r["Conf"], "factores": traducir_factores(str(r["Factores"])),
    })

groups = {}
for g in sorted(clas["Grupo"].unique()):
    sub = clas[clas["Grupo"]==g].sort_values("Pos"); rows=[]
    for _, r in sub.iterrows():
        pos=int(r["Pos"]); team=r["Equipo"]
        status = "directo" if pos<=2 else ("tercero_pasa" if (pos==3 and team in terceros_pasan)
                  else ("tercero_fuera" if pos==3 else "fuera"))
        rows.append({"pos":pos,"equipo":es_name(team),"code":code(team),
                     "pts":float(r["Pts_esp"]),"gf":float(r["GF_esp"]),"gc":float(r["GC_esp"]),
                     "ptop2":round(float(r["P_top2"])*100) if "P_top2" in r.index else None,
                     "status":status})
    groups[g]=rows

clasificados={"directos":[],"terceros":[]}
for g,rows in groups.items():
    for row in rows:
        if row["status"]=="directo": clasificados["directos"].append({**row,"grupo":g})
for i,(_,r) in enumerate(terc_sorted.iterrows()):
    clasificados["terceros"].append({"equipo":es_name(r["Equipo"]),"code":code(r["Equipo"]),
        "grupo":r["Grupo"],"pts":float(r["Pts_esp"]),"pasa":i<8})

# Favorito por grupo y favorito global (mayor pts esperados)
fav_global = max(clas.itertuples(), key=lambda x:x.Pts_esp)

DATA = {
    "matches":matches, "groups":groups, "clasificados":clasificados,
    "kpis":{"partidos":len(matches),"selecciones":48,"grupos":12,"goles":total_goles},
    "torneo":{
        "anfitriones":[["ca","Canadá"],["mx","México"],["us","EE. UU."]],
        "inicio":"11 jun","fin":"19 jul 2026","sedes":16,"total":104,
        "favorito":{"equipo":es_name(fav_global.Equipo),"code":code(fav_global.Equipo),
                    "pts":round(float(fav_global.Pts_esp),1),"grupo":fav_global.Grupo},
    },
}

# ============================================================================
# 3 — HTML / CSS / JS  (estética broadcast deportivo)
# ============================================================================
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0a3d20">
<title>Mundial 2026 · Pronósticos</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --grass-a:#1c8a43; --grass-b:#178a3f; --grass-dk:#0a3d20; --grass-dk2:#072e18;
  --card:#ffffff; --ink:#0f1e16; --muted:#5b6b62; --line:#e4ebe6;
  --gold:#f4c430; --gold-dk:#c9971f; --gold-soft:#fde68a;
  --green:#16a34a; --amber:#f59e0b; --blue:#2563eb; --red:#dc2626; --slate:#94a3b8;
  --shadow:0 2px 6px rgba(7,46,24,.10),0 14px 38px rgba(7,46,24,.16);
  --shadow-sm:0 1px 3px rgba(7,46,24,.12);
  --radius:16px;
  --cond:"Barlow Condensed",sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:"Inter",-apple-system,BlinkMacSystemFont,sans-serif;color:var(--ink);
  -webkit-font-smoothing:antialiased;padding-bottom:env(safe-area-inset-bottom);
  background:
    repeating-linear-gradient(0deg,var(--grass-dk) 0 46px,var(--grass-dk2) 46px 92px);
  background-attachment:fixed}
img{display:block}

/* ===== HERO = CAMPO DE FÚTBOL ===== */
.hero{position:relative;overflow:hidden;color:#fff;
  background:repeating-linear-gradient(90deg,var(--grass-a) 0 64px,var(--grass-b) 64px 128px);
  padding:26px 18px 70px;border-bottom:3px solid rgba(255,255,255,.25)}
.hero::before{content:"";position:absolute;inset:0;
  background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(255,255,255,.18),transparent 60%),
             linear-gradient(180deg,rgba(7,46,24,.05),rgba(7,46,24,.45))}
.pitch{position:absolute;inset:0;width:100%;height:100%;z-index:0;opacity:.55}
.hero-in{position:relative;z-index:2;max-width:1080px;margin:0 auto;text-align:center}

/* emblema */
.emblem{width:96px;height:96px;margin:0 auto 6px;filter:drop-shadow(0 6px 14px rgba(0,0,0,.35))}
.kicker{font-family:var(--cond);font-weight:700;letter-spacing:.32em;font-size:.8rem;
  text-transform:uppercase;color:var(--gold-soft);margin-top:4px}
h1{font-family:var(--cond);font-weight:900;font-size:2.5rem;line-height:.98;letter-spacing:.01em;
  text-transform:uppercase;text-shadow:0 2px 12px rgba(0,0,0,.35);margin-top:2px}
h1 .yr{color:var(--gold)}
.tagline{font-size:.92rem;opacity:.95;margin-top:8px;font-weight:500}
.host{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:16px}
.host .h{display:flex;align-items:center;gap:7px;background:rgba(0,0,0,.22);
  border:1px solid rgba(255,255,255,.25);padding:6px 13px;border-radius:999px;
  font-family:var(--cond);font-weight:600;font-size:.86rem;letter-spacing:.03em}
.host img{width:24px;height:17px;border-radius:3px;box-shadow:0 1px 2px rgba(0,0,0,.3)}
.meta-strip{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:14px}
.ms{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:8px;
  padding:5px 11px;font-size:.74rem;font-weight:600;display:flex;align-items:center;gap:5px}
.ms b{font-family:var(--cond);font-size:.92rem;font-weight:800;letter-spacing:.02em}

/* ===== KPIs ===== */
.kpis{max-width:1080px;margin:-48px auto 0;padding:0 18px;position:relative;z-index:5;
  display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.kpi{background:var(--card);border-radius:14px;padding:15px 10px;box-shadow:var(--shadow);
  text-align:center;border-top:3px solid var(--gold)}
.kpi .ic{font-size:1.05rem;line-height:1}
.kpi .n{font-family:var(--cond);font-size:1.7rem;font-weight:900;color:var(--grass-dk);line-height:1;margin-top:2px}
.kpi .l{font-size:.66rem;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.05em;font-weight:700}

/* favorito banner */
.fav{max-width:1080px;margin:14px auto 0;padding:0 18px}
.fav-in{background:linear-gradient(100deg,#0a3d20,#11512c);border-radius:14px;box-shadow:var(--shadow);
  padding:13px 18px;display:flex;align-items:center;gap:14px;border:1px solid rgba(244,196,48,.35);color:#fff}
.fav .trophy{font-size:1.4rem;filter:drop-shadow(0 2px 4px rgba(0,0,0,.4))}
.fav img{width:40px;height:28px;border-radius:5px;box-shadow:0 2px 5px rgba(0,0,0,.35)}
.fav .ft{font-family:var(--cond);text-transform:uppercase;letter-spacing:.14em;font-size:.68rem;color:var(--gold-soft);font-weight:700}
.fav .fn{font-family:var(--cond);font-weight:800;font-size:1.25rem;line-height:1}
.fav .fp{margin-left:auto;text-align:right;font-size:.72rem;opacity:.85}
.fav .fp b{font-family:var(--cond);font-size:1.5rem;font-weight:900;display:block;color:var(--gold)}

/* ===== WRAP / TABS ===== */
.wrap{max-width:1080px;margin:0 auto;padding:18px 18px 30px}
.tabs{display:flex;gap:5px;background:rgba(7,46,24,.55);backdrop-filter:blur(8px);
  padding:5px;border-radius:14px;margin:18px 0 16px;position:sticky;top:8px;z-index:30;
  box-shadow:var(--shadow);border:1px solid rgba(255,255,255,.12)}
.tab{flex:1;border:none;background:transparent;color:rgba(255,255,255,.7);
  font-family:var(--cond);font-weight:700;font-size:1rem;letter-spacing:.04em;text-transform:uppercase;
  padding:11px 6px;border-radius:10px;cursor:pointer;transition:.18s}
.tab.active{background:var(--card);color:var(--grass-dk);box-shadow:var(--shadow-sm)}

/* ===== FILTERS ===== */
.filters{display:flex;flex-direction:column;gap:9px;margin-bottom:16px}
.filter-row{display:flex;gap:7px;overflow-x:auto;padding-bottom:3px;scrollbar-width:none}
.filter-row::-webkit-scrollbar{display:none}
.flabel{font-family:var(--cond);font-size:.82rem;color:#fff;font-weight:700;text-transform:uppercase;
  letter-spacing:.05em;min-width:62px;display:flex;align-items:center;opacity:.85}
.pill{flex:0 0 auto;border:1.5px solid rgba(255,255,255,.25);background:rgba(255,255,255,.1);
  color:#fff;padding:7px 14px;border-radius:999px;font-size:.82rem;font-weight:700;cursor:pointer;
  transition:.15s;white-space:nowrap;font-family:inherit;backdrop-filter:blur(4px)}
.pill.active{background:var(--gold);border-color:var(--gold);color:var(--grass-dk)}
.search{width:100%;border:1.5px solid rgba(255,255,255,.25);background:rgba(255,255,255,.95);
  border-radius:12px;padding:12px 14px;font-size:.92rem;font-family:inherit;color:var(--ink)}
.search:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgba(244,196,48,.25)}
.search::placeholder{color:var(--muted)}

/* ===== MATCH CARDS ===== */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}
.match{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);
  padding:0 0 13px;cursor:pointer;transition:.2s;overflow:hidden;border:1px solid rgba(7,46,24,.04)}
.match:hover{transform:translateY(-3px);box-shadow:0 4px 10px rgba(7,46,24,.14),0 22px 44px rgba(7,46,24,.20)}
.m-top{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;
  background:linear-gradient(90deg,#0a3d20,#11512c);color:#fff;font-size:.72rem;font-weight:600}
.m-meta{display:flex;align-items:center;gap:7px;letter-spacing:.01em}
.jchip{background:var(--gold);color:var(--grass-dk);padding:2px 7px;border-radius:5px;
  font-family:var(--cond);font-weight:800;font-size:.72rem;letter-spacing:.03em}
.inaug{background:#fff;color:var(--grass-dk);padding:2px 7px;border-radius:5px;font-weight:800;font-size:.62rem;letter-spacing:.03em}
.conf{padding:3px 9px;border-radius:999px;font-size:.64rem;font-weight:800;letter-spacing:.03em;text-transform:uppercase}
.conf.ALTO{background:#dcfce7;color:#15803d} .conf.MEDIO{background:#fef3c7;color:#b45309} .conf.BAJO{background:#fee2e2;color:#b91c1c}
.conf.star{box-shadow:inset 0 0 0 1.5px currentColor}
.m-teams{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;padding:16px 14px 4px}
.team{display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center}
.team img{width:54px;height:38px;object-fit:cover;border-radius:7px;box-shadow:0 2px 6px rgba(0,0,0,.22);
  border:2px solid #fff;outline:1px solid var(--line)}
.team .tn{font-family:var(--cond);font-size:1rem;font-weight:700;line-height:1.05;letter-spacing:.01em}
.score{font-family:var(--cond);font-size:2.1rem;font-weight:900;letter-spacing:.02em;padding:0 4px;
  color:var(--grass-dk);white-space:nowrap}
.score small{font-family:"Inter";font-size:.62rem;color:var(--muted);font-weight:700;display:block;
  text-align:center;letter-spacing:.04em;text-transform:uppercase;margin-top:1px}
.bar{display:flex;height:8px;border-radius:5px;overflow:hidden;margin:14px 14px 0;background:var(--line)}
.bar i{display:block;height:100%}
.bar .b1{background:var(--green)} .bar .bx{background:var(--slate)} .bar .b2{background:var(--blue)}
.plabels{display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);
  margin:7px 14px 0;font-weight:600}
.plabels b{color:var(--ink);font-family:var(--cond);font-size:.82rem}
.xg{font-size:.7rem;color:var(--muted);margin:11px 14px 0;font-weight:600;display:none}
.facts{margin:11px 14px 0;padding-top:10px;border-top:1px dashed var(--line);display:none;flex-wrap:wrap;gap:6px}
.match.open .facts,.match.open .xg{display:flex}
.match.open .xg{display:block}
.fact{background:#eef5f0;color:#3c6b4f;font-size:.69rem;padding:3px 9px;border-radius:7px;font-weight:600}
.hint{font-size:.6rem;color:var(--slate);text-align:center;margin-top:9px;letter-spacing:.03em;text-transform:uppercase;font-weight:700}
.match.open .hint{display:none}

/* ===== GROUP TABLES ===== */
.groups{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
.gcard{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}
.gh{background:repeating-linear-gradient(90deg,#0a3d20 0 22px,#0c4423 22px 44px);
  color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;
  border-bottom:3px solid var(--gold)}
.gh .gl{font-family:var(--cond);font-weight:900;font-size:1.25rem;letter-spacing:.04em;text-transform:uppercase}
.gh .gt{font-size:.66rem;opacity:.8;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.grow{display:grid;grid-template-columns:22px 32px 1fr auto;align-items:center;gap:10px;
  padding:11px 14px;border-bottom:1px solid var(--line);font-size:.9rem}
.grow:last-child{border-bottom:none}
.grow .gp{font-family:var(--cond);font-weight:800;color:var(--muted);font-size:.95rem;text-align:center}
.grow img{width:30px;height:21px;object-fit:cover;border-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.18)}
.grow .ge{font-weight:700;display:flex;flex-direction:column;justify-content:center;line-height:1.18}
.grow .gprob{font-size:.62rem;color:var(--muted);font-weight:600}
.grow.directo .gprob{color:var(--green)} .grow.tercero_pasa .gprob{color:var(--amber)}
.grow .gpts{font-family:var(--cond);font-weight:800;font-size:1.05rem;color:var(--grass-dk);font-variant-numeric:tabular-nums}
.grow .gpts small{color:var(--muted);font-weight:600;font-size:.62rem;font-family:"Inter"}
.grow.directo{background:linear-gradient(90deg,rgba(22,163,74,.12),transparent)}
.grow.directo .gp{color:var(--green)}
.grow.tercero_pasa{background:linear-gradient(90deg,rgba(245,158,11,.14),transparent)}
.grow.tercero_pasa .gp{color:var(--amber)}
.tag{font-family:var(--cond);font-size:.62rem;font-weight:800;padding:1px 6px;border-radius:5px;
  margin-left:7px;letter-spacing:.04em}
.tag.d{background:#dcfce7;color:#15803d} .tag.t{background:#fef3c7;color:#b45309}

/* ===== LEGEND ===== */
.legend{display:flex;flex-wrap:wrap;gap:14px;background:var(--card);border-radius:12px;
  padding:12px 16px;box-shadow:var(--shadow);margin-bottom:16px;font-size:.76rem;color:var(--muted)}
.legend span{display:flex;align-items:center;gap:6px;font-weight:600}
.sw{width:13px;height:13px;border-radius:4px}

/* ===== PASE ===== */
.section-title{font-family:var(--cond);font-size:1.3rem;font-weight:800;text-transform:uppercase;
  letter-spacing:.04em;color:#fff;margin:6px 0 13px;display:flex;align-items:center;gap:9px;
  text-shadow:0 1px 6px rgba(0,0,0,.3)}
.qgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:10px;margin-bottom:26px}
.qcard{background:var(--card);border-radius:12px;box-shadow:var(--shadow);padding:12px;
  display:flex;align-items:center;gap:10px;border-left:4px solid var(--green)}
.qcard.amber{border-left-color:var(--amber)}
.qcard.out{border-left-color:var(--line);opacity:.45}
.qcard img{width:34px;height:24px;object-fit:cover;border-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.18)}
.qcard .qn{font-family:var(--cond);font-weight:700;font-size:.96rem;line-height:1.05}
.qcard .qg{font-size:.66rem;color:var(--muted);font-weight:600}

.foot{max-width:1080px;margin:0 auto;padding:22px 18px 46px;color:rgba(255,255,255,.7);
  font-size:.73rem;text-align:center;line-height:1.65}
.foot b{color:var(--gold-soft)}
.hidden{display:none!important}
.empty{text-align:center;color:rgba(255,255,255,.8);padding:40px;font-size:.95rem;font-weight:600}

@media(max-width:640px){
  h1{font-size:2rem} .emblem{width:80px;height:80px}
  .kpis{grid-template-columns:repeat(2,1fr)}
  .grid,.groups,.qgrid{grid-template-columns:1fr}
  .score{font-size:1.85rem} .fav .fp{font-size:.66rem}
}
</style>
</head>
<body>

<header class="hero">
  <!-- líneas del campo -->
  <svg class="pitch" viewBox="0 0 1000 360" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <g fill="none" stroke="rgba(255,255,255,.85)" stroke-width="2.5">
      <rect x="14" y="14" width="972" height="332" rx="2"/>
      <line x1="500" y1="14" x2="500" y2="346"/>
      <circle cx="500" cy="180" r="62"/>
      <circle cx="500" cy="180" r="3.5" fill="rgba(255,255,255,.9)" stroke="none"/>
      <rect x="14" y="96" width="96" height="168"/>
      <rect x="14" y="138" width="38" height="84"/>
      <rect x="890" y="96" width="96" height="168"/>
      <rect x="948" y="138" width="38" height="84"/>
      <path d="M110 138 A48 48 0 0 1 110 222"/>
      <path d="M890 138 A48 48 0 0 0 890 222"/>
    </g>
  </svg>

  <div class="hero-in">
    <!-- EMBLEMA TROFEO (diseño propio) -->
    <svg class="emblem" viewBox="0 0 100 100" aria-label="Emblema del torneo">
      <defs>
        <linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#fde68a"/><stop offset=".5" stop-color="#f4c430"/><stop offset="1" stop-color="#b8860b"/>
        </linearGradient>
        <radialGradient id="gBg" cx=".5" cy=".4" r=".7">
          <stop offset="0" stop-color="#11512c"/><stop offset="1" stop-color="#072e18"/>
        </radialGradient>
      </defs>
      <circle cx="50" cy="50" r="47" fill="url(#gBg)" stroke="url(#gGold)" stroke-width="3.5"/>
      <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(244,196,48,.35)" stroke-width="1"/>
      <!-- copa -->
      <g fill="url(#gGold)">
        <path d="M34 24 h32 v9 a16 16 0 0 1 -32 0 z"/>
        <path d="M34 26 h-7 a7 8 0 0 0 9 13 l-2 -5 a4 4 0 0 1 -4 -6 h4 z"/>
        <path d="M66 26 h7 a7 8 0 0 1 -9 13 l2 -5 a4 4 0 0 0 4 -6 h-4 z"/>
        <rect x="47" y="48" width="6" height="10"/>
        <path d="M38 58 h24 l-3 7 h-18 z"/>
        <rect x="36" y="65" width="28" height="5" rx="2"/>
      </g>
      <!-- balón mini -->
      <circle cx="50" cy="34" r="5" fill="#0a3d20" stroke="#fde68a" stroke-width="1"/>
      <text x="50" y="84" text-anchor="middle" font-family="Barlow Condensed,sans-serif"
        font-size="13" font-weight="900" fill="url(#gGold)" letter-spacing="1">2026</text>
    </svg>

    <div class="kicker">Canadá · México · EE.&nbsp;UU.</div>
    <h1>Mundial <span class="yr">2026</span></h1>
    <div class="tagline">Pronósticos de la fase de grupos · modelo cuantitativo</div>

    <div class="host" id="host"></div>
    <div class="meta-strip" id="metastrip"></div>
  </div>
</header>

<div class="kpis" id="kpis"></div>
<div class="fav"><div class="fav-in" id="favbox"></div></div>

<div class="wrap">
  <div class="tabs">
    <button class="tab active" data-view="partidos">⚽ Partidos</button>
    <button class="tab" data-view="grupos">📊 Grupos</button>
    <button class="tab" data-view="pase">🏆 Octavos</button>
  </div>

  <section id="view-partidos">
    <div class="filters">
      <input class="search" id="search" placeholder="🔎 Busca tu selección (México, España...)">
      <div class="filter-row" id="fjornada">
        <span class="flabel">Jornada</span>
        <button class="pill active" data-j="all">Todas</button>
        <button class="pill" data-j="1">Jornada 1</button>
        <button class="pill" data-j="2">Jornada 2</button>
        <button class="pill" data-j="3">Jornada 3</button>
      </div>
      <div class="filter-row" id="fgrupo">
        <span class="flabel">Grupo</span>
        <button class="pill active" data-g="all">Todos</button>
      </div>
    </div>
    <div class="grid" id="matches"></div>
    <div class="empty hidden" id="noMatch">⚠️ No hay partidos con esos filtros.</div>
  </section>

  <section id="view-grupos" class="hidden">
    <div class="legend">
      <span><i class="sw" style="background:var(--green)"></i> 1.º–2.º clasifican directos</span>
      <span><i class="sw" style="background:var(--amber)"></i> 3.º entre los 8 mejores → octavos</span>
      <span><i class="sw" style="background:var(--slate)"></i> eliminado</span>
    </div>
    <div class="groups" id="groups"></div>
  </section>

  <section id="view-pase" class="hidden">
    <div class="section-title">✅ Clasificados directos</div>
    <div class="qgrid" id="qdirect"></div>
    <div class="section-title">🟡 Mejores terceros · pasan 8 de 12</div>
    <div class="qgrid" id="qthird"></div>
  </section>
</div>

<div class="foot">
  <b>Mundial 2026</b> · 48 selecciones · 104 partidos · 16 sedes en 3 países.<br>
  Estimaciones de un modelo Poisson bivariante (v6 DEFINITIVA: auditada — doble conteo corregido, Dixon-Coles, MC con desempates): no son certezas, el fútbol tiene azar.<br>
  Hecho para la porra · banderas © flagcdn.com
</div>

<script>
const DATA = __DATA__;
const FLAG  = c => `https://flagcdn.com/w80/${c}.png`;
const FLAGS = c => `https://flagcdn.com/w40/${c}.png`;
const T = DATA.torneo;

/* anfitriones + meta strip */
document.getElementById('host').innerHTML = T.anfitriones.map(([c,n])=>
  `<div class="h"><img src="${FLAGS(c)}" alt="">${n}</div>`).join('');
document.getElementById('metastrip').innerHTML = [
  ['📅',`<b>${T.inicio}</b> – ${T.fin}`],['🏟️',`<b>${T.sedes}</b> sedes`],
  ['⚽',`<b>${T.total}</b> partidos`],['🌍',`<b>48</b> selecciones`]
].map(([i,t])=>`<span class="ms">${i} ${t}</span>`).join('');

/* KPIs */
document.getElementById('kpis').innerHTML = [
  ['⚽','Partidos',DATA.kpis.partidos],['🌍','Selecciones',DATA.kpis.selecciones],
  ['📊','Grupos',DATA.kpis.grupos],['🥅','Goles previstos',DATA.kpis.goles]
].map(([ic,l,n])=>`<div class="kpi"><div class="ic">${ic}</div><div class="n">${n}</div><div class="l">${l}</div></div>`).join('');

/* favorito */
const f=T.favorito;
document.getElementById('favbox').innerHTML=`
  <span class="trophy">🏆</span>
  <img src="${FLAG(f.code)}" alt="">
  <div><div class="ft">Favorito del modelo</div><div class="fn">${f.equipo}</div></div>
  <div class="fp">Grupo ${f.grupo}<b>${f.pts}</b>pts esperados</div>`;

/* tabs */
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  ['partidos','grupos','pase'].forEach(v=>
    document.getElementById('view-'+v).classList.toggle('hidden', v!==t.dataset.view));
  window.scrollTo({top:0,behavior:'smooth'});
});

/* match card */
function confClass(c){const b=c.replace('*','');return `conf ${b}${c.includes('*')?' star':''}`;}
function confTxt(c){const m={ALTO:'Alta',MEDIO:'Media',BAJO:'Baja'};return (m[c.replace('*','')]||c)+(c.includes('*')?' ★':'');}
function matchCard(m){
  const facts=m.factores.split(' | ').filter(f=>f&&f!=='Equilibrado').map(f=>`<span class="fact">${f}</span>`).join('');
  const inaug=m.id===1?'<span class="inaug">🎉 INAUGURAL</span>':'';
  return `<div class="match" data-j="${m.j}" data-g="${m.grupo}"
       data-teams="${(m.local+' '+m.visit).toLowerCase()}" onclick="this.classList.toggle('open')">
    <div class="m-top">
      <div class="m-meta"><span class="jchip">J${m.j}</span>${inaug} ${m.fecha} · ${m.sede}</div>
      <span class="${confClass(m.conf)}">${confTxt(m.conf)}</span>
    </div>
    <div class="m-teams">
      <div class="team"><img loading="lazy" src="${FLAG(m.localCode)}" alt=""><div class="tn">${m.local}</div></div>
      <div class="score">${m.marcador}<small>Grupo ${m.grupo}</small></div>
      <div class="team"><img loading="lazy" src="${FLAG(m.visitCode)}" alt=""><div class="tn">${m.visit}</div></div>
    </div>
    <div class="bar"><i class="b1" style="width:${m.p1}%"></i><i class="bx" style="width:${m.px}%"></i><i class="b2" style="width:${m.p2}%"></i></div>
    <div class="plabels"><span><b>${m.p1}%</b> ${m.local}</span><span>${m.px}% X</span><span>${m.visit} <b>${m.p2}%</b></span></div>
    <div class="xg">📐 xG previstos · ${m.local} ${m.xgL.toFixed(2)} — ${m.visit} ${m.xgV.toFixed(2)}</div>
    ${facts?`<div class="facts">${facts}</div>`:''}
    <div class="hint">toca para ver el análisis ▾</div>
  </div>`;
}
document.getElementById('matches').innerHTML = DATA.matches.map(matchCard).join('');

/* grupo pills */
const grupos=Object.keys(DATA.groups);
document.getElementById('fgrupo').insertAdjacentHTML('beforeend',
  grupos.map(g=>`<button class="pill" data-g="${g}">Grupo ${g}</button>`).join(''));

/* filtros */
let fJ='all',fG='all',fQ='';
function applyFilters(){
  let vis=0;
  document.querySelectorAll('#matches .match').forEach(el=>{
    const ok=(fJ==='all'||el.dataset.j===fJ)&&(fG==='all'||el.dataset.g===fG)&&(!fQ||el.dataset.teams.includes(fQ));
    el.classList.toggle('hidden',!ok); if(ok)vis++;
  });
  document.getElementById('noMatch').classList.toggle('hidden',vis>0);
}
document.querySelectorAll('#fjornada .pill').forEach(p=>p.onclick=()=>{
  document.querySelectorAll('#fjornada .pill').forEach(x=>x.classList.remove('active'));
  p.classList.add('active');fJ=p.dataset.j;applyFilters();});
document.getElementById('fgrupo').addEventListener('click',e=>{
  if(!e.target.dataset.g)return;
  document.querySelectorAll('#fgrupo .pill').forEach(x=>x.classList.remove('active'));
  e.target.classList.add('active');fG=e.target.dataset.g;applyFilters();});
document.getElementById('search').oninput=e=>{fQ=e.target.value.trim().toLowerCase();applyFilters();};

/* grupos */
document.getElementById('groups').innerHTML=grupos.map(g=>{
  const rows=DATA.groups[g].map(r=>{
    const tag=r.status==='directo'?'<span class="tag d">PASA</span>':(r.status==='tercero_pasa'?'<span class="tag t">3.º</span>':'');
    const prob=r.ptop2!=null?`<span class="gprob">${r.ptop2}% clasifica</span>`:'';
    return `<div class="grow ${r.status}"><span class="gp">${r.pos}</span>
      <img loading="lazy" src="${FLAGS(r.code)}" alt="">
      <span class="ge"><span>${r.equipo}${tag}</span>${prob}</span>
      <span class="gpts">${r.pts.toFixed(1)} <small>pts</small></span></div>`;}).join('');
  return `<div class="gcard"><div class="gh"><span class="gl">Grupo ${g}</span><span class="gt">% de clasificar</span></div>${rows}</div>`;
}).join('');

/* pase */
document.getElementById('qdirect').innerHTML=DATA.clasificados.directos.map(d=>`
  <div class="qcard"><img loading="lazy" src="${FLAGS(d.code)}" alt="">
    <div><div class="qn">${d.equipo}</div><div class="qg">Grupo ${d.grupo} · ${d.pts.toFixed(1)} pts</div></div></div>`).join('');
document.getElementById('qthird').innerHTML=DATA.clasificados.terceros.map(t=>`
  <div class="qcard ${t.pasa?'amber':'out'}"><img loading="lazy" src="${FLAGS(t.code)}" alt="">
    <div><div class="qn">${t.equipo}</div><div class="qg">Grupo ${t.grupo} · ${t.pts.toFixed(1)} pts${t.pasa?'':' · fuera'}</div></div></div>`).join('');
</script>
</body>
</html>"""

html_out = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
with open("dashboard_mundial.html", "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"✓ dashboard_mundial.html generado ({len(html_out)//1024} KB)")
print(f"  {len(matches)} partidos · {len(groups)} grupos · {DATA['kpis']['goles']} goles · favorito: {DATA['torneo']['favorito']['equipo']}")
print("  Estética deportiva: campo de césped + emblema + datos del torneo")
