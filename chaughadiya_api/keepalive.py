from __future__ import annotations

import threading
import time
from typing import Optional

import requests
from flask import Flask


def _ping_forever(url: str, interval: int) -> None:
    while True:
        time.sleep(interval // 2)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception:
            pass
        time.sleep(interval // 2)


def maybe_start_keepalive(app: Flask) -> None:  # pragma: no cover - glue logic
    if not app.config.get("ENABLE_KEEP_ALIVE"):
        return

    if app.config.get("_keepalive_thread"):
        return

    url = f"{app.config['EXTERNAL_URL'].rstrip('/')}/health"
    thread = threading.Thread(target=_ping_forever, args=(url, app.config["KEEP_ALIVE_INTERVAL"]), daemon=True)
    thread.start()
    app.config["_keepalive_thread"] = thread

