import os
import sys
import uuid
import time
import math
import shutil
import asyncio
import threading
import re
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import yt_dlp
import imageio_ffmpeg

# Paths
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
STATIC_DIR = BASE_DIR / "static"
CACHE_DIR = BASE_DIR / ".cache"

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# Detect Node.js executable for yt-dlp JS runtime (accelerates YouTube signature parsing)
NODE_CANDIDATES = [
    r"C:\Users\APMC\AppData\Local\Programs\nodejs\node.exe",
    shutil.which("node") or "node"
]
NODE_PATH = next((p for p in NODE_CANDIDATES if p and os.path.exists(p)), None)

app = FastAPI(title="OmniStream - High Speed Universal Media Downloader", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    err_str = str(exc)
    print(f"[ERROR] Global exception caught: {err_str}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Server Processing Error",
            "message": f"Unable to process request: {err_str}",
            "type": type(exc).__name__
        }
    )

# In-memory download jobs
jobs: Dict[str, Dict[str, Any]] = {}

# In-memory high-speed metadata cache
INFO_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 1800  # 30 minutes TTL

class ExtractRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    media_type: str  # "video" or "audio"
    format_id: Optional[str] = None
    resolution: Optional[str] = None
    audio_quality: Optional[str] = "320"  # kbps: 320, 256, 192, 128 or original
    ext: Optional[str] = "mp4"

def clean_old_jobs():
    """Remove files and jobs older than 1 hour, and purge expired cache items."""
    now = time.time()
    to_delete_jobs = []
    for jid, job in list(jobs.items()):
        if now - job.get("created_at", now) > 3600:
            file_path = job.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            to_delete_jobs.append(jid)
    for jid in to_delete_jobs:
        jobs.pop(jid, None)

    to_delete_cache = [k for k, v in INFO_CACHE.items() if now - v.get("timestamp", now) > CACHE_TTL]
    for k in to_delete_cache:
        INFO_CACHE.pop(k, None)

def normalize_url(url: str) -> str:
    """Strips useless marketing/tracking query parameters to maximize cache hits."""
    url = url.strip()
    try:
        parsed = urlparse(url)
        # For youtube: keep v= and list= if needed, strip others (si, feature, pp, etc.)
        if "youtube.com" in parsed.netloc:
            qs = parse_qs(parsed.query)
            keep_params = {k: v for k, v in qs.items() if k in ["v", "list"]}
            new_query = urlencode(keep_params, doseq=True)
            return urlunparse(parsed._replace(query=new_query, fragment=""))
        elif "youtu.be" in parsed.netloc:
            return urlunparse(parsed._replace(query="", fragment=""))
        elif "instagram.com" in parsed.netloc:
            return urlunparse(parsed._replace(query="", fragment=""))
        elif "x.com" in parsed.netloc or "twitter.com" in parsed.netloc:
            return urlunparse(parsed._replace(query="", fragment=""))
    except Exception:
        pass
    return url

def detect_platform(url: str) -> Dict[str, str]:
    """Detects platform branding and domain information."""
    u = url.lower()
    if "youtube.com" in u or "youtu.be" in u:
        return {"name": "YouTube", "icon": "youtube", "color": "#FF0000"}
    if "instagram.com" in u:
        return {"name": "Instagram", "icon": "instagram", "color": "#E1306C"}
    if "facebook.com" in u or "fb.watch" in u or "fb.com" in u:
        return {"name": "Facebook", "icon": "facebook", "color": "#1877F2"}
    if "tiktok.com" in u:
        return {"name": "TikTok", "icon": "tiktok", "color": "#FE2C55"}
    if "twitter.com" in u or "://x.com" in u or ".x.com" in u or "/x.com" in u:
        return {"name": "X / Twitter", "icon": "twitter", "color": "#1DA1F2"}
    if "terabox.com" in u or "1024tera.com" in u or "teraboxapp.com" in u or "mirrobox.com" in u:
        return {"name": "TeraBox", "icon": "terabox", "color": "#00A4FF"}
    if "hotstar.com" in u or "disneyplus.com" in u:
        return {"name": "Disney+ Hotstar", "icon": "hotstar", "color": "#133E87"}
    if "whatsapp.com" in u:
        return {"name": "WhatsApp", "icon": "whatsapp", "color": "#25D366"}
    if "reddit.com" in u or "redd.it" in u:
        return {"name": "Reddit", "icon": "reddit", "color": "#FF4500"}
    if "soundcloud.com" in u:
        return {"name": "SoundCloud", "icon": "soundcloud", "color": "#FF5500"}
    if "vimeo.com" in u:
        return {"name": "Vimeo", "icon": "vimeo", "color": "#1AB7EA"}
    if "dailymotion.com" in u:
        return {"name": "Dailymotion", "icon": "dailymotion", "color": "#0066DC"}
    if "twitch.tv" in u:
        return {"name": "Twitch", "icon": "twitch", "color": "#9146FF"}
    if "pinterest.com" in u or "pin.it" in u:
        return {"name": "Pinterest", "icon": "pinterest", "color": "#E60023"}
    return {"name": "Web Media Source", "icon": "globe", "color": "#6366F1"}

