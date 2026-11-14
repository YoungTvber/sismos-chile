@echo off
REM Genera dist\DashboardSismos.exe (requiere Python instalado en Windows)
cd /d "%~dp0"

set PY=
py --version >nul 2>&1 && set PY=py
if not defined PY (python --version >nul 2>&1 && set PY=python)
if not defined PY (
  echo No se encontro Python. Instalelo desde https://www.python.org/downloads/
  echo y marque la casilla "Add python.exe to PATH" durante la instalacion.
  pause
  exit /b 1
)

echo Usando: %PY%
%PY% -m pip install pyinstaller pandas numpy matplotlib
if errorlevel 1 goto error

%PY% -m PyInstaller --noconfirm --onefile --windowed --name DashboardSismos ^
  --hidden-import matplotlib.backends.backend_tkagg ^
  --add-data "datos\procesados\dataset_limpio.csv;datos\procesados" ^
  --add-data "src;src" app.py
if errorlevel 1 goto error

if exist "dist\DashboardSismos.exe" (
  echo.
  echo Listo: dist\DashboardSismos.exe
  pause
  exit /b 0
)

:error
echo.
echo Hubo un error. Revise los mensajes de arriba.
pause
exit /b 1
