import asyncio
import ssl
import websockets
import json
import logging
from typing import Callable, Optional
from pathlib import Path

LOG_FILE = Path.home() / "stemweek_debug.log"


def debug_log(*args):
    with LOG_FILE.open("a", encoding="utf-8") as f:
        print(*args, file=f, flush=True)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class QuestionService:
    SUBJECT_PROTOCOL_IDS = {
        "BIO": "BIO",
        "CHEM": "CHEM",
        "MATH AND PHYSICS": "MATH_PHYS",
        "CS": "CS",
        "MEGA": "MEGA",
    }

    def __init__(self, team_id: int, team_pin: str, uri: str = "wss://localhost:8080"):
        self.team_id = team_id
        self.team_pin = team_pin
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._connected = asyncio.Event()
        self._authenticated = asyncio.Event()
        self._shutdown = asyncio.Event()

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
                debug_log("[Question] connect entered")
                debug_log("[Question] URI =", self.uri)
                debug_log("[Question] team_pin =", self.team_pin)
                debug_log("[Question] Opening websocket...")

                async with websockets.connect(
                    self.uri,
                    ssl=ssl_context,
                    open_timeout=30,
                    close_timeout=10,
                    ping_interval=None,
                    compression=None,
                    proxy=None,
                ) as websocket:
                    debug_log("[Question] websocket opened")

                    self.websocket = websocket
                    self._connected.set()
                    self._authenticated.clear()

                    if self.on_connected:
                        self.on_connected()

                    debug_log("[Question] sending VERIFY_PIN")
                    await websocket.send(f"VERIFY_PIN {self.team_pin}")
                    debug_log("[Question] VERIFY_PIN sent")

                    async for message in websocket:
                        debug_log("[Question] recv =", message)
                        self._handle_message(message)

            except asyncio.CancelledError:
                import traceback
                debug_log("[Question] connect task cancelled")
                debug_log(traceback.format_exc())
                raise

            except Exception as e:
                import traceback
                debug_log("[Question] exception =", repr(e))
                debug_log(traceback.format_exc())

                if self.on_error:
                    self.on_error(repr(e))

            self.websocket = None
            self._connected.clear()
            self._authenticated.clear()

            if not self._shutdown.is_set():
                debug_log("[Question] retrying in 5 seconds...")
                await asyncio.sleep(5)

    def _handle_message(self, message: str):
        debug_log("[Question] _handle_message raw =", message)

        try:
            data = json.loads(message)
            debug_log("[Question] _handle_message parsed =", data)

            msg_type = data.get("type")

            if msg_type == "PIN_VERIFIED":
                self._authenticated.set()
                debug_log("[Question] authenticated set")

            elif msg_type == "STATUS":
                if self.on_status_update:
                    self.on_status_update(data)

            elif msg_type == "LEADERBOARD":
                teams = data.get("teams", [])
                if self.on_leaderboard_update:
                    self.on_leaderboard_update(teams)

            elif msg_type == "FEEDBACK":
                correct = bool(data.get("correct", False))
                if self.on_feedback:
                    self.on_feedback(correct)

            elif msg_type == "PROTOCOL_STARTED":
                if self.on_protocol_started:
                    self.on_protocol_started()

            elif msg_type == "ROTATION_FINISHED":
                if self.on_rotation_finished:
                    self.on_rotation_finished()

            elif msg_type == "ERROR":
                reason = data.get("reason", "Unknown error")
                if self.on_error:
                    self.on_error(reason)

        except Exception as e:
            import traceback
            debug_log("[Question] _handle_message exception =", repr(e))
            debug_log(traceback.format_exc())

    async def send_command(self, command: str) -> bool:
        if self.websocket and self._connected.is_set():
            try:
                await self.websocket.send(command)
                return True
            except Exception as e:
                logger.error(f"Failed to send command: {e}")
                return False
        else:
            logger.warning(f"Cannot send command '{command}': Not connected.")
            return False

    async def start_protocol(self):
        await self.send_command(f"START {self.team_id}")

    async def get_status(self):
        await self.send_command(f"GET_STATUS {self.team_id}")

    async def get_leaderboard(self):
        await self.send_command("GET_LEADERBOARD")

    def _normalize_subject(self, subject: str) -> str:
        if subject in self.SUBJECT_PROTOCOL_IDS:
            return self.SUBJECT_PROTOCOL_IDS[subject]
        return subject.replace(" ", "_")

    async def submit_answer(self, subject: str, answer: str):
        subject_id = self._normalize_subject(subject)
        clean_answer = answer.strip().replace(" ", "_")
        await self.send_command(f"SUBMIT {self.team_id} {subject_id} {clean_answer}")

    async def submit_final_code(self, code: str):
        subject_id = self._normalize_subject("MEGA")
        clean_code = code.strip().replace(" ", "_")
        await self.send_command(f"SUBMIT {self.team_id} {subject_id} {clean_code}")

    def shutdown(self):
        self._shutdown.set()
