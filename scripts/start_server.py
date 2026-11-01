"""Run the local app in the foreground and open Firefox only after readiness."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


HOST = "127.0.0.1"
APP_ID = "matching-reply-assistant"
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def local_app_ready(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{port}/api/status", timeout=1) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return (
            response.status == 200
            and payload.get("app_id") == APP_ID
            and isinstance(payload.get("demo"), bool)
            and isinstance(payload.get("model"), str)
            and payload["model"].startswith("gemini-")
        )
    except (OSError, urllib.error.URLError, ValueError, TypeError):
        return False


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        try:
            listener.bind((HOST, port))
        except OSError:
            return False
    return True


def port_accepts_connections(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex((HOST, port)) == 0


def find_firefox() -> str | None:
    candidates = [
        Path(os.getenv("ProgramFiles", r"C:\Program Files")) / "Mozilla Firefox" / "firefox.exe",
        Path(os.getenv("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Mozilla Firefox" / "firefox.exe",
    ]
    return next((str(path) for path in candidates if path.is_file()), None)


def main() -> int:
    try:
        port = int(os.getenv("MRA_PORT", "8765"))
    except ValueError:
        print("MRA_PORT must be a valid TCP port number.")
        return 2
    if not 1 <= port <= 65535:
        print("MRA_PORT must be between 1 and 65535.")
        return 2

    url = f"http://{HOST}:{port}/"
    if local_app_ready(port):
        print(f"Matching Reply Assistant is already running at {url}.")
        firefox = find_firefox()
        if firefox:
            subprocess.Popen([firefox, url])
        else:
            print("Firefox was not found. Open the URL in Firefox.")
        return 0
    if not port_is_free(port):
        print(f"Port {port} is occupied by another process. It was left running.")
        print("Close that application yourself or set MRA_PORT to another available port.")
        return 2

    import uvicorn

    config = uvicorn.Config("app:app", host=HOST, port=port, log_level="info")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, name="mra-uvicorn", daemon=True)
    server_thread.start()
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if server.started and local_app_ready(port):
            break
        if not server_thread.is_alive():
            print("The local server stopped before becoming ready.")
            return 2
        time.sleep(0.2)
    else:
        server.should_exit = True
        server_thread.join(timeout=10)
        print("The local server did not become ready within 30 seconds.")
        return 2

    print(f"Ready at {url}. Press Ctrl+C in this window to stop the app.")
    firefox = find_firefox()
    if firefox:
        subprocess.Popen([firefox, url])
    else:
        print("Firefox was not found. Open the URL in Firefox.")
    try:
        while server_thread.is_alive():
            server_thread.join(timeout=0.5)
    except KeyboardInterrupt:
        print("Stopping the local server...")
        server.should_exit = True
        server_thread.join(timeout=10)
    if server_thread.is_alive():
        print("The local server did not stop cleanly.")
        return 2
    deadline = time.monotonic() + 5
    while port_accepts_connections(port) and time.monotonic() < deadline:
        time.sleep(0.2)
    if port_accepts_connections(port):
        print(f"Port {port} is still accepting connections after shutdown; no process was terminated.")
        return 2
    print(f"Stopped. Port {port} no longer accepts connections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
