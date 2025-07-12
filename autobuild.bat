@echo off
color 0A
echo === Compiling Hunting Calculator ===

where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not installed. Run: pip install pyinstaller
    pause
    exit /b
)

if exist dist (
    echo === Removing dist folder ===
    rmdir /s /q dist
) else (
    echo dist folder not found, skipping delete.
)

pyinstaller --noconfirm --onefile --windowed ^
--icon "res\icons\app_icons\matchlock.ico" ^
--name "Hunting Calculator" ^
--add-data "res;res" ^
"src\main.py"

echo Cleaning temp files...
if exist "Hunting Calculator.spec" (
    echo === Removing Hunting Calculator.spec ===
    del "Hunting Calculator.spec"
)

if exist "build" (
    echo === Removing build folder ===
    rmdir /s /q build
) else (
    echo build folder not found, skipping delete.
)

echo.
echo === Build ready! ===
echo Output: dist\Hunting Calculator.exe

pause
