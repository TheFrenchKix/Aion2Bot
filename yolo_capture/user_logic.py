"""Point d'entree pour VOS besoins : appele a chaque frame traitee, dans le thread
d'inference. Gardez-le rapide (sinon le FPS baisse) ou deleguez a un autre thread."""
import numpy as np

from inference import Detection


def on_result(frame: np.ndarray, detections: list[Detection]) -> None:
    """frame : image BGR de la fenetre. detections : coordonnees en pixels de `frame`.

    Exemple :
        for d in detections:
            if d.label == "mon_objet" and d.score > 0.6:
                cx, cy = d.center
                ...
    """
    pass
