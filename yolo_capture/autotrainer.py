"""Auto-trainer (debug) : enregistre une image toutes les N images ou le modele detecte
quelque chose, pour agrandir le dataset. Les images sont brutes : elles sont labellisees
ensuite par l'auto-labellisation (autolabel.py). Les predictions du modele peuvent etre
ecrites en option dans pre_labels/ (simple reference, jamais utilisees pour l'entrainement).
L'ecriture disque se fait dans un thread dedie : l'inference n'est jamais ralentie."""
import queue
import threading
from datetime import datetime
from pathlib import Path

import cv2

from inference import Detection

DATASET_DIR = Path(__file__).resolve().parent / "dataset_auto"


def count_dataset_images(out_dir: Path = DATASET_DIR) -> int:
    d = out_dir / "images"
    return sum(1 for _ in d.glob("*.png")) if d.exists() else 0


class AutoTrainer:
    def __init__(self, interval: int = 1000, save_labels: bool = True,
                 names: dict[int, str] | None = None, out_dir: Path = DATASET_DIR) -> None:
        self.interval = max(1, int(interval))
        self.save_labels = save_labels
        self.images_dir = out_dir / "images"
        self.labels_dir = out_dir / "pre_labels"  # pre-annotations du modele, distinctes de labels/
        self.images_dir.mkdir(parents=True, exist_ok=True)
        if save_labels:
            self.labels_dir.mkdir(parents=True, exist_ok=True)
        if save_labels and names:
            (self.labels_dir / "classes.txt").write_text(
                "\n".join(names[k] for k in sorted(names)), encoding="utf-8")
        self._detected_frames = 0
        self._saved = 0
        self._queue: queue.Queue = queue.Queue(maxsize=8)
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def on_result(self, frame, detections: list[Detection]) -> None:
        """A appeler pour chaque frame traitee (thread d'inference) : tres leger."""
        if not detections:
            return
        self._detected_frames += 1
        if self._detected_frames % self.interval:
            return
        try:  # copie car le backend de capture peut reutiliser son buffer
            self._queue.put_nowait((frame.copy(), list(detections)))
        except queue.Full:
            print("[auto-trainer] file d'ecriture pleine : image ignoree")

    def _worker(self) -> None:
        while (item := self._queue.get()) is not None:
            try:
                self._write(*item)
            except Exception as e:  # ne jamais faire tomber l'application pour du debug
                print(f"[auto-trainer] erreur d'ecriture : {e}")

    def _write(self, frame, detections: list[Detection]) -> None:
        self._saved += 1
        name = f"{datetime.now():%Y%m%d_%H%M%S}_{self._saved:05d}"
        ok, buf = cv2.imencode(".png", frame)  # imencode : robuste aux chemins non ASCII
        if not ok:
            return
        (self.images_dir / f"{name}.png").write_bytes(buf.tobytes())
        if self.save_labels:
            h, w = frame.shape[:2]
            lines = []
            for d in detections:
                cx, cy = (d.x1 + d.x2) / 2 / w, (d.y1 + d.y2) / 2 / h
                bw, bh = (d.x2 - d.x1) / w, (d.y2 - d.y1) / h
                lines.append(f"{d.cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
            (self.labels_dir / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[auto-trainer] image {self._saved} enregistree : {name}.png "
              f"({len(detections)} detection(s))")

    def close(self) -> None:
        self._queue.put(None)  # vide la file puis arrete le thread
        self._thread.join(timeout=10)
