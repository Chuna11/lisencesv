@echo off
chcp 65001 >nul
setlocal

set "EXE=dist\RzStats\RzStats.exe"
set "EXE_PROT=dist\RzStats\RzStats_protected.exe"
set "VMP="

if defined VMPROTECT_PATH (
    set "VMP=%VMPROTECT_PATH%\VMProtect_Con.exe"
    if exist "%VMP%" goto :run_vmp
)
if exist "C:\Program Files\VMProtect\VMProtect_Con.exe" set "VMP=C:\Program Files\VMProtect\VMProtect_Con.exe" & goto :run_vmp
if exist "C:\Program Files (x86)\VMProtect\VMProtect_Con.exe" set "VMP=C:\Program Files (x86)\VMProtect\VMProtect_Con.exe" & goto :run_vmp
if exist "C:\Program Files\VMProtect Demo\VMProtect_Con.exe" set "VMP=C:\Program Files\VMProtect Demo\VMProtect_Con.exe" & goto :run_vmp

echo === Build RzStats + VMProtect ===
echo.
echo [Loi] Khong tim thay VMProtect_Con.exe
echo.
echo Cai dat VMProtect roi set duong dan:
echo   set VMPROTECT_PATH=C:\Program Files\VMProtect
echo.
echo Hoac dat VMProtect_Con.exe tai: C:\Program Files\VMProtect\
echo.
pause
exit /b 1

:run_vmp
echo === Build RzStats + VMProtect ===
echo.

if not exist "%EXE%" (
    echo [1/2] Build exe truoc (chua co)...
    pip install pyinstaller pyarmor setproctitle --quiet 2>nul
    pyarmor gen --pack ColorAim.spec -r q7.py m2.py k9.py p4.py t1.py w6.py n3.py v8.py x0.py license_key.py
    if %errorlevel% neq 0 (
        pyinstaller --noconfirm ColorAim.spec
    )
    if exist r0.json copy r0.json dist\RzStats\ >nul 2>nul
    if not exist "%EXE%" (
        echo [Loi] Build that bai. Chay build_protected.bat truoc.
        pause
        exit /b 1
    )
) else (
    echo [1/2] Da co exe, bo qua build.
)

echo.
echo [2/2] Protect voi VMProtect...
if exist "RzStats.vmp" (
    "%VMP%" "%EXE%" "%EXE_PROT%" -pf RzStats.vmp
) else (
    "%VMP%" "%EXE%" "%EXE_PROT%"
)

if %errorlevel% neq 0 (
    echo.
    echo [Loi] VMProtect that bai. Console version chi co o ban Standard/Ultimate.
    echo       Ban Lite khong co VMProtect_Con.exe.
    pause
    exit /b 1
)

echo.
echo Thay exe goc bang ban da protect...
copy /Y "%EXE_PROT%" "%EXE%" >nul
del "%EXE_PROT%" 2>nul

echo.
echo [OK] Xong: %EXE% (da duoc VMProtect)
echo.
echo Luu y: Tao RzStats.vmp trong VMProtect GUI de tuy chinh bao ve.
pause
