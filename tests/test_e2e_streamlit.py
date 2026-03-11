from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_port(port: int, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for Streamlit on port {port}")


def test_streamlit_dashboard_renders(page):
    repo_root = Path(__file__).resolve().parents[1]
    port = _free_port()
    env = os.environ.copy()
    env["APP_ENV"] = "test"

    process = subprocess.Popen(
        [
            "poetry",
            "run",
            "streamlit",
            "run",
            "streamlit_app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(port),
        ],
        cwd=repo_root,
        env=env,
    )

    try:
        _wait_for_port(port)
        page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
        page.get_by_text("Ops Weekly Summary").wait_for()
        assert "Ops Weekly Summary" in page.text_content("body")
    finally:
        process.terminate()
        process.wait(timeout=15)
