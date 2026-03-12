@echo off
cd /d "%~dp0"
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;C:\Program Files\Python312;C:\Program Files (x86)\Python312;%PATH%"
chcp 65001 >nul
echo === Setup Python 3.12 de obfuscate (PyArmor) ===
echo.

set "PY312="
if exist "C:\Program Files\Python312\python.exe" set "PY312=C:\Program Files\Python312\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY312=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
where py >nul 2>&1
if errorlevel 1 if not defined PY312 (
    echo [Loi] Khong tim thay Python 3.12. Cai tai: https://www.python.org/downloads/release/python-3120/
    pause
    exit /b 1
)

echo Tao venv voi Python 3.12...
if defined PY312 (
    "%PY312%" -m venv venv312
) else (
    py -3.12 -m venv venv312
)
if errorlevel 1 (
    echo.
    echo [Loi] Python 3.12 chua cai. Tai tai: https://www.python.org/downloads/release/python-3120/
    echo       Chon "Windows installer (64-bit)" va cai. Nho tick "Add to PATH".
    pause
    exit /b 1
)

echo.
echo Cai dat package...
call venv312\Scripts\activate.bat
pip install "pyinstaller==5.10.1" pyarmor setproctitle --quiet

echo.
echo [OK] Xong. Gio chay build_protected.bat de build co obfuscate.
pause
