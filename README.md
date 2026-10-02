# 🎬 OmniStream — Universal Video & Audio Downloader

A full-stack, high-performance web application that extracts and downloads video and audio streams from virtually any public link with all available resolutions, formats, and audio extraction options.

---

## ✨ Key Features

1. **All Possible Video Qualities**:
   - **8K Ultra HD** (4320p)
   - **4K Ultra HD** (2160p)
   - **2K QHD** (1440p)
   - **1080p Full HD** (60fps & 30fps)
   - **720p HD**, **480p SD**, **360p**, and more.
   - *Automatic Stream Merging*: High-resolution video streams on platforms like YouTube are merged with high-bitrate audio streams using an integrated standalone **FFmpeg** pipeline into standard `.mp4`.

2. **Select Video or Song / Music / Audio Only**:
   - Dedicated **Audio Only (Music)** selector:
     - **320 kbps Studio MP3** (Richer, highest fidelity)
     - **256 kbps MP3** (High quality)
     - **192 kbps MP3** (Balanced standard)
     - **128 kbps MP3** (Compact, lightweight)
     - **Original M4A / AAC** (Direct lossless stream)

3. **Multi-Platform Support**:
   - **YouTube**: Videos, Shorts, Music
   - **Instagram**: Reels, Posts, IGTV, Video Carousels
   - **Facebook**: Public videos, Watch, and Reels
   - **TikTok**: HD videos without watermark
   - **Twitter / X**: Video tweets and clips
   - **TeraBox**: Shared video download links
   - **Reddit**: Native video posts with merged sound
   - **SoundCloud / Bandcamp**: Music tracks and playlists
   - **Vimeo, Dailymotion, Twitch Clips**, and 1,800+ other sites supported by the `yt-dlp` engine.

4. **Real-Time Progress & Speed Tracking**:
   - Live download percentage bar (`0% - 100%`)
   - Download speed indicator (e.g. `12.5 MB/s`) and estimated time remaining (ETA).
   - Multi-step status indicator: `Extract Stream` ➔ `FFmpeg Merging` ➔ `Ready to Save`.

---

## 🔒 Platform Specifics & Technical Notes

- **Disney+ Hotstar, Netflix, Prime Video**: Commercial subscription services protect their video library using **Widevine DRM (Digital Rights Management)**. Public media tools cannot decrypt DRM-protected streams. The application detects and informs users gracefully.
- **WhatsApp**: Messages and status updates are end-to-end encrypted private files with no public web URLs. WhatsApp status and media are stored locally on your device storage (e.g., inside WhatsApp Media directory).
- **Google Chrome**: Chrome is a browser. You can copy any video or audio page URL directly from your Chrome address bar and paste it into OmniStream.

---

## 🚀 Quick Start Guide

### 1. Launch the Server
Open a terminal in `C:\Users\APMC\.gemini\antigravity\scratch\universal-downloader` and run:

```bash
# Using python launcher
py -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Or simply double-click `start.bat`.

### 2. Open the Web App
Open your web browser and navigate to:
```
http://localhost:8000
```

### 3. Download Media
1. Copy any video or music link.
2. Click **Paste** or press `Ctrl + V`.
3. Click **Extract Streams**.
4. Choose **Video** (pick your resolution) or **Audio Only** (pick your MP3 bitrate).
5. Click **Download** and watch the real-time progress!

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14 + FastAPI + Uvicorn
- **Engine**: `yt-dlp` + standalone `imageio-ffmpeg`
- **Frontend**: Modern Vanilla JS, CSS3 (Glassmorphism, CSS Grid, Fluid Typography, Animated Glowing Orbs), Accessible HTML5
