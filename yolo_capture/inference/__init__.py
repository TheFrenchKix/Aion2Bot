from pathlib import Path

from .base import Detection, Detector, NullDetector

SEARCH_DIRS = (str(Path(__file__).resolve().parent.parent / "models"),)


def resolve_model(model: str | None) -> str | None:
    """Trouve et prepare le modele sans rien demander a l'utilisateur.

    - sans argument : cherche best.onnx / *.onnx puis best.pt / *.pt dans ./models puis ./
    - un .pt est exporte automatiquement en .onnx (mis en cache a cote du .pt)
    """
    path: Path | None = Path(model) if model else None
    if path is None:
        for d in SEARCH_DIRS:
            for pattern in ("best.onnx", "*.onnx", "best.pt", "*.pt"):
                found = sorted(Path(d).glob(pattern))
                if found:
                    path = found[0]
                    print(f"[inference] modele detecte automatiquement : {path}")
                    break
            if path:
                break
    if path is None:
        return None
    if not path.exists():
        raise FileNotFoundError(f"Modele introuvable : {path}")
    if path.suffix == ".pt":
        onnx = path.with_suffix(".onnx")
        if not onnx.exists() or onnx.stat().st_mtime < path.stat().st_mtime:
            try:
                from ultralytics import YOLO
            except ImportError as e:
                raise RuntimeError("Un .pt doit etre exporte en ONNX : installer 'ultralytics' "
                                   "(pip install ultralytics) ou fournir le .onnx") from e
            print(f"[inference] export {path.name} -> ONNX (une seule fois)...")
            YOLO(str(path)).export(format="onnx", simplify=True)
        return str(onnx)
    return str(path)


def make_detector(model: str | None, discover: bool = True, **kwargs) -> Detector:
    """discover=False : pas de recherche automatique (model vide = capture seule)."""
    resolved = resolve_model(model) if (model or discover) else None
    if not resolved:
        print("[inference] aucun modele trouve : capture seule (NullDetector)")
        return NullDetector()
    from .onnx_detector import OnnxDetector
    return OnnxDetector(resolved, **kwargs)
