from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import yt_dlp
import uuid
import threading

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def baixar_audio(url):
    nome = str(uuid.uuid4()) + ".mp3"
    caminho = os.path.join(DOWNLOAD_DIR, nome)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': caminho,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return caminho

def baixar_video(url, qualidade):
    nome = str(uuid.uuid4()) + ".mp4"
    caminho = os.path.join(DOWNLOAD_DIR, nome)
    ydl_opts = {
        'format': f'bestvideo[height<={qualidade}]+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': caminho,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return caminho

@app.get("/api/info")
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL faltando"}), 400
    with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
        meta = ydl.extract_info(url, download=False)
    return jsonify({
        "title": meta["title"],
        "thumbnail": meta["thumbnails"][-1]["url"]
    })

@app.get("/api/mp3")
def api_mp3():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL faltando"}), 400
    caminho = baixar_audio(url)
    return send_file(caminho, as_attachment=True)

@app.get("/api/mp4")
def api_mp4():
    url = request.args.get("url")
    qualidade = request.args.get("q", "720")
    caminho = baixar_video(url, qualidade)
    return send_file(caminho, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