def human_filesize(bytes_val: Optional[float]) -> str:
    if not bytes_val or bytes_val <= 0:
        return "Standard size"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_val, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_val / p, 1)
    return f"{s} {units[i]}"

def format_duration(seconds: Optional[float]) -> str:
    if not seconds:
        return "Unknown"
    sec = int(seconds)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def get_fast_ydl_extract_opts() -> Dict[str, Any]:
    """Generates ultra-fast extractor parameters for yt-dlp."""
    opts: Dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,            # Do not traverse entire playlists when a single video is requested
        "lazy_playlist": True,
        "socket_timeout": 8,           # Fast connection timeout
        "no_color": True,
        "cachedir": str(CACHE_DIR),    # Persist connection & session tokens for instant repeat queries
        "ffmpeg_location": FFMPEG_PATH,
    }
    if NODE_PATH:
        opts["js_runtimes"] = {"node": {"path": NODE_PATH}}
    return opts

@app.post("/api/extract")
async def extract_media_info(payload: ExtractRequest):
    clean_old_jobs()
    raw_url = payload.url.strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="Please provide a valid media URL.")

    platform_meta = detect_platform(raw_url)
    if platform_meta["icon"] == "whatsapp":
        return JSONResponse(
            status_code=400,
            content={
                "error": "WhatsApp Media Notice",
                "message": "WhatsApp media is encrypted and stored directly inside your phone's storage. To save WhatsApp status or videos, open WhatsApp on your phone and tap 'Save' or check your phone's WhatsApp Media folder.",
                "platform": platform_meta
            }
        )

    # Check cache first for instant 0.001s response
    norm_url = normalize_url(raw_url)
    if norm_url in INFO_CACHE:
        cached_entry = INFO_CACHE[norm_url]
        if time.time() - cached_entry["timestamp"] < CACHE_TTL:
            cached_data = dict(cached_entry["data"])
            cached_data["cached"] = True
            return cached_data

    ydl_opts = get_fast_ydl_extract_opts()

    try:
        loop = asyncio.get_event_loop()
        def _extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(raw_url, download=False)
        info = await loop.run_in_executor(None, _extract)
    except Exception as e:
        err_msg = str(e)
        if "DRM" in err_msg.upper() or "HOTSTAR" in platform_meta["name"].upper():
            return JSONResponse(
                status_code=400,
                content={
                    "error": "DRM Protected Content",
                    "message": "This platform protects its video streams using commercial Widevine DRM encryption. Content protected by DRM cannot be extracted by third-party tools.",
                    "platform": platform_meta
                }
            )
        return JSONResponse(
            status_code=400,
            content={
                "error": "Extraction Error",
                "message": f"Could not extract media from this URL: {err_msg}",
                "platform": platform_meta
            }
        )

    if not info:
        raise HTTPException(status_code=404, detail="No media stream found at this URL.")

    if "entries" in info and info["entries"]:
        info = info["entries"][0]

    title = info.get("title", "Untitled Media")
    thumbnail = info.get("thumbnail") or info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else None
    duration = format_duration(info.get("duration"))
    duration_raw = info.get("duration") or 0
    uploader = info.get("uploader") or info.get("channel") or info.get("creator") or platform_meta["name"]
    view_count = info.get("view_count")
    webpage_url = info.get("webpage_url") or raw_url

    raw_formats = info.get("formats", [])
    
    # Process video formats - group cleanly by height
    video_formats_map = {}
    for f in raw_formats:
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")
        height = f.get("height")
        width = f.get("width")
        ext = f.get("ext", "mp4")
        filesize = f.get("filesize") or f.get("filesize_approx")
        fps = f.get("fps")

        if height and height > 0:
            res_label = f"{height}p"
            quality_badge = "SD"
            if height >= 4320:
                quality_badge = "8K Ultra HD"
            elif height >= 2160:
                quality_badge = "4K Ultra HD"
            elif height >= 1440:
                quality_badge = "2K QHD"
            elif height >= 1080:
                quality_badge = "1080p Full HD"
            elif height >= 720:
                quality_badge = "720p HD"

            key = (height, fps if fps and fps >= 50 else 0)
            has_audio = (acodec != "none" and acodec is not None)

            est_size = filesize
            if est_size and not has_audio and duration_raw > 0:
                est_size += int((128 * 1024 / 8) * duration_raw)

            candidate = {
                "format_id": f.get("format_id"),
                "height": height,
                "width": width,
                "resolution": res_label,
                "fps": f"{int(fps)}fps" if fps else "",
                "quality_badge": quality_badge,
                "ext": "mp4",
                "has_audio": has_audio,
                "filesize_bytes": est_size,
                "filesize": human_filesize(est_size),
                "vcodec": vcodec,
                "preference": (10 if ext == "mp4" else 5) + (10 if has_audio else 0)
            }

            current = video_formats_map.get(key)
            if not current or candidate["preference"] > current["preference"]:
                video_formats_map[key] = candidate

    sorted_videos = sorted(video_formats_map.values(), key=lambda x: (x["height"], x.get("fps", "")), reverse=True)

    audio_presets = [
        {
            "id": "mp3-320",
            "name": "MP3 High Definition",
            "bitrate": "320 kbps",
            "quality_badge": "Best Quality",
            "ext": "mp3",
            "recommended": True,
            "description": "Studio grade MP3 with richest sound clarity."
        },
        {
            "id": "mp3-256",
            "name": "MP3 High Quality",
            "bitrate": "256 kbps",
            "quality_badge": "High",
            "ext": "mp3",
            "recommended": False,
            "description": "Crisp audio, slightly smaller file size."
        },
        {
            "id": "mp3-192",
            "name": "MP3 Standard",
            "bitrate": "192 kbps",
            "quality_badge": "Standard",
            "ext": "mp3",
            "recommended": False,
            "description": "Standard audio for mobile and earbuds."
        },
        {
            "id": "mp3-128",
            "name": "MP3 Compact",
            "bitrate": "128 kbps",
            "quality_badge": "Light",
            "ext": "mp3",
            "recommended": False,
            "description": "Fast download, low storage usage."
        },
        {
            "id": "m4a-original",
            "name": "Original M4A / AAC",
            "bitrate": "Source Stream",
            "quality_badge": "Lossless / Direct",
            "ext": "m4a",
            "recommended": False,
            "description": "Unconverted original source audio stream."
        }
    ]

    response_data = {
        "success": True,
        "title": title,
        "thumbnail": thumbnail,
        "duration": duration,
        "uploader": uploader,
        "view_count": f"{view_count:,}" if isinstance(view_count, int) else None,
        "webpage_url": webpage_url,
        "platform": platform_meta,
        "video_formats": sorted_videos,
        "audio_formats": audio_presets,
        "cached": False
    }

    # Store in metadata cache
    INFO_CACHE[norm_url] = {
        "timestamp": time.time(),
        "data": response_data
    }

    return response_data

