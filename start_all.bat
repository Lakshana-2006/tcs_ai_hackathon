@echo off
echo ============================================================
echo   HEATSHIELD AI — Urban Climate Resilience Digital Twin
echo   Launching Backend and Frontend services...
echo ============================================================
start "HEATSHIELD AI - Backend API" cmd /c "start_backend.bat"
timeout /t 3 /nobreak >nul
start "HEATSHIELD AI - Frontend UI" cmd /c "start_frontend.bat"
echo.
echo Services launched!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo ============================================================

