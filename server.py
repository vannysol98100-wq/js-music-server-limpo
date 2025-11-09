from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOADS_FOLDER = "downloads"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

def gerar_nome():
    return str(uuid.uuid4())

@app.route("/api/info")
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL inválida"}), 400

    ydl_opts = {"quiet": True, "skip_download": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)

    formatos = []
    for f in data["formats"]:
        if f.get("url") and f.get("height"):
            formatos.append({
                "itag": f["format_id"],
                "resolution": f.get("height", "audio"),
                "audio": "com áudio" if f.get("acodec") != "none" else "sem áudio",
                "type": f.get("ext")
            })

    return jsonify({
        "title": data["title"],
        "thumbnail": data["thumbnail"],
        "formats": formatos
    })

@app.route("/api/download")
def download():
    url = request.args.get("url")
    itag = request.args.get("itag")

    if not url or not itag:
        return "Parâmetros faltando", 400

    nome = gerar_nome()
    caminho_saida = f"{DOWNLOADS_FOLDER}/{nome}.mp4"

    ydl_opts = {
        "format": itag,
        "outtmpl": caminho_saida,
        "merge_output_format": "mp4",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(caminho_saida, as_attachment=True)

@app.route("/")
def home():
    return "Servidor JS MUSIC OK ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