def run_download_thread(job_id: str, payload: DownloadRequest):
    job = jobs[job_id]
    job["status"] = "downloading"
    job["progress"] = 0.0
    job["speed"] = "Connecting..."
    job["eta"] = "Estimating..."

    out_tmpl = str(DOWNLOADS_DIR / f"{job_id}_%(title).100s.%(ext)s")

    def progress_hook(d):
        if d.get("status") == "downloading":
            job["status"] = "downloading"
            downloaded = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            if total > 0:
                pct = round((downloaded / total) * 100, 1)
                job["progress"] = min(pct, 99.0)
            else:
                job["progress"] = 50.0

            speed_bytes = d.get("speed")
            if speed_bytes:
                job["speed"] = f"{round(speed_bytes / (1024*1024), 2)} MB/s"
            
            eta_sec = d.get("eta")
            if eta_sec:
                job["eta"] = f"{int(eta_sec)}s remaining"
            else:
                job["eta"] = "Almost ready"
                
        elif d.get("status") == "finished":
            job["status"] = "processing"
            job["progress"] = 99.0
            job["speed"] = "FFmpeg fast merging..."
            job["eta"] = "Finalizing..."

    # High performance download options:
    # 1. concurrent_fragment_downloads = 8 (Parallel stream download)
    # 2. http_chunk_size = 10MB (Maximizes network pipe)
    # 3. Stream copy with -c copy avoids expensive CPU re-encoding
    ydl_opts: Dict[str, Any] = {
        "ffmpeg_location": FFMPEG_PATH,
        "outtmpl": out_tmpl,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "cachedir": str(CACHE_DIR),
        "concurrent_fragment_downloads": 8,
        "http_chunk_size": 10485760,
    }
    if NODE_PATH:
        ydl_opts["js_runtimes"] = {"node": {"path": NODE_PATH}}

    media_type = payload.media_type
    if media_type == "audio":
        audio_q = payload.audio_quality or "320"
        if payload.ext == "m4a":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }]
        else:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_q,
            }]
            # Multi-threaded audio transcode
            ydl_opts["postprocessor_args"] = {
                "ffmpeg": ["-threads", "4", "-q:a", "0"]
            }
    else:
        # Video stream: Stream copy -c copy merges audio & video instantly without re-encoding!
        if payload.format_id:
            ydl_opts["format"] = f"{payload.format_id}+bestaudio/best"
        elif payload.resolution:
            h = payload.resolution.replace("p", "")
            ydl_opts["format"] = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best"
        else:
            ydl_opts["format"] = "bestvideo+bestaudio/best"
        
        ydl_opts["merge_output_format"] = "mp4"
        ydl_opts["postprocessor_args"] = {
            "merger": ["-c", "copy"]  # Ultra-fast container copy
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            extracted = ydl.extract_info(payload.url, download=True)
            filename = ydl.prepare_filename(extracted)
            
            base_no_ext, _ = os.path.splitext(filename)
            final_path = None
            for cand in [filename, f"{base_no_ext}.mp4", f"{base_no_ext}.mp3", f"{base_no_ext}.m4a", f"{base_no_ext}.webm"]:
                if os.path.exists(cand):
                    final_path = cand
                    break

            if not final_path:
                for f in os.listdir(DOWNLOADS_DIR):
                    if f.startswith(job_id):
                        final_path = str(DOWNLOADS_DIR / f)
                        break

            if final_path and os.path.exists(final_path):
                job["file_path"] = final_path
                job["filename"] = os.path.basename(final_path)
                job["status"] = "finished"
                job["progress"] = 100.0
                job["speed"] = "Completed"
                job["eta"] = "Ready"
                job["file_size"] = human_filesize(os.path.getsize(final_path))
            else:
                job["status"] = "error"
                job["error"] = "Download finished but file could not be located."

    except Exception as e:
        err_str = str(e)
        job["status"] = "error"
        if "Sign in" in err_str or "login" in err_str.lower():
            job["error"] = "This media is private or requires authentication to access."
        elif "DRM" in err_str.upper():
            job["error"] = "This media is protected by DRM encryption and cannot be downloaded."
        elif "429" in err_str or "rate limit" in err_str.lower():
            job["error"] = "Rate limit reached on source platform. Please wait a moment and try again."
        elif "Video unavailable" in err_str or "404" in err_str:
            job["error"] = "This video is unavailable, deleted, or region-restricted."
        elif "Unsupported URL" in err_str:
            job["error"] = "This URL format is not supported for media extraction."
        else:
            job["error"] = f"Download failed: {err_str[:250]}"

@app.post("/api/download/start")
async def start_download(payload: DownloadRequest):
    clean_old_jobs()
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id": job_id,
        "url": payload.url,
        "status": "queued",
        "progress": 0.0,
        "speed": "Starting...",
        "eta": "Calculating...",
        "created_at": time.time(),
        "error": None,
        "file_path": None,
        "filename": None
    }

    t = threading.Thread(target=run_download_thread, args=(job_id, payload), daemon=True)
    t.start()

    return {"success": True, "job_id": job_id}

