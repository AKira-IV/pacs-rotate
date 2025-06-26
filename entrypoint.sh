#!/bin/bash
set -e

echo "🕒 Iniciando cron del PACS Rotator..."

# Cargar variables de entorno
export $(grep -v '^#' .env | xargs)

# Iniciar cron en foreground (no daemon)
cron -f
echo "✅ Cron del PACS Rotator iniciado."