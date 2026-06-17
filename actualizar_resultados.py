"""
Fetches World Cup 2026 match results from football-data.org (free tier)
and updates compartir/index.html with real scores + prediction accuracy.

Usage:
  python3 actualizar_resultados.py --api-key YOUR_KEY
  python3 actualizar_resultados.py --api-key YOUR_KEY --deploy   # also deploys to Netlify

Register free at: https://www.football-data.org/client/register
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import requests

BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "WC"
HTML_PATH = Path(__file__).parent / "compartir" / "index.html"

# Código FIFA (tla) → nombre en español usado en el HTML.
# Los tla son ESTABLES: no cambian aunque football-data renombre al equipo
# ("Cape Verde"→"Cape Verde Islands", "DR Congo"→"Congo DR"...). Emparejar por
# tla hace la actualización inmune a esos renombrados, que ya nos rompieron varias veces.
TLA_ES = {
    "URU": "Uruguay", "GER": "Alemania", "ESP": "España", "PAR": "Paraguay",
    "ARG": "Argentina", "GHA": "Ghana", "BRA": "Brasil", "POR": "Portugal",
    "JPN": "Japón", "MEX": "México", "ENG": "Inglaterra", "USA": "EE. UU.",
    "KOR": "Corea del Sur", "FRA": "Francia", "RSA": "Sudáfrica", "ALG": "Argelia",
    "AUS": "Australia", "NZL": "Nueva Zelanda", "SUI": "Suiza", "ECU": "Ecuador",
    "SWE": "Suecia", "CZE": "Chequia", "CRO": "Croacia", "KSA": "Arabia Saudí",
    "TUN": "Túnez", "TUR": "Turquía", "SEN": "Senegal", "BEL": "Bélgica",
    "MAR": "Marruecos", "AUT": "Austria", "COL": "Colombia", "EGY": "Egipto",
    "CAN": "Canadá", "HAI": "Haití", "IRN": "Irán", "BIH": "Bosnia",
    "PAN": "Panamá", "CPV": "Cabo Verde", "COD": "RD Congo", "CIV": "Costa de Marfil",
    "QAT": "Catar", "JOR": "Jordania", "IRQ": "Irak", "UZB": "Uzbekistán",
    "NED": "Países Bajos", "NOR": "Noruega", "SCO": "Escocia", "CUW": "Curazao",
}

# Fallback por nombre, por si algún partido viniera sin tla.
NAME_ES = {
    "Mexico": "México", "Spain": "España", "France": "Francia", "England": "Inglaterra",
    "Morocco": "Marruecos", "Brazil": "Brasil", "Netherlands": "Países Bajos",
    "Belgium": "Bélgica", "Croatia": "Croacia", "United States": "EE. UU.",
    "Japan": "Japón", "Switzerland": "Suiza", "Iran": "Irán", "Turkey": "Turquía",
    "South Korea": "Corea del Sur", "Algeria": "Argelia", "Egypt": "Egipto",
    "Norway": "Noruega", "Canada": "Canadá", "Ivory Coast": "Costa de Marfil",
    "Sweden": "Suecia", "Czechia": "Chequia", "Scotland": "Escocia",
    "DR Congo": "RD Congo", "Congo DR": "RD Congo", "Tunisia": "Túnez",
    "Uzbekistan": "Uzbekistán", "Germany": "Alemania", "New Zealand": "Nueva Zelanda",
    "Qatar": "Catar", "South Africa": "Sudáfrica", "Saudi Arabia": "Arabia Saudí",
    "Haiti": "Haití", "Curacao": "Curazao", "Curaçao": "Curazao",
    "Bosnia-Herzegovina": "Bosnia", "Bosnia and Herzegovina": "Bosnia",
    "Cape Verde": "Cabo Verde", "Cape Verde Islands": "Cabo Verde",
    "Jordan": "Jordania", "Iraq": "Irak",
}


def _team_es(team: dict) -> str | None:
    """Nombre ES a partir del tla (estable) y, si faltara, del nombre."""
    return TLA_ES.get(team.get("tla")) or NAME_ES.get(team.get("name"))


def fetch_results(api_key: str) -> dict[str, dict]:
    """Returns {(local_es, visit_es): {'gl': int, 'gv': int}} for finished matches."""
    headers = {"X-Auth-Token": api_key}
    r = requests.get(f"{BASE_URL}/competitions/{COMPETITION}/matches", headers=headers, timeout=10)
    r.raise_for_status()

    results = {}
    sin_mapear = set()
    for m in r.json().get("matches", []):
        if m["status"] != "FINISHED":
            continue
        home, away = _team_es(m["homeTeam"]), _team_es(m["awayTeam"])
        for t, es in ((m["homeTeam"], home), (m["awayTeam"], away)):
            if not es:
                sin_mapear.add(f"{t.get('tla')}/{t.get('name')}")
        if home and away:
            results[(home, away)] = {
                "gl": m["score"]["fullTime"]["home"],
                "gv": m["score"]["fullTime"]["away"],
            }

    if sin_mapear:
        print(f"  ⚠️  EQUIPOS SIN MAPEAR (revisar TLA_ES): {sorted(sin_mapear)}")
    return results


def outcome(gl: int, gv: int) -> str:
    if gl > gv:
        return "1"
    if gl == gv:
        return "X"
    return "2"


def marcador_outcome(marcador: str) -> str:
    gl, gv = map(int, marcador.split("-"))
    return outcome(gl, gv)


def inject_results(results: dict) -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    m = re.search(r"(const DATA = \{.+\});", html)
    if not m:
        sys.exit("ERROR: const DATA not found in index.html")

    data = json.loads(m.group(1)[len("const DATA = "):])
    updated = 0

    for match in data["matches"]:
        key = (match["local"], match["visit"])
        if key not in results:
            match.pop("resultado", None)
            match.pop("acierto", None)
            continue

        r = results[key]
        real_outcome = outcome(r["gl"], r["gv"])
        pred_outcome = marcador_outcome(match["marcador"])

        match["resultado"] = f"{r['gl']}-{r['gv']}"
        match["acierto"] = real_outcome == pred_outcome

        if match.get("amalia"):
            al, av = map(int, match["amalia"].split("-"))
            match["amalia_acierto"] = outcome(al, av) == real_outcome

        updated += 1

    new_const = "const DATA = " + json.dumps(data, ensure_ascii=False) + ";"
    new_html = html[: m.start()] + new_const + html[m.end() :]
    HTML_PATH.write_text(new_html, encoding="utf-8")
    return updated


NETLIFY_SITE_ID = "aa1989c6-5720-4b30-a499-b42192329c3f"  # whimsical-strudel-c8cd24
LAST_COUNT_FILE = Path(__file__).parent / ".last_deployed_count"


def get_last_deployed_count() -> int:
    try:
        return int(LAST_COUNT_FILE.read_text().strip())
    except Exception:
        return -1


def save_deployed_count(n: int):
    LAST_COUNT_FILE.write_text(str(n))

def deploy():
    result = subprocess.run(
        ["/opt/homebrew/bin/netlify", "deploy", "--prod", "--dir", str(HTML_PATH.parent), "--site", NETLIFY_SITE_ID],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Deploy error:", result.stderr)
    else:
        url = next((l for l in result.stdout.splitlines() if "netlify.app" in l), "")
        print(f"Deployed → {url.strip()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--deploy", action="store_true", help="Deploy to Netlify after update")
    args = parser.parse_args()

    print("Fetching results from football-data.org...")
    results = fetch_results(args.api_key)
    current_count = len(results)
    print(f"  {current_count} partidos finalizados encontrados")

    # Optimización solo para deploy local: si no cambió el nº de partidos, no redesplegar.
    # En GitHub Actions se ejecuta sin --deploy y el control de cambios lo hace git diff.
    last_count = get_last_deployed_count()
    if args.deploy and current_count == last_count:
        print(f"  Sin cambios desde el último deploy ({last_count} partidos) — deploy omitido.")
        return

    updated = inject_results(results)
    print(f"  {updated} partidos actualizados en index.html")

    if args.deploy:
        print(f"  Desplegando ({last_count} → {current_count} partidos)...")
        deploy()
        save_deployed_count(current_count)


if __name__ == "__main__":
    main()
