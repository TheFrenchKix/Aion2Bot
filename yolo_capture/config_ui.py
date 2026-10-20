"""Menu de configuration PySide6 + QML (interface dans ./ui). Ce module est le backend :
il expose l'etat a QML et verifie la compatibilite ; les options incompatibles avec la
machine sont desactivees cote interface avec leur raison."""
import os
import sys
from pathlib import Path

from PySide6.QtCore import Property, QCoreApplication, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from capture.compat import BACKENDS, check_backends
from capture.winapi import list_windows
from inference.compat import PROVIDERS, check_providers, inspect_model
from settings import CONFIG_PATH, Settings

APP_DIR = Path(__file__).resolve().parent
UI_DIR = APP_DIR / "ui"
WINDOW_TITLE = "Aion2Bot - Configuration"
NO_MODEL = "Aucun (capture seule)"


MODELS_DIR = APP_DIR / "models"


def discover_models() -> list[Path]:
    """Tous les .onnx / .pt du dossier models (sous-dossiers inclus), tries par nom."""
    MODELS_DIR.mkdir(exist_ok=True)
    found = [p for ext in ("*.onnx", "*.pt") for p in MODELS_DIR.rglob(ext)]
    return sorted(found, key=lambda p: str(p).lower())


def _options(catalog: dict, availability: dict) -> list[dict]:
    return [{"key": key, "label": label, "description": desc,
             "available": availability[key].ok, "reason": availability[key].reason}
            for key, (label, desc) in catalog.items()]


