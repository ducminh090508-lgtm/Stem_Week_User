from __future__ import annotations
import asyncio
import ssl
import json
import time
from typing import Callable, Optional

import websockets
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Header, Footer, Label, Input

# --- LEADREBOARD / TIMER IMPORTS (From user folder) ---
try:
    from app.leaderboard import Leaderboard, Entry
    from app.timerProtocol import StopwatchView
except ImportError:
    # Fallback if running from within the user folder
    from leaderboard import Leaderboard, Entry
    from timerProtocol import StopwatchView

import os
import sys

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- BACKEND SERVICE ---
class QuestionService:
    def __init__(self, team_id: int, uri: str = "wss://localhost:8080"):
        self.team_id = team_id
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = asyncio.Event()
        self._shutdown = asyncio.Event()

        # Callbacks
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[str], None]] = None
        self.on_status_update: Optional[Callable[[dict], None]] = None
        self.on_leaderboard_update: Optional[Callable[[list], None]] = None
        self.on_feedback: Optional[Callable[[bool], None]] = None
        self.on_protocol_started: Optional[Callable[[], None]] = None
        self.on_rotation_finished: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        while not self._shutdown.is_set():
            try:
                async with websockets.connect(self.uri, ssl=ssl_context) as websocket:
                    self.websocket = websocket
                    self._connected.set()
                    if self.on_connected: self.on_connected()
                    async for message in websocket:
                        self._handle_message(message)
            except Exception as e:
                if self.on_error: self.on_error(repr(e))
                self.websocket = None
                self._connected.clear()
                if not self._shutdown.is_set():
                    await asyncio.sleep(5)

    def _handle_message(self, message: str):
        if message.startswith("["):
             try:
                 data = json.loads(message)
                 if self.on_leaderboard_update: self.on_leaderboard_update(data)
             except: pass
        elif message.startswith("{"):
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                if msg_type == "STATUS" and self.on_status_update: self.on_status_update(data)
                elif msg_type == "PROTOCOL_STARTED" and self.on_protocol_started: self.on_protocol_started()
                elif msg_type == "ROTATION_FINISHED" and self.on_rotation_finished: self.on_rotation_finished()
            except: pass
        elif message == "CORRECT":
            if self.on_feedback: self.on_feedback(True)
        elif message == "INCORRECT":
            if self.on_feedback: self.on_feedback(False)

    async def send_command(self, command: str) -> bool:
        if self.websocket and self._connected.is_set():
            try:
                await self.websocket.send(command)
                return True
            except:
                return False
        return False

    async def get_status(self):
        await self.send_command(f"GET_STATUS {self.team_id}")

    async def get_leaderboard(self):
        await self.send_command("GET_LEADERBOARD")

    async def submit_answer(self, subject: str, answer: str):
        # Convert human name to protocol ID
        subj_map = {"BIO":"BIO", "CHEM":"CHEM", "MATH AND PHYSICS":"MATH_PHYS", "CS":"CS", "MEGA":"MEGA"}
        subj_id = subj_map.get(subject, subject.replace(" ", "_"))
        clean_answer = answer.strip().replace(" ", "_")
        await self.send_command(f"SUBMIT {self.team_id} {subj_id} {clean_answer}")

    async def submit_final_code(self, code: str):
        await self.send_command(f"SUBMIT {self.team_id} MEGA {code.strip()}")

    def shutdown(self):
        self._shutdown.set()

# --- UI COMPONENTS ---

PIN_LENGTH = 12

