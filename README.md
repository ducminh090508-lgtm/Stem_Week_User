# STEM WEEK User App

A standalone terminal-based application for teams to participate in STEM Week competitions.

## Features

- **Team Login**: Secure PIN-based access for team participation
- **Question Interface**: Interactive module selection for different subjects (BIO, CHEM, MATH & PHYSICS, CS)
- **Real-time Timer**: Live countdown timer synced with server
- **Live Leaderboard**: View team standings and rankings
- **Answer Submission**: Submit answers with instant feedback
- **Multi-page Navigation**: Easy switching between questions, timer, and leaderboard

## Quick Start

### Windows

1. Extract the user-app folder
2. Open Command Prompt and navigate to the user-app folder
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Update `config.ini` with your server IP address
5. Run the app:
   ```
   python main.py
   ```
   or double-click `run.bat`

### macOS / Linux

1. Extract the user-app folder
2. Open Terminal and navigate to the user-app folder
3. Ensure you have the `python3-venv` package installed (e.g. `sudo apt install python3-venv`).
4. Install dependencies:
   ```
   pip3 install -r requirements.txt
   ```
   *(or simply run `./run.sh` which installs automatically)*
5. Update `config.ini` with your server IP address
6. Make launcher executable once:
   ```sh
   chmod +x run.sh
   ```
7. Run the app:
   ```sh
   ./run.sh
   ```
   or `python3 main.py`

> The launcher will create a `.venv` directory on first run and install all dependencies inside it, avoiding system-wide package installs.

## Configuration

Edit `config.ini` to set your server connection:

```ini
[server]
ip = 192.168.1.100      # Change to your server IP
port = 8080             # Change if using a different port
```

## Keyboard Controls

### Login Screen
- Type your team PIN and press Enter

### Question Screen
- `1` - Questions
- `2` - Timer
- `3` - Leaderboard
- `escape` - Back to questions
- `q` - Quit

### Entering Answers
- Type your answer and press Enter

## Team PINs

Default team PINs (can be configured):
- `1001` - test1
- `1002` - test2
- `1234` - Team Alpha
- `5678` - Team Beta

## Troubleshooting

**Can't connect to server**
- Verify the server IP in `config.ini` is correct
- Ensure the server is running and accessible on port 8080
- Check firewall settings

**Can't find team PIN**
- Contact your event administrator to confirm your team PIN
- Ensure you're using the correct PIN (case-sensitive)

**Import errors or missing packages**
- Delete the `__pycache__` folder and try again
- Reinstall requirements: `pip install --upgrade -r requirements.txt`

## System Requirements

- Python 3.8+
- Windows, macOS, or Linux
- Terminal/Command Prompt with UTF-8 support
- Internet connection to access server
