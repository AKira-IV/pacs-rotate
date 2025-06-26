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

pacs-rotate/
├── rotate_studies_http_v4.py # Script principal
├── requirements.txt # Dependencias Python
├── .env # Configuración (URLs, credenciales)
├── cronjob # Tarea semanal para cron
├── Dockerfile # Docker image
├── entrypoint.sh # Inicializador
├── log_migracion.csv # (Se genera automáticamente)
└── resumen_csv.sh # Script en Bash para analizar el log
