@echo off
setlocal
cd /d "%~dp0"
set "DASHBOARD_PY="
where py >nul 2>nul
if not errorlevel 1 set "DASHBOARD_PY=py"
if not defined DASHBOARD_PY (
    where python >nul 2>nul
    if not errorlevel 1 set "DASHBOARD_PY=python"
)
if not defined DASHBOARD_PY if exist "%LocalAppData%\Python\pythoncore-3.14-64\python.exe" set "DASHBOARD_PY=%LocalAppData%\Python\pythoncore-3.14-64\python.exe"
if not defined DASHBOARD_PY (
    echo Python 3.10 or later is required. Please use your dashboard's normal Python installation.
    pause
    exit /b 1
)
"%DASHBOARD_PY%" scripts\import_dashboard.py --source "..\..\Design_Performance.html"
if errorlevel 1 goto failed
"%DASHBOARD_PY%" scripts\build.py
if errorlevel 1 goto failed
echo.
echo READY TO UPLOAD. No files have been sent to GitHub yet.
echo 1. Upload site\dashboards\sample\index.html into the GitHub sample folder.
echo 2. Upload dashboards.json into the GitHub repository root.
echo Read HOW_TO_PUBLISH.md for the exact links and steps.
echo.
pause
exit /b 0
:failed
echo.
echo STOPPED. The new dashboard has not been published. Review the error above.
pause
exit /b 1
