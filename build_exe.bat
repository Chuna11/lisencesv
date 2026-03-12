@echo off
cd /d "%~dp0"
set "PATH=%LOCALAPPDATA%\Programs\Python\Python313\Scripts;C:\Program Files\Python313\Scripts;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;C:\Program Files\Python314\Scripts;%PATH%"
chcp 65001 >nul
echo === Build RzStats.exe ===

set "PY=py -3"
py -3.13 -c "" 2>nul && set "PY=py -3.13"
%PY% -m pip install pyinstaller setproctitle pywin32-ctypes --quiet
%PY% -m PyInstaller --noconfirm ColorAim.spec

if %errorlevel% equ 0 (
    if exist r0.json copy r0.json dist\RzStats\ >nul
    echo.
    echo [OK] Build xong: dist\RzStats\RzStats.exe
    echo.
    echo Huong dan:
    echo - Chay RzStats.exe (se yeu cau UAC neu chua co quyen admin)
    echo - Mo trinh duyet: http://localhost:8000
    echo - Neu bi Windows Defender chan: Them thư muc dist\RzStats vao Exclusion
    echo - Dat vao thu muc gan Razer (VD: C:\Program Files (x86)\Razer\) de giam nghy
) else (
    echo [Loi] Build that bai
)

pause
