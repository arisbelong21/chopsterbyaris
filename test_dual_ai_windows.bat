@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"
echo ========================================
echo Chopster Dual AI Audit v8.2
echo ========================================
python -m pytest -q tests/test_dual_ai_vision_final.py tests/test_ai_vision_integration.py tests/test_ai_failover.py tests/test_full_ai_integration.py
if errorlevel 1 (
  echo.
  echo [FAIL] Dual AI audit gagal.
  pause
  exit /b 1
)
echo.
echo [PASS] Dual AI + Vision + Failover audit selesai.
pause
