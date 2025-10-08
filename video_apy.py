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

    downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    try:
        ydl_opts = {
            'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
            'format': 'best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return FileResponse(
            filename,
            media_type="video/mp4",
            filename=os.path.basename(filename)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
