#!/bin/bash
set -e

echo "[*] Cleaning previous builds..."

echo "[*] Packaging STEM Week User App for macOS..."
# --windowed: builds a macOS .app bundle without terminal window
# --add-data: includes the .tcss file inside the app bundle
# --name: sets the app name

pyinstaller \
    --windowed \
    --add-data "app/questionProtocol.tcss:." \
    --name "StemWeek_User_App" \
    app/dashboardProtocol.py

echo
echo "[OK] Build successful!"
echo "[OK] Your macOS app bundle is in: dist/StemWeek_User_App.app"