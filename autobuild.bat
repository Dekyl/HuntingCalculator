@echo off
echo Compiling Hunting Calculator...

pyinstaller --noconfirm --onefile --windowed --icon ".\res\matchlock.ico" --name "Hunting Calculator" --add-data ".\res;res/" ".\src\main.py"

echo Cleaning temp files...

del "Hunting Calculator.spec"

rmdir /s /q build

echo Build ready, .exe at:
echo dist\Hunting Calculator.exe

pause
