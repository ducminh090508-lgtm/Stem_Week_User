from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Header, Footer
import questionProtocol

class DashboardApp(App):
    CSS = """
    Screen {
        background: #101010;
        color: white;
    }

    #main-container {
        height: 1fr;
        width: 100%;
        align: center middle;
        padding: 2;
    }

    #split-view {
        height: auto;
        width: auto;
        layout: horizontal;
        align: center middle;
    }

    #ascii-art {
        width: auto;
        color: #e0af68;
        content-align: right middle;
        padding-right: 2;
    }

    #info-panel {
        width: auto;
        content-align: left middle;
        color: #a9b1d6;
        padding-left: 2;
    }

    .key {
        color: #f7768e;
        text-style: bold;
    }

    .value {
        color: #7dcfff;
    }

    #input-area {
        height: 3;
        width: 60%;
        margin-top: 2;
        border: ascii #333333;
        align: center middle;
    }

    Input {
        background: #101010;
        border: none;
        color: #33d17a;
        width: 100%;
        text-align: center;
    }
    """

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
        
        infoText = """
[bold white]USER[/] @ [bold white]STEM WEEK[/]
------------------
[#f7768e bold]OS[/]:      [#7dcfff]STEM WEEK OS[/]
[#f7768e bold]Host[/]:    [#7dcfff]Terminal-042[/]
[#f7768e bold]Uptime[/]:  [#7dcfff]00:42:19[/]
[#f7768e bold]Team[/]:    [#7dcfff]Ducks[/]
[#f7768e bold]Rank[/]:    [#7dcfff]#3[/]
[#f7768e bold]Status[/]:  [#7dcfff]Protocol Pending[/]
"""

        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Container(id="split-view"):
                yield Static(duckAscii, id="ascii-art")
                yield Static(infoText, id="info-panel")
            
            with Vertical(id="input-area"):
                yield Input(placeholder="ENTER TEAM ID TO ACCESS PROTOCOL...")

        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        team_id_input = event.value.strip()
        
        # Team Mapping: ID -> {id, name}
        # In a real app, this could be fetched from the server or a database.
        TEAMS = {
            "1001": {"id": 1, "name": "test1"},
            "1002": {"id": 2, "name": "test2"},
            "1234": {"id": 3, "name": "Team Alpha"},
            "5678": {"id": 4, "name": "Team Beta"},
        }
        
        if team_id_input in TEAMS:
            self.exit(result=TEAMS[team_id_input])
        else:
            self.notify("INVALID TEAM ID", severity="error")
            event.input.value = ""
            
    def on_mount(self) -> None:
        self.title = "STEM WEEK TERMINAL // ACCESS"

if __name__ == "__main__":
    while True:
        app = DashboardApp()
        team_data = app.run()
        
        if team_data and isinstance(team_data, dict):
            print(f"\nInitializing Protocol for {team_data['name']}...")
            resultProto = questionProtocol.run(team_data['id'], team_data['name'])
            
            if resultProto == 100:
                continue
            else:
                break
        else:
            print("\nShutting down...")
            break
