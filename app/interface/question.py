from __future__ import annotations
import sys
import os

# Ensure the parent directory is in the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Header, Footer, Label, Input
from textual import events
from textual.css.query import NoMatches
from rich.text import Text

from app.interface.timer import StopwatchView
from app.interface.final_puzzle import FinalPuzzleView
from app.leaderboard import Leaderboard, Entry

# Import the backend logic
from app.functions.question import QuestionService


SUBJECT_CONFIG = {
    "BIO": {
        "title": "Mysterious Death",
        "color": "#f07178",
        "desc": "Explore the wonders of life. Identify the species and complete the genetic sequence.",
        "id": "btn-bio",
    },
    "CHEM": {
        "title": "CHEM",
        "color": "#33d17a",
        "desc": "Analyze the reactions. Balance the equations and identify the mysterious compound.",
        "id": "btn-chem",
    },
    "MATH AND PHYSICS": {
        "title": "MATH AND PHYSICS",
        "color": "#4cc9f0",
        "desc": "Solve the fundamental laws. Calculate the forces and find the unknown variables.",
        "id": "btn-mathphysics",
    },
    "CS": {
        "title": "CS",
        "color": "#f72585",
        "desc": "Hack into the system. Decipher the code and debug the faulty algorithms.",
        "id": "btn-cs",
    },
}


class ModuleCard(Static, can_focus=True):
    def __init__(self, idName: str, title: str, color: str):
        super().__init__(
            f"\n\n[b]{title}[/]\n\nPress Enter or Click",
            id=idName,
            classes="module-box",
        )
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

    def on_enter(self, event: events.Enter) -> None:
        self.styles.color = "black"
        self.styles.background = "#f8f8f2"

    def on_leave(self, event: events.Leave) -> None:
        if not self.has_focus:
            self.styles.color = self.subject_color
            self.styles.background = "#101010"

    def on_click(self) -> None:
        self.app.switchToSubject(self.targetPage)

    def on_key(self, event: events.Key) -> None:
        if event.key in ("enter", "space"):
            self.app.switchToSubject(self.targetPage)
            event.prevent_default()
            event.stop()


class FinalPuzzleCard(Static, can_focus=True):
    def __init__(self):
        super().__init__(
            "\n\n[b]FINAL PUZZLE[/]\n\nPress Enter or Click",
            id="final-puzzle-card",
            classes="module-box",
        )
        self.styles.color = "#f8f8f2"

    def on_focus(self) -> None:
        self.styles.color = "black"
        self.styles.background = "#f8f8f2"

    def on_blur(self) -> None:
        self.styles.color = "#f8f8f2"
        self.styles.background = "transparent"

    def on_enter(self, event: events.Enter) -> None:
        self.styles.color = "black"
        self.styles.background = "#f8f8f2"

    def on_leave(self, event: events.Leave) -> None:
        if not self.has_focus:
            self.styles.color = "#f8f8f2"
            self.styles.background = "transparent"

    def on_click(self) -> None:
        self.app.switchToFinalPuzzle()

    def on_key(self, event: events.Key) -> None:
        if event.key in ("enter", "space"):
            self.app.switchToFinalPuzzle()
            event.prevent_default()
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
            if self.final_unlocked:
                yield FinalPuzzleCard()
            else:
                yield Static(
                    "\n[#565f89]LOCKED\n\nComplete subject modules to unlock the final puzzle.[/]",
                    id="mega-box",
                )


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


