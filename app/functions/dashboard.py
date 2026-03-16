import argparse
import sys
import os
import json
import ssl
import websockets
import asyncio
from typing import Optional, Dict

class DashboardService:
    # Handles network and authentication verification with the server
    def __init__(self, target_ip: str = "127.0.0.1", port: int = 8080):
        self.target_ip = target_ip
        self.port = port
        self.uri = f"wss://{self.target_ip}:{self.port}"

    async def verify_team_online(self, team_pin: str) -> Optional[Dict]:
        # Connects to the server temporarily to verify the PIN
        clean_pin = team_pin.strip()
        if not clean_pin:
            return None

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            # Set a timeout for the entire verification process
            async with asyncio.timeout(5):
                async with websockets.connect(self.uri, ssl=ssl_context) as websocket:
                    # Send verification command
                    await websocket.send(f"VERIFY_PIN {clean_pin}")
                    
                    # Wait for response
                    response = await websocket.recv()
                    data = json.loads(response)
                    
                    if data.get("type") == "PIN_VERIFIED":
                        return {
                            "id": data.get("teamId"),
                            "name": data.get("teamName")
                        }
                    else:
                        return None
        except Exception as e:
            print(f"Connection error during PIN verification: {e}")
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
