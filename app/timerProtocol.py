# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Union

from art import text2art  # type: ignore
from rich.align import Align
from rich.console import Group
from rich.text import Text
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Footer, Header

DEFAULT_FONT: str = os.environ.get("TIMER_FONT", "c1")

Number = Union[int, float]

def standardize_time_str(num: Number) -> str:
    num = round(num)
    if num <= 0:
        return "00"
    s = str(num)
    return s if len(s) > 1 else f"0{s}"

def createTimeString(hrs: Number, mins: Number, secs: Number) -> str:
    h = str(int(round(hrs))) if int(round(hrs)) >= 100 else standardize_time_str(hrs)
    return f"{h}:{standardize_time_str(mins)}:{standardize_time_str(secs)}"

def colour_for_elapsed(elapsed_seconds: int) -> str:
    if elapsed_seconds < 10 * 60:
        return "#33d17a" # Green
    if elapsed_seconds < 60 * 60:
        return "#f9e2af" # Yellow
    return "#f38ba8" # Red

@dataclass(frozen=True)
class StopwatchConfig:
    message: str
    font: str
    start_offset_seconds: int

class StopwatchView(Static):
    elapsed_seconds: int = reactive(0)
    message: str = reactive("")
    font: str = reactive(DEFAULT_FONT)
    paused: bool = reactive(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._base_elapsed = 0
        self._run_start = time.perf_counter()
        self.expand = True

    def on_mount(self) -> None:
        self.set_interval(1, self._tick)

    def _tick(self) -> None:
        if self.paused:
            return
        self.elapsed_seconds = self._base_elapsed + int(time.perf_counter() - self._run_start)

    def toggle_pause(self) -> None:
        if not self.paused:
            self._base_elapsed = self.elapsed_seconds
            self.paused = True
        else:
            self._run_start = time.perf_counter()
            self.paused = False

    def reset(self) -> None:
        self._base_elapsed = 0
        self._run_start = time.perf_counter()
        self.elapsed_seconds = 0
        self.paused = False

    def sync_time(self, total_seconds: int) -> None:
        """Update local timer with authoritative time from server."""
        self._base_elapsed = total_seconds
        self._run_start = time.perf_counter()
        self.elapsed_seconds = total_seconds
        self.refresh()

    def render(self):
        hrs = max(0, self.elapsed_seconds // 3600)
        mins = max(0, (self.elapsed_seconds // 60) % 60)
        secs = max(0, self.elapsed_seconds % 60)
        t = createTimeString(hrs, mins, secs)

        color = colour_for_elapsed(self.elapsed_seconds)
        timer_style = f"bold {color}"
        if self.paused:
            timer_style = "bold #f9e2af"

        # Use rstrip and ensure no_wrap to prevent ASCII art from breaking on resize
        ascii_timer = text2art(t, font=self.font).rstrip()
        timer_text = Text(ascii_timer, style=timer_style, no_wrap=True)
        
        msg_text = Text(self.message, style="#7dcfff") if self.message else Text("")
        state_text = Text(" // SYSTEM PAUSED // " if self.paused else "", style="bold #f9e2af")

        body = Group(
            Align.center(timer_text),
            Align.center(Text("")), # Spacer
            Align.center(msg_text),
            Align.center(state_text),
        )
        # Vertical centering only works if the widget fills the parent
        return Align.center(body, vertical="middle")

class StopwatchApp(App):
    CSS = """
    Screen { 
        align: center middle; 
        background: #101010;
    }
    StopwatchView { width: 100%; height: 100%; }
    """

    BINDINGS = [
        ("q", "quit", "Exit Utility"),
        ("space", "toggle_pause", "Pause/Resume"),
        ("r", "reset", "Reset Timer"),
    ]

    def __init__(self, cfg: StopwatchConfig):
        super().__init__()
        self.cfg = cfg

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        self.timer_view = StopwatchView()
        yield self.timer_view
        yield Footer()

    def on_mount(self) -> None:
        self.title = "STEM WEEK // CHRONO OBSERVER"
        self.timer_view.message = self.cfg.message
        self.timer_view.font = self.cfg.font
        # If there's an offset in config, we could set it here
        # self.timer_view._base_elapsed = self.cfg.start_offset_seconds

    def action_toggle_pause(self) -> None:
        self.timer_view.toggle_pause()

    def action_reset(self) -> None:
        self.timer_view.reset()

def main() -> None:
    cfg = StopwatchConfig(
        message="TEMPORAL OVERWATCH ACTIVE", 
        font=DEFAULT_FONT, 
        start_offset_seconds=0
    )
    StopwatchApp(cfg).run()

if __name__ == "__main__":
    main()
