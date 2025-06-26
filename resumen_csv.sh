#!/bin/bash

CSV="log_migracion.csv"

if [ ! -f "$CSV" ]; then
  echo "❌ No se encuentra el archivo $CSV"
  exit 1
fi

echo "📊 Estadísticas del archivo $CSV"
echo "-----------------------------------"

total=$(tail -n +2 "$CSV" | wc -l)
transferidos=$(grep -c 'Transferido' "$CSV")
verificados=$(grep -c 'Verificado y eliminado' "$CSV")
incompletos=$(grep -c 'Backup incompleto' "$CSV")

echo "🗂 Total de estudios procesados: $total"
echo "📦 Estudios transferidos        : $transferidos"
echo "✅ Verificados y eliminados     : $verificados"
echo "⚠️  Backup incompleto            : $incompletos"

echo
echo "📅 Estadísticas por fecha:"
echo "--------------------------"
cut -d',' -f1,7 "$CSV" | tail -n +2 | cut -d'T' -f1 | sort | uniq -c | sort -nr | awk '{ printf "📆 %s - %s estudios\n", $2, $1 }'
