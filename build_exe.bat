@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo  Chopster by Aris v8.2 - Build EXE
 echo ========================================
where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo [WARN] Perintah pyinstaller tidak ada di PATH. Mencoba python -m PyInstaller...
  python -m PyInstaller --version >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] PyInstaller tidak ditemukan. Jalankan install_dependencies.bat terlebih dahulu.
    exit /b 1
  )
  set "PYI=python -m PyInstaller"
) else (
  set "PYI=pyinstaller"
)
where ffmpeg >nul 2>&1
if errorlevel 1 echo [WARN] FFmpeg tidak ada di PATH. Letakkan ffmpeg.exe dan ffprobe.exe di sebelah EXE hasil build.

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Chopster by Aris.spec" del /q "Chopster by Aris.spec"

%PYI% --noconfirm --clean --windowed --name "Chopster by Aris" ^
  --icon "resources\icons\app.ico" ^
  --add-data "resources;resources" ^
  --add-data "browser_extension;browser_extension" ^
  --hidden-import "yt_dlp" ^
  --hidden-import "yt_dlp_ejs" ^
  --hidden-import "av" ^
  --hidden-import "ctranslate2" ^
  --hidden-import "cv2" ^
  --hidden-import "chopster.ai.local_provider" ^
  --hidden-import "chopster.ai.embedded_gemini" ^
  --collect-data "yt_dlp_ejs" ^
  --collect-all "faster_whisper" ^
  --collect-all "ctranslate2" ^
  --collect-all "av" ^
  --collect-all "cv2" ^
  --collect-submodules "yt_dlp" ^
  --collect-data "PIL" ^
  --collect-all "PySide6.QtMultimedia" ^
  main.py

if errorlevel 1 (
  echo [ERROR] Build gagal.
  exit /b 1
)

echo.
echo ========================================
echo  Build selesai.
echo  Folder: dist\Chopster by Aris\
echo  EXE: dist\Chopster by Aris\Chopster by Aris.exe
echo.
echo  Untuk subtitle/transkripsi lokal, model Whisper akan diunduh saat pertama kali dipakai.
echo  Pastikan ffmpeg.exe + ffprobe.exe tersedia di PATH atau di sebelah EXE.
echo ========================================
endlocal


REM Bundle Deno next to the onedir EXE when available, so YouTube works
REM without a separate runtime installation on the target PC.
if exist "%~dp0deno.exe" (
  if exist "%~dp0dist\Chopster by Aris" copy /Y "%~dp0deno.exe" "%~dp0dist\Chopster by Aris\deno.exe" >nul
  if exist "%~dp0dist\Chopster" copy /Y "%~dp0deno.exe" "%~dp0dist\Chopster\deno.exe" >nul
)
