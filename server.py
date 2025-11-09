from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOADS = "downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

@app.route("/api/info")
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL requerida"}), 400
    
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail")
        })

@app.route("/api/mp3")
def mp3():
    url = request.args.get("url")
    if not url:
        return "Missing URL", 400

    output_id = str(uuid.uuid4())
    outpath = os.path.join(DOWNLOADS, f"{output_id}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOADS, f"{output_id}.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(outpath, as_attachment=True)
    except Exception as e:
        return str(e), 500


@app.route("/api/mp4")
def mp4():
    url = request.args.get("url")
    quality = request.args.get("q", "best")
    if not url:
        return "Missing URL", 400

    output_id = str(uuid.uuid4())
    outpath = os.path.join(DOWNLOADS, f"{output_id}.mp4")

    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best" if quality != "best" else "best",
        "merge_output_format": "mp4",
        "outtmpl": outpath,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(outpath, as_attachment=True)
    except Exception as e:
        return str(e), 500


@app.route("/")
def home():
    return "JS MUSIC SERVER ONLINE ✅"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
