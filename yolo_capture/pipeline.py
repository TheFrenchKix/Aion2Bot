"""Pipeline : capture (thread du backend) -> inference (thread dedie) -> affichage (main)."""
import threading
import time
from collections import deque
from dataclasses import dataclass, field

import cv2
import numpy as np

from capture.base import CaptureBackend
from inference import Detection, Detector


class FpsMeter:
    def __init__(self, window: int = 60) -> None:
        self.t = deque(maxlen=window)

    def tick(self) -> None:
        self.t.append(time.perf_counter())

    @property
    def fps(self) -> float:
        if len(self.t) < 2:
            return 0.0
        return (len(self.t) - 1) / (self.t[-1] - self.t[0])


@dataclass
class Result:
    frame: np.ndarray
    detections: list[Detection]
    infer_ms: float = 0.0


class Pipeline:
    def __init__(self, capture: CaptureBackend, detector: Detector, on_result=None) -> None:
        self.capture, self.detector, self.on_result = capture, detector, on_result
        self.fps = FpsMeter()
        self.result: Result | None = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)
        self.capture.stop()

    def _loop(self) -> None:
        last_id = -1
        while not self._stop.is_set():
            got = self.capture.latest(last_id)
            if got is None:
                time.sleep(0.0005)
                continue
            frame, last_id = got
            t0 = time.perf_counter()
            dets = self.detector.predict(frame)
            infer_ms = (time.perf_counter() - t0) * 1000
            self.fps.tick()
            with self._lock:
                self.result = Result(frame, dets, infer_ms)
            if self.on_result:
                self.on_result(frame, dets)

    def get_result(self) -> Result | None:
        with self._lock:
            return self.result


def draw(res: Result, fps: float) -> np.ndarray:
    img = res.frame.copy()
    for d in res.detections:
        p1, p2 = (int(d.x1), int(d.y1)), (int(d.x2), int(d.y2))
        cv2.rectangle(img, p1, p2, (0, 255, 0), 2)
        cv2.putText(img, f"{d.label} {d.score:.2f}", (p1[0], max(p1[1] - 6, 12)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    cv2.putText(img, f"{fps:.0f} FPS | {res.infer_ms:.1f} ms", (8, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2, cv2.LINE_AA)
    return img
