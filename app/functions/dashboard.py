import argparse
import sys
import os
import json
import ssl
import websockets
import asyncio
from typing import Optional, Dict
from pathlib import Path

LOG_FILE = Path.home() / "stemweek_debug.log"

def debug_log(*args):
    with LOG_FILE.open("a", encoding="utf-8") as f:
        print(*args, file=f, flush=True)

class DashboardService:
    # Handles network and authentication verification with the server
    def __init__(self, target_ip: str = "127.0.0.1", port: int = 8080):
        self.target_ip = target_ip
        self.port = port
        self.uri = f"wss://{self.target_ip}:{self.port}"

    async def verify_team_online(self, team_pin: str):
        clean_pin = team_pin.strip()
        if not clean_pin:
            debug_log("[Dashboard] Empty PIN")
            return None

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        debug_log("[Dashboard] verify_team_online entered")
        debug_log("[Dashboard] URI =", self.uri)
        debug_log("[Dashboard] PIN =", clean_pin)

        try:
            async with asyncio.timeout(10):
                debug_log("[Dashboard] Opening websocket...")
                async with websockets.connect(
                    self.uri,
                    ssl=ssl_context,
                    open_timeout=30,
                    close_timeout=10,
                    ping_interval=None,
                    compression=None,
                    proxy=None,
                ) as websocket:
                    debug_log("[Dashboard] websocket opened")
                    await websocket.send(f"VERIFY_PIN {clean_pin}")
                    debug_log("[Dashboard] VERIFY_PIN sent")

                    response = await websocket.recv()
                    debug_log("[Dashboard] response =", response)

                    data = json.loads(response)
                    debug_log("[Dashboard] parsed response =", data)

                    if data.get("type") == "PIN_VERIFIED":
                        result = {
                            "id": data.get("teamId"),
                            "name": data.get("teamName"),
                        }
                        debug_log("[Dashboard] PIN verified:", result)
                        return result

                    debug_log("[Dashboard] PIN rejected or unexpected response")
                    return None

        except Exception as e:
            import traceback
            debug_log("[Dashboard] exception =", repr(e))
            debug_log(traceback.format_exc())
            return None

def parse_args():
    # Parses command line arguments for the server IP
    parser = argparse.ArgumentParser(description="STEM WEEK Terminal Dashboard")
    parser.add_argument(
        "server_ip", 
        nargs="?", 
        default="127.0.0.1", 
        help="IP Address of the STEM Week server (default: 127.0.0.1)"
    )
    # Allows bypassing arguments during Textual testing or if invoked incorrectly
    args, unknown = parser.parse_known_args()
    return args
