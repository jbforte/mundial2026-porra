"""
Modelo cuantitativo v3: Fase de grupos Mundial 2026
=======================================================
42 variables documentadas con etiqueta [EVIDENCIA] o [HEURÍSTICA].

Bloques implementados:
  A. Fuerza base        — Elo, TM, ligas top-5, exp. mundial, portero, entrenador
  B. Forma/competitivo  — forma reciente, clasificatorio, xG tendencia, balón parado, H2H
  C. Plantilla          — lesiones, fatiga club, edad×calor, profundidad
  D. Logística          — descanso, distancia, jet-lag dirección, hora×calor, motivación J3
  E. Entorno físico     — altitud, aclimatación, WBGT/calor, humedad, cesped (nota)
  F. Localía/arbitraje  — local, diáspora, sesgo arbitral, familiaridad sede
  G. Tácticos           — choque estilos [nota], planteamiento J3 [nota]
  H. Psicológicos       — presión [nota], cohesión [nota], moral [en FORMA]
  I. In-game (no son inputs pre-partido — documentados como limitación)

Fuentes verificadas: eloratings.net, sportingpedia.com, rotowire.com, ESPN, si.com
Fecha: 2026-06-07

ACTUALIZACIÓN 2026-06-08 — Resultados de amistosos de preparación (verified ESPN/FOX):
  31-May  Brasil 6-2 Panamá          → FORMA Brasil ↑
  31-May  EE.UU. 3-2 Senegal         → FORMA USA neutro (luego perdió vs Alemania), Senegal ↓
  02-Jun  Croacia 0-2 Bélgica        → Tielemans + Lukaku; FORMA Bélgica ↑, Croacia ↓
  04-Jun  Francia 1-2 Costa de Marfil → Marcador final pese a rotaciones en 2T; FORMA Francia ↓, CdM ↑
  04-Jun  España 1-1 Irak            → Rotaciones; FORMA España ligero ↓
  05-Jun  Noruega 3-1 Suecia         → Larsen×2 + Nusa; FORMA Noruega ↑↑, Suecia ↓
  05-Jun  Turquía 4-0 Macedonia Norte → FORMA Turquía ↑
  05-Jun  Austria 1-0 Túnez          → FORMA Austria ↑
  05-Jun  Colombia 3-1 Costa Rica    → D.Sánchez + L.Díaz + L.Suárez; FORMA Colombia ↑
  05-Jun  Canadá 2-0 Uzbekistán      → FORMA Canadá ↑
  06-Jun  Brasil 2-1 Egipto          → Guimarães + Endrick; Wesley roto (OUT Mundial), Neymar no viajó
  06-Jun  Argentina 2-0 Honduras     → L.Martínez (pen) + G.Simeone; Messi de banquillo (fatiga)
  06-Jun  EE.UU. 1-2 Alemania        → En suelo americano; FORMA Alemania ↑
  BAJAS CONFIRMADAS: Wesley (Brasil) OUT todo el Mundial; Neymar OUT para J1 vs Marruecos
"""

import numpy as np
import pandas as pd
from scipy.stats import poisson
from math import radians, sin, cos, sqrt, atan2

# ============================================================================
# SECCIÓN 1 — FUERZA BASE
# ============================================================================

# --- Elo (worldfootballrankings.com, 06-Jun-2026) — [HEURÍSTICA con valor predictivo]
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
    # [ESTIMADO] f(rank)=1900−6.1r
    "Qatar":1590.18,"South Africa":1534.00,"Bosnia":1582.80,"Ghana":1503.50,
    "Panama":1576.70,"Cape Verde":1473.00,"Saudi Arabia":1552.30,"Iraq":1527.90,
    "Jordan":1485.20,"Haiti":1393.70,"Curacao":1405.90,
}

# --- Valor de plantilla Transfermarkt (€M) — [HEURÍSTICA] sportingpedia.com Jun-2026
TM_VALUE = {
    "France":1530,"England":1310,"Spain":1260,"Portugal":1020,"Germany":998,
    "Brazil":912,"Netherlands":837,"Argentina":819,"Belgium":549,"Norway":601,
    "Ivory Coast":531,"Turkey":494,"Morocco":488,"Senegal":473,"Uruguay":406,
    "Croatia":386,"Ecuador":376,"Colombia":350,"Switzerland":334,"Austria":285,
    "USA":270,"Algeria":258,"Ghana":240,"Sweden":205,"Canada":203,"Mexico":195,
    "Czech Republic":190,"South Korea":184,"Bosnia":149,"Paraguay":157,
    "Scotland":148,"Japan":285,"Tunisia":54,"South Africa":46,"Australia":41,
    "Egypt":78,"Iran":51,"Saudi Arabia":15,"Qatar":20,"DR Congo":30,"Panama":35,
    "Iraq":25,"Jordan":20,"Cape Verde":25,"Haiti":15,"Curacao":12,
    "Uzbekistan":22,"New Zealand":18,
}

# --- Cuotas de campeonato (ESPN/DraftKings, Jun-2026) — [EVIDENCIA señal mercado]
CHAMPIONSHIP_ODDS_USA = {
    "Spain":450,"France":475,"England":700,"Portugal":850,"Argentina":900,
    "Brazil":950,"Germany":1400,"Netherlands":2000,"Norway":3500,"Belgium":4000,
    "Colombia":4000,"Morocco":5000,"USA":6000,"Switzerland":6500,"Uruguay":6500,
    "Japan":6500,"Mexico":8000,"Ecuador":8000,"Turkey":9000,"Croatia":9000,
    "Senegal":9000,"Sweden":12000,"Austria":15000,"Canada":20000,
    "Scotland":20000,"Ivory Coast":25000,"Czech Republic":25000,
    "Paraguay":30000,"Egypt":30000,"Ghana":30000,"Algeria":35000,
}

# --- Jugadores en ligas top-5 por selección — [HEURÍSTICA] estimado CBS/FIFA
# cbssports.com: total 503/1248 jugadores en top-5 ligas (~10.5 media)
TOP5_PLAYERS = {
    "France":25,"England":25,"Spain":24,"Germany":22,"Portugal":22,
    "Netherlands":20,"Belgium":20,"Brazil":18,"Norway":18,"Argentina":16,
    "Croatia":16,"Morocco":16,"Switzerland":15,"Turkey":14,"Senegal":14,
    "Scotland":14,"Canada":13,"Colombia":13,"Japan":13,"Sweden":13,
    "Austria":12,"Ivory Coast":12,"Czech Republic":11,"Ecuador":10,
    "Algeria":10,"South Korea":10,"Ghana":10,"Uruguay":10,"USA":9,
    "Australia":9,"DR Congo":8,"Tunisia":8,"Haiti":8,"Curacao":8,
    "Mexico":6,"New Zealand":6,"Paraguay":7,"Iran":4,"Uzbekistan":4,
    "Cape Verde":10,"Panama":5,"Saudi Arabia":2,"Qatar":2,"Iraq":3,
    "Jordan":3,"South Africa":5,"Bosnia":12,
}
TOP5_MEAN = 10.5

