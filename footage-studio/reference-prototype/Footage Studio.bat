@echo off
REM Footage Studio - Windows launcher. Double-click to open the app.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 isn't installed. Get it from https://www.python.org/downloads/
  echo IMPORTANT: tick "Add python.exe to PATH" during install.
  pause
  exit /b 1
)
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo ffmpeg isn't installed.
  echo Download a build from https://www.gyan.dev/ffmpeg/builds/ , unzip,
  echo and add the bin folder to your PATH.
  pause
  exit /b 1
)

python footage_studio.py
