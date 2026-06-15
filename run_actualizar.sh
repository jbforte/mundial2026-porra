#!/bin/bash
# Wrapper para launchd — activa el venv y ejecuta el actualizador

LOG="/Users/jburgosforte/Documents/Claude/mundial2026/logs/actualizar.log"
mkdir -p "$(dirname "$LOG")"

echo "--- $(date '+%Y-%m-%d %H:%M:%S') ---" >> "$LOG"

/Users/jburgosforte/Documents/Claude/.venv/bin/python3 \
  /Users/jburgosforte/Documents/Claude/mundial2026/actualizar_resultados.py \
  --api-key 2903cb32cf5545e98ae55074c592c81b \
  --deploy >> "$LOG" 2>&1

echo "" >> "$LOG"