# --- Apariciones en Copas del Mundo — [HEURÍSTICA] + debutantes ya penalizados
WC_APPEARANCES = {
    "Brazil":22,"Germany":20,"Argentina":18,"Mexico":17,"Spain":16,"France":16,
    "England":16,"Italy":14,"Uruguay":14,"Belgium":14,"Sweden":12,"Switzerland":13,
    "Netherlands":11,"USA":11,"South Korea":11,"Paraguay":10,"Scotland":8,
    "Croatia":8,"Portugal":8,"Czech Republic":8,"Austria":8,"Japan":8,
    "Morocco":6,"Saudi Arabia":6,"Tunisia":6,"Algeria":5,"Ecuador":5,
    "DR Congo":3,"Senegal":3,"Canada":3,"Ivory Coast":3,"Colombia":7,
    "Australia":5,"Iran":6,"Egypt":3,"Norway":3,"Bosnia":1,"Turkey":3,
    "Ghana":4,"South Africa":3,"Qatar":1,"Uzbekistan":0,"Curacao":0,
    "Jordan":0,"Cape Verde":0,"Haiti":1,"Iraq":2,"New Zealand":3,
    "Panama":1,
}
# Años desde última participación (para penalizar "oxidados")
LAST_WC = {
    "Norway":1998,"Iraq":2026,"Haiti":2026,  # Qatar 2022=2022, etc
    # Los demás tienen participación reciente (2018 o 2022)
}

# --- Calidad del portero titular (escala 1-10, 7.5=mediana WC) — [HEURÍSTICA]
# Fuente: si.com ranking GK Jun-2026, beinsports.com
GK_QUALITY = {
    "Argentina":9.5,  # E. Martínez – favorito Golden Glove, campeón 2022
    "Belgium":9.5,    # Courtois – "gold standard"
    "France":9.0,     # Maignan – cat-like reflexes, AC Milan
    "Brazil":9.0,     # Alisson – Champions League winner
    "Croatia":8.5,    # Livaković – héroe de penaltis 2022
    "Spain":8.5,      # D. Raya – 19 clean sheets PL 2025-26
    "Portugal":8.5,   # D. Costa
    "Morocco":8.0,    # Bounou – muy fiable en presión
    "Germany":8.0,    # Neuer – aging pero lúcido
    "Netherlands":8.0,# Verbruggen – Euro 2024 sólido
    "Switzerland":7.8,# Kobel/Sommer – combinación de experiencia
    "Mexico":7.8,     # Ochoa – veterano, especialista grandes torneos
    "Iran":7.5,       # Beiranvand
    "Australia":7.5,  # M. Ryan – Copa Asia sólido
    "Turkey":7.5,     # U. Çakır
    "England":7.5,    # Pickford – bueno pero no élite
    "Uruguay":7.5,    # Rochet
    "Colombia":7.5,   # C. Vargas
    "USA":7.5,        # Turner – mejorado en años recientes
    "Sweden":7.5,     # Olsen
    "South Africa":7.5,# R. Williams – sólido en clasificatorio
    "Japan":7.5,      # Gonda/Nakamura
    "Senegal":7.0,    # Dieng/Mendy
    "Norway":7.0,     # Nyland
    "Egypt":7.0,      # el-Shenawy
    "South Korea":7.0,# Jo H-w
    "Ecuador":7.0,    # Domínguez – irregular
    "Scotland":7.0,   # C. Gordon (43 años) – experimentado pero edad
    "Canada":7.0,     # Crépeau/Borjan
    "Algeria":7.0,    # Mandrea
    "Ivory Coast":7.0,# Fofana
    "Ghana":7.0,      # Ati-Zigi
    "Austria":7.0,    # Pentz
    "Panama":7.0,     # Mosquera
    "Tunisia":7.0,    # Ben Mustapha
    "Cape Verde":7.0, # Vozinha
    "Saudi Arabia":7.0,# Al-Burayk
    "Qatar":7.0,      # Al-Sheeb
    "Bosnia":7.0,
    "Czech Republic":7.0,
    "Paraguay":6.5,   # A. Silva – inconsistente
    "Haiti":6.5,
    "Curacao":6.5,
    "Uzbekistan":6.5,
    "Jordan":6.5,
    "Iraq":6.5,
    "DR Congo":6.5,
    "New Zealand":6.5,
}
GK_BASELINE = 7.5

# --- H2H reciente (últimos 3 años competitivo) — [HEURÍSTICA]
# Formato: (equipo_a, equipo_b) → mod_a (>1 si A tiene ventaja H2H reciente)
# Solo para pares con ≥2 partidos relevantes recientes. Resto: 1.0
H2H = {
    # France 2-1 Brazil Mar-2026 friendly [VERIFICADO del search]
    ("Brazil","France"): 0.98,
    # England 3-0 Croatia EURO 2020, CN 2023 3-1; Croatia ganó WC 2018 SF
    ("England","Croatia"): 1.04,
    # Spain consistentemente domina Uruguay
    ("Spain","Uruguay"): 1.03,
    # Marruecos semis 2022, récord reciente positivo vs equipos europeos medios
    ("Morocco","Scotland"): 1.05,
    # Alemania domina históricamente a Ecuador
    ("Germany","Ecuador"): 1.04,
    # Francia domina a Noruega en clasificatorio y amistosos
    ("France","Norway"): 1.05,
    # Belgium vs Egypt: Belgium dominante históricamente
    ("Belgium","Egypt"): 1.03,
    # Países Bajos vs Japón: Países Bajos ganó los pocos que se han jugado
    ("Netherlands","Japan"): 1.03,
    # Portugal vs Colombia: Portugal ganó amistoso 2023
    ("Portugal","Colombia"): 1.02,
}

def get_h2h(team_a, team_b):
    """Retorna (mod_a, mod_b) del H2H para el par dado."""
    if (team_a, team_b) in H2H:
        m = H2H[(team_a, team_b)]
        return m, 2.0 - m      # si A ventaja 1.04, B es 0.96
    if (team_b, team_a) in H2H:
        m = H2H[(team_b, team_a)]
        return 2.0 - m, m
    return 1.0, 1.0