class StemApp(App):
    CSS_PATH = "question.tcss"
    BINDINGS = [
        ("q", "exitToDashboard", "Return to Dashboard"),
        ("1", "navQuestions", "Questions [1]"),
        ("2", "navTimer", "Timer [2]"),
        ("3", "navLeaderboard", "Standings [3]"),
        ("escape", "navQuestions", "Back"),
    ]

    def __init__(self, team_id: int, team_name: str, team_pin: str, uri: str = "wss://localhost:8080", **kwargs):
        super().__init__(**kwargs)
        self.team_id = team_id
        self.team_name = team_name
        self.team_pin = team_pin
        self.question_service = QuestionService(team_id=team_id, team_pin=team_pin, uri=uri)
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

        self.question_service.on_connected = self.on_server_connected
        self.question_service.on_disconnected = self.on_server_disconnected
        self.question_service.on_status_update = self.on_status_update
        self.question_service.on_protocol_started = self.on_protocol_started
        self.question_service.on_rotation_finished = self.on_rotation_finished
        self.question_service.on_feedback = self.on_feedback
        self.question_service.on_leaderboard_update = self.on_leaderboard_update

        self.run_worker(self.question_service.connect(), exclusive=False)
        self.run_worker(self.status_polling_loop(), exclusive=False)

    def on_server_connected(self):
        self.notify("Connected to Server", severity="information")

    def on_server_disconnected(self, reason: str):
        self.notify(f"Disconnected: {reason}", severity="warning")

    def on_status_update(self, data: dict):
        total_seconds = data.get("total", 0)
        in_progress = data.get("inProgress", False)
        timer_query = self.query("#page-timer")
        if timer_query:
            timer = timer_query.first()
            timer.sync_time(total_seconds, paused=not in_progress)

    def on_protocol_started(self):
        self.notify("PROTOCOL STARTED // TIMER ACTIVE", severity="information")

    def on_rotation_finished(self):
        self.notify("ROTATION COMPLETED // STOPPING TIMER", severity="success")

    def on_feedback(self, correct: bool):
        # If the full-screen final puzzle is active, route feedback there.
        active_final = None
        for view in self.query(FinalPuzzleView):
            if view.display:
                active_final = view
                break

        if active_final is not None:
            active_final.handle_feedback(correct)
            if correct:
                timer_query = self.query("#page-timer")
                if timer_query:
                    timer_query.first().paused = True
            return

        # Mark subject completion based on the last submitted subject.
        if correct and self._last_submitted_subject:
            subject_name = self._last_submitted_subject
            if subject_name not in self.completed_subjects:
                self.completed_subjects.add(subject_name)

            if not self.final_unlocked and len(self.completed_subjects) == len(SUBJECT_CONFIG):
                self.final_unlocked = True

                def unlock_final_card():
                    mega_query = self.query(".mega-container")
                    if not mega_query:
                        self.switchToMainPage("questions")
                        return

                    mega_container = mega_query.first()

                    for child in list(mega_container.children):
                        child.remove()

                    card = FinalPuzzleCard()
                    mega_container.mount(card)

                    def focus_card():
                        if card.parent is not None:
                            card.focus()

                    self.call_after_refresh(focus_card)

                self.call_after_refresh(unlock_final_card)

        # Update the current subject input UI if one is visible.
        input_view = None
        for view in self.query(InputView):
            if view.display:
                input_view = view
                break

        if input_view:
            feedback = input_view.query_one("#answer-feedback")
            if correct:
                feedback.update(Text("CORRECT", style="#33d17a", justify="center"))
                self.notify("Correct Answer! Timer Paused.", severity="success")

                timer_query = self.query("#page-timer")
                if timer_query:
                    timer_query.first().paused = True
            else:
                feedback.update(Text("INCORRECT", style="#f72585", justify="center"))
                self.notify("Incorrect Answer. Try again.", severity="error")

    def on_leaderboard_update(self, data: list):
        def update_ui():
            entries = []
            for i, item in enumerate(data):
                rank = item.get("rank", i + 1)
                rank_label = f"{rank:02d}" if isinstance(rank, int) else str(rank)
                name = item.get("name", f"Team {i+1}")
                total = item.get("total")
                if total is None or total < 0:
                    time_display = "DNF"
                else:
                    minutes = int(total) // 60
                    seconds = int(total) % 60
                    time_display = f"{minutes:02d}:{seconds:02d}"

                entries.append(
                    Entry(
                        rank_label=rank_label,
                        team=name,
                        time_display=time_display,
                        hints=item.get("hints", 0),
                        dnf=item.get("dnf", 0),
                        inaccurate=item.get("inaccurate", 0),
                    )
                )

            leaderboard_query = self.query(Leaderboard)
            if leaderboard_query:
                lb = leaderboard_query.first()
                lb.entries = entries
                lb.refresh()

        self.call_later(update_ui)

    async def status_polling_loop(self):
        import asyncio
        while True:
            if self.question_service._connected.is_set():
                await self.question_service.get_status()
            await asyncio.sleep(5)

    async def send_submission(self, subject: str, answer: str):
        self._last_submitted_subject = subject
        await self.question_service.submit_answer(subject=subject, answer=answer)

    async def send_final_code(self, code: str):
        await self.question_service.submit_final_code(code)

    def action_navQuestions(self) -> None:
        self.switchToMainPage("questions")

    def action_navTimer(self) -> None:
        self.switchToMainPage("timer")

    def action_navLeaderboard(self) -> None:
        self.switchToMainPage("leaderboard")
        self.run_worker(self.question_service.get_leaderboard())

    def switchToMainPage(self, pageName: str) -> None:
        switcher = self.query_one("#main-switcher")

        for child in switcher.children:
            child.display = False

        target_id = f"page-{pageName}"
        existing = switcher.query(f"#{target_id}")

        if existing:
            page = existing.first()
            page.display = True

            if pageName == "questions" and self.final_unlocked:
                mega_query = page.query(".mega-container")
                if mega_query:
                    mega_container = mega_query.first()
                    has_card = bool(mega_container.query("#final-puzzle-card"))
                    if not has_card:
                        for child in list(mega_container.children):
                            child.remove()
                        mega_container.mount(FinalPuzzleCard())
            return

        if pageName == "questions":
            view = QuestionSelectionView(final_unlocked=self.final_unlocked, id=target_id)
            view.add_class("layout-vertical")
            switcher.mount(view)

        elif pageName == "timer":
            view = StopwatchView(id=target_id)
            view.message = "TIMER ACTIVE"
            view.styles.height = "100%"
            view.styles.width = "100%"
            switcher.mount(view)

        elif pageName == "leaderboard":
            mock_entries = [Entry("00", "Loading...", "00:00", 0, 0, 0)]
            view = Leaderboard(mock_entries, id=target_id)
            switcher.mount(view)

    def switchToSubject(self, pageName: str) -> None:
        switcher = self.query_one("#main-switcher")

        for child in switcher.children:
            child.display = False

        found_config = None
        for _, config in SUBJECT_CONFIG.items():
            if config["id"] == pageName or config["title"].lower() in pageName.lower():
                found_config = config
                break

        if not found_config:
            return

        subject = found_config["title"]
        target_id = f"page-input-{subject.lower().replace(' ', '')}"
        existing = switcher.query(f"#{target_id}")

        def focus_input():
            try:
                view.query_one(Input).focus()
            except NoMatches:
                pass

        if existing:
            view = existing.first()
            view.display = True
            self.call_after_refresh(focus_input)
        else:
            view = InputView(subject, found_config["color"], found_config["desc"], id=target_id)
            view.add_class("layout-horizontal")
            switcher.mount(view)
            self.call_after_refresh(focus_input)

    def switchToFinalPuzzle(self) -> None:
        switcher = self.query_one("#main-switcher")

        for child in switcher.children:
            child.display = False

        target_id = "page-final"
        existing = switcher.query(f"#{target_id}")

        if existing:
            view = existing.first()
            view.display = True
        else:
            view = FinalPuzzleView(id=target_id)
            view.add_class("layout-vertical")
            switcher.mount(view)

    async def action_exitToDashboard(self) -> None:
        self.question_service.shutdown()
        self.exit(result=100)


def run(team_id: int = 1, team_name: str = "Team 1", team_pin: str = "1001", uri: str = "wss://localhost:8080"):
    app = StemApp(team_id=team_id, team_name=team_name, team_pin=team_pin, uri=uri)
    return app.run()


if __name__ == "__main__":
    run()
