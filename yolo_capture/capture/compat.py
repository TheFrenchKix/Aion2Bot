"""Compatibilite des methodes de capture avec CETTE machine (sans lancer de capture)."""
import ctypes
import importlib.util
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Availability:
    ok: bool
    reason: str = ""


def _has(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def _is_remote_session() -> bool:
    try:
        return bool(ctypes.windll.user32.GetSystemMetrics(0x1000))  # SM_REMOTESESSION
    except Exception:
        return False


def check_wgc() -> Availability:
    if sys.platform != "win32":
        return Availability(False, "Windows uniquement")
    if sys.getwindowsversion().build < 18362:
        return Availability(False, "Windows 10 1903 (build 18362) minimum requis")
    if not _has("windows_capture"):
        return Availability(False, "Paquet 'windows-capture' non installé (pip install windows-capture)")
    return Availability(True)


def check_dxcam() -> Availability:
    if sys.platform != "win32":
        return Availability(False, "Windows uniquement")
    if _is_remote_session():
        return Availability(False, "Session Bureau à distance (RDP) : duplication DXGI indisponible")
    if not _has("dxcam"):
        return Availability(False, "Paquet 'dxcam' non installé (pip install dxcam)")
    try:  # sonde reelle : le pilote/GPU supporte-t-il Desktop Duplication ?
        import dxcam
        cam = dxcam.create(output_color="BGR")
        if hasattr(cam, "release"):
            cam.release()
    except Exception as e:
        return Availability(False, f"Initialisation DXGI impossible : {str(e)[:80]}")
    return Availability(True)


def check_mss() -> Availability:
    if not _has("mss"):
        return Availability(False, "Paquet 'mss' non installé (pip install mss)")
    return Availability(True)


# cle -> (libelle, description)
BACKENDS = {
    "auto": ("Automatique", "Meilleure méthode compatible, avec repli automatique"),
    "wgc": ("Windows Graphics Capture", "Rapide, capture la fenêtre même partiellement masquée"),
    "dxcam": ("DXGI Desktop Duplication", "Très rapide (200+ FPS), fenêtre visible au premier plan"),
    "mss": ("GDI (mss)", "Le plus compatible, plus lent (~60 FPS)"),
}


def check_backends() -> dict[str, Availability]:
    res = {"wgc": check_wgc(), "dxcam": check_dxcam(), "mss": check_mss()}
    if any(a.ok for a in res.values()):
        res["auto"] = Availability(True)
    else:
        res["auto"] = Availability(False, "Aucune méthode de capture disponible")
    return res
