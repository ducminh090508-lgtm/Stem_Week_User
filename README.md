# STEM WEEK User App

A standalone terminal-based application for teams to participate in STEM Week competitions.

[📄 System Architecture & API Documentation](documentation.txt)

## Download & Fast Start

### Windows (Recommended)
1. **Download**: Get the latest `StemWeek_User_Portal.exe` from the [GitHub Releases](https://github.com/ducminh090508-lgtm/Stem_Week_User/releases).
2. **Configure**: Update the `ip` field with the server IP provided by the administrator.
3. **Run**: Double-click `StemWeek_User_Portal.exe` to start.

### MacOS (Horrible experience setting it up)
1. **Download**: Get the latest `StemWeek_User_Portal.app` from the [GitHub Releases](https://github.com/ducminh090508-lgtm/Stem_Week_User/releases)
2. **Configure**: Update the `ip` field with the server IP provided by administrator
3. **Run**: Right click `Stem_Week_User_Portal.app` > Show Package Contents > Contents > macOS > `Stem_Week_User_App` to start
---

## Features

- **Team Login**: Secure PIN-based access for team participation
- **Question Interface**: Interactive module selection for different subjects (BIO, CHEM, MATH & PHYSICS, CS)
- **Real-time Timer**: Live countdown timer synced with server
- **Live Leaderboard**: View team standings and rankings
- **Answer Submission**: Submit answers with instant feedback
- **Multi-page Navigation**: Easy switching between questions, timer, and leaderboard

## Manual Setup (Developers / macOS / Linux)

### Installation
1. Clone this repository or download the source code.
2. Open your terminal and navigate to the folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Update `config.ini` with your server IP address.
5. Run the app:
   ```bash
   python main.py
   ```

*(On macOS/Linux, you may need to use `python3` and `pip3`)*

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

## System Requirements

- Windows 10/11 (for `.exe`) OR Python 3.8+
- Terminal/Command Prompt with UTF-8 support
- Network connection to access the competition server
