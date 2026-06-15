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

# Map football-data.org team names → names used in our HTML
TEAM_MAP = {
    "Mexico": "México", "Spain": "España", "France": "Francia",
    "England": "Inglaterra", "Morocco": "Marruecos", "Brazil": "Brasil",
    "Portugal": "Portugal", "Netherlands": "Países Bajos", "Belgium": "Bélgica",
    "Croatia": "Croacia", "Colombia": "Colombia", "Argentina": "Argentina",
    "Senegal": "Senegal", "Uruguay": "Uruguay", "United States": "EE. UU.",
    "Japan": "Japón", "Switzerland": "Suiza", "Iran": "Irán",
    "Turkey": "Turquía", "Ecuador": "Ecuador", "Austria": "Austria",
    "South Korea": "Corea del Sur", "Australia": "Australia", "Algeria": "Argelia",
    "Egypt": "Egipto", "Norway": "Noruega", "Canada": "Canadá",
    "Ivory Coast": "Costa de Marfil", "Sweden": "Suecia", "Czechia": "Chequia",
    "Paraguay": "Paraguay", "Scotland": "Escocia", "DR Congo": "RD Congo",
    "Tunisia": "Túnez", "Uzbekistan": "Uzbekistán", "Germany": "Alemania",
    "New Zealand": "Nueva Zelanda", "Qatar": "Catar", "South Africa": "Sudáfrica",
    "Saudi Arabia": "Arabia Saudí", "Haiti": "Haití", "Curacao": "Curazao",
    "Bosnia and Herzegovina": "Bosnia", "Bosnia-Herzegovina": "Bosnia",
    "Cape Verde": "Cabo Verde",
    "Jordan": "Jordania", "Iraq": "Irak", "Ghana": "Ghana", "Panama": "Panamá",
}


def fetch_results(api_key: str) -> dict[str, dict]:
    """Returns {(local_es, visit_es): {'gl': int, 'gv': int}} for finished matches."""
    headers = {"X-Auth-Token": api_key}
    r = requests.get(f"{BASE_URL}/competitions/{COMPETITION}/matches", headers=headers, timeout=10)
    r.raise_for_status()

    results = {}
    for m in r.json().get("matches", []):
        if m["status"] != "FINISHED":
            continue
        home = TEAM_MAP.get(m["homeTeam"]["name"], m["homeTeam"]["name"])
        away = TEAM_MAP.get(m["awayTeam"]["name"], m["awayTeam"]["name"])
        gl = m["score"]["fullTime"]["home"]
        gv = m["score"]["fullTime"]["away"]
        results[(home, away)] = {"gl": gl, "gv": gv}
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
