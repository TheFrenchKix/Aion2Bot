"""Reglages utilisateur, sauvegardes dans config.json a cote du projet."""
import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


@dataclass
class Settings:
    window: str = ""          # partie du titre de la fenetre
    model: str = ""           # chemin .onnx/.pt ; vide = capture seule
    capture: str = "auto"
    provider: str = "auto"
    conf: float = 0.25
    iou: float = 0.45
    imgsz: int = 640          # utilise si l'ONNX a une taille dynamique
    preview: bool = True
    display_fps: int = 30
    # Debug : enregistre une image toutes les N images avec detection
    auto_trainer: bool = False
    auto_trainer_interval: int = 1000
    auto_trainer_labels: bool = False   # pre-annotations du modele (optionnel, dans pre_labels/)
    # Dataset : auto-labellisation
    label_method: str = "references"    # "references" | "model"
    label_threshold: float = 0.75
    label_overwrite: bool = False

    @classmethod
    def load(cls) -> "Settings":
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            known = {f.name for f in fields(cls)}
            return cls(**{k: v for k, v in data.items() if k in known})
        except Exception:
            return cls()

    def save(self) -> None:
        try:
            CONFIG_PATH.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False),
                                   encoding="utf-8")
        except OSError:
            pass
