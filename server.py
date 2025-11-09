import os, re, uuid, shutil
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def slug(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:120] if s else str(uuid.uuid4())

def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None or shutil.which("ffprobe") is not None

@app.get("/api/info")
def api_info():
    url = request.args.get("url", "").strip()
    if not url: return jsonify({"error":"URL faltando"}), 400
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "channel": info.get("channel"),
            "duration": info.get("duration")
        })
    except Exception as e:
        return jsonify({"error": f"Falha ao obter info: {e}"}), 500

@app.get("/api/mp3")
def api_mp3():
    url = request.args.get("url", "").strip()
    if not url: return "URL faltando", 400

    # se não houver ffmpeg no servidor, cai para m4a (sem transcode)
    use_ffmpeg = has_ffmpeg()
    temp_id = uuid.uuid4().hex
    out_base = os.path.join(DOWNLOAD_DIR, temp_id)

    ydl_opts = {
        "quiet": True,
        "outtmpl": out_base + ".%(ext)s",
        "format": "bestaudio/best",
    }

    if use_ffmpeg:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        # baixa direto em m4a
        ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = slug(info.get("title") or "audio")
            if use_ffmpeg:
                final_path = out_base + ".mp3"
                download_path = final_path
                download_name = f"{title}.mp3"
            else:
                # descobrir extensão resultante (geralmente .m4a)
                ext = ydl.prepare_filename(info).split(".")[-1]
                download_path = f"{out_base}.{ext}"
                download_name = f"{title}.{ext}"

        return send_file(download_path, as_attachment=True, download_name=download_name)
    except Exception as e:
        return f"Erro ao baixar áudio: {e}", 500

@app.get("/api/mp4")
def api_mp4():
    url = request.args.get("url", "").strip()
    quality = request.args.get("q", "best").strip().lower()
    if not url: return "URL faltando", 400

    temp_id = uuid.uuid4().hex
    out_base = os.path.join(DOWNLOAD_DIR, temp_id)

    # melhor vídeo até a qualidade pedida + melhor áudio
    fmt = "best"
    if quality != "best":
        fmt = f"bestvideo[height<={quality}]+bestaudio/best"

    ydl_opts = {
        "quiet": True,
        "outtmpl": out_base + ".%(ext)s",
        "format": fmt,
        "merge_output_format": "mp4",  # tenta sair em mp4 quando possível
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = slug(info.get("title") or "video")
            final_path = ydl.prepare_filename(info)
            # normaliza p/ .mp4 quando possível
            if not final_path.endswith(".mp4"):
                base_no_ext = ".".join(final_path.split(".")[:-1])
                mp4_candidate = base_no_ext + ".mp4"
                if os.path.exists(mp4_candidate):
                    final_path = mp4_candidate
            return send_file(final_path, as_attachment=True, download_name=f"{title}.mp4")
    except Exception as e:
        return f"Erro ao baixar vídeo: {e}", 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
