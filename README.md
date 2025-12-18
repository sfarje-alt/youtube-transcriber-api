# YouTube Transcriber API

API para transcribir videos de YouTube usando yt-dlp + AssemblyAI.

## Endpoints

- `POST /transcribe` - Transcribir un video
  - Body: `{ "videoId": "VIDEO_ID", "language": "es" }`
  - Response: `{ "success": true, "text": "...", "duration": 123, "title": "..." }`

- `GET /health` - Health check

## Deploy en Railway

1. Fork este repositorio
2. Ir a [railway.app](https://railway.app)
3. New Project → Deploy from GitHub repo
4. Seleccionar este repositorio
5. Agregar variable de entorno: `ASSEMBLYAI_API_KEY`
6. Railway despliega automáticamente

## Variables de entorno

- `ASSEMBLYAI_API_KEY` - Tu API key de AssemblyAI (requerido)
- `PORT` - Puerto del servidor (default: 5000)

## Uso local

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
export ASSEMBLYAI_API_KEY=tu_api_key
python main.py

