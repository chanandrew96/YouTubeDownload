import logging
from typing import Union
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pytube import YouTube
# from __future__ import unicode_literals
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()

@app.get("/")
def read_root():
    response = RedirectResponse(url='/docs')
    return response

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

class DownloadRequest(BaseModel):
    url: str
    fileFormat: str
    resolution: str
    downloadPath: str

@app.post("/download")
async def download(downloadReq: DownloadRequest):
    # yt = YouTube("https://www.youtube.com/watch?v=n06H7OcPd-g")
    # yt = yt.get('mp4', '720p')
    # yt.download('/path/to/download/directory')
    # Download Highest Quality
    # YouTube('video_url').streams.first().download('save_path')
    yt = YouTube(downloadReq.url)
    # yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
    # yt = yt.get(downloadReq.fileFormat, downloadReq.resolution)
    # await yt.download(downloadReq.downloadPath)
    yt.streams.filter(file_extension='mp4')
    stream = yt.streams.get_by_itag(22)
    stream.download()
    return {"Result": "Completed"}

@app.post("/downloadVideo")
async def downloadVideo(downloadReq: DownloadRequest):
    # ydl_opts = {}
    # https://stackoverflow.com/questions/79226520/pytube-throws-http-error-403-forbidden-since-a-few-days
    # Use cookie from txt file
    ydl_opts = {'outtmpl': f"{downloadReq.downloadPath}/%(title)s.%(ext)s", 'cookiefile': 'cookies.txt'}
    # Use cookie from Chrom
    # ydl_opts = {'outtmpl': f"{downloadReq.downloadPath}/%(title)s.%(ext)s", 'cookiesfrombrowser': ('chrome',)}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([downloadReq.url])

    