from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import yt_dlp
import io
import tempfile
import os

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/download_file")
def download_video_file(data: VideoRequest):
    url = data.url

    try:
        # Crear un archivo temporal para la descarga
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                'format': 'best',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # Leer el video en memoria
            video_file = open(filename, "rb")

            # StreamingResponse enviará el video como binario
            response = StreamingResponse(video_file, media_type="video/mp4")
            response.headers["Content-Disposition"] = f'attachment; filename="{os.path.basename(filename)}"'

            return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
