FROM python:3.11-slim

# Instalar FFmpeg (necesario para yt-dlp)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Puerto
EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--timeout", "300", "--workers", "2"]

