"""Backend DXGI Desktop Duplication via dxcam : tres rapide, fenetre visible au premier plan."""
import threading

from .base import CaptureBackend
from .winapi import client_region, monitor_index_of, monitors


class DxcamBackend(CaptureBackend):
    name = "dxcam"

    def __init__(self, hwnd: int, target_fps: int = 0) -> None:
        super().__init__()
        self.hwnd = hwnd
        self.target_fps = target_fps
        self._cam = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        import dxcam
        r = client_region(self.hwnd)
        out_idx = monitor_index_of(r)
        mon = monitors()[out_idx]
        # dxcam attend une region relative au moniteur : (left, top, right, bottom)
        left, top = r.left - mon.left, r.top - mon.top
        region = (left, top, left + r.width, top + r.height)
        # Portables hybrides : si l'image est noire, essayer d'autres device_idx.
        self._cam = dxcam.create(output_idx=out_idx, output_color="BGR")
        self._cam.start(region=region, target_fps=self.target_fps, video_mode=True)
        # Le thread interne de dxcam capture ; on ne fait que relayer la derniere frame.
        self._thread = threading.Thread(target=self._pump, daemon=True)
        self._thread.start()

    def _pump(self) -> None:
        while not self._stop.is_set():
            frame = self._cam.get_latest_frame()
            if frame is not None:
                self._publish(frame)

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        if self._cam is not None:
            try:
                self._cam.stop()
            finally:
                del self._cam
