import os, uuid, subprocess, tempfile, urllib.request
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE=Path(__file__).resolve().parent
OUT=BASE/"output"; OUT.mkdir(exist_ok=True)
app=FastAPI(title="Horeh Clip AI")
app.mount("/media", StaticFiles(directory=OUT), name="media")

class Req(BaseModel):
    url:str

@app.get("/")
def home():
    return FileResponse(BASE.parent/"frontend"/"index.html")

def duration(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True)
    if p.returncode: raise HTTPException(400,"The URL did not return a readable video.")
    return float(p.stdout.strip())

@app.post("/api/process-url")
def process(req:Req):
    u=req.url.strip()
    parsed=urlparse(u)
    if parsed.scheme not in ("http","https"): raise HTTPException(400,"Use an http/https video URL.")
    job=uuid.uuid4().hex
    src=OUT/f"{job}-source"
    try:
        request=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(request,timeout=30) as r, open(src,"wb") as f:
            f.write(r.read())
        if src.stat().st_size>500*1024*1024: raise HTTPException(413,"Video is too large (500 MB max).")
        dur=duration(src)
        if dur<9: raise HTTPException(400,"Video must be at least 9 seconds long.")
        clips=[]
        length=min(30.0,max(9.0,dur/3))
        starts=[0,max(0,(dur-length)/2),max(0,dur-length)]
        for i,start in enumerate(starts,1):
            out=OUT/f"{job}-short-{i}.mp4"
            subprocess.run(["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(length),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920","-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k","-movflags","+faststart",str(out)],check=True,capture_output=True)
            clips.append({"name":f"Short {i}","url":f"/media/{out.name}"})
        return {"clips":clips}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(500,"Could not process that URL. Use a direct video file URL such as MP4/WebM.")
    finally:
        if src.exists(): src.unlink(missing_ok=True)
