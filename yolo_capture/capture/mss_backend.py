"""Backend GDI via mss : le plus lent mais le plus compatible (repli final)."""
import threading

import numpy as np

from .base import CaptureBackend
from .winapi import client_region


class MssBackend(CaptureBackend):
    name = "mss"

    def __init__(self, hwnd: int) -> None:
        super().__init__()
        self.hwnd = hwnd
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        import mss  # noqa: F401  (leve ImportError tot si absent)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        import mss
        with mss.mss() as sct:  # une instance mss par thread
            while not self._stop.is_set():
                r = client_region(self.hwnd)  # suit la fenetre si elle bouge
                if r.width <= 0 or r.height <= 0:
                    self._stop.wait(0.05)
                    continue
                shot = sct.grab({"left": r.left, "top": r.top,
                                 "width": r.width, "height": r.height})
                bgra = np.asarray(shot)
                self._publish(np.ascontiguousarray(bgra[:, :, :3]))

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
