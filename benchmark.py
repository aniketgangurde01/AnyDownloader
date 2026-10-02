import time
import yt_dlp

url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
NODE_PATH = r"C:\Users\APMC\AppData\Local\Programs\nodejs\node.exe"

# Benchmark 1: Standard
t0 = time.time()
with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
    info1 = ydl.extract_info(url, download=False)
t1 = time.time() - t0
print(f"Standard: {t1:.2f}s, formats={len(info1.get('formats', []))}")

# Benchmark 2: Tuned options
t0 = time.time()
opts_tuned = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
    "noplaylist": True,
    "socket_timeout": 8,
    "no_color": True,
    "js_runtimes": {"node": {"path": NODE_PATH}},
}
with yt_dlp.YoutubeDL(opts_tuned) as ydl:
    info2 = ydl.extract_info(url, download=False)
t2 = time.time() - t0
print(f"Tuned: {t2:.2f}s, formats={len(info2.get('formats', []))}")

# Benchmark 3: Cache simulation
cache = {url: info2}
t0 = time.time()
cached_info = cache.get(url)
t3 = time.time() - t0
print(f"Cache hit: {t3*1000:.3f}ms")
