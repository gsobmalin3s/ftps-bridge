FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /home/ftpuser

COPY server.py .

# Puerto de control FTP + rango pasivo
EXPOSE 21
EXPOSE 60000-60010

CMD ["python", "server.py"]
