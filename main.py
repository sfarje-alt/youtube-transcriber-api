from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import assemblyai as aai
import os
import tempfile
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir llamadas desde LawMeter

# Configurar AssemblyAI
aai.settings.api_key = os.environ.get('ASSEMBLYAI_API_KEY')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    video_id = data.get('videoId')
    language = data.get('language', 'es')
    
    if not video_id:
        return jsonify({'error': 'videoId is required'}), 400
    
    logger.info(f"Starting transcription for video: {video_id}")
    
    try:
        # 1. Descargar audio con yt-dlp
        url = f'https://www.youtube.com/watch?v={video_id}'
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, '%(id)s.%(ext)s')
            
# En ydl_opts, agregar:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'cookiefile': 'cookies.txt',  # <-- Agregar esta línea
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '64',
                }]
            }

            
            logger.info(f"Downloading audio from YouTube...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_ext = info.get('ext', 'm4a')
                audio_file = os.path.join(tmpdir, f"{info['id']}.{video_ext}")
                
                # Verificar que el archivo existe
                if not os.path.exists(audio_file):
                    # Buscar cualquier archivo descargado
                    files = os.listdir(tmpdir)
                    if files:
                        audio_file = os.path.join(tmpdir, files[0])
                    else:
                        return jsonify({'error': 'Audio file not downloaded'}), 500
            
            logger.info(f"Audio downloaded: {audio_file}")
            logger.info(f"Starting AssemblyAI transcription...")
            
            # 2. Transcribir con AssemblyAI
            config = aai.TranscriptionConfig(language_code=language)
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file, config)
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"AssemblyAI error: {transcript.error}")
                return jsonify({'error': transcript.error}), 500
            
            logger.info(f"Transcription completed successfully")
            
            return jsonify({
                'success': True,
                'text': transcript.text,
                'duration': info.get('duration'),
                'title': info.get('title'),
                'videoId': video_id
            })
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error: {str(e)}")
        return jsonify({'error': f'YouTube download failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'youtube-transcriber-api',
        'assemblyai_configured': bool(os.environ.get('ASSEMBLYAI_API_KEY'))
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'YouTube Transcriber API',
        'endpoints': {
            'POST /transcribe': 'Transcribe a YouTube video',
            'GET /health': 'Health check'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

