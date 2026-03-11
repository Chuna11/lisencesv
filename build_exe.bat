@echo off
chcp 65001 >nul
echo === Build RzStats.exe ===

python -m pip install pyinstaller setproctitle --quiet 2>nul
python -m PyInstaller --noconfirm ColorAim.spec

if %errorlevel% equ 0 (
    if exist r0.json copy r0.json dist\RzStats\ >nul
    echo.
    echo [OK] Build xong: dist\RzStats\RzStats.exe
    echo.
    echo Huong dan:
    echo - Chay RzStats.exe (se yeu cau UAC neu chua co quyen admin)
    echo - Mo trinh duyet: http://127.0.0.1:5873
    echo - Neu bi Windows Defender chan: Them thư muc dist\RzStats vao Exclusion
    echo - Dat vao thu muc gan Razer (VD: C:\Program Files (x86)\Razer\) de giam nghy
) else (
    echo [Loi] Build that bai
)

pause