class FinalPuzzleView(Container):
    def compose(self) -> ComposeResult:
        with Container(id="final-puzzle-root"):
            with Vertical(id="final-puzzle-panel"):
                yield Static("[#7dcfff bold]FINAL OVERRIDE PIN[/]", id="final-puzzle-header")
                with Vertical(id="pin-grid", classes="pin-grid-wrap"):
                    with Horizontal(id="pin-row-top", classes="pin-row"):
                        for i in range(8): yield Static(" ", id=f"pin-top-{i}", classes="pin-slot")
                    with Horizontal(id="pin-row-bottom", classes="pin-row"):
                        for i in range(4): yield Static(" ", id=f"pin-bottom-{i}", classes="pin-slot")
                yield Input(placeholder="Enter final code...", id="final-input")
                yield Static("", id="final-status")

    def on_mount(self) -> None:
        self.query_one("#final-input", Input).focus()

    def update_slots(self, code: str) -> None:
        code = "".join(ch for ch in code if not ch.isspace())[:PIN_LENGTH].upper()
        for i in range(8):
            ch = code[i] if i < len(code) else " "
            self.query_one(f"#pin-top-{i}", Static).update(ch)
        for i in range(4):
            idx = 8 + i
            ch = code[idx] if idx < len(code) else " "
            self.query_one(f"#pin-bottom-{i}", Static).update(ch)

    def on_input_changed(self, event: Input.Changed) -> None:
        cleaned = "".join(ch for ch in event.value if not ch.isspace())[:PIN_LENGTH].upper()
        if event.value != cleaned: event.input.value = cleaned
        self.update_slots(cleaned)
        self.query_one("#final-status", Static).update("")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        code = "".join(ch for ch in event.value if not ch.isspace())[:PIN_LENGTH].upper()
        if len(code) != PIN_LENGTH:
            self.query_one("#final-status", Static).update(Text("INCOMPLETE CODE", style="#f72585", justify="center"))
            return
        self.query_one("#final-status", Static).update(Text("VERIFYING OVERRIDE CODE...", style="#7dcfff", justify="center"))
        if hasattr(self.app, "send_final_code"):
            await self.app.send_final_code(code)

    def handle_feedback(self, correct: bool) -> None:
        status = self.query_one("#final-status", Static)
        if correct: status.update(Text("ACCESS GRANTED", style="#33d17a", justify="center"))
        else: status.update(Text("ACCESS DENIED", style="#f72585", justify="center"))

SUBJECT_CONFIG = {
    "BIO": {"title": "BIO", "color": "#f07178", "desc": "Explore life's mysteries.", "id": "btn-bio"},
    "CHEM": {"title": "CHEM", "color": "#33d17a", "desc": "Analyze chemical reactions.", "id": "btn-chem"},
    "MATH AND PHYSICS": {"title": "MATH AND PHYSICS", "color": "#4cc9f0", "desc": "Calculate physical laws.", "id": "btn-mathphysics"},
    "CS": {"title": "CS", "color": "#f72585", "desc": "Debug complex systems.", "id": "btn-cs"},
}

class ModuleCard(Static, can_focus=True):
    def __init__(self, idName: str, title: str, color: str):
        super().__init__(f"\n\n[b]{title}[/]\n\nPress Enter or Click", id=idName, classes="module-box")
        self.subject_color = color
        self.styles.color = color
        self.titleText = title
        self.targetPage = f"input_{title.lower()}"

    def on_focus(self) -> None:
        self.styles.color = "black"
        self.styles.background = "#f8f8f2"

    def on_blur(self) -> None:
        self.styles.color = self.subject_color
        self.styles.background = "#101010"

    def on_click(self) -> None: self.app.switchToSubject(self.targetPage)

    def on_key(self, event: events.Key) -> None:
        if event.key in ("enter", "space"):
            self.app.switchToSubject(self.targetPage)
            event.stop()

class FinalPuzzleCard(Static, can_focus=True):
    def __init__(self):
        super().__init__("\n\n[b]FINAL PUZZLE[/]\n\nPress Enter or Click", id="final-puzzle-card", classes="module-box")
        self.styles.color = "#f8f8f2"

    def on_focus(self) -> None:
        self.styles.color = "black"
        self.styles.background = "#f8f8f2"

    def on_blur(self) -> None:
        self.styles.color = "#f8f8f2"
        self.styles.background = "transparent"

    def on_click(self) -> None: self.app.switchToFinalPuzzle()

    def on_key(self, event: events.Key) -> None:
        if event.key in ("enter", "space"):
            self.app.switchToFinalPuzzle()
            event.stop()

