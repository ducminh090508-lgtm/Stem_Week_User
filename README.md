# STEM WEEK User App

A standalone terminal-based application for teams to participate in STEM Week competitions.

[System Architecture & API Documentation](documentation.txt)

## Download & Fast Start

### Windows (Recommended)
1. **Download**: Get the latest `StemWeek_User_Portal.exe` from the [GitHub Releases](https://github.com/ducminh090508-lgtm/Stem_Week_User/releases).
2. **Run**: Double-click `StemWeek_User_Portal.exe` to start.
3. **Blocked**: Windows Defender will say my app is suspicious, don't worry all I do is track ur public IP address.
<img width="261" height="238" alt="{7273D1C1-1EB0-448A-B24F-27E6CCDD551B}" src="https://github.com/user-attachments/assets/77445ebd-e280-49bc-8ead-174661ceac8c" />

4. **Authorize**: Click on more info > Run anyway
<img width="230" height="213" alt="{A16F7980-5CBB-4227-8DE0-8EAFF9F3B03A}" src="https://github.com/user-attachments/assets/16f46015-a252-4224-ace5-f31d2d8e489e" />

5. **Configure**: You'll be prompted to enter the server IP, which will be provided by your administrator

### MacOS
1. **Download**: Get the latest `StemWeek_User_Portal.zip` from the [GitHub Releases](https://github.com/ducminh090508-lgtm/Stem_Week_User/releases)
2. **Run**: Unzip the file (if needed), Right click `StemWeek_User_Portal.app` > Show Package Contents > Contents > macOS > `StemWeek_User_App`
3. **Blocked**: MacOS will prevent the program from running, do not panic. 
<img width="245" height="266" alt="Screenshot 2026-03-18 at 12 34 30" src="https://github.com/user-attachments/assets/a8601506-3a21-41e5-8f2d-407b4164dd2f" />

4. **Authorize**: Navigate to your System Settings > Privacy & Security, scroll down and you should see something like this. Click `Open Anyway`
<img width="451" height="111" alt="Screenshot 2026-03-18 at 12 33 53" src="https://github.com/user-attachments/assets/bfb6ba5f-be20-43bc-a9e3-d71860096c02" />

You will also be prompted to allow the .app file to run, just allow it anyways and run the terminal application (shown here)

<img width="119" height="120" alt="Screenshot 2026-03-18 at 12 40 27" src="https://github.com/user-attachments/assets/f1900329-9400-4688-a14a-42f8e6b74003" />

(Note: The .app file will never run on its own, you will need to run the terminal application)

5. **Configure**: You'll be prompted to enter the server IP, which will be provided by your administrator
<img width="553" height="108" alt="Screenshot 2026-03-18 at 12 44 44" src="https://github.com/user-attachments/assets/ffd9278f-4732-47dd-8828-635d10dd684b" />

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
