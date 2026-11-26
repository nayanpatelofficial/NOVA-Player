@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  python --version >nul 2>nul
  if %errorlevel%==0 (
    set "PY=python"
  ) else (
    if exist "%LocalAppData%\Programs\Python\Python315\python.exe" (
      set "PY="%LocalAppData%\Programs\Python\Python315\python.exe""
    ) else if exist "%LocalAppData%\Programs\Python\Python314\python.exe" (
      set "PY="%LocalAppData%\Programs\Python\Python314\python.exe""
    ) else if exist "%LocalAppData%\Programs\Python\Python313\python.exe" (
      set "PY="%LocalAppData%\Programs\Python\Python313\python.exe""
    ) else (
      echo Python 3 was not found. Install Python from https://www.python.org/downloads/windows/
      echo During installation, enable "Add python.exe to PATH", then run this file again.
      pause
      exit /b 1
    )
  )
)

if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
  if errorlevel 1 goto failed
)

call ".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
call ".venv\Scripts\python.exe" main.py
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Setup or startup failed. Check the error above and confirm internet access for dependency installation.
pause
exit /b 1
