from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

@app.get("/api/mp3")
def download_mp3():
    url = request.args.get("url")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400

    filename = f"{uuid.uuid4()}.mp3"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filename, as_attachment=True)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.get("/api/mp4")
def download_mp4():
    url = request.args.get("url")
    quality = request.args.get("q", "720")

    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best",
        "outtmpl": filename,
        "merge_output_format": "mp4"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filename, as_attachment=True)
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.get("/")
def home():
    return "✅ JS MUSIC SERVER ONLINE"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