# --- Eficacia en balones parados — [HEURÍSTICA]
# +: ataque → incrementa xG propio. -: defensa → reduce xG concedido
SET_PIECE_ATK = {
    "England":1.03,"Germany":1.03,"France":1.02,"Morocco":1.02,"Brazil":1.02,
    "Spain":1.01,"Argentina":1.01,"Netherlands":1.01,"Portugal":1.01,
    "Norway":1.02,  # Haaland dominancia área
}
SET_PIECE_DEF = {
    "New Zealand":0.97,"Curacao":0.97,"Haiti":0.97,"Jordan":0.97,
    "Uzbekistan":0.98,"Cape Verde":0.98,
}

# --- Fatiga acumulada temporada de club 2025-26 — [HEURÍSTICA] estimado
# Arsenal ganó PL (Raya→España), Liverpool UCL, etc.
CLUB_FATIGUE = {
    "Spain":0.985,    # Arsenal PL + Real Madrid UCL profundo + Barcelona
    "England":0.985,  # Arsenal PL + Liverpool UCL
    "France":0.988,   # PSG + Monaco activos
    "Germany":0.990,  # Bayern + Dortmund UCL
    "Portugal":0.990, # Benfica + Sporting
    "Netherlands":0.992,
    "Belgium":0.992,
    "Norway":0.995,   # menos clubs top-5
}

# ============================================================================
# SECCIÓN 2 — PLANTILLA: DISPONIBILIDAD Y FÍSICO
# ============================================================================

# --- Lesiones confirmadas (ESPN injuries tracker, 07-Jun-2026) — [HEURÍSTICA alto impacto]
LESIONES_MOD = {
    # [ACTUALIZADO 08-Jun]
    "Brazil":0.93,      # Rodrygo OUT, Estevão OUT, Wesley OUT (muslo vs Egipto 06-Jun), Neymar OUT J1 (pantorrilla ~3 sem)
    "Netherlands":0.97, # Xavi Simons ACL (profundidad afectada)
    "Germany":0.99,     # Lennart Karl OUT → reemplazado por Ouédraogo
    "Scotland":0.99,    # Billy Gilmour OUT
    "Argentina":0.99,   # Messi fatiga muscular (banco vs Honduras 06-Jun), recuperación en curso para J1
}

# --- Edad media de plantilla (RotoWire, Jun-2026) — [EVIDENCIA parcial]
# rotowire.com/soccer/article/2026-fifa-world-cup-squad-ages (verificado)
AVG_AGE = {
    "Ivory Coast":25.35,"Ecuador":25.58,"Bosnia":25.92,"Morocco":25.92,
    "Tunisia":26.15,"Spain":26.19,"Norway":26.35,"South Africa":26.35,
    "Canada":26.42,"Ghana":26.42,"USA":26.42,"Algeria":26.46,"France":26.58,
    "England":26.62,"Senegal":26.62,"Iraq":26.65,"Australia":26.88,
    "Sweden":27.00,"Haiti":27.08,"Belgium":27.12,"Japan":27.19,
    "Czech Republic":27.23,"Turkey":27.23,"Netherlands":27.27,
    "South Korea":27.46,"Mexico":27.50,"Curacao":27.54,"Germany":27.54,
    "Portugal":27.54,"New Zealand":27.62,"Switzerland":27.81,"Croatia":27.88,
    "Saudi Arabia":27.96,"Uzbekistan":27.96,"Jordan":28.08,"Austria":28.12,
    "Uruguay":28.19,"DR Congo":28.50,"Paraguay":28.54,"Argentina":28.62,
    "Brazil":28.65,"Egypt":28.69,"Scotland":28.73,"Qatar":28.92,
    "Cape Verde":29.23,"Colombia":29.58,"Iran":29.81,"Panama":30.00,
}
AVG_AGE_MEAN = 27.5  # media del torneo

# ============================================================================
# SECCIÓN 3 — SEDES: COORDS, ALTITUD, WBGT
# ============================================================================

VENUE_COORDS = {
    "Mexico City":(19.303,-99.151),"Guadalajara":(20.668,-103.462),
    "Monterrey":(25.669,-100.246),"Atlanta":(33.755,-84.401),
    "Kansas City":(39.049,-94.484),"Dallas":(32.748,-97.093),
    "Houston":(29.685,-95.411),"Los Angeles":(33.953,-118.339),
    "San Francisco":(37.403,-121.970),"Seattle":(47.595,-122.332),
    "Vancouver":(49.277,-123.112),"Toronto":(43.633,-79.418),
    "Boston":(42.091,-71.264),"Philadelphia":(39.901,-75.168),
    "New York":(40.814,-74.074),"Miami":(25.958,-80.239),
}

ALTITUD = {
    "Mexico City":2240,"Guadalajara":1566,"Monterrey":540,"Atlanta":320,
    "Kansas City":270,"Dallas":180,"Houston":50,"Los Angeles":30,
    "San Francisco":20,"Seattle":10,"Vancouver":10,"Toronto":76,
    "Boston":30,"Philadelphia":30,"New York":10,"Miami":5,
}

# WBGT estimado en junio (°C) — [EVIDENCIA: Periard et al., FIFA heat guidelines]
# Umbral crítico >28°C: -10% sprints, -25m/min alta intensidad (WC2014 estudio)
# Periard et al. 2022 identificó 14/16 sedes WC2026 superando 28°C WBGT en verano
WBGT = {
    "Monterrey":33.0,   # más alto — 37°C temperatura + humedad
    "Houston":31.5,     # NRG Stadium
    "Miami":30.5,       # Hard Rock
    "Dallas":29.5,      # AT&T Stadium
    "Kansas City":28.5, # Arrowhead
    "Atlanta":28.0,     # Mercedes-Benz (techo retráctil — umbral exacto)
    "Toronto":25.5,     # BMO — tolerable
    "New York":25.0,    # MetLife
    "Philadelphia":25.0,
    "Boston":24.5,
    "Los Angeles":22.5, # Brisa del Pacífico — bajo estrés térmico
    "Seattle":20.0,     # Lumen Field — fresco
    "Vancouver":19.5,   # BC Place — fresco
    "San Francisco":18.0,# Levi's — niebla y viento, bajo estrés
    "Mexico City":20.0, # Altitud enfría — WBGT bajo
    "Guadalajara":22.0, # algo más cálido que CDMX
}

