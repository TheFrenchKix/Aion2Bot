"""Interface commune des backends : ils publient toujours la DERNIERE frame BGR."""
import threading
from abc import ABC, abstractmethod

import numpy as np


class CaptureBackend(ABC):
    name = "base"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._frame_id = 0

    def _publish(self, frame: np.ndarray) -> None:
        # On ecrase : pas de file d'attente, les anciennes frames sont jetees.
        with self._lock:
            self._frame = frame
            self._frame_id += 1

    def latest(self, last_id: int = -1) -> tuple[np.ndarray, int] | None:
        """(frame, id) si une frame plus recente que `last_id` existe, sinon None."""
        with self._lock:
            if self._frame is None or self._frame_id == last_id:
                return None
            return self._frame, self._frame_id

    @abstractmethod
    def start(self) -> None:
        """Demarre la capture. Doit lever une exception si le backend est inutilisable."""

    @abstractmethod
    def stop(self) -> None: ...

    def wait_first_frame(self, timeout: float = 3.0) -> bool:
        """Verifie qu'une vraie frame arrive (certains backends renvoient du noir/rien)."""
        import time
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < timeout:
            res = self.latest()
            if res is not None and res[0].size and res[0].any():
                return True
            time.sleep(0.01)
        return False