class Backend(QObject):
    changed = Signal()

    def __init__(self, initial: Settings) -> None:
        super().__init__()
        self.initial = initial
        self.result: Settings | None = None

        cap_av, prov_av = check_backends(), check_providers()
        self._capture_options = _options(BACKENDS, cap_av)
        self._provider_options = _options(PROVIDERS, prov_av)
        self._capture = initial.capture if cap_av.get(initial.capture, cap_av["auto"]).ok else "auto"
        self._provider = (initial.provider if prov_av.get(initial.provider, prov_av["auto"]).ok
                          else "auto")
        self._conf = float(initial.conf)
        self._preview = bool(initial.preview)

        self._windows: list[str] = []
        self._window_index = -1
        self._models: list[tuple[str, str]] = []  # (libelle, chemin)
        self._model_index = 0
        self._model_info, self._model_ok, self._model_neutral = "", True, True

        self._scan_models()
        self._select_initial_model()
        self.refreshWindows()
        self._refresh_model_info()

    # --- modeles --------------------------------------------------------------------
    def _scan_models(self) -> None:
        self._models = [(str(p.relative_to(MODELS_DIR)), str(p)) for p in discover_models()]

    def _select_initial_model(self) -> None:
        saved = self.initial.model
        for i, (_l, p) in enumerate(self._models):
            if saved and Path(p) == Path(saved):
                self._model_index = i + 1
                return
        first_run = not CONFIG_PATH.exists()  # 1er lancement : preselectionner un modele trouve
        self._model_index = 1 if (first_run and self._models) else 0

    def _selected_model_path(self) -> str:
        return self._models[self._model_index - 1][1] if self._model_index > 0 else ""

    def _refresh_model_info(self) -> None:
        path = self._selected_model_path()
        if not path:
            self._model_ok, self._model_neutral = True, True
            self._model_info = ("Aucune détection : seule la capture sera testée." if self._models
                                else "Le dossier « models » est vide : déposez-y un .onnx ou .pt, "
                                     "puis actualisez.")
        else:
            info = inspect_model(path)
            self._model_ok, self._model_neutral = info.ok, False
            self._model_info = info.text if info.ok else f"Incompatible : {info.text}"
        self.changed.emit()

    # --- proprietes lues par QML ----------------------------------------------------
    @Property(list, notify=changed)
    def windowTitles(self):
        return self._windows

    @Property(int, notify=changed)
    def windowIndex(self):
        return self._window_index

    @Property(list, notify=changed)
    def modelLabels(self):
        return [NO_MODEL] + [label for label, _ in self._models]

    @Property(int, notify=changed)
    def modelIndex(self):
        return self._model_index

    @Property(str, notify=changed)
    def modelInfo(self):
        return self._model_info

    @Property(bool, notify=changed)
    def modelOk(self):
        return self._model_ok

    @Property(bool, notify=changed)
    def modelNeutral(self):
        return self._model_neutral

    @Property(list, notify=changed)
    def captureOptions(self):
        return self._capture_options

    @Property(str, notify=changed)
    def captureKey(self):
        return self._capture

    @Property(list, notify=changed)
    def providerOptions(self):
        return self._provider_options

    @Property(str, notify=changed)
    def providerKey(self):
        return self._provider

    def _get_conf(self):
        return self._conf

    def _set_conf(self, v: float):
        self._conf = round(float(v), 2)
        self.changed.emit()

    conf = Property(float, _get_conf, _set_conf, notify=changed)

    def _get_preview(self):
        return self._preview

    def _set_preview(self, v: bool):
        self._preview = bool(v)
        self.changed.emit()

    preview = Property(bool, _get_preview, _set_preview, notify=changed)

    @Property(str, notify=changed)
    def hint(self):
        if self._window_index < 0:
            return "Sélectionnez une fenêtre à capturer."
        if not self._model_ok:
            return "Le modèle choisi est incompatible."
        return ""

    @Property(bool, notify=changed)
    def canLaunch(self):
        return self.hint == ""

    # --- actions appelees par QML ---------------------------------------------------
    @Slot()
    def refreshWindows(self) -> None:
        current = self._windows[self._window_index] if self._window_index >= 0 else \
            self.initial.window
        titles = sorted({t for _h, t in list_windows()
                         if t.strip() and t != WINDOW_TITLE}, key=str.lower)
        self._windows = titles
        self._window_index = next((i for i, t in enumerate(titles)
                                   if current and current.lower() in t.lower()), -1)
        self.changed.emit()

    @Slot(int)
    def setWindowIndex(self, i: int) -> None:
        self._window_index = i
        self.changed.emit()

    @Slot(int)
    def setModelIndex(self, i: int) -> None:
        self._model_index = i
        self._refresh_model_info()

    @Slot()
    def refreshModels(self) -> None:
        """Rescanne le dossier models en conservant la selection si le fichier existe encore."""
        current = self._selected_model_path()
        self._scan_models()
        self._model_index = next((i + 1 for i, (_l, p) in enumerate(self._models)
                                  if current and p == current), 0)
        self._refresh_model_info()

    @Slot()
    def openModelsFolder(self) -> None:
        MODELS_DIR.mkdir(exist_ok=True)
        os.startfile(MODELS_DIR)

    @Slot(str)
    def selectCapture(self, key: str) -> None:
        if any(o["key"] == key and o["available"] for o in self._capture_options):
            self._capture = key  # une option incompatible est refusee, meme si l'UI l'envoie
            self.changed.emit()

    @Slot(str)
    def selectProvider(self, key: str) -> None:
        if any(o["key"] == key and o["available"] for o in self._provider_options):
            self._provider = key
            self.changed.emit()

    @Slot()
    def launch(self) -> None:
        self.result = Settings(
            window=self._windows[self._window_index], model=self._selected_model_path(),
            capture=self._capture, provider=self._provider, conf=self._conf,
            iou=self.initial.iou, imgsz=self.initial.imgsz, preview=self._preview,
            display_fps=self.initial.display_fps)
        self.result.save()
        QCoreApplication.quit()

    @Slot()
    def quit(self) -> None:
        QCoreApplication.quit()


def run_menu(initial: Settings) -> Settings | None:
    os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.*=false")  # bruit DPI deja configure
    QQuickStyle.setStyle("Basic")  # style personnalisable (les autres imposent leur look)
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    backend = Backend(initial)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(str(UI_DIR / "Main.qml")))
    if not engine.rootObjects():
        raise RuntimeError("Impossible de charger l'interface QML (voir les erreurs ci-dessus).")
    app.exec()
    result = backend.result
    del engine
    return result