EQUIPOS_ALTURA = {"Ecuador","Colombia","Bolivia","Peru"}
EQUIPOS_ALTURA_MEDIA = {"South Africa","Mexico"}
EQUIPOS_FRIO = {
    "Germany","Netherlands","Belgium","Switzerland","Austria","Norway",
    "Sweden","Scotland","England","Czech Republic","Bosnia","South Korea",
    "Japan","Canada",
}
# Equipos tropicales/calurosos habituados al calor [HEURÍSTICA]
EQUIPOS_CALOR = {"Brazil","Colombia","Ivory Coast","Senegal","Ghana","Morocco",
                 "Tunisia","Cameroon","Nigeria","Mexico","Honduras","Costa Rica",
                 "Ecuador","DR Congo","Cape Verde","Iraq","Iran","Saudi Arabia",
                 "Qatar","Haiti","Panama"}

# ============================================================================
# SECCIÓN 4 — LOGÍSTICA
# ============================================================================

# Debutantes y retornos largos — [HEURÍSTICA con evidencia de rendimiento]
DEBUTANTS    = {"Curacao","Jordan","Uzbekistan","Cape Verde"}
LONG_ABSENCE = {"Haiti","Iraq","DR Congo"}  # > 40 años ausencia

# Riesgo de rotación en J3 (equipo casi seguro de clasificar vs rival eliminado)
# [HEURÍSTICA — "partidos sin nada en juego" sí tienen respaldo en literatura]
ROTATION_RISK_J3 = {
    # (equipo_que_rota, match_id): % reducción xG
    ("France",   61): 0.04,  # Francia vs Noruega — Francia top, Irak eliminado
    ("Argentina",70): 0.04,  # Argentina vs Jordania — Argentina top, Jordania out
    ("Belgium",  64): 0.04,  # Nueva Zelanda vs Bélgica — Bélgica segura 1ª
    ("England",  67): 0.03,  # Panamá vs Inglaterra — Inglaterra segura
    ("Germany",  56): 0.02,  # Ecuador vs Alemania — Alemania probable 1ª
    ("Portugal", 47): 0.03,  # Portugal vs Uzbekistán — Portugal top
    ("Spain",    66): 0.02,  # Uruguay vs España — España segura 1ª
    ("Brazil",   49): 0.02,  # Escocia vs Brasil — Brasil probable 1ª
}

HOST_CITIES = {
    "Mexico":{"Mexico City","Guadalajara","Monterrey"},
    "USA":{"Dallas","Houston","Los Angeles","San Francisco","Seattle",
           "New York","Philadelphia","Kansas City","Atlanta","Miami"},
    "Canada":{"Toronto","Vancouver"},
}

# Familiaridad con sedes USA/Canadá — MLS players ventaja menor — [HEURÍSTICA]
MLS_FAMILIARITY = {
    "USA":    {"Dallas","Houston","Los Angeles","San Francisco","Seattle",
               "New York","Philadelphia","Kansas City","Atlanta","Miami"},
    "Canada": {"Toronto","Vancouver"},
    "Mexico": {"Dallas","Houston","Los Angeles","Kansas City"},  # Liga MX juega en USA
}

# ============================================================================
# SECCIÓN 5 — FORMA Y CONTEXTO COMPETITIVO
# ============================================================================

FORMA = {
    # [ACTUALIZADO 08-Jun] — basado en resultados amistosos previos al Mundial
    "France":1.02,      # ↓ 1.04→1.02: perdió 1-2 vs CdMarfil (04-Jun), aunque 1T titular fue 1-0 arriba
    "Spain":1.01,       # ↓ 1.02→1.01: empató 1-1 vs Irak (04-Jun) con rotaciones
    "Argentina":1.03,   # = sin cambio: 2-0 vs Honduras pero Messi de banquillo; sólido con alternativas
    "Portugal":1.02,
    "Germany":1.02,     # ↑ 1.01→1.02: ganó 2-1 a EE.UU. (06-Jun) en suelo americano
    "Morocco":1.02,
    "Netherlands":1.01,
    "England":1.00,
    "Belgium":1.02,     # ↑ 1.00→1.02: 2-0 a Croacia (02-Jun), Lukaku gol
    "Croatia":0.96,     # ↓ 0.97→0.96: 0-2 vs Bélgica, tercer partido sin ganar
    "Colombia":1.02,    # ↑ 1.01→1.02: 3-1 a Costa Rica (05-Jun), L.Díaz titular y goleador
    "Norway":1.04,      # ↑↑ 1.02→1.04: 3-1 a Suecia (05-Jun), Larsen×2 + Nusa
    "Japan":1.02,
    "Ivory Coast":1.04, # ↑↑ 1.01→1.04: remontó y ganó 2-1 a Francia (04-Jun) — resultado sorpresa
    "Sweden":0.99,      # ↓ 1.01→0.99: 1-3 vs Noruega (05-Jun)
    "Turkey":1.02,      # ↑ 1.01→1.02: 4-0 a Macedonia del Norte (05-Jun)
    "Brazil":0.97,      # ↑ 0.96→0.97: ganó vs Panamá 6-2 y Egipto 2-1, pero bajas crecen
    "Mexico":1.01,
    "USA":1.01,         # = : ganó 3-2 a Senegal pero perdió 1-2 vs Alemania; equilibrado
    "Senegal":0.99,     # ↓ 1.00→0.99: 2-3 vs EE.UU. (31-May); Mané 2 goles pero derrota
    "Switzerland":1.01,
    "Bosnia":1.01,
    "Uruguay":1.00,
    "Ecuador":1.00,
    "Austria":1.01,     # ↑ 1.00→1.01: 1-0 a Túnez (05-Jun)
    "South Korea":1.00,
    "Australia":1.00,
    "Algeria":1.00,
    "Czech Republic":1.00,
    "Paraguay":1.00,
    "Scotland":0.98,
    "Iran":0.98,
    "Egypt":0.99,
    "Canada":1.01,      # ↑ 1.00→1.01: 2-0 a Uzbekistán (jun)
    "Ghana":0.99,
    "Tunisia":0.99,
    "Saudi Arabia":0.98,
    "Qatar":0.99,
    "South Africa":1.00,
    "Panama":1.00,
    "Iraq":1.00,
    "Jordan":1.00,
    "Haiti":0.99,
    "Curacao":0.98,
    "DR Congo":1.00,
    "Uzbekistan":1.00,
    "Cape Verde":1.00,
    "New Zealand":0.98,
}

# Diferencial de goles en clasificatorio por partido — [HEURÍSTICA]
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

# Dependencia de estrella — afecta anchura de IC, no la media — [HEURÍSTICA]
STAR_DEPENDENCY = {
    "Norway":  {"player":"Haaland", "factor":0.65},
    "Egypt":   {"player":"Salah",   "factor":0.60},
    "Portugal":{"player":"Ronaldo", "factor":0.45},
    "Senegal": {"player":"Mané",    "factor":0.40},
    "Argentina":{"player":"Messi",  "factor":0.55},
    "Colombia":{"player":"L.Díaz",  "factor":0.45},
}

