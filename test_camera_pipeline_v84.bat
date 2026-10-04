@echo off
setlocal
cd /d "%~dp0.."
set PYTHONPATH=.
python -m pytest -q chopster\tests\test_v84_camera_ai_move.py chopster\tests\test_camera_director.py
if errorlevel 1 (
  echo [FAIL] Camera AI pipeline regression test failed.
  pause
  exit /b 1
)
echo [OK] Camera AI pipeline tests passed.
pause
