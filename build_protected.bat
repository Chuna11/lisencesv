@echo off
cd /d "%~dp0"
chcp 65001 >nul

if exist venv312\Scripts\python.exe (
    call venv312\Scripts\activate.bat
    set "PYARMOR_PYTHON=venv312"
)
set "PATH=%APPDATA%\Python\Python312\Scripts;C:\Program Files\Python312\Scripts;%APPDATA%\Python\Python314\Scripts;C:\Program Files\Python314\Scripts;%PATH%"

echo === Build RzStats (BAO VE SOURCE - PyArmor) ===
echo.

if defined PYARMOR_PYTHON (
    python -m pip install "pyinstaller==5.10.1" pyarmor setproctitle --quiet
) else (
    python -m pip install pyinstaller pyarmor setproctitle --quiet
)
if errorlevel 1 (
    echo [Loi] pip install that bai
    pause
    exit /b 1
)

echo [1/2] Obfuscating va pack voi PyArmor...
pyarmor gen --pack ColorAim.spec -r q7.py m2.py k9.py p4.py t1.py w6.py n3.py v8.py x0.py license_key.py
if errorlevel 1 (
    echo.
    echo [Thu lai] Obfuscate don gian...
    pyarmor gen --pack ColorAim.spec -r q7.py m2.py k9.py p4.py t1.py w6.py n3.py v8.py x0.py license_key.py
)
if errorlevel 1 (
    echo.
    echo [Loi] PyArmor that bai.
    echo.
    echo De obfuscate chay duoc, dung Python 3.12:
    echo   Chay setup_obfuscate.bat (tao venv + cai PyInstaller 5.10.1, PyArmor)
    echo   Roi chay lai build_protected.bat
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] Post-build...
if exist r0.json copy r0.json dist\RzStats\ >nul 2>nul
if exist .pyarmor\pack\dist (
    echo [OK] Build xong: dist\RzStats\RzStats.exe
    echo     Source da duoc obfuscate bang PyArmor
) else (
    echo [OK] Build xong: dist\RzStats\RzStats.exe
)

echo.
echo Huong dan:
echo - Chay RzStats.exe (se yeu cau UAC neu chua co quyen admin)
echo - Mo trinh duyet: http://localhost:8000
echo - Xem PROTECTION.md de biet them cac cach bao ve khac
pause
