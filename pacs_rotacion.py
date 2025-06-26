import os
import csv
import argparse
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# Configuración desde .env
MAIN_URL = os.getenv("ORTHANC_MAIN", "http://localhost:8042")
BACKUP_URL = os.getenv("ORTHANC_BACKUP", "http://172.27.48.10:8044")
USERNAME = os.getenv("ORTHANC_USER", "orthanc")
PASSWORD = os.getenv("ORTHANC_PASS", "orthanc")

LOG_FILE = "log_migracion.csv"
auth = HTTPBasicAuth(USERNAME, PASSWORD)

def obtener_estudios():
    r = requests.get(f"{MAIN_URL}/studies", auth=auth)
    r.raise_for_status()
    return r.json()

def obtener_info_estudio(base_url, study_id):
    r = requests.get(f"{base_url}/studies/{study_id}", auth=auth)
    r.raise_for_status()
    return r.json()

def obtener_estudio_por_uid(base_url, study_uid):
    r = requests.post(f"{base_url}/tools/find", json={
        "Level": "Study",
        "Query": {"StudyInstanceUID": study_uid}
    }, auth=auth)
    r.raise_for_status()
    return r.json()

def exportar_y_subir(study_id):
    print(f"📦 Exportando estudio {study_id} desde MAIN...")
    r = requests.get(f"{MAIN_URL}/studies/{study_id}/archive", auth=auth, stream=True)
    r.raise_for_status()
    print("⬆️ Subiendo ZIP al BACKUP...")
    upload = requests.post(f"{BACKUP_URL}/tools/upload", data=r.raw, auth=auth)
    upload.raise_for_status()
    print("✅ Transferencia completada.\n")

def eliminar_estudio_main(study_id):
    r = requests.delete(f"{MAIN_URL}/studies/{study_id}?resources=true", auth=auth)
    return r.ok

def loguear_operacion(data):
    existe = os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as archivo:
        writer = csv.writer(archivo)
        if not existe:
            writer.writerow([
                "timestamp", "study_uid", "study_id", "fecha_estudio",
                "imagenes_main", "imagenes_backup", "accion", "estado"
            ])
        writer.writerow(data)

def main(dias, dry_run):
    cutoff = datetime.now() - timedelta(days=dias)
    estudios = obtener_estudios()

    for study_id in estudios:
        info_main = obtener_info_estudio(MAIN_URL, study_id)
        fecha_raw = info_main.get("MainDicomTags", {}).get("StudyDate")
        study_uid = info_main.get("MainDicomTags", {}).get("StudyInstanceUID")
        imagenes_main = len(info_main.get("Instances", []))
        fecha_estudio_str = fecha_raw if fecha_raw else "00000000"

        if not fecha_raw or not study_uid:
            continue

        fecha_estudio = datetime.strptime(fecha_estudio_str, "%Y%m%d")
        if fecha_estudio >= cutoff:
            continue

        print(f"\n🔍 Estudio {study_uid} ({fecha_estudio.date()}) candidato.")

        estudios_en_backup = obtener_estudio_por_uid(BACKUP_URL, study_uid)

        accion = estado = "Sin cambios"
        imagenes_backup = 0

        if estudios_en_backup:
            study_id_backup = estudios_en_backup[0]
            info_backup = obtener_info_estudio(BACKUP_URL, study_id_backup)
            imagenes_backup = len(info_backup.get("Instances", []))

            if imagenes_main == imagenes_backup:
                print(f"✅ Estudio ya presente en BACKUP y completo ({imagenes_main} imágenes).")

                if not dry_run:
                    if eliminar_estudio_main(study_id):
                        estado = "Estudio eliminado del MAIN"
                        accion = "Verificado y eliminado"
                        print("🗑️ Estudio eliminado correctamente del MAIN.")
                    else:
                        estado = "No se pudo eliminar"
                        accion = "Verificado pero falló eliminación"
                        print("❌ No se pudo eliminar el estudio.")
                else:
                    estado = "Dry Run (no eliminado)"
                    accion = "Verificado"
                    print("🧪 [Dry Run] Estudio sería eliminado del MAIN.")
            else:
                estado = "Backup incompleto"
                accion = "Transferencia pendiente"
                print(f"⚠️ Estudio presente en BACKUP pero incompleto ({imagenes_backup}/{imagenes_main}).")
        else:
            if not dry_run:
                exportar_y_subir(study_id)
                accion = "Transferido"
                estado = "Transferencia realizada"
            else:
                accion = "Transferencia pendiente"
                estado = "Dry Run (sin transferencia)"
                print("🧪 [Dry Run] Se transferiría este estudio.")

        loguear_operacion([
            datetime.now().isoformat(),
            study_uid,
            study_id,
            fecha_estudio_str,
            imagenes_main,
            imagenes_backup,
            accion,
            estado
        ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotar estudios de Orthanc Main a Backup usando HTTP.")
    parser.add_argument("--days", type=int, required=True, help="Estudios anteriores a esta cantidad de días serán migrados.")
    parser.add_argument("--dry-run", action="store_true", help="No ejecuta acciones, solo muestra lo que haría.")
    args = parser.parse_args()

    main(dias=args.days, dry_run=args.dry_run)
