from __future__ import annotations
import sys
import os
import asyncio

# Ensure the parent directory is in the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Header, Footer

from app.functions.dashboard import DashboardService, parse_args
from app.interface import question

# Utility to locate bundled resources when running as a PyInstaller executable
def resource_path(relative_path: str) -> str:
    """Resolve a path to bundled resources.

    Tries several locations so that both development runs and PyInstaller
    single-file executables can find the file. Returns the first existing
    candidate, or a sensible default path.
    """
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")

    candidates = [
        os.path.join(base_path, relative_path),
        os.path.join(base_path, os.path.basename(relative_path)),
        os.path.abspath(relative_path),
    ]

    for cand in candidates:
        if os.path.exists(cand):
            return cand

    # Return first candidate (likely the bundled location) so the caller
    # receives a consistent path even if the file is missing.
    return candidates[0]

class DashboardApp(App):
    # Resolve CSS path so it works when running from source and when bundled by PyInstaller
    CSS_PATH = resource_path("app/interface/dashboard.tcss")

    def __init__(self, server_ip: str, server_port: int = 8080, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_service = DashboardService(target_ip=server_ip, port=server_port)

    def compose(self) -> ComposeResult:
        duckAscii = """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣉⡥⠶⢶⣿⣿⣿⣿⣷⣆⠉⠛⠿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡿⢡⡞⠁⠀⠀⠤⠈⠿⠿⠿⠿⣿⠀⢻⣦⡈⠻⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡇⠘⡁⠀⢀⣀⣀⣀⣈⣁⣐⡒⠢⢤⡈⠛⢿⡄⠻⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡇⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠉⠐⠄⡈⢀⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠇⢠⣿⣿⣿⣿⡿⢿⣿⣿⣿⠁⢈⣿⡄⠀⢀⣀⠸⣿⣿⣿⣿
⣿⣿⣿⣿⡿⠟⣡⣶⣶⣬⣭⣥⣴⠀⣾⣿⣿⣿⣶⣾⣿⣧⠀⣼⣿⣷⣌⡻⢿⣿
⣿⣿⠟⣋⣴⣾⣿⣿⣿⣿⣿⣿⣿⡇⢿⣿⣿⣿⣿⣿⣿⡿⢸⣿⣿⣿⣿⣷⠄⢻
⡏⠰⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⢂⣭⣿⣿⣿⣿⣿⠇⠘⠛⠛⢉⣉⣠⣴⣾
⣿⣷⣦⣬⣍⣉⣉⣛⣛⣉⠉⣤⣶⣾⣿⣿⣿⣿⣿⣿⡿⢰⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡘⣿⣿⣿⣿⣿⣿⣿⣿⡇⣼⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⢸⣿⣿⣿⣿⣿⣿⣿⠁⣿⣿⣿⣿⣿⣿⣿⣿⣿
        """
        
        infoText = f"""
[bold white]USER[/] @ [bold white]STEM WEEK[/]
------------------
[#f7768e bold]OS[/]:      [#7dcfff]STEM WEEK OS[/]
[#f7768e bold]Host[/]:    [#7dcfff]{self.dashboard_service.target_ip}[/]
[#f7768e bold]Port[/]:    [#7dcfff]{self.dashboard_service.port}[/]
[#f7768e bold]Status[/]:  [#7dcfff]Connection Pending[/]
"""

        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Container(id="split-view"):
                yield Static(duckAscii, id="ascii-art")
                yield Static(infoText, id="info-panel")
            
            with Vertical(id="input-area"):
                yield Input(placeholder="ENTER TEAM ID TO ACCESS PROTOCOL...")

        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        team_id_input = event.value.strip()
        
        # Call the new async verification method
        team_data = await self.dashboard_service.verify_team_online(team_id_input)
        
        if team_data:
            self.exit(result={"team": team_data, "pin": team_id_input, "uri": self.dashboard_service.uri})
        else:
            self.notify("INVALID TEAM ID", severity="error")
            event.input.value = ""
            
    def on_mount(self) -> None:
        self.title = "STEM WEEK TERMINAL // ACCESS"

def main(server_ip: str | None = None, server_port: int | None = None):
    # If values aren't provided programmatically, fall back to CLI parsing.
    if server_ip is None or server_port is None:
        args = parse_args()
        if server_ip is None:
            server_ip = args.server_ip
        if server_port is None:
            # allow parse_args to be extended later; default port 8080
            server_port = 8080

    while True:
        app = DashboardApp(server_ip=server_ip, server_port=server_port)
        result_data = app.run()
        
        if result_data and isinstance(result_data, dict):
            team_data = result_data["team"]
            team_pin = result_data["pin"]
            target_uri = result_data["uri"]
            print(f"\nInitializing Protocol for {team_data['name']} on {target_uri}...")
            
            # Launch Question Protocol and inject URI
            resultProto = question.run(team_data['id'], team_data['name'], team_pin=team_pin, uri=target_uri)
            
            if resultProto == 100:
                continue
            else:
                break
        else:
            print("\\nShutting down...")
            break

if __name__ == "__main__":
    main()
