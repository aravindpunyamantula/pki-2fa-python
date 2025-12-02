FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt && \
    rm -rf /root/.cache/pip

FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

RUN apt-get update && \
    apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
ENV PYTHONPATH=/usr/local

COPY app ./app
COPY scripts ./scripts
COPY cron ./cron

COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .

RUN chmod +x scripts/log_2fa_cron.py

RUN cp cron/2fa-cron /etc/cron.d/2fa-cron && \
    chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

RUN mkdir -p /data /cron && chmod 755 /data /cron

VOLUME ["/data", "/cron"]

EXPOSE 8080

CMD ["sh", "-c", "cron && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
