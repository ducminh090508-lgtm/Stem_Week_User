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
    # Prompt the user for the server host or host:port (fallback to localhost:8080)
    import re
    import ipaddress

    default_host = "127.0.0.1"
    default_port = 8080

    def validate_host(h: str) -> bool:
        try:
            ipaddress.ip_address(h)
            return True
        except Exception:
            # allow simple hostnames (letters, numbers, hyphen, dot)
            return re.match(r"^[A-Za-z0-9.-]+$", h) is not None

    host = None
    port = default_port

    try:
        while True:
            raw = input(f"Server (host or host:port) [default {default_host}:{default_port}]: ")
            raw = (raw or f"{default_host}:{default_port}").strip()

            if ":" in raw:
                parts = raw.split(":")
                if len(parts) != 2:
                    print("Invalid format. Use host or host:port")
                    continue
                cand_host, cand_port = parts[0].strip(), parts[1].strip()
                if not cand_host or not validate_host(cand_host):
                    print("Invalid host. Enter a valid IP or hostname.")
                    continue
                try:
                    cand_port_i = int(cand_port)
                    if not (1 <= cand_port_i <= 65535):
                        print("Port must be between 1 and 65535.")
                        continue
                except ValueError:
                    print("Port must be a number.")
                    continue
                host = cand_host
                port = cand_port_i
                break
            else:
                cand_host = raw
                if not cand_host or not validate_host(cand_host):
                    print("Invalid host. Enter a valid IP or hostname.")
                    continue
                host = cand_host
                port = default_port
                break
    except (EOFError, KeyboardInterrupt):
        print("\nUsing default server.")
        host = default_host
        port = default_port

    from app.interface.dashboard import main as start_app
    start_app(server_ip=host, server_port=port)

if __name__ == "__main__":
    main()
