# Horeh Clip AI V3

Paste an authorized direct video URL, then generate 3 vertical 9:16 MP4 clips.

## Run
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

Open http://localhost:8000

## Important
This version accepts direct HTTP/HTTPS video file URLs (for example MP4/WebM). It does not bypass YouTube, TikTok, or other platforms' download restrictions.
