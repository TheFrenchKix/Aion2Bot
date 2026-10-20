"""Choix automatique du backend de capture, du plus rapide au plus compatible."""
from .base import CaptureBackend
from .winapi import find_window, set_dpi_aware

ORDER = ("wgc", "dxcam", "mss")


def _build(name: str, hwnd: int, title: str) -> CaptureBackend:
    if name == "wgc":
        from .wgc_backend import WgcBackend
        return WgcBackend(title)
    if name == "dxcam":
        from .dxcam_backend import DxcamBackend
        return DxcamBackend(hwnd)
    if name == "mss":
        from .mss_backend import MssBackend
        return MssBackend(hwnd)
    raise ValueError(f"Backend inconnu : {name}")


def make_capture(window: str, preferred: str = "auto") -> CaptureBackend:
    """Demarre le premier backend qui fournit une vraie frame."""
    set_dpi_aware()
    hwnd, title = find_window(window)
    names = ORDER if preferred == "auto" else (preferred,)
    errors = []
    for name in names:
        backend = None
        try:
            backend = _build(name, hwnd, title)
            backend.start()
            if backend.wait_first_frame():
                print(f"[capture] backend '{name}' sur la fenetre : {title}")
                return backend
            errors.append(f"{name}: aucune frame valide (image noire ou vide)")
        except Exception as e:  # ImportError, erreur DXGI/WGC, etc.
            errors.append(f"{name}: {type(e).__name__}: {e}")
        if backend is not None:
            backend.stop()
    raise RuntimeError("Aucun backend de capture utilisable :\n  " + "\n  ".join(errors))
