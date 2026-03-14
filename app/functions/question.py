import asyncio
import ssl
import websockets
import json
import logging
from typing import Callable, Optional

# Set up logging for the network layer
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class QuestionService:
    """
    Handles all WebSocket communication with the Stem Week server.
    Provides methods to send commands and register callbacks for incoming events.
    """

    # Mapping from human-readable subject titles in the UI to protocol IDs
    # used by the C++ server / database (see Subjects table in database.sql).
    SUBJECT_PROTOCOL_IDS = {
        "BIO": "BIO",
        "CHEM": "CHEM",
        "MATH AND PHYSICS": "MATH_PHYS",
        "CS": "CS",
        "MEGA": "MEGA",
    }

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
        """Main loop to connect and handle incoming messages."""
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        while not self._shutdown.is_set():
            try:
                logger.info(f"Connecting to {self.uri}...")
                print(f"[QuestionService] Connecting to {self.uri}...")  # debug print
                async with websockets.connect(self.uri, ssl=ssl_context) as websocket:
                    self.websocket = websocket
                    self._connected.set()
                    
                    if self.on_connected:
                        self.on_connected()
                    
                    async for message in websocket:
                        self._handle_message(message)
                        
            except websockets.exceptions.ConnectionClosedError as e:
                msg = f"Connection closed: {e}"
                logger.warning(msg)
                print(f"[QuestionService] {msg}")
                if self.on_disconnected:
                    self.on_disconnected(str(e))
            except Exception as e:
                msg = f"Connection failed: {repr(e)}"
                logger.error(msg)
                print(f"[QuestionService] {msg}")
                if self.on_error:
                    self.on_error(repr(e))
                
            self.websocket = None
            self._connected.clear()
            
            if not self._shutdown.is_set():
                logger.info("Retrying in 5 seconds...")
                print("[QuestionService] Retrying in 5 seconds...")
                await asyncio.sleep(5)

    def _handle_message(self, message: str):
        """Parses and routes incoming messages to the appropriate callbacks."""
        logger.debug(f"Received: {message}")
        if message.startswith("["): # JSON Leaderboard Array
             try:
                 data = json.loads(message)
                 if self.on_leaderboard_update:
                     self.on_leaderboard_update(data)
             except json.JSONDecodeError:
                 logger.error("Failed to decode leaderboard JSON")
        
        elif message.startswith("{"): # JSON Object (e.g. STATUS, PROTOCOL_STARTED)
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "STATUS" and self.on_status_update:
                    self.on_status_update(data)
                elif msg_type == "PROTOCOL_STARTED" and self.on_protocol_started:
                    self.on_protocol_started()
                elif msg_type == "ROTATION_FINISHED" and self.on_rotation_finished:
                    self.on_rotation_finished()
            except json.JSONDecodeError:
                 logger.error("Failed to decode object JSON")

        elif message == "CORRECT":
            if self.on_feedback:
                self.on_feedback(True)
        elif message == "INCORRECT":
            if self.on_feedback:
                self.on_feedback(False)

    async def send_command(self, command: str) -> bool:
        """Helper to send a raw command string."""
        if self.websocket and self._connected.is_set():
            try:
                await self.websocket.send(command)
                return True
            except Exception as e:
                logger.error(f"Failed to send command: {e}")
                return False
        else:
            # Don't notify user for expected "not connected" during startup/reconnect
            logger.warning(f"Cannot send command '{command}': Not connected.")
            return False

    async def start_protocol(self):
        """Starts the timer/protocol for the current team."""
        await self.send_command(f"START {self.team_id}")

    async def get_status(self):
        """Requests the current time/status."""
        await self.send_command(f"GET_STATUS {self.team_id}")

    async def get_leaderboard(self):
        """Requests the current leaderboard data."""
        await self.send_command("GET_LEADERBOARD")
        # await self.send_command(f"SET_WIN {self.team_id} true") # TODO: remove debug command

    def _normalize_subject(self, subject: str) -> str:
        """
        Convert a human-readable subject title (e.g. 'MATH AND PHYSICS')
        into the protocol subject ID expected by the server (e.g. 'MATH_PHYS').
        """
        if subject in self.SUBJECT_PROTOCOL_IDS:
            return self.SUBJECT_PROTOCOL_IDS[subject]
        # Fallback: remove spaces as a best-effort guess
        return subject.replace(" ", "_")

    async def submit_answer(self, subject: str, answer: str):
        """Submits an answer for a specific subject."""
        subject_id = self._normalize_subject(subject)
        # Ensure answer string doesn't have spaces that might break the simple parser
        # Usually better to send JSON, but keeping format compatible with current C++ server
        clean_answer = answer.strip().replace(" ", "_")
        await self.send_command(f"SUBMIT {self.team_id} {subject_id} {clean_answer}")

    async def submit_final_code(self, code: str):
        """Submits the final override PIN as the MEGA subject so it is recorded in the main database."""
        subject_id = self._normalize_subject("MEGA")
        clean_code = code.strip().replace(" ", "_")
        await self.send_command(f"SUBMIT {self.team_id} {subject_id} {clean_code}")

    def shutdown(self):
        """Signals the connect loop to exit."""
        self._shutdown.set()
        if self.websocket:
            # We can't await close here easily if it's called from sync code,
            # but the loop will break.
            pass