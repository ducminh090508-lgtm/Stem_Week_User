#!/bin/bash
set -e

echo "[*] Cleaning previous builds..."

echo "[*] Packaging STEM Week User App for macOS..."
# --windowed: builds a macOS .app bundle without terminal window
# --add-data: includes the .tcss file inside the app bundle
# --name: sets the app name

ls main.py

pyinstaller \
    --windowed --clean \
    --add-data "app/interface/question.tcss:app/interface" \
    --add-data "app/interface/dashboard.tcss:app/interface" \
    --collect-all websockets \
    --name "StemWeek_User_App" \
    main.py

echo
echo "[OK] Build successful!"
echo "[OK] Your macOS app bundle is in: dist/StemWeek_User_App.app"
