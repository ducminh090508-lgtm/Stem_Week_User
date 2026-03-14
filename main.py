#!/usr/bin/env python3
import sys
import os
import argparse
from configparser import ConfigParser

# Ensure the app folder is importable
sys.path.append(os.getcwd())

def load_config(config_path="config.ini"):
    config = ConfigParser()
    if not os.path.exists(config_path):
        config.add_section("server")
        config.set("server", "ip", "127.0.0.1")
        config.set("server", "port", "8080")
        with open(config_path, "w") as f:
            config.write(f)
    config.read(config_path)
    return config.get("server", "ip", fallback="127.0.0.1")

def main():
    server_ip = load_config()
    
    # Inject the IP into sys.argv for the dashboard's parse_args
    sys.argv = [sys.argv[0], server_ip]
    
    from app.interface.dashboard import main as start_app
    start_app()

if __name__ == "__main__":
    main()
