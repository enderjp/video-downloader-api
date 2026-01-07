from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

class VideoRequest(BaseModel):
    url: str


@app.post("/download_file")
def download_video_file(data: VideoRequest):
    url = data.url

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    downloads_dir = os.path.join(BASE_DIR, "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    # 👉 Ruta al archivo de cookies (misma carpeta del proyecto)
    COOKIES_FILE = os.path.join(BASE_DIR, "facebook.cookies.txt")

    if not os.path.exists(COOKIES_FILE):
        raise HTTPException(
            status_code=500,
            detail="Cookies file not found on server"
        )

    try:
        ydl_opts = {
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',

            # ⭐ CAMBIO CLAVE
            'cookiefile': COOKIES_FILE,

            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            raise HTTPException(
                status_code=500,
                detail="Downloaded file not found"
            )

        return FileResponse(
            path=filename,
            media_type="video/mp4",
            filename=os.path.basename(filename)
        )

    except Exception as e:
        error_text = str(e)

        # 🔎 Error típico cuando las cookies expiran
        if "only available for registered users" in error_text.lower():
            raise HTTPException(
                status_code=403,
                detail="FACEBOOK_LOGIN_REQUIRED"
            )

        raise HTTPException(
            status_code=500,
            detail=error_text
        )