# ============================================================================
# SECCIÓN 6 — COMPOSITE ELO (Elo 60% + TM 25% + Mercado 15%)
# ============================================================================

def odds_usa_to_prob(o):
    return 100/(o+100)

def build_composite_elos():
    teams = list(ELO.keys())
    e  = np.array([ELO[t] for t in teams])
    em, es = e.mean(), e.std()
    z_elo = {t:(ELO[t]-em)/es for t in teams}

    tm = np.array([np.log(TM_VALUE.get(t,50)) for t in teams])
    tm_m, tm_s = tm.mean(), tm.std()
    z_tm = {t:(np.log(TM_VALUE.get(t,50))-tm_m)/tm_s for t in teams}

    mkt = {t:odds_usa_to_prob(o) for t,o in CHAMPIONSHIP_ODDS_USA.items() if t in ELO}
    mkt_log = {t:np.log(p) for t,p in mkt.items()}
    if mkt_log:
        mv = np.array(list(mkt_log.values()))
        mm, ms = mv.mean(), mv.std()
        z_mkt = {t:(mkt_log[t]-mm)/ms for t in mkt_log}
    else:
        z_mkt = {}

    comp = {}
    for t in teams:
        if t in z_mkt:
            z = 0.60*z_elo[t] + 0.25*z_tm[t] + 0.15*z_mkt[t]
        else:
            z = 0.70*z_elo[t] + 0.30*z_tm[t]
        comp[t] = z*es + em
    return comp

COMPOSITE_ELO = build_composite_elos()

def effective_strength(team):
    return COMPOSITE_ELO[team] * LESIONES_MOD.get(team, 1.0)

# ============================================================================
# SECCIÓN 7 — FUNCIONES MODIFICADORAS
# ============================================================================

def haversine_km(lat1,lon1,lat2,lon2):
    R=6371.0; dlat=radians(lat2-lat1); dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R*2*atan2(sqrt(a),sqrt(1-a))

# A3 — Jugadores en ligas top-5 [HEURÍSTICA]
def mod_top5(team_a, team_b):
    """Diferencia de densidad en ligas top-5 → ajuste pequeño en xG."""
    delta = TOP5_PLAYERS.get(team_a, TOP5_MEAN) - TOP5_PLAYERS.get(team_b, TOP5_MEAN)
    return 1.0 + delta * 0.003   # cada jugador extra en top-5: +0.3%

# A4 — Experiencia mundialista [HEURÍSTICA]
def mod_wc_experience(team):
    apps = WC_APPEARANCES.get(team, 0)
    if team in DEBUTANTS:
        return 1.0   # ya penalizado por mod_debut
    if apps >= 15:   return 1.02   # tradición fuerte
    if apps >= 8:    return 1.01
    if apps >= 4:    return 1.00
    if apps >= 1:    return 0.99   # poca experiencia
    return 1.0

# A5 — Calidad portero: afecta xG concedido por el equipo [HEURÍSTICA]
def mod_portero_defensivo(team):
    """Retorna el multiplicador sobre los goles que ese equipo concede.
    GK rating 9.5 → concede 8% menos que la mediana.
    GK rating 6.5 → concede 4% más."""
    gk = GK_QUALITY.get(team, GK_BASELINE)
    return 1.0 - (gk - GK_BASELINE) * 0.04

# A6 — Calidad/experiencia del entrenador [HEURÍSTICA — efecto pequeño]
COACH_MOD = {
    # Solo entrenadores con impacto verificable vía trayectoria WC
    "France":1.01,    # Deschamps: 2 WC finales, 1 título
    "Argentina":1.01, # Scaloni: campeón 2022
    "Germany":1.00,   # Nagelsmann: talentoso pero sin WC como HC
    "Brazil":0.99,    # Ancelotti: debut como técnico de Brasil en WC
    "Portugal":1.00,  # R. Martínez: Euros con Bélgica
}

# B11 — Balón parado [HEURÍSTICA]
def mod_balon_parado_atk(team):
    return SET_PIECE_ATK.get(team, 1.0)

def mod_balon_parado_def(team):
    return SET_PIECE_DEF.get(team, 1.0)

# C15 — Fatiga acumulada de temporada de club [HEURÍSTICA]
def mod_fatiga_club(team):
    return CLUB_FATIGUE.get(team, 1.0)

# C17 — Edad media × calor [EVIDENCIA parcial]
# Referencia: Mohr et al. (2012) — jugadores mayores corren menos distancia a alta
# velocidad en condiciones de calor
def mod_edad_calor(team, venue):
    wbgt = WBGT.get(venue, 20)
    if wbgt < 28:
        return 1.0
    age = AVG_AGE.get(team, AVG_AGE_MEAN)
    # Penalización: 0.8% por cada año sobre la media del torneo (27.5), en sedes WBGT>28
    heat_factor = (wbgt - 27) / 6.0  # 0 en 27°C, 1 en 33°C
    pen = max(0, age - AVG_AGE_MEAN) * 0.008 * heat_factor
    return 1.0 - pen

# D18/D19 — Descanso y distancia [EVIDENCIA: Drust et al. 2012 <96h = +30% lesiones]
def mod_viaje(team, dist_km, days_rest):
    if days_rest >= 7: return 1.0
    if dist_km < 500:   pen_dist = 0.0
    elif dist_km < 2000: pen_dist = 0.005*(dist_km-500)/500
    else:                pen_dist = 0.015+0.005*(dist_km-2000)/1000
    pen_dist = min(pen_dist, 0.04)
    rest_fac = max(0.0, 1.0-(7-days_rest)*0.1)
    return 1.0 - pen_dist*(1.0-rest_fac)

# D20 — Dirección del jet lag (este más difícil) [EVIDENCIA: Waterhouse et al. 2007]
def jetlag_direction(from_city, to_city):
    """East travel harder: circadian rhythm must advance.
    Retorna penalización adicional sobre el equipo viajero."""
    if from_city is None or to_city is None: return 0.0
    lon_from = VENUE_COORDS[from_city][1]
    lon_to   = VENUE_COORDS[to_city][1]
    delta_lon = lon_to - lon_from
    # Normalizar a -180..+180
    if delta_lon > 180:  delta_lon -= 360
    if delta_lon < -180: delta_lon += 360
    if delta_lon > 10:   return 0.015   # viaje este: -1.5%
    if delta_lon < -10:  return 0.005   # viaje oeste: -0.5%
    return 0.0

