"""Start an isolated local Streamlit server for browser acceptance."""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def test(synthetic):
    with socket.socket() as reserve:
        reserve.bind(("127.0.0.1", 0))
        port = reserve.getsockname()[1]
    environ = os.environ.copy()
    if synthetic:
        environ["WNS_DATA_MODE"] = "synthetic"
    else:
        environ.pop("WNS_DATA_MODE", None)
    url = f"http://127.0.0.1:{port}"
    with subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard/app.py",
                           "--server.port", str(port)], cwd=ROOT, env=environ) as server:
        try:
            deadline = time.monotonic() + 35
            while time.monotonic() < deadline:
                if server.poll() is not None:
                    raise RuntimeError("Streamlit exited before startup.")
                try:
                    with urlopen(f"{url}/_stcore/health", timeout=2) as response:
                        if response.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(.4)
            else:
                raise TimeoutError("Streamlit did not become healthy.")
            command = [sys.executable, "tests/browser_handover.py", "--url", url]
            if synthetic:
                command.append("--synthetic")
            subprocess.run(command, cwd=ROOT, check=True)
        finally:
            if server.poll() is None:
                server.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorized", action="store_true")
    test(not parser.parse_args().authorized)
