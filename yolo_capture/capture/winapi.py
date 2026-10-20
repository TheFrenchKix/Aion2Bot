"""Helpers Win32 (ctypes uniquement) : recherche de fenetre, zone client, ecran."""
import ctypes
from ctypes import wintypes
from dataclasses import dataclass

user32 = ctypes.windll.user32


def set_dpi_aware() -> None:
    """A appeler au demarrage : evite des coordonnees fausses avec le zoom Windows."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


@dataclass(frozen=True)
class Region:
    left: int
    top: int
    width: int
    height: int


def list_windows() -> list[tuple[int, str]]:
    """Fenetres visibles avec un titre : [(hwnd, titre), ...]."""
    out: list[tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                buf = ctypes.create_unicode_buffer(n + 1)
                user32.GetWindowTextW(hwnd, buf, n + 1)
                out.append((hwnd, buf.value))
        return True

    user32.EnumWindows(cb, 0)
    return out


def find_window(title_part: str) -> tuple[int, str]:
    """Premiere fenetre dont le titre contient `title_part` (insensible a la casse)."""
    needle = title_part.lower()
    for hwnd, title in list_windows():
        if needle in title.lower():
            return hwnd, title
    raise LookupError(f"Aucune fenetre dont le titre contient '{title_part}'")


def client_region(hwnd: int) -> Region:
    """Zone client (sans barre de titre ni bordures) en coordonnees ecran."""
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    pt = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return Region(pt.x, pt.y, rect.right - rect.left, rect.bottom - rect.top)


def is_minimized(hwnd: int) -> bool:
    return bool(user32.IsIconic(hwnd))


def monitors() -> list[Region]:
    """Moniteurs dans l'ordre d'enumeration Windows (en coordonnees ecran)."""
    out: list[Region] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HANDLE, wintypes.HDC,
                        ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    def cb(_h, _dc, rect, _l):
        r = rect.contents
        out.append(Region(r.left, r.top, r.right - r.left, r.bottom - r.top))
        return True

    user32.EnumDisplayMonitors(None, None, cb, 0)
    return out


def monitor_index_of(region: Region) -> int:
    """Index du moniteur contenant le centre de `region`."""
    cx, cy = region.left + region.width // 2, region.top + region.height // 2
    for i, m in enumerate(monitors()):
        if m.left <= cx < m.left + m.width and m.top <= cy < m.top + m.height:
            return i
    return 0