# D21/E25-E27 — Calor + horario [EVIDENCIA: Mohr et al. WC2014 WBGT>28°C]
def mod_calor_wbgt(team, venue, hora):
    """
    Penalización basada en WBGT y horario.
    Mohr et al.: WBGT>28°C → -10% sprints, -25m/min para equipos no adaptados.
    Aquí lo traducimos a ~-7% en xG para equipos de clima frío.
    Partidos antes de 15h local: penalización x1.4 (pico de calor).
    """
    wbgt = WBGT.get(venue, 20)
    if wbgt < 28:
        return 1.0
    # Equipos habituados al calor: sin penalización
    if team in EQUIPOS_CALOR:
        return 1.0
    # Magnitud base proporcional a WBGT sobre 28°C
    base_pen = 0.035 * (wbgt - 27) / 4.0   # 3.5% por cada 4°C sobre 27
    base_pen = min(base_pen, 0.07)
    # Amplificación si el partido es matutino
    time_mult = 1.4 if hora <= 14 else 1.0
    total_pen = base_pen * time_mult
    # Equipos de clima frío: doble sensibilidad
    if team in EQUIPOS_FRIO:
        total_pen *= 1.5
    return 1.0 - min(total_pen, 0.10)

# E23/E24 — Altitud y días de aclimatación — [EVIDENCIA: McSharry 2007]
# McSharry: +0.45 goles/1000m diferencia para equipo local de altura
# Aquí usamos la penalización fisiológica sobre el visitante no aclimatado
def mod_altitud(team, venue):
    alt = ALTITUD.get(venue, 0)
    if team in EQUIPOS_ALTURA:   return 1.0
    if team in EQUIPOS_ALTURA_MEDIA:
        return 1.0 if alt < 2000 else 0.98
    # Penalización basada en McSharry: ~-0.45 goles/1000m → ~-0.45/1.35 por equipo
    # En CDMX 2240m: -(0.45*2.24)/2 /1.35 ≈ -9% por equipo no aclimatado
    if alt >= 2000: return 0.91
    if alt >= 1400: return 0.96
    return 1.0

# E28 — Tipo de césped/techo [HEURÍSTICA — efecto mínimo con césped híbrido]
# No se implementa como modificador: todos los estadios WC2026 tienen césped
# híbrido o natural FIFA-certificado. Metros bajo techo (Atlanta, Vancouver)
# reducen lluvia pero no afectan xG de forma medible. NOTA INFORMATIVA SOLO.

# E29 — Clima del día [HEURÍSTICA — desconocido en modelo pre-partido]
# No implementable como input. Se recomienda actualizar el modelo con WBGT
# real el día del partido (dato FIFA disponible D-1).

# F30/F31 — Ventaja de local y diáspora [EVIDENCIA: Nevill & Holder 1999; Pollard 2008]
# Probabilidad local ≈ 67% en partidos decisivos. +1.5% por cada 10% más espectadores.
def mod_local(team, venue, is_host_country):
    if is_host_country:
        return 1.10  # +10% rendimiento anfitrión
    # Familiaridad sede (F33) [HEURÍSTICA]
    if venue in MLS_FAMILIARITY.get(team, set()):
        return 1.02  # jugadores de MLS con esa sede como casa
    # Diáspora
    DIASPORA = {
        "Mexico":   {"Houston","Dallas","Los Angeles","San Francisco","Kansas City"},
        "Argentina":{"Miami","New York"},
        "Brazil":   {"Miami","New York","Los Angeles"},
        "Colombia": {"Miami","New York"},
        "Ecuador":  {"Los Angeles","New York"},
    }
    if venue in DIASPORA.get(team, set()):
        return 1.03
    return 1.0

# F32 — Sesgo arbitral inducido por la multitud [EVIDENCIA: Nevill et al. 2002]
# +25% tarjetas amarillas a visitante; desaparece sin público.
# Implementado como bonus adicional para el equipo anfitrión del país sede.
def mod_sesgo_arbitral(team, venue):
    """Solo aplica al país anfitrión jugando en sus propias sedes."""
    if venue in HOST_CITIES.get(team, set()):
        return 1.015  # 1.5% adicional = efecto de sesgo arbitral crowd-induced
    return 1.0

# C/D — Debut y retorno largo
def mod_debut(team, match_day):
    if team in DEBUTANTS:
        return {1:0.92, 2:0.96, 3:1.00}.get(match_day, 1.0)
    if team in LONG_ABSENCE:
        return {1:0.96, 2:0.98, 3:1.00}.get(match_day, 1.0)
    return 1.0

# B7/B8 — Forma reciente y clasificatorio
def mod_qual(team):
    qdiff = QUAL_DIFF.get(team, 0.5)
    return 1.0 + 0.02*(qdiff - 0.8)

# H37 — Rotación J3 [HEURÍSTICA con algo de respaldo empírico]
def mod_rotation(team, match_id):
    return 1.0 - ROTATION_RISK_J3.get((team, match_id), 0.0)

# ============================================================================
# SECCIÓN 8 — LOGÍSTICA: ITINERARIO DE VIAJE Y JET LAG
# ============================================================================

def build_travel_map():
    date_map = {l:d for d,l in enumerate([
        "11-Jun","12-Jun","13-Jun","14-Jun","15-Jun","16-Jun","17-Jun",
        "18-Jun","19-Jun","20-Jun","21-Jun","22-Jun","23-Jun","24-Jun",
        "25-Jun","26-Jun","27-Jun"
    ])}
    team_matches = {}
    for row in FIXTURE:
        mid,fecha,venue,local,visit,grupo,hora,jl,jv = row
        for team,j in [(local,jl),(visit,jv)]:
            team_matches.setdefault(team,[]).append((date_map[fecha],venue,mid))

    travel = {}
    for team,matches in team_matches.items():
        ms = sorted(matches, key=lambda x:x[0])
        for i in range(1,len(ms)):
            pd,pv,_ = ms[i-1]; cd,cv,cm = ms[i]
            c1,c2 = VENUE_COORDS[pv], VENUE_COORDS[cv]
            dist = haversine_km(c1[0],c1[1],c2[0],c2[1])
            days = cd-pd
            jl_dir = jetlag_direction(pv,cv)
            travel[(team,cm)] = (dist, days, jl_dir, pv)
    return travel

# ============================================================================
# SECCIÓN 9 — FIXTURE (72 PARTIDOS)
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

TRAVEL_MAP = build_travel_map()

def is_host(team, venue):
    return venue in HOST_CITIES.get(team, set())

# ============================================================================
# SECCIÓN 10 — MODELO xG
# ============================================================================

BASE_LAMBDA = 1.35

