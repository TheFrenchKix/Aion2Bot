"""Backend Windows Graphics Capture (windows-capture) : capture une fenetre precise,
meme partiellement masquee. Le callback tourne dans le thread de capture : il ne doit
rien faire de lourd, on se contente de publier la frame."""
import numpy as np

from .base import CaptureBackend


class WgcBackend(CaptureBackend):
    name = "wgc"

    def __init__(self, window_title: str) -> None:
        super().__init__()
        self.window_title = window_title
        self._control = None

    def start(self) -> None:
        from windows_capture import WindowsCapture

        capture = WindowsCapture(
            cursor_capture=False,
            draw_border=False,  # ignore sur les Windows qui ne le supportent pas
            window_name=self.window_title,
        )

        @capture.event
        def on_frame_arrived(frame, capture_control):
            buf = frame.frame_buffer  # ndarray BGRA (h, w, 4)
            self._publish(np.ascontiguousarray(buf[:, :, :3]))

        @capture.event
        def on_closed():
            pass

        self._control = capture.start_free_threaded()

    def stop(self) -> None:
        if self._control is not None:
            try:
                self._control.stop()
            except Exception:
                pass