class QuestionSelectionView(Container):
    def __init__(self, final_unlocked: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.final_unlocked = final_unlocked

    def compose(self) -> ComposeResult:
        with Container(classes="modules-container"):
            for _, config in SUBJECT_CONFIG.items():
                yield ModuleCard(config["id"], config["title"], config["color"])
        with Container(classes="mega-container"):
            if self.final_unlocked: yield FinalPuzzleCard()
            else: yield Static("\n[#565f89]LOCKED\n\nComplete subject modules to unlock the final puzzle.[/]", id="mega-box")

class InputView(Container):
    def __init__(self, subject: str, color: str, description: str, **kwargs):
        super().__init__(**kwargs)
        self.subject = subject
        self.color = color
        self.description = description

    def compose(self) -> ComposeResult:
        with Static(classes="sidebar") as sidebar:
            sidebar.styles.border = ("round", self.color)
            yield Static(f"[{self.color} bold]{self.subject}[/]\n\n[#a9b1d6]{self.description}[/]")
        with Vertical(classes="main-content-area") as area:
            area.styles.border = ("round", "#333333")
            yield Static(f"[{self.color}]// AUTHORIZED ENTRY //[/]", classes="area-header")
            with Vertical(id="question-list"):
                yield Label("\nPart 1 : [_ _ _ _ _] ( )")
                yield Label("Part 2 : [_ _ _ _ _] ( )")
                yield Label("Final  : [_ _ _ _ _] ( )\n")
            yield Static("", classes="spacer")
            yield Static("", id="answer-feedback")
            with Vertical(id="input-field"):
                yield Input(placeholder="Enter answer...")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        answer = event.value.strip().upper()
        self.query_one("#answer-feedback").update("")
        await self.app.send_submission(self.subject, answer)
        event.input.value = ""

# --- MAIN APP ---

class StemApp(App):
    CSS_PATH = resource_path("questionProtocol.tcss")
    BINDINGS = [
        ("q", "exitToDashboard", "Return to Dashboard"),
        ("1", "navQuestions", "Questions [1]"),
        ("2", "navTimer", "Timer [2]"),
        ("3", "navLeaderboard", "Standings [3]"),
        ("escape", "navQuestions", "Back"),
    ]

    def __init__(self, team_id: int, team_name: str, uri: str = "wss://localhost:8080", **kwargs):
        super().__init__(**kwargs)
        self.team_id = team_id
        self.team_name = team_name
        self.question_service = QuestionService(team_id=team_id, uri=uri)
        self.completed_subjects: set[str] = set()
        self.final_unlocked: bool = False
        self._last_submitted_subject: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-switcher"):
            yield QuestionSelectionView(final_unlocked=self.final_unlocked, id="page-questions")
        yield Footer()

    async def on_mount(self) -> None:
        self.title = f"STEM WEEK // {self.team_name.upper()}"
        self.question_service.on_connected = lambda: self.notify("Connected to Server")
        self.question_service.on_status_update = self.on_status_update
        self.question_service.on_feedback = self.on_feedback
        self.question_service.on_leaderboard_update = self.on_leaderboard_update
        self.run_worker(self.question_service.connect(), exclusive=False)
        self.run_worker(self.status_polling_loop(), exclusive=False)

    def on_status_update(self, data: dict):
        timer_q = self.query("#page-timer")
        if timer_q: timer_q.first().sync_time(data.get("total", 0), paused=not data.get("inProgress", False))

    def on_feedback(self, correct: bool):
        active_f = self.query(FinalPuzzleView).filter(".display")
        if active_f:
            active_f.first().handle_feedback(correct)
            if correct: self.query("#page-timer").first().paused = True
            return

        if correct and self._last_submitted_subject:
            self.completed_subjects.add(self._last_submitted_subject)
            if len(self.completed_subjects) >= len(SUBJECT_CONFIG):
                self.final_unlocked = True
                self.switchToMainPage("questions")

        input_view = self.query(InputView).filter(".display")
        if input_view:
            fb = input_view.first().query_one("#answer-feedback")
            if correct:
                fb.update(Text("CORRECT", style="#33d17a", justify="center"))
                self.notify("Correct!", severity="success")
            else:
                fb.update(Text("INCORRECT", style="#f72585", justify="center"))
                self.notify("Incorrect.", severity="error")

    def on_leaderboard_update(self, data: list):
        entries = []
        for i, item in enumerate(data):
            total = item.get("score", 0) # serverv2 uses 'score'
            time_display = f"{int(total)//60:02d}:{int(total)%60:02d}" if total >= 0 else "DNF"
            entries.append(Entry(rank_label=f"{item.get('rank', i+1):02d}", team=item.get("name", "Team"), time_display=time_display,
                                 hints=item.get("hints", 0), inaccurate=item.get("inaccurate", 0)))
        lb_q = self.query(Leaderboard)
        if lb_q:
            lb_q.first().entries = entries
            lb_q.first().refresh()

    async def status_polling_loop(self):
        while True:
            if self.question_service._connected.is_set(): await self.question_service.get_status()
            await asyncio.sleep(5)

    async def send_submission(self, subject: str, answer: str):
        self._last_submitted_subject = subject
        await self.question_service.submit_answer(subject, answer)

    async def send_final_code(self, code: str):
        await self.question_service.submit_final_code(code)

    def action_navQuestions(self) -> None: self.switchToMainPage("questions")
    def action_navTimer(self) -> None: self.switchToMainPage("timer")
    def action_navLeaderboard(self) -> None:
        self.switchToMainPage("leaderboard")
        self.run_worker(self.question_service.get_leaderboard())

    def switchToMainPage(self, page: str) -> None:
        sw = self.query_one("#main-switcher")
        for c in sw.children: c.display = False
        target = f"page-{page}"
        existing = sw.query(f"#{target}")
        if existing:
            existing.first().display = True
            return
        if page == "questions": v = QuestionSelectionView(final_unlocked=self.final_unlocked, id=target)
        elif page == "timer": v = StopwatchView(id=target)
        elif page == "leaderboard": v = Leaderboard([], id=target)
        v.styles.display = "block"
        sw.mount(v)

    def switchToSubject(self, page: str) -> None:
        sw = self.query_one("#main-switcher")
        for c in sw.children: c.display = False
        config = next((c for _, c in SUBJECT_CONFIG.items() if c["id"] == page or c["title"].lower() in page.lower()), None)
        if not config: return
        tid = f"page-input-{config['title'].lower().replace(' ','')}"
        existing = sw.query(f"#{tid}")
        if existing:
            v = existing.first()
            v.display = True
        else:
            v = InputView(config["title"], config["color"], config["desc"], id=tid)
            v.add_class("layout-horizontal")
            sw.mount(v)
        v.query_one(Input).focus()

    def switchToFinalPuzzle(self) -> None:
        sw = self.query_one("#main-switcher")
        for c in sw.children: c.display = False
        tid = "page-final"
        existing = sw.query(f"#{tid}")
        if existing: existing.first().display = True
        else:
            v = FinalPuzzleView(id=tid)
            sw.mount(v)

    async def action_exitToDashboard(self) -> None:
        self.question_service.shutdown()
        self.exit(result=100)

def run(team_id: int = 1, team_name: str = "Team 1"):
    app = StemApp(team_id=team_id, team_name=team_name)
    return app.run()

if __name__ == "__main__":
    run()