def elo_ratio(ea, eb):
    p = 1/(1+10**(-(ea-eb)/400))
    return (p/(1-p))**0.5

def calc_xg_all_mods(local, visit, venue, hora, mid, j_l, j_v):
    """Calcula (xg_local, xg_visit) aplicando TODOS los modificadores."""
    ea = effective_strength(local)
    eb = effective_strength(visit)
    rl = elo_ratio(ea, eb); rv = elo_ratio(eb, ea)
    xg_l = BASE_LAMBDA*2*rl/(rl+rv)
    xg_v = BASE_LAMBDA*2*rv/(rl+rv)

    # --- H2H (B12) ---
    h2h_l, h2h_v = get_h2h(local, visit)

    # --- Viaje y jet lag (D19, D20) ---
    tl = TRAVEL_MAP.get((local,  mid), (0, 99, 0.0, None))
    tv = TRAVEL_MAP.get((visit, mid), (0, 99, 0.0, None))
    dist_l, rest_l, jlag_l, _ = tl
    dist_v, rest_v, jlag_v, _ = tv

    host_l = is_host(local,  venue)
    host_v = is_host(visit, venue)

    # Modificadores ATACANTES (afectan al xG propio)
    def atk_mods(team, dist, rest, jlag, j_day, host):
        return (
            mod_altitud(team, venue)
            * mod_calor_wbgt(team, venue, hora)
            * mod_local(team, venue, host)
            * mod_sesgo_arbitral(team, venue)     # F32
            * FORMA.get(team, 1.0)
            * mod_debut(team, j_day)
            * mod_viaje(team, dist, rest)
            * (1.0 - jlag)                         # D20
            * mod_qual(team)
            * mod_wc_experience(team)              # A4
            * COACH_MOD.get(team, 1.0)             # A6
            * mod_balon_parado_atk(team)           # B11 ofensivo
            * mod_fatiga_club(team)                # C15
            * mod_edad_calor(team, venue)          # C17
            * mod_rotation(team, mid)              # H37
            * mod_top5(team, visit if team==local else local)  # A3
        )

    # Modificadores DEFENSIVOS del rival (afectan al xG que ese equipo CONCEDE)
    # El portero del equipo defensor reduce los goles que le meten
    def def_mods(team):
        return (
            mod_portero_defensivo(team)            # A5
            * mod_balon_parado_def(team)           # B11 defensivo
        )

    xg_l_final = xg_l * atk_mods(local, dist_l, rest_l, jlag_l, j_l, host_l) * h2h_l * def_mods(visit)
    xg_v_final = xg_v * atk_mods(visit, dist_v, rest_v, jlag_v, j_v, host_v) * h2h_v * def_mods(local)

    return (
        round(xg_l_final, 3), round(xg_v_final, 3),
        round(dist_l), round(dist_v), rest_l, rest_v
    )

def poisson_probs(xg_l, xg_v, max_g=8):
    p1=px=p2=0.0; best=(0,0); bp=0.0
    for gl in range(max_g+1):
        for gv in range(max_g+1):
            p=poisson.pmf(gl,xg_l)*poisson.pmf(gv,xg_v)
            if   gl>gv: p1+=p
            elif gl==gv: px+=p
            else:  p2+=p
            if p>bp: bp=p; best=(gl,gv)
    return p1,px,p2,best

def confidence_level(local, visit, p1, px, p2):
    gap = abs(effective_strength(local)-effective_strength(visit))
    p_fav = max(p1,p2)
    base = "ALTO" if gap>200 and p_fav>0.65 else ("MEDIO" if gap>100 or p_fav>0.55 else "BAJO")
    star_dep = max(
        STAR_DEPENDENCY.get(local,{}).get("factor",0),
        STAR_DEPENDENCY.get(visit,{}).get("factor",0),
    )
    if star_dep>=0.55 and base=="ALTO":  base="MEDIO*"
    elif star_dep>=0.40 and base=="MEDIO": base="BAJO*"
    return base

# ============================================================================
# SECCIÓN 11 — EJECUTAR LOS 72 PARTIDOS
# ============================================================================

results = []
for row in FIXTURE:
    mid,fecha,venue,local,visit,grupo,hora,j_l,j_v = row
    xg_l,xg_v,dist_l,dist_v,rest_l,rest_v = calc_xg_all_mods(
        local,visit,venue,hora,mid,j_l,j_v)
    p1,px,p2,sc = poisson_probs(xg_l,xg_v)
    conf = confidence_level(local,visit,p1,px,p2)

    ea,eb = effective_strength(local),effective_strength(visit)
    facs=[]
    if abs(ea-eb)>150:
        fav=local if ea>eb else visit
        facs.append(f"Elo gap {abs(ea-eb):.0f}→{fav}")
    if is_host(local,venue):  facs.append(f"Local {local}")
    if ALTITUD.get(venue,0)>=1400: facs.append(f"Altitud {ALTITUD[venue]}m")
    if WBGT.get(venue,0)>=28 and hora<=14: facs.append("WBGT calor mediodía")
    elif WBGT.get(venue,0)>=28:           facs.append("WBGT calor")
    if local in DEBUTANTS:  facs.append(f"Debut J{j_l} {local}")
    if visit in DEBUTANTS:  facs.append(f"Debut J{j_v} {visit}")
    if dist_l>1500: facs.append(f"Viaje {local} {dist_l}km")
    if dist_v>1500: facs.append(f"Viaje {visit} {dist_v}km")
    rot_l = ROTATION_RISK_J3.get((local,mid),0)
    rot_v = ROTATION_RISK_J3.get((visit,mid),0)
    if rot_l: facs.append(f"Rotación {local} J3")
    if rot_v: facs.append(f"Rotación {visit} J3")
    for t in [local,visit]:
        dep=STAR_DEPENDENCY.get(t)
        if dep: facs.append(f"Dep.★ {dep['player']}")
    if not facs: facs.append("Equilibrado")

    results.append({
        "P":mid,"Fecha":fecha,"Sede":venue,"H":hora,
        "Local":local,"Visit":visit,"G":grupo,
        "xG_L":xg_l,"xG_V":xg_v,
        "Marcador":f"{sc[0]}-{sc[1]}",
        "P(1)":round(p1,3),"P(X)":round(px,3),"P(2)":round(p2,3),
        "Conf":conf,"km_L":dist_l,"km_V":dist_v,
        "Factores":" | ".join(facs[:5]),
    })

df = pd.DataFrame(results)

# ============================================================================
# SECCIÓN 12 — SIMULACIÓN MONTE CARLO (10k)
# ============================================================================