@app.get("/api/download/status/{job_id}")
async def get_download_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found or expired.")
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "speed": job["speed"],
        "eta": job["eta"],
        "error": job.get("error"),
        "filename": job.get("filename"),
        "file_size": job.get("file_size"),
    }

@app.get("/api/download/file/{job_id}")
async def download_file(job_id: str, background_tasks: BackgroundTasks):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Download session expired or not found.")
    job = jobs[job_id]
    
    if job.get("status") == "error":
        raise HTTPException(status_code=400, detail=job.get("error", "Download process failed."))

    file_path = job.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File is not available or has expired.")
    
    clean_filename = os.path.basename(file_path)
    if clean_filename.startswith(job_id + "_"):
        clean_filename = clean_filename[len(job_id) + 1:]

    # 1. ASCII fallback for legacy HTTP latin-1 headers (prevents UnicodeEncodeError on emojis, fullwidth symbols, Hindi, etc.)
    ascii_fallback = re.sub(r"[^\w\.-]", "_", clean_filename) or f"{job_id}.mp4"
    # 2. RFC 5987 / RFC 6266 UTF-8 encoded filename for modern browsers
    encoded_filename = quote(clean_filename, encoding="utf-8")

    # Background cleanup of temporary file after stream delivery
    def remove_temp_file():
        time.sleep(20)  # Grace period for stream delivery
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

    background_tasks.add_task(remove_temp_file)

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{encoded_filename}'}
    )

