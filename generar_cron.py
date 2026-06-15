"""
Genera el bloque `schedule:` del workflow de GitHub Actions con una entrada
cron por partido, a kickoff + 150 min (2h30) y un reintento a +180 min.

GitHub Actions usa UTC y el utcDate de la API ya viene en UTC → conversión directa.
El reintento +30 min no gasta créditos: si el primer deploy ya capturó el
resultado, el segundo no encuentra cambios (git diff limpio) y no despliega.

Uso:
  python3 generar_cron.py            # imprime el bloque schedule
  python3 generar_cron.py --write    # reescribe .github/workflows/actualizar.yml
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import requests

API_KEY = "2903cb32cf5545e98ae55074c592c81b"
WORKFLOW = Path(__file__).parent / ".github" / "workflows" / "actualizar.yml"
OFFSETS_MIN = [150]  # 2h30 tras el inicio. El script recoge TODOS los partidos
                     # finalizados en cada corrida, así que hay redundancia natural.


def get_matches():
    r = requests.get(
        "https://api.football-data.org/v4/competitions/WC/matches?season=2026",
        headers={"X-Auth-Token": API_KEY}, timeout=10,
    )
    r.raise_for_status()
    return r.json()["matches"]


def build_schedule(matches) -> str:
    times = set()
    for m in matches:
        kickoff = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        for off in OFFSETS_MIN:
            t = (kickoff + timedelta(minutes=off)).replace(second=0, microsecond=0)
            times.add((t.minute, t.hour, t.day, t.month))

    lines = ["  schedule:"]
    for minute, hour, day, month in sorted(times, key=lambda x: (x[3], x[2], x[1], x[0])):
        lines.append(f"    - cron: '{minute} {hour} {day} {month} *'")
    return "\n".join(lines)


def write_workflow(schedule_block: str):
    content = WORKFLOW.read_text()
    lines = content.splitlines()

    # Reemplazar desde la línea 'schedule:' (incluida) hasta 'workflow_dispatch'
    start = next(i for i, l in enumerate(lines) if l.strip() == "schedule:")
    end = next(i for i, l in enumerate(lines) if "workflow_dispatch" in l)

    # schedule_block ya incluye '  schedule:' como primera línea
    new_lines = lines[:start] + schedule_block.splitlines() + lines[end:]
    WORKFLOW.write_text("\n".join(new_lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    matches = get_matches()
    schedule = build_schedule(matches)
    n_entries = schedule.count("- cron:")
    print(f"{len(matches)} partidos → {n_entries} entradas cron (UTC)\n")

    if args.write:
        write_workflow(schedule)
        print(f"Workflow actualizado: {WORKFLOW}")
    else:
        print(schedule)


if __name__ == "__main__":
    main()
