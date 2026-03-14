import argparse
import sys
from typing import Optional, Dict

# Team Mapping: ID -> {id, name}
# In a real app, this could be fetched from the server or a database.
TEAMS = {
    "1001": {"id": 1, "name": "test1"},
    "1002": {"id": 2, "name": "test2"},
    "1234": {"id": 3, "name": "Team Alpha"},
    "5678": {"id": 4, "name": "Team Beta"},
}

class DashboardService:
    """
    Handles network and authentication configuration for the dashboard.
    """
    def __init__(self, target_ip: str = "127.0.0.1", port: int = 8080):
        self.target_ip = target_ip
        self.port = port
        self.uri = f"wss://{self.target_ip}:{self.port}"

    def verify_team(self, team_pin: str) -> Optional[Dict]:
        """
        Validates the team PIN and returns the team details if valid.
        """
        clean_pin = team_pin.strip()
        if clean_pin in TEAMS:
            return TEAMS[clean_pin]
        return None

def parse_args():
    """
    Parses command line arguments for the server IP.
    """
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
