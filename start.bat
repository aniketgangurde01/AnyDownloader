@echo off
title OmniStream - Universal Downloader
echo ========================================================
echo  OmniStream - High Performance Video & Audio Downloader
echo ========================================================
echo.
echo Starting backend server on http://localhost:8000 ...
py -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
pause
