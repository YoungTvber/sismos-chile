@echo off
REM Genera dist\DashboardSismos.exe (requiere Python instalado en Windows)
pip install pyinstaller pandas numpy matplotlib
pyinstaller --noconfirm --onefile --windowed --name DashboardSismos ^
  --hidden-import matplotlib.backends.backend_tkagg ^
  --add-data "datos\procesados\dataset_limpio.csv;datos\procesados" ^
  --add-data "src;src" app.py
echo.
echo Listo: dist\DashboardSismos.exe
pause
