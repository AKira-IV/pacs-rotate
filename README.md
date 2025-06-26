# 🧠 PACS Rotator - Orthanc Main → Backup

Sistema automático para migrar estudios DICOM antiguos desde un servidor **Orthanc Principal (Main)** hacia un **Orthanc de Respaldo (Backup)**, asegurando la **trazabilidad, seguridad y performance** del sistema PACS de hospitales grandes.

---

## 🚀 ¿Qué hace este sistema?

- 🔍 Revisa estudios con antigüedad mayor a `X` días (por default: 180).
- 📦 Verifica si ya existen en el servidor de backup.
- 🧮 Compara cantidad de imágenes (instancias) entre Main y Backup.
- ⬆️ Transfiere estudios completos mediante HTTP (ZIP → upload).
- 🗑️ Elimina automáticamente los estudios en Main si fueron verificados y migrados correctamente.
- 🧾 Registra todo en un archivo `log_migracion.csv`.
- 📅 Corre automáticamente cada semana mediante `cron` dentro de Docker.

---

## 🏗️ Estructura del proyecto

```
pacs-rotate/
├── rotate_studies_http_v4.py # Script principal
├── requirements.txt # Dependencias Python
├── .env # Configuración (URLs, credenciales)
├── cronjob # Tarea semanal para cron
├── Dockerfile # Docker image
├── entrypoint.sh # Inicializador
├── log_migracion.csv # (Se genera automáticamente)
└── resumen_csv.sh # Script en Bash para analizar el log
```
---
## 🐳 Cómo usar con Docker

🔨 Construir la imagen

```
docker build -t pacs-rotate .

Ejecutar el contenedor con:

docker run -d \
  --name pacs-rotate \
  -v /ruta/logs:/app/logs \
  pacs-rotate

```
## 📊 Analizar estadísticas con Bash

```
chmod +x resumen_csv.sh
./resumen_csv.sh
```
Ejemplo de salida:
```
🗂 Total de estudios procesados: 1320
📦 Estudios transferidos        : 284
✅ Verificados y eliminados     : 1023
⚠️  Backup incompleto            : 13

📅 Estadísticas por fecha:
📆 2025-06-25 - 220 estudios
📆 2025-06-18 - 180 estudios

```

## Cron por defecto para implementar 

```
0 3 * * 1 /usr/local/bin/python3 /app/rotate_studies_http_v4.py --days 180 >> /app/log_migracion.csv 2>&1
```
 