@app.get("/api/supported-platforms")
async def get_supported_platforms():
    return {
        "categories": [
            {
                "name": "Popular Video & Social",
                "items": [
                    {"name": "YouTube", "desc": "Videos, Shorts, Playlists up to 8K 60fps", "supported": True, "badge": "8K / 4K / MP3"},
                    {"name": "Instagram", "desc": "Reels, Posts, Carousels, IGTV", "supported": True, "badge": "Full HD"},
                    {"name": "Facebook", "desc": "Public videos, Watch & Reels", "supported": True, "badge": "HD / MP4"},
                    {"name": "TikTok", "desc": "HD videos without watermark", "supported": True, "badge": "No Watermark"},
                    {"name": "Twitter / X", "desc": "Media clips, GIFs & video tweets", "supported": True, "badge": "High Res"},
                    {"name": "Reddit", "desc": "Native video posts with audio track", "supported": True, "badge": "Audio Merged"},
                ]
            },
            {
                "name": "Audio & Podcasts",
                "items": [
                    {"name": "SoundCloud", "desc": "High quality tracks & playlists", "supported": True, "badge": "320 kbps MP3"},
                    {"name": "Mixcloud", "desc": "DJ sets, podcasts, radio shows", "supported": True, "badge": "High Quality"},
                    {"name": "Bandcamp", "desc": "Artist releases and previews", "supported": True, "badge": "Lossless / MP3"},
                ]
            },
            {
                "name": "Cloud Drives & File Hosts",
                "items": [
                    {"name": "TeraBox", "desc": "Shared video & file links", "supported": True, "badge": "Direct Extract"},
                    {"name": "Vimeo", "desc": "Creator videos, 1080p / 4K", "supported": True, "badge": "Original Res"},
                    {"name": "Dailymotion", "desc": "Channels and viral streams", "supported": True, "badge": "All Qualities"},
                    {"name": "Twitch", "desc": "Broadcast clips & highlights", "supported": True, "badge": "1080p 60fps"},
                ]
            },
            {
                "name": "Special Platforms Notice",
                "items": [
                    {
                        "name": "Disney+ Hotstar",
                        "desc": "Uses commercial Widevine DRM encryption. Third-party extractors cannot bypass DRM-protected content.",
                        "supported": False,
                        "badge": "DRM Protected"
                    },
                    {
                        "name": "WhatsApp",
                        "desc": "End-to-end encrypted private messaging. Media is stored locally on your device storage.",
                        "supported": False,
                        "badge": "End-to-End Encrypted"
                    },
                    {
                        "name": "Google Chrome",
                        "desc": "Browser itself. Copy and paste any media page link directly from the URL bar.",
                        "supported": True,
                        "badge": "Paste Direct Link"
                    }
                ]
            }
        ]
    }

# Mount static files for HTML/CSS/JS
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting OmniStream High-Speed server on http://localhost:8000")
    print(f"🔧 Using FFmpeg at: {FFMPEG_PATH}")
    print(f"⚡ Node.js JS runtime: {NODE_PATH}")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
