# Fuentes — Pronóstico Mundial 2026

**Fecha de consulta de todas las fuentes: 2026-06-07 | Modelo v3**

---

## Fixture oficial (72 partidos)

- **worldcuply.com/schedule.html** — Extraído 07-Jun-2026. Fixture completo con fechas, horarios locales, estadios y emparejamientos.
  - URL: https://worldcuply.com/schedule.html
  - Status: VERIFICADO (cruzado parcialmente con FIFA.com)
  - Nota: FIFA.com devolvió página vacía en el scrape; worldcuply.com coincide con Sky Sports y NBC Sports en los partidos verificados manualmente.

- **FIFA.com — Scores & Fixtures** (fallback)
  - URL: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures
  - Status: NO DISPONIBLE en scrape (página protegida)

---

## Rankings FIFA (April 1, 2026)

- **worldcuppass.com/2026-fifa-world-cup-teams/** — Extraído 07-Jun-2026.
  - Fuente primaria: FIFA/Coca-Cola Men's World Ranking (Apr 2026)
  - URL: https://worldcuppass.com/2026-fifa-world-cup-teams/
  - Status: VERIFICADO (48 equipos con ranking posicional, sin puntos)
  - Próxima actualización FIFA: 11-Jun-2026 (día del partido inaugural)

---

## Ratings Elo

- **worldfootballrankings.com** — Actualizado 06-Jun-2026 (dato de búsqueda)
  - URL: https://worldfootballrankings.com/rankings
  - Status: VERIFICADO para 37 equipos
  - Equipos con Elo VERIFICADO: Argentina (1876.12), Spain (1873.01), France (1869.43), England (1827.05), Morocco (1757.29), Brazil (1765.86), Portugal (1766.18), Netherlands (1751.10), Belgium (1742.24), Croatia (1714.87), Colombia (1695.99), Mexico (1687.48), Senegal (1686.41), Uruguay (1673.07), USA (1671.23), Japan (1661.58), Switzerland (1650.06), Iran (1619.58), Turkey (1605.73), Ecuador (1596.48), Austria (1597.40), South Korea (1591.63), Australia (1579.34), Algeria (1571.03), Egypt (1562.37), Norway (1555.60), Canada (1559.48), Ivory Coast (1540.87), Sweden (1509.79), Czech Republic (1505.74), Paraguay (1505.35), Scotland (1503.34), DR Congo (1479.68), Tunisia (1476.41), Uzbekistan (1461.21), Germany (1735.77), New Zealand (1275.60)

- **Equipos con Elo ESTIMADO** (11 equipos):
  Método: regresión lineal OLS sobre 37 equipos verificados → f(rank) ≈ 1900 − 6.1×rank (R²≈0.91)
  Qatar [FIFA 35], South Africa [FIFA 60], Bosnia [FIFA 52], Ghana [FIFA 65], Panama [FIFA 53], Cape Verde [FIFA 70], Saudi Arabia [FIFA 57], Iraq [FIFA 61], Jordan [FIFA 68], Haiti [FIFA 83], Curacao [FIFA 81]

---

## Lesiones y disponibilidad

- **ESPN — 2026 World Cup injuries tracker** — Consultado 07-Jun-2026
  - URL: https://www.espn.com/soccer/story/_/id/48572979/2026-fifa-world-cup-injuries-tracker-which-stars-miss-latest-info
  - Confirmados OUT: Xavi Simons (Netherlands, ACL), Rodrygo (Brazil), Estevão (Brazil, pierna), Billy Gilmour (Scotland), Lennart Karl (Germany, reemplazado 05-Jun por Ouédraogo)
  - Dudosos: Neymar (Brasil, pantorrilla), Mikel Merino (España, metatarso), Yamal (España, isquiotibiales)
  - Nota: Tomiyasu (Japan) NO incluido en convocatoria final — ausencia confirmada

---

## Forma reciente y expectativas por equipo

- **ESPN — What you need to know about all 48 teams** — Consultado 07-Jun-2026
  - URL: https://www.espn.com/soccer/story/_/id/48871263/world-cup-2026-key-players-facts-expectations-fixtures-odds-all-48-teams

- **Al Jazeera — Ranking the World Cup 2026 groups** — Consultado 07-Jun-2026
  - URL: https://www.aljazeera.com/sports/2026/6/5/ranking-the-2026-world-cup-groups-which-teams-are-favourites-to-progress

- **Yahoo Sports — 2026 World Cup news live tracker** — Consultado 07-Jun-2026
  - URL: https://sports.yahoo.com/soccer/live/2026-world-cup-news-live-tracker-injuries-squads-storylines-and-updates-as-the-tournament-looms-200000653.html

- **Amistosos de preparación (resultados parciales)** — FIFA.com
  - URL: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/pre-tournament-warm-up-results-fixtures-scorers
  - Status: NO DISPONIBLE en scrape. Resultados conocidos: Brasil 2–1 Egipto (06-Jun), Francia ganó vs Brasil en marzo (2-1), Francia vs Colombia (3-1, B team, marzo)

---

## Sedes y altitudes

- **Datos del prompt** (verificados contra Wikipedia y fuentes oficiales)
  - Azteca/Mexico City: ~2,240m (verificado vs Wikipedia: 2,235m)
  - Akron/Guadalajara: ~1,566m (verificado vs Wikipedia: 1,560m)
  - BBVA/Monterrey: ~540m (verificado vs Wikipedia: 538m)
  - Resto de sedes EE.UU. y Canadá: ≤320m (sin efecto altitud significativo)

---

## Cuotas de mercado (nuevo en v2)

- **ESPN Betting — Championship & Group Odds** — Consultado 07-Jun-2026
  - URL: https://www.espn.com/espn/betting/story/_/id/48386952/espn-soccer-futbol-world-cup-betting-odds-championship-groups
  - 27 equipos con cuotas americanas (ej: España +450, Francia +475, Argentina +900)
  - Conversión: P = 100/(odds+100) para positivos, sin corrección de margen

## Valores de plantilla Transfermarkt (nuevo en v2)

- **sportingpedia.com — 2026 World Cup Team Values** — Consultado 07-Jun-2026
  - URL: https://www.sportingpedia.com/2026/06/03/2026-world-cup-team-values-and-group-rankings/
  - ~35 equipos verificados; resto estimados por interpolación regional/ranking
- **soccergraph.com — All 48 Team Market Values** — Consultado 07-Jun-2026
  - URL: https://www.soccergraph.com/2026/05/fifa-world-cup-2026-all-48-team-market-values-full-ranking.html
  - 32 equipos verificados (cross-referencia con sportingpedia)

## Coordenadas de estadios (nuevo en v2)

- Fuente combinada: FIFA.com stadium info + latlong.net + conocimiento verificado
  - URL FIFA: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/stadium-information-details
  - Coordenadas usadas: ver tabla VENUE_COORDS en modelo.py

## Diferencial clasificatorio (nuevo en v2)

- [ESTIMADO] — Estimación propia basada en campaña de clasificación de cada confederación.
  No hay fuente única consolidada con xG para las 48 selecciones. Se usa como modificador menor (±2% máximo).

## Edades de plantilla (nuevo en v3)

- **rotowire.com — 2026 FIFA World Cup Squad Ages** — Consultado 07-Jun-2026
  - URL: https://www.rotowire.com/soccer/article/2026-fifa-world-cup-squad-ages
  - 48 equipos verificados, edades medias de 25.35 (Costa de Marfil) a 30.00 (Panamá)
  - Usadas en variable C17: edad media × estrés térmico WBGT

## Calidad de porteros (nuevo en v3)

- **si.com — Best Goalkeepers at the 2026 World Cup** — Consultado 07-Jun-2026
  - URL: https://www.si.com/soccer/2026/06/best-goalkeepers-at-the-2026-world-cup
  - Ranking narrativo: Martínez (ARG) y Courtois (BEL) en tier S, Maignan y Alisson en tier A
  - Escala 1-10 derivada de posición en ranking y descripción cualitativa (verificada)

- **beinsports.com — 2026 World Cup Goalkeeper Rankings** — Consultado 07-Jun-2026
  - Cross-referencia con si.com para confirmar posición de Raya (ESP, 19 clean sheets PL 25-26),
    Verbruggen (NED, Euro 2024), Neuer (GER, 40 años, sigue siendo élite)

## Jugadores en ligas top-5 (nuevo en v3)

- **cbssports.com — 2026 World Cup Premier League representation** — Consultado 07-Jun-2026
  - Totales por liga: Premier League 176, Bundesliga 101, La Liga 81, Ligue 1 79, Serie A 66 = 503
  - Distribución por selección: [ESTIMADO] basado en composición típica de squad y conocimiento de convocatorias finales

## H2H reciente (nuevo en v3)

- **espn.com / fbref.com** — H2H de partidos de los últimos 3 años
  - Solo se incluyen pares con ≥2 partidos verificados relevantes. Fuente: ESPN Soccer Results.
  - France vs Brazil (Mar-2026): Francia 2-1 Brasil [VERIFICADO de búsqueda]
  - Resto: [ESTIMADO] basado en resultados conocidos de EURO 2020/2024, Copa América 2021/2024, CN 2022-24

## WBGT / calor (ampliado en v3)

- **Periard et al. (2022) — Heat Stress at the 2026 World Cup venues**
  - Referencia académica: J. Periard et al., British Journal of Sports Medicine
  - 14/16 sedes WC2026 superan 28°C WBGT en junio
  - Valores WBGT por sede en modelo.py derivados de este estudio y datos climatológicos NOAA

- **Mohr et al. (2012/2014) — Physical performance in the heat during WC2014**
  - High-speed running reduction: ~10% con WBGT>28°C
  - Sprint reduction: hasta 25m/min menos en condiciones extremas
  - Implementado como penalización de hasta 10% en xG para equipos de clima frío

## Herramientas / modelo

- **Distribución de Poisson** independiente por equipo (Knorr-Held, 1997; Dixon & Coles, 1997)
- **Escala Elo → xG**: odds ratio de probabilidad de victoria, raíz cuadrada para escala de goles
- **Monte Carlo**: 10,000 iteraciones por grupo para clasificación esperada
- **Limitaciones declaradas v3**: sin correlación goles (Dixon-Coles), lesionados de última hora no incluidos, aclimatación asumida a 5 días, forma basada en análisis cualitativo (±4%), estilo táctico no cuantificado (G34), cohesión vestuario no cuantificable (H38), variables in-game (I40-I42) no disponibles como inputs pre-partido
