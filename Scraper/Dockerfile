FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

COPY internship_cron /etc/cron.d/internship_cron
RUN chmod 0644 /etc/cron.d/internship_cron \
    && crontab /etc/cron.d/internship_cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]