def simulate_group(g_matches, n=10_000):
    teams = list({m["Local"] for m in g_matches}|{m["Visit"] for m in g_matches})
    pts={t:0.0 for t in teams}; gf={t:0.0 for t in teams}; gc={t:0.0 for t in teams}
    for _ in range(n):
        p={t:0 for t in teams}; f={t:0 for t in teams}; c={t:0 for t in teams}
        for m in g_matches:
            l,v=m["Local"],m["Visit"]
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

print("="*70)
print("PRONÓSTICO MUNDIAL 2026 v3 — 42 variables")
print("="*70)
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
print("\n✓ CSV guardados")

# ============================================================================
# SECCIÓN 13 — TABLA RESUMEN
# ============================================================================
print("\n"+"="*90)
cols=["P","Fecha","Sede","Local","Visit","G","Marcador","P(1)","P(X)","P(2)","Conf","Factores"]
print(df[cols].to_string(index=False))

# ============================================================================
# SECCIÓN 14 — REGISTRO DE 42 VARIABLES: IMPLEMENTADAS vs LIMITACIONES
# ============================================================================
VARIABLES_DOC = """
REGISTRO DE VARIABLES — v3
============================================================
BLOQUE A — FUERZA BASE
  A1  [HEURÍSTICA+valor predictivo] Elo → composite 60%  IMPLEMENTADO
  A2  [HEURÍSTICA] TM value → composite 25%              IMPLEMENTADO
  A3  [HEURÍSTICA] Jugadores top-5 ligas                  IMPLEMENTADO (±0.3%/jugador)
  A4  [HEURÍSTICA] Experiencia mundialista                IMPLEMENTADO (±1-2%)
  A5  [HEURÍSTICA] Calidad portero                        IMPLEMENTADO (±4%/punto sobre GK 7.5)
  A6  [HEURÍSTICA] Calidad entrenador                     IMPLEMENTADO (±1%, solo top)

BLOQUE B — FORMA / CONTEXTO COMPETITIVO
  B7  [HEURÍSTICA] Forma reciente                         IMPLEMENTADO (cuali → escalar)
  B8  [HEURÍSTICA] Rendimiento clasificatorio             IMPLEMENTADO (xg proxy ±2%)
  B9  [HEURÍSTICA] Amistosos prep — absorbido en B7       NOTA
  B10 [HEURÍSTICA] Tendencia xG — proxied por B8          NOTA
  B11 [HEURÍSTICA] Eficacia balón parado                  IMPLEMENTADO (±2-3%)
  B12 [HEURÍSTICA] H2H reciente                          IMPLEMENTADO (±2-5% para pares verificados)

BLOQUE C — PLANTILLA
  C13 [HEURÍSTICA alto impacto] Lesiones                  IMPLEMENTADO (multiplicativo)
  C14 [HEURÍSTICA] Sanciones/amarillas J3                 LIMITACIÓN: sin datos pre-torneo
  C15 [HEURÍSTICA] Fatiga temporada club                  IMPLEMENTADO (-0.5 a -1.5%)
  C16 [HEURÍSTICA] Profundidad plantilla — proxied por TM  NOTA
  C17 [EVIDENCIA parcial] Edad media × calor              IMPLEMENTADO (age > 27.5 en WBGT>28)

BLOQUE D — LOGÍSTICA / CALENDARIO
  D18 [EVIDENCIA] Días de descanso (<96h)                 IMPLEMENTADO
  D19 [EVIDENCIA] Distancia viaje (Haversine)             IMPLEMENTADO
  D20 [EVIDENCIA] Jet lag dirección (este más duro)       IMPLEMENTADO (-1.5% este, -0.5% oeste)
  D21 [EVIDENCIA] Hora partido × WBGT                    IMPLEMENTADO (amplif. x1.4 si hora≤14)
  D22 [HEURÍSTICA] Orden fixture / motivación J3          IMPLEMENTADO como ROTATION_RISK_J3

BLOQUE E — ENTORNO FÍSICO
  E23 [EVIDENCIA] Altitud (McSharry 2007)                IMPLEMENTADO (−9% CDMX, −4% GDL)
  E24 [EVIDENCIA] Días aclimatación → absorbido en E23    NOTA
  E25 [EVIDENCIA] WBGT > 28°C (Mohr et al. WC2014)       IMPLEMENTADO (hasta −10%)
  E26 [EVIDENCIA] Humedad → absorbida en WBGT             IMPLEMENTADO
  E27 [EVIDENCIA] Riesgo térmico sede/hora               IMPLEMENTADO (WBGT × hora)
  E28 [HEURÍSTICA] Tipo de césped/techo                  NO IMPLEMENTADO — efecto mínimo
  E29 [HEURÍSTICA] Clima del día                         NO IMPLEMENTADO — desconocido pre-partido

BLOQUE F — LOCALÍA / ARBITRAJE
  F30 [EVIDENCIA] Ventaja de local (+10%)                IMPLEMENTADO
  F31 [EVIDENCIA] Afición desplazada (+3%)               IMPLEMENTADO
  F32 [EVIDENCIA Nevill 2002] Sesgo arbitral crowd       IMPLEMENTADO (+1.5% anfitrión)
  F33 [HEURÍSTICA] Familiaridad sede MLS/Liga MX          IMPLEMENTADO (+2%)

BLOQUE G — TÁCTICOS
  G34 [HEURÍSTICA] Choque de estilos                     NO IMPLEMENTADO — requiere datos tácticos
  G35 [HEURÍSTICA] Planteamiento J3                      PARCIAL → ROTATION_RISK_J3

BLOQUE H — PSICOLÓGICOS
  H36 [HEURÍSTICA] Presión/expectativas                  PARCIAL → absorbido en FORMA
  H37 [HEURÍSTICA] Motivación J3                         IMPLEMENTADO → ROTATION_RISK_J3
  H38 [HEURÍSTICA] Cohesión vestuario                    NO IMPLEMENTADO — no cuantificable
  H39 [HEURÍSTICA] Moral/confianza                       ABSORBIDO en FORMA

BLOQUE I — DINÁMICAS IN-GAME (no son inputs, son outputs del modelo)
  I40 [EVIDENCIA] Marcar primero                         LIMITACIÓN DECLARADA
  I41 [EVIDENCIA] Expulsiones/tarjetas                   LIMITACIÓN DECLARADA
  I42 [EVIDENCIA] Posesión/tiros/xG in-game              LIMITACIÓN DECLARADA (modelo pre-partido)

VARIABLES NO IMPLEMENTABLES SIN DATOS ADICIONALES:
  C14 (amarillas acumuladas), E28 (césped), E29 (clima día),
  G34 (choque estilos), H38 (cohesión)
============================================================
"""
print(VARIABLES_DOC)
