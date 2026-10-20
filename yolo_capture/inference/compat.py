"""Compatibilite des providers d'inference et des modeles avec CETTE machine."""
import importlib.util
import shutil
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from capture.compat import Availability

PROVIDERS = {
    "auto": ("Automatique", "Le plus rapide disponible, avec repli automatique"),
    "TensorrtExecutionProvider": ("NVIDIA TensorRT", "Le plus rapide sur GPU NVIDIA"),
    "CUDAExecutionProvider": ("NVIDIA CUDA", "GPU NVIDIA"),
    "DmlExecutionProvider": ("DirectML", "Tout GPU DirectX 12 (AMD, Intel, NVIDIA)"),
    "OpenVINOExecutionProvider": ("Intel OpenVINO", "CPU / GPU intégré Intel"),
    "CPUExecutionProvider": ("CPU", "Toujours disponible, le plus lent"),
}

_NEEDS = {
    "TensorrtExecutionProvider": "onnxruntime-gpu",
    "CUDAExecutionProvider": "onnxruntime-gpu",
    "DmlExecutionProvider": "onnxruntime-directml",
    "OpenVINOExecutionProvider": "onnxruntime-openvino",
}


@lru_cache(maxsize=1)
def _has_nvidia() -> bool:
    return shutil.which("nvidia-smi") is not None


def check_providers() -> dict[str, Availability]:
    try:
        import onnxruntime as ort
        available = set(ort.get_available_providers())
    except Exception:
        none = Availability(False, "onnxruntime non installé (lancer install.py)")
        return {k: none for k in PROVIDERS}
    res: dict[str, Availability] = {}
    for key in PROVIDERS:
        if key == "auto":
            continue
        if key in available:
            res[key] = Availability(True)
        elif key in ("TensorrtExecutionProvider", "CUDAExecutionProvider") and not _has_nvidia():
            res[key] = Availability(False, "GPU NVIDIA non détecté")
        else:
            res[key] = Availability(False, f"Nécessite le paquet '{_NEEDS[key]}' (lancer install.py)")
    res["auto"] = Availability(True)
    return res


@dataclass(frozen=True)
class ModelInfo:
    ok: bool
    text: str


def inspect_model(path: str) -> ModelInfo:
    p = Path(path)
    if not p.exists():
        return ModelInfo(False, "Fichier introuvable")
    if p.suffix == ".pt":
        if importlib.util.find_spec("ultralytics") is None:
            return ModelInfo(False, "Un .pt nécessite 'ultralytics' (pip install ultralytics)")
        return ModelInfo(True, ".pt : sera exporté en ONNX au premier lancement")
    if p.suffix != ".onnx":
        return ModelInfo(False, "Format non supporté (.onnx ou .pt)")
    try:
        import ast
        import onnxruntime as ort
        sess = ort.InferenceSession(str(p), providers=["CPUExecutionProvider"])
    except ImportError:
        return ModelInfo(False, "onnxruntime non installé (lancer install.py)")
    except Exception as e:
        return ModelInfo(False, f"ONNX illisible : {str(e)[:80]}")
    meta = sess.get_modelmeta().custom_metadata_map
    task = meta.get("task", "detect")
    if task != "detect":
        return ModelInfo(False, f"Modèle '{task}' non supporté : seule la détection est gérée")
    shape = sess.get_inputs()[0].shape
    size = f"{shape[3]}x{shape[2]}" if isinstance(shape[2], int) else "taille dynamique"
    try:
        n = len(ast.literal_eval(meta["names"]))
        classes = f"{n} classe{'s' if n > 1 else ''}"
    except Exception:
        classes = "classes inconnues"
    return ModelInfo(True, f"Détection | entrée {size} | {classes}")
