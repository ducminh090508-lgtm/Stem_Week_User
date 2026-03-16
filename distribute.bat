@echo off
echo [*] Cleaning previous builds...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo [*] Packaging STEM Week User App...
:: --onefile: Bundles everything into a single .exe
:: --noconsole: Prevents a command prompt from popping up (optional, keep off for debugging TUIs)
:: --add-data: Includes the .tcss file inside the .exe bundle
:: --name: Sets the name of the output executable

pyinstaller --onefile ^
    --add-data "app\questionProtocol.tcss;." ^
    --name "StemWeek_User_App" ^
    app\dashboardProtocol.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo [OK] Build Successful! 
    echo [OK] Your standalone executable is in: dist\StemWeek_User_App.exe
) else (
    echo [!] Build Failed.
)
pause
