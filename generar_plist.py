"""
Genera el launchd plist con un StartCalendarInterval por partido,
programado 150 minutos (2h30m) después del kickoff UTC,
convertido a la hora local de la máquina.

Uso:
  python3 generar_plist.py --api-key YOUR_KEY
"""

import argparse
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

BASE_URL  = "https://api.football-data.org/v4"
PLIST_PATH = Path.home() / "Library/LaunchAgents/com.mundial2026.actualizar.plist"
PYTHON    = "/Users/jburgosforte/Documents/Claude/.venv/bin/python3"
SCRIPT    = "/Users/jburgosforte/Documents/Claude/mundial2026/actualizar_resultados.py"
API_KEY   = "2903cb32cf5545e98ae55074c592c81b"
OFFSET_MIN = 150  # minutos después del kickoff para actualizar


def get_matches(api_key):
    r = requests.get(
        f"{BASE_URL}/competitions/WC/matches?season=2026",
        headers={"X-Auth-Token": api_key}, timeout=10
    )
    r.raise_for_status()
    return r.json()["matches"]


def utc_to_local(dt_utc: datetime) -> datetime:
    local_offset = datetime.now().astimezone().utcoffset()
    return dt_utc + local_offset


def build_plist(update_times: list[datetime]) -> str:
    intervals = "\n".join(
        f"    <dict>"
        f"<key>Month</key><integer>{t.month}</integer>"
        f"<key>Day</key><integer>{t.day}</integer>"
        f"<key>Hour</key><integer>{t.hour}</integer>"
        f"<key>Minute</key><integer>{t.minute}</integer>"
        f"</dict>"
        for t in sorted(set(
            t.replace(second=0, microsecond=0) for t in update_times
        ))
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.mundial2026.actualizar</string>

  <key>ProgramArguments</key>
  <array>
    <string>{PYTHON}</string>
    <string>{SCRIPT}</string>
    <string>--api-key</string>
    <string>{API_KEY}</string>
    <string>--deploy</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/jburgosforte/Documents/Claude/mundial2026</string>

  <key>StartCalendarInterval</key>
  <array>
{intervals}
  </array>

  <key>RunAtLoad</key>
  <false/>

  <key>StandardOutPath</key>
  <string>/Users/jburgosforte/Documents/Claude/mundial2026/logs/actualizar.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/jburgosforte/Documents/Claude/mundial2026/logs/actualizar.log</string>
</dict>
</plist>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=API_KEY)
    args = parser.parse_args()

    print("Obteniendo calendario de partidos...")
    matches = get_matches(args.api_key)

    update_times = []
    for m in matches:
        kickoff_utc = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        update_utc  = kickoff_utc + timedelta(minutes=OFFSET_MIN)
        update_local = utc_to_local(update_utc)
        update_times.append(update_local)
        status = "✓" if m["status"] == "FINISHED" else " "
        print(f"  {status} {m['homeTeam']['name']} vs {m['awayTeam']['name']} "
              f"→ actualizar a las {update_local.strftime('%d %b %H:%M')}")

    plist_content = build_plist(update_times)

    # Descargar agente si está cargado
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)],
                   capture_output=True)

    PLIST_PATH.write_text(plist_content)
    print(f"\nPlist generado: {PLIST_PATH}")

    result = subprocess.run(["launchctl", "load", str(PLIST_PATH)],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print("Agente launchd recargado correctamente.")
    else:
        print("Error al recargar:", result.stderr)


if __name__ == "__main__":
    main()
