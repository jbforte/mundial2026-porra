"""
Generador de informe narrativo v3: por qué el modelo predice cada resultado.
Ejecutar DESPUÉS de modelo.py (importa sus variables y funciones).
Output: informe_partidos.md
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modelo import (
    FIXTURE, COMPOSITE_ELO, ELO, TM_VALUE, FORMA, LESIONES_MOD,
    QUAL_DIFF, STAR_DEPENDENCY, DEBUTANTS, LONG_ABSENCE,
    ALTITUD, WBGT, EQUIPOS_ALTURA, EQUIPOS_FRIO, EQUIPOS_CALOR,
    CHAMPIONSHIP_ODDS_USA, TRAVEL_MAP, AVG_AGE, AVG_AGE_MEAN,
    GK_QUALITY, GK_BASELINE, TOP5_PLAYERS, TOP5_MEAN,
    H2H, get_h2h, CLUB_FATIGUE, ROTATION_RISK_J3,
    WC_APPEARANCES, HOST_CITIES,
    effective_strength, calc_xg_all_mods, poisson_probs, confidence_level,
    is_host, mod_altitud, mod_calor_wbgt, mod_debut, mod_viaje,
    mod_edad_calor, odds_usa_to_prob, BASE_LAMBDA,
    # --- nuevos v4 ---
    ATK_STYLE, DEF_FRAILTY, TEMPO, VENUE_ROOF, get_effective_wbgt,
    LAST_TOURNAMENT_BOOST, COACH_TENURE, VENUE_CHANGES,
)

# ============================================================================
# HELPERS NARRATIVOS
# ============================================================================

NOMBRES_ES = {
    "Argentina":"Argentina","Spain":"España","France":"Francia",
    "England":"Inglaterra","Morocco":"Marruecos","Brazil":"Brasil",
    "Portugal":"Portugal","Netherlands":"Países Bajos","Belgium":"Bélgica",
    "Croatia":"Croacia","Colombia":"Colombia","Mexico":"México",
    "Senegal":"Senegal","Uruguay":"Uruguay","USA":"EE. UU.",
    "Japan":"Japón","Switzerland":"Suiza","Iran":"Irán",
    "Turkey":"Turquía","Ecuador":"Ecuador","Austria":"Austria",
    "South Korea":"Corea del Sur","Australia":"Australia",
    "Algeria":"Argelia","Egypt":"Egipto","Norway":"Noruega",
    "Canada":"Canadá","Ivory Coast":"Costa de Marfil","Sweden":"Suecia",
    "Czech Republic":"Chequia","Paraguay":"Paraguay","Scotland":"Escocia",
    "DR Congo":"RD Congo","Tunisia":"Túnez","Uzbekistan":"Uzbekistán",
    "Germany":"Alemania","New Zealand":"Nueva Zelanda","Qatar":"Catar",
    "South Africa":"Sudáfrica","Bosnia":"Bosnia-Herzegovina",
    "Ghana":"Ghana","Panama":"Panamá","Cape Verde":"Cabo Verde",
    "Saudi Arabia":"Arabia Saudí","Iraq":"Irak","Jordan":"Jordania",
    "Haiti":"Haití","Curacao":"Curazao",
}

SEDES_ES = {
    "Mexico City":"Ciudad de México (Azteca)","Guadalajara":"Guadalajara (Akron)",
    "Monterrey":"Monterrey (BBVA)","Atlanta":"Atlanta (Mercedes-Benz)",
    "Kansas City":"Kansas City (Arrowhead)","Dallas":"Dallas (AT&T)",
    "Houston":"Houston (NRG)","Los Angeles":"Los Ángeles (SoFi)",
    "San Francisco":"San Francisco (Levi's)","Seattle":"Seattle (Lumen Field)",
    "Vancouver":"Vancouver (BC Place)","Toronto":"Toronto (BMO Field)",
    "Boston":"Boston/Foxborough (Gillette)","Philadelphia":"Filadelfia (Lincoln Financial)",
    "New York":"Nueva York/NJ (MetLife)","Miami":"Miami (Hard Rock)",
}

def nombre(team):
    return NOMBRES_ES.get(team, team)

def sede(venue):
    return SEDES_ES.get(venue, venue)

def describe_gap(ea, eb, team_l, team_v):
    gap = ea - eb
    fav = nombre(team_l) if gap > 0 else nombre(team_v)
    und = nombre(team_v) if gap > 0 else nombre(team_l)
    abs_gap = abs(gap)
    if abs_gap < 50:
        return f"Las fuerzas compuestas son prácticamente iguales ({ea:.0f} vs {eb:.0f} pts Elo), por lo que el partido es muy abierto."
    if abs_gap < 120:
        return f"{fav} aventaja levemente a {und} en fuerza compuesta ({abs_gap:.0f} pts, {ea:.0f} vs {eb:.0f})."
    if abs_gap < 220:
        return f"{fav} es el claro favorito con una ventaja compuesta de {abs_gap:.0f} pts sobre {und}."
    return f"Hay una diferencia de nivel significativa: {fav} supera a {und} en {abs_gap:.0f} pts de Elo compuesto."

def describe_tm(team_l, team_v):
    vl = TM_VALUE.get(team_l, 50)
    vv = TM_VALUE.get(team_v, 50)
    ratio = vl / vv if vv > 0 else 1
    nl, nv = nombre(team_l), nombre(team_v)
    if ratio > 5:
        return f"En valor de plantilla la diferencia es abismal: {nl} (€{vl:.0f}M) frente a {nv} (€{vv:.0f}M)."
    if ratio > 2.5:
        return f"La plantilla de {nl} (€{vl:.0f}M) es claramente más valiosa que la de {nv} (€{vv:.0f}M)."
    if ratio > 1.4:
        return f"{nl} (€{vl:.0f}M) tiene mayor profundidad de plantel que {nv} (€{vv:.0f}M)."
    if abs(ratio - 1) < 0.2:
        return f"Los valores de plantilla son equiparables: {nl} €{vl:.0f}M vs {nv} €{vv:.0f}M."
    larger  = nl if vl > vv else nv
    smaller = nv if vl > vv else nl
    return f"{larger} supera en valor de plantilla a {smaller} (€{max(vl,vv):.0f}M vs €{min(vl,vv):.0f}M)."

def describe_mercado(team_l, team_v):
    partes = []
    for team in [team_l, team_v]:
        odds = CHAMPIONSHIP_ODDS_USA.get(team)
        if odds:
            p = odds_usa_to_prob(odds) * 100
            partes.append(f"{nombre(team)} con {p:.1f}% de ganar el torneo según el mercado")
    return ". ".join(partes) + "." if partes else None

def describe_altitud(team_l, team_v, venue):
    alt = ALTITUD.get(venue, 0)
    if alt < 1400:
        return None
    mod_l = mod_altitud(team_l, venue)
    mod_v = mod_altitud(team_v, venue)
    partes = []
    for team, mod in [(team_l, mod_l), (team_v, mod_v)]:
        if mod < 0.99:
            partes.append(f"{nombre(team)} no adaptado (−{(1-mod)*100:.0f}%)")
        else:
            partes.append(f"{nombre(team)} habituado a la altura")
    if mod_l < 0.99 and mod_v < 0.99:
        return f"Altitud {sede(venue)} ({alt}m): penaliza a ambos — " + ", ".join(partes) + "."
    return f"Altitud {sede(venue)} ({alt}m): " + "; ".join(partes) + "."

def describe_calor(team_l, team_v, venue, hora):
    wbgt = WBGT.get(venue, 20)
    if wbgt < 28:
        return None
    partes = []
    for team in [team_l, team_v]:
        if team in EQUIPOS_FRIO:
            mod = mod_calor_wbgt(team, venue, hora)
            pen = (1 - mod) * 100
            momento = "a pleno mediodía" if hora <= 14 else "por la tarde"
            partes.append(f"{nombre(team)} (clima frío) acusa el WBGT de {wbgt}°C {momento}: −{pen:.0f}%")
        elif team not in EQUIPOS_CALOR:
            mod = mod_calor_wbgt(team, venue, hora)
            pen = (1 - mod) * 100
            if pen > 0.5:
                partes.append(f"{nombre(team)} penalizado levemente por calor: −{pen:.0f}%")
    if not partes:
        return f"El calor de {sede(venue)} (WBGT≈{wbgt}°C) no penaliza significativamente a ninguno de los dos."
    return "Calor: " + "; ".join(partes) + "."

def describe_edad_calor(team_l, team_v, venue):
    """Penalización por edad media alta en sedes calurosas."""
    wbgt = WBGT.get(venue, 20)
    if wbgt < 28:
        return None
    partes = []
    for team in [team_l, team_v]:
        age = AVG_AGE.get(team, AVG_AGE_MEAN)
        if age > AVG_AGE_MEAN + 0.5:
            mod = mod_edad_calor(team, venue)
            pen = (1 - mod) * 100
            if pen > 0.2:
                partes.append(
                    f"{nombre(team)} (edad media {age:.1f} años, +{age-AVG_AGE_MEAN:.1f} sobre la media del torneo) "
                    f"sufre penalización adicional por calor: −{pen:.1f}%"
                )
    return "Edad×calor: " + "; ".join(partes) + "." if partes else None

def describe_portero(team_l, team_v):
    """Diferencia de calidad en el puesto de portero."""
    gk_l = GK_QUALITY.get(team_l, GK_BASELINE)
    gk_v = GK_QUALITY.get(team_v, GK_BASELINE)
    diff = abs(gk_l - gk_v)
    if diff < 0.8:
        return None
    if gk_l > gk_v:
        mejor, peor = nombre(team_l), nombre(team_v)
        rating_mejor, rating_peor = gk_l, gk_v
    else:
        mejor, peor = nombre(team_v), nombre(team_l)
        rating_mejor, rating_peor = gk_v, gk_l
    pen_peor = (rating_peor - GK_BASELINE) * (-0.04) * 100
    return (
        f"Portería: {mejor} tiene el guardameta superior ({rating_mejor:.1f}/10 vs {rating_peor:.1f}/10), "
        f"lo que reduce los goles que encaja en ~{abs(pen_peor):.0f}% frente a la mediana."
    )

def describe_top5(team_l, team_v):
    """Ventaja en densidad de ligas top-5."""
    t5_l = TOP5_PLAYERS.get(team_l, TOP5_MEAN)
    t5_v = TOP5_PLAYERS.get(team_v, TOP5_MEAN)
    diff = abs(t5_l - t5_v)
    if diff < 5:
        return None
    mayor = nombre(team_l) if t5_l > t5_v else nombre(team_v)
    n_mayor = max(t5_l, t5_v)
    n_menor = min(t5_l, t5_v)
    return (
        f"Exposición a ligas élite: {mayor} lleva {n_mayor:.0f} jugadores de top-5 ligas "
        f"vs {n_menor:.0f} del rival, ventaja de calidad táctica y competitiva."
    )

def describe_h2h(team_l, team_v):
    """H2H reciente si hay datos verificados."""
    mod_l, mod_v = get_h2h(team_l, team_v)
    if mod_l == 1.0 and mod_v == 1.0:
        return None
    if mod_l > mod_v:
        fav, und = nombre(team_l), nombre(team_v)
        edge = (mod_l - 1.0) * 100
    else:
        fav, und = nombre(team_v), nombre(team_l)
        edge = (mod_v - 1.0) * 100
    return f"H2H reciente: {fav} ha tenido mejores resultados contra {und} en los últimos 3 años (+{edge:.0f}% en el modelo)."

def describe_fatiga(team_l, team_v):
    """Fatiga por temporada larga de club."""
    partes = []
    for team in [team_l, team_v]:
        fat = CLUB_FATIGUE.get(team, 1.0)
        if fat < 0.995:
            pen = (1 - fat) * 100
            partes.append(f"{nombre(team)} llega con fatiga acumulada de temporada de club (−{pen:.1f}%)")
    return "; ".join(partes) + "." if partes else None

def describe_wc_exp(team_l, team_v):
    """Contraste de experiencia mundialista."""
    apps_l = WC_APPEARANCES.get(team_l, 0)
    apps_v = WC_APPEARANCES.get(team_v, 0)
    if abs(apps_l - apps_v) < 5:
        return None
    mayor = nombre(team_l) if apps_l > apps_v else nombre(team_v)
    n_mayor = max(apps_l, apps_v)
    menor  = nombre(team_v) if apps_l > apps_v else nombre(team_l)
    n_menor = min(apps_l, apps_v)
    return f"Experiencia mundialista: {mayor} ({n_mayor} Mundiales) vs {menor} ({n_menor}); la veteranía da una ventaja menor pero real."

def describe_viaje(team_l, team_v, match_id):
    partes = []
    for team in [team_l, team_v]:
        data = TRAVEL_MAP.get((team, match_id), (0, 99, 0.0, None))
        dist, days, jlag, _ = data
        if dist > 800:
            pen = (1 - mod_viaje(team, dist, days)) * 100
            txt = f"{nombre(team)} viajó {dist:.0f} km desde su partido anterior"
            if pen > 0.5:
                txt += f" (−{pen:.1f}%)"
            if jlag > 0.005:
                txt += f", jet lag dirección este (−{jlag*100:.1f}% adicional)"
            partes.append(txt)
    return "Desplazamiento: " + "; ".join(partes) + "." if partes else None

def describe_debut(team_l, team_v, j_l, j_v):
    partes = []
    for team, jday in [(team_l, j_l), (team_v, j_v)]:
        if team in DEBUTANTS:
            pen = (1 - mod_debut(team, jday)) * 100
            partes.append(f"{nombre(team)} debuta en el Mundial (−{pen:.0f}% J{jday})")
        elif team in LONG_ABSENCE:
            pen = (1 - mod_debut(team, jday)) * 100
            partes.append(f"{nombre(team)} vuelve al Mundial tras +40 años ausente (−{pen:.0f}% J{jday})")
    return "; ".join(partes) + "." if partes else None

def describe_lesiones(team_l, team_v):
    BAJAS = {
        "Brazil":      "Rodrygo y Estevão fuera, Neymar y Militão dudosos",
        "Netherlands": "Xavi Simons OUT (ligamento cruzado)",
        "Germany":     "Lennart Karl reemplazado antes del torneo",
        "Scotland":    "Billy Gilmour OUT (convocatoria final)",
    }
    partes = []
    for team in [team_l, team_v]:
        mod = LESIONES_MOD.get(team, 1.0)
        if mod < 1.0:
            partes.append(f"{nombre(team)} mermado: {BAJAS.get(team,'baja importante')}")
    return ". ".join(partes) + "." if partes else None

def describe_estrella(team_l, team_v):
    partes = []
    for team in [team_l, team_v]:
        dep = STAR_DEPENDENCY.get(team)
        if dep:
            partes.append(
                f"{nombre(team)} depende de {dep['player']} "
                f"({dep['factor']*100:.0f}% del juego creativo) — amplía la varianza"
            )
    return "; ".join(partes) + "." if partes else None

def describe_local(team, venue):
    if is_host(team, venue):
        return f"{nombre(team)} juega como anfitrión en su propio país (+10% estimado)."
    DIASPORA = {
        "Mexico":    {"Houston","Dallas","Los Angeles","San Francisco","Kansas City"},
        "Argentina": {"Miami","New York"},
        "Brazil":    {"Miami","New York","Los Angeles"},
        "Colombia":  {"Miami","New York"},
        "Ecuador":   {"Los Angeles","New York"},
    }
    if venue in DIASPORA.get(team, set()):
        return f"{nombre(team)} tendrá gran apoyo de su diáspora en {sede(venue)} (+3%)."
    return None

def describe_rotation(team_l, team_v, match_id):
    partes = []
    for team in [team_l, team_v]:
        rot = ROTATION_RISK_J3.get((team, match_id), 0)
        if rot > 0:
            partes.append(f"{nombre(team)} probablemente rotará su once en este J3 al tener la clasificación virtualmente resuelta (−{rot*100:.0f}%)")
    return "; ".join(partes) + "." if partes else None

# --- NUEVAS NARRATIVAS v4 ---

def describe_perfil_tactico(team_l, team_v):
    """V47/V48/V51/V52/V67 — estilo ataque-defensa y ritmo del partido."""
    partes = []
    for team in [team_l, team_v]:
        atk = ATK_STYLE.get(team, 1.0)
        dfr = DEF_FRAILTY.get(team, 1.0)
        if atk >= 1.03:
            partes.append(f"{nombre(team)} tiene un perfil muy ofensivo (genera +{(atk-1)*100:.0f}% de ocasiones)")
        elif atk <= 0.97:
            partes.append(f"{nombre(team)} es pragmático y produce poco en ataque ({(atk-1)*100:.0f}%)")
        if dfr <= 0.96:
            partes.append(f"{nombre(team)} defiende con una línea muy sólida (concede −{(1-dfr)*100:.0f}%)")
        elif dfr >= 1.04:
            partes.append(f"{nombre(team)} es frágil atrás (concede +{(dfr-1)*100:.0f}%)")
    tempo = (TEMPO.get(team_l,1.0) * TEMPO.get(team_v,1.0)) ** 0.5
    if tempo >= 1.015:
        partes.append("ritmo alto: se espera un partido abierto y con goles")
    elif tempo <= 0.985:
        partes.append("ritmo bajo: choque cerrado, pocos goles esperados")
    return "Perfil táctico: " + "; ".join(partes) + "." if partes else None

def describe_calor_techo(team_l, team_v, venue, hora):
    """V89 — techo retráctil que mitiga el calor."""
    raw = WBGT.get(venue, 20)
    eff = get_effective_wbgt(venue, hora)
    if raw >= 28 and eff < 28:
        roof = VENUE_ROOF.get(venue)
        if roof == "retractable_ac":
            return f"El calor de {sede(venue)} (WBGT crudo {raw:.0f}°C) queda neutralizado: estadio con techo retráctil y aire acondicionado (WBGT efectivo {eff:.0f}°C)."
        if roof == "fixed_canopy":
            return f"El techo fijo de {sede(venue)} alivia parcialmente el calor (WBGT {raw:.0f}→{eff:.0f}°C)."
    return None

def describe_momentum_dt(team_l, team_v):
    """V100/V103 — momentum del último torneo y continuidad del seleccionador."""
    partes = []
    for team in [team_l, team_v]:
        boost = LAST_TOURNAMENT_BOOST.get(team, 1.0)
        if boost >= 1.01:
            partes.append(f"{nombre(team)} llega con inercia positiva de su último gran torneo (+{(boost-1)*100:.1f}%)")
        elif boost <= 0.996:
            partes.append(f"{nombre(team)} arrastra un ciclo en declive ({(boost-1)*100:.1f}%)")
        yrs = COACH_TENURE.get(team)
        if yrs is not None and yrs >= 6:
            partes.append(f"{nombre(team)} mantiene al mismo seleccionador desde hace {yrs} años (automatismos consolidados)")
        elif yrs is not None and yrs <= 1:
            partes.append(f"{nombre(team)} estrena proyecto con un técnico recién llegado (incertidumbre)")
    return "; ".join(partes) + "." if partes else None

def describe_dif_logistica(team_l, team_v, match_id):
    """V82/V83/V85 — diferencial de descanso/viaje y cambios de sede."""
    data_l = TRAVEL_MAP.get((team_l, match_id), (0, 99, 0.0, None))
    data_v = TRAVEL_MAP.get((team_v, match_id), (0, 99, 0.0, None))
    dist_l, rest_l = data_l[0], data_l[1]
    dist_v, rest_v = data_v[0], data_v[1]
    partes = []
    if rest_l - rest_v <= -2:
        partes.append(f"{nombre(team_l)} llega con {rest_v-rest_l} día(s) menos de descanso que su rival")
    elif rest_v - rest_l <= -2:
        partes.append(f"{nombre(team_v)} llega con {rest_l-rest_v} día(s) menos de descanso que su rival")
    if dist_l - dist_v >= 1500:
        partes.append(f"{nombre(team_l)} ha viajado {dist_l-dist_v:.0f} km más que su rival")
    elif dist_v - dist_l >= 1500:
        partes.append(f"{nombre(team_v)} ha viajado {dist_v-dist_l:.0f} km más que su rival")
    return "Logística diferencial: " + "; ".join(partes) + "." if partes else None

def describe_forma(team_l, team_v):
    partes = []
    for team in [team_l, team_v]:
        f = FORMA.get(team, 1.0)
        qdiff = QUAL_DIFF.get(team, 0.5)
        if f >= 1.03:
            partes.append(f"{nombre(team)} llega en excelente forma ({f:.2f}×, +{qdiff:.1f} g/p en clasificatorio)")
        elif f <= 0.97:
            partes.append(f"{nombre(team)} muestra irregularidades recientes (mod. {f:.2f}×)")
    return "; ".join(partes) + "." if partes else None

def describe_resultado(p1, px, p2, sc, team_l, team_v):
    fav_name = nombre(team_l) if p1 > p2 else nombre(team_v)
    p_fav    = max(p1, p2) * 100
    p_draw   = px * 100
    nl, nv   = nombre(team_l), nombre(team_v)
    resultado = f"{sc[0]}-{sc[1]}"
    if p_fav >= 80:
        intro = f"El modelo es muy claro: **{fav_name} gana** con una probabilidad del {p_fav:.0f}%."
    elif p_fav >= 65:
        intro = f"**{fav_name}** es el favorito sólido con un {p_fav:.0f}% de probabilidad de victoria."
    elif p_fav >= 55:
        intro = f"**{fav_name}** tiene ventaja, aunque el partido es competido ({p_fav:.0f}% de ganar)."
    else:
        intro = f"El encuentro está muy igualado. Ningún equipo supera el {p_fav:.0f}% de probabilidad."
    marcador_txt = (
        f"El marcador más probable es **{nl} {resultado} {nv}** "
        f"(P victoria {nl}: {p1*100:.0f}%, empate: {p_draw:.0f}%, victoria {nv}: {p2*100:.0f}%)."
    )
    return intro + " " + marcador_txt

def confianza_texto(conf):
    mapa = {
        "ALTO":   "🟢 Alta confianza — diferencia de nivel clara; factores de contexto confirman al favorito.",
        "MEDIO":  "🟡 Confianza media — favorito identificable, pero con incertidumbre real.",
        "BAJO":   "🔴 Baja confianza — partido muy igualado; cualquier resultado es plausible.",
        "MEDIO*": "🟡⚠️ Confianza media — hay favorito, pero la dependencia de una estrella amplía la varianza.",
        "BAJO*":  "🔴⚠️ Baja confianza — partido abierto y con alta dependencia de un jugador clave.",
    }
    return mapa.get(conf, conf)

# ============================================================================
# GENERAR INFORME COMPLETO
# ============================================================================

lineas = [
    "# Informe narrativo: pronóstico de los 72 partidos — Mundial 2026",
    "",
    "> Generado el 2026-06-08 con modelo Poisson **v5** (las 60 variables de v4 + total de goles dinámico que recupera las goleadas; las 42 originales + descomposición ataque/defensa, ritmo de goles, diferenciales logísticos, techo→WBGT efectivo, altura, cohesión, momentum y continuidad del seleccionador).",
    "> Los porcentajes son estimaciones probabilísticas, no certezas.",
    "",
    "---",
    "",
]

grupos_partidos = {}
for row in FIXTURE:
    grupos_partidos.setdefault(row[5], []).append(row)

for g in sorted(grupos_partidos):
    equipos_grupo = set()
    for row in grupos_partidos[g]:
        equipos_grupo.add(row[3]); equipos_grupo.add(row[4])
    nombres_grupo = " · ".join(nombre(t) for t in sorted(equipos_grupo))
    lineas += [f"## GRUPO {g} — {nombres_grupo}", ""]

    for row in grupos_partidos[g]:
        mid, fecha, venue, local, visit, grupo, hora, j_l, j_v = row

        xg_l, xg_v, dist_l, dist_v, rest_l, rest_v = calc_xg_all_mods(
            local, visit, venue, hora, mid, j_l, j_v)
        p1, px, p2, sc = poisson_probs(xg_l, xg_v)
        ea = effective_strength(local)
        eb = effective_strength(visit)
        conf = confidence_level(local, visit, p1, px, p2)
        nl, nv = nombre(local), nombre(visit)

        lineas += [
            f"### Partido {mid} · {fecha} · J{j_l} — {nl} vs {nv}",
            f"**Sede:** {sede(venue)} (altitud {ALTITUD.get(venue,0)}m, WBGT≈{WBGT.get(venue,0)}°C) · **Hora local:** {hora:02d}:00",
            "",
            "#### Análisis de fuerzas",
        ]

        lineas.append(describe_gap(ea, eb, local, visit))
        lineas.append(describe_tm(local, visit))
        mkt = describe_mercado(local, visit)
        if mkt: lineas.append(mkt)
        forma_txt = describe_forma(local, visit)
        if forma_txt: lineas.append(forma_txt)
        top5_txt = describe_top5(local, visit)
        if top5_txt: lineas.append(top5_txt)
        wc_txt = describe_wc_exp(local, visit)
        if wc_txt: lineas.append(wc_txt)
        les = describe_lesiones(local, visit)
        if les: lineas.append(f"**Bajas:** {les}")
        fat = describe_fatiga(local, visit)
        if fat: lineas.append(f"**Fatiga de club:** {fat}")

        lineas.append("")
        lineas.append("#### Factores de contexto")

        any_factor = False
        for fn, args in [
            (describe_local,       (local,  venue)),
            (describe_local,       (visit,  venue)),
            (describe_altitud,     (local, visit, venue)),
            (describe_calor,       (local, visit, venue, hora)),
            (describe_edad_calor,  (local, visit, venue)),
            (describe_portero,     (local, visit)),
            (describe_h2h,         (local, visit)),
            (describe_viaje,       (local, visit, mid)),
            (describe_debut,       (local, visit, j_l, j_v)),
            (describe_rotation,    (local, visit, mid)),
            (describe_estrella,    (local, visit)),
            # --- nuevos v4 ---
            (describe_perfil_tactico, (local, visit)),
            (describe_calor_techo,    (local, visit, venue, hora)),
            (describe_dif_logistica,  (local, visit, mid)),
            (describe_momentum_dt,    (local, visit)),
        ]:
            txt = fn(*args)
            if txt:
                lineas.append(f"- {txt}")
                any_factor = True

        if not any_factor:
            lineas.append("- No hay factores de contexto relevantes. El resultado depende casi exclusivamente de la fuerza relativa.")

        lineas.append("")
        lineas.append("#### Pronóstico")
        lineas.append(describe_resultado(p1, px, p2, sc, local, visit))
        lineas.append(f"> xG: {nl} {xg_l:.2f} — {nv} {xg_v:.2f}")
        lineas.append("")
        lineas.append(f"**Confianza:** {confianza_texto(conf)}")
        lineas.append("")
        lineas.append("---")
        lineas.append("")

output_path = "informe_partidos.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lineas))

print(f"✓ {output_path} generado ({len(lineas)} líneas)")
print("  Abre con VS Code, Obsidian o Typora")
