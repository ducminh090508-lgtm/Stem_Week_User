from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input
from rich.text import Text


PIN_LENGTH = 12


class FinalPuzzleView(Container):
    def compose(self) -> ComposeResult:
        with Container(id="final-puzzle-root"):
            with Vertical(id="final-puzzle-panel"):
                yield Static("[#7dcfff bold]FINAL OVERRIDE PIN[/]", id="final-puzzle-header")

                with Vertical(id="pin-grid", classes="pin-grid-wrap"):
                    with Horizontal(id="pin-row-top", classes="pin-row"):
                        for i in range(8):
                            yield Static(" ", id=f"pin-top-{i}", classes="pin-slot")

                    with Horizontal(id="pin-row-bottom", classes="pin-row"):
                        for i in range(4):
                            yield Static(" ", id=f"pin-bottom-{i}", classes="pin-slot")

                yield Input(
                    placeholder="Enter final code...",
                    id="final-input",
                )
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
        if event.value != cleaned:
            event.input.value = cleaned
        self.update_slots(cleaned)
        self.query_one("#final-status", Static).update("")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        code = "".join(ch for ch in event.value if not ch.isspace())[:PIN_LENGTH].upper()
        self.update_slots(code)

        status = self.query_one("#final-status", Static)
        if len(code) != PIN_LENGTH:
            status.update(Text("INCOMPLETE CODE", style="#f72585", justify="center"))
            return

        status.update(Text("VERIFYING OVERRIDE CODE...", style="#7dcfff", justify="center"))
        if hasattr(self.app, "send_final_code"):
            await self.app.send_final_code(code)

    def handle_feedback(self, correct: bool) -> None:
        status = self.query_one("#final-status", Static)
        if correct:
            status.update(Text("ACCESS GRANTED", style="#33d17a", justify="center"))
        else:
            status.update(Text("ACCESS DENIED", style="#f72585", justify="center"))