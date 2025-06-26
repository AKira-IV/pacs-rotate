FROM python:3.11-slim

# Instalación
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt \
 && chmod +x entrypoint.sh \
 && apt-get update && apt-get install -y cron

# Copia cronjob y lo instala
COPY cronjob /etc/cron.d/rotate-pacs
RUN chmod 0644 /etc/cron.d/rotate-pacs \
 && crontab /etc/cron.d/rotate-pacs

# Expone logs (opcional)
VOLUME /app/logs

ENTRYPOINT ["./entrypoint.sh"]
