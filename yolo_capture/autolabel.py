"""Auto-labellisation des images de dataset_auto/images, puis construction du dataset
d'entrainement.

Methodes de labellisation :
  - ReferenceLabeler : recherche de l'objet par correspondance de modele multi-echelle
    a partir d'images de reference (references/<classe>.png, <classe>__2.png, ...).
    Independant du modele : evite de reinjecter ses propres erreurs.
  - ModelLabeler : pre-annotation par le modele charge (a relire).

Les labels sont ecrits dans dataset_auto/labels ; des apercus annotes dans
dataset_auto/preview servent au controle visuel avant l'entrainement."""
import random
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from autotrainer import DATASET_DIR
from inference import Detection

APP_DIR = Path(__file__).resolve().parent
REFERENCES_DIR = APP_DIR / "references"
TRAIN_DIR = APP_DIR / "dataset_train"
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp"}


# --- references ----------------------------------------------------------------------
def list_references(ref_dir: Path = REFERENCES_DIR) -> dict[str, list[Path]]:
    """{classe: [fichiers]} ; le nom de classe est le nom du fichier avant '__'."""
    refs: dict[str, list[Path]] = {}
    if ref_dir.exists():
        for p in sorted(ref_dir.iterdir()):
            if p.suffix.lower() in IMG_EXT:
                refs.setdefault(p.stem.split("__")[0], []).append(p)
    return refs


def _imread(path: Path, flags=cv2.IMREAD_COLOR):
    return cv2.imdecode(np.fromfile(str(path), np.uint8), flags)  # robuste aux chemins unicode


def _load_template(path: Path):
    """Charge une reference ; un PNG transparent est recadre sur l'objet."""
    img = _imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 4:
        ys, xs = np.where(img[:, :, 3] > 10)
        if len(xs):
            img = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        img = img[:, :, :3]
    return np.ascontiguousarray(img)


# --- labellers -----------------------------------------------------------------------
class ReferenceLabeler:
    def __init__(self, refs: dict[str, list[Path]], threshold: float = 0.75,
                 scales: np.ndarray | None = None) -> None:
        self.names = sorted(refs)
        self.threshold = threshold
        self.scales = scales if scales is not None else np.geomspace(0.6, 1.8, 13)
        self.templates = [(cid, t) for cid, name in enumerate(self.names)
                          for p in refs[name] if (t := _load_template(p)) is not None]
        if not self.templates:
            raise ValueError("Aucune image de reference lisible.")

    def label(self, img: np.ndarray) -> list[Detection]:
        H, W = img.shape[:2]
        boxes, scores, cids = [], [], []
        for cid, tmpl in self.templates:
            for s in self.scales:
                t = cv2.resize(tmpl, None, fx=s, fy=s,
                               interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
                th, tw = t.shape[:2]
                if th < 8 or tw < 8 or th > H or tw > W:
                    continue
                res = np.nan_to_num(cv2.matchTemplate(img, t, cv2.TM_CCOEFF_NORMED),
                                    nan=0.0, posinf=0.0, neginf=0.0)
                ys, xs = np.where(res >= self.threshold)
                if len(xs) > 500:  # garder les meilleurs pics seulement
                    top = np.argsort(res[ys, xs])[-500:]
                    ys, xs = ys[top], xs[top]
                for x, y in zip(xs.tolist(), ys.tolist()):
                    boxes.append([x, y, tw, th])
                    scores.append(float(res[y, x]))
                    cids.append(cid)
        out: list[Detection] = []
        for cid in set(cids):
            idx = [i for i, c in enumerate(cids) if c == cid]
            keep = cv2.dnn.NMSBoxes([boxes[i] for i in idx], [scores[i] for i in idx], 0.0, 0.3)
            for k in np.asarray(keep).flatten():
                x, y, w, h = boxes[idx[int(k)]]
                out.append(Detection(x, y, x + w, y + h, scores[idx[int(k)]], cid, self.names[cid]))
        return out


class ModelLabeler:
    def __init__(self, detector) -> None:
        self.detector = detector
        self.names = [detector.names[k] for k in sorted(detector.names)]

    def label(self, img: np.ndarray) -> list[Detection]:
        return self.detector.predict(img)


# --- labellisation du dossier ---------------------------------------------------------
@dataclass
class LabelReport:
    total: int = 0
    labeled: int = 0
    empty: int = 0
    skipped: int = 0
    boxes: int = 0


def label_stats(out_dir: Path = DATASET_DIR) -> tuple[int, int]:
    """(images, images avec au moins un label)"""
    images = list((out_dir / "images").glob("*.png")) if (out_dir / "images").exists() else []
    labeled = sum(1 for p in images
                  if (f := out_dir / "labels" / f"{p.stem}.txt").exists() and f.stat().st_size > 0)
    return len(images), labeled


def _draw_preview(img, dets: list[Detection]) -> np.ndarray:
    for d in dets:
        cv2.rectangle(img, (int(d.x1), int(d.y1)), (int(d.x2), int(d.y2)), (0, 255, 0), 2)
        cv2.putText(img, f"{d.label} {d.score:.2f}", (int(d.x1), max(int(d.y1) - 6, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
    if img.shape[1] > 960:
        img = cv2.resize(img, (960, round(img.shape[0] * 960 / img.shape[1])))
    return img


def run_autolabel(labeler, class_names: list[str], overwrite: bool = False, progress=None,
                  out_dir: Path = DATASET_DIR) -> LabelReport:
    images = sorted((out_dir / "images").glob("*.png"))
    labels_dir, preview_dir = out_dir / "labels", out_dir / "preview"
    labels_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    classes_file = out_dir / "classes.txt"
    if classes_file.exists() and not overwrite and any(labels_dir.glob("*.txt")):
        existing = classes_file.read_text(encoding="utf-8").split("\n")
        if [c for c in existing if c] != class_names:
            raise ValueError("Les classes diffèrent de celles des labels existants : "
                             "activez « Écraser les labels » ou videz dataset_auto/labels.")
    classes_file.write_text("\n".join(class_names), encoding="utf-8")

    rep = LabelReport(total=len(images))
    for i, path in enumerate(images, 1):
        lbl = labels_dir / f"{path.stem}.txt"
        if lbl.exists() and not overwrite:
            rep.skipped += 1
        else:
            img = _imread(path)
            dets = labeler.label(img) if img is not None else []
            if dets:
                h, w = img.shape[:2]
                lines = [f"{d.cls} {(d.x1 + d.x2) / 2 / w:.6f} {(d.y1 + d.y2) / 2 / h:.6f} "
                         f"{(d.x2 - d.x1) / w:.6f} {(d.y2 - d.y1) / h:.6f}" for d in dets]
                lbl.write_text("\n".join(lines) + "\n", encoding="utf-8")
                ok, buf = cv2.imencode(".jpg", _draw_preview(img.copy(), dets),
                                       [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ok:
                    (preview_dir / f"{path.stem}.jpg").write_bytes(buf.tobytes())
                rep.labeled += 1
                rep.boxes += len(dets)
            else:
                lbl.unlink(missing_ok=True)  # label perime d'un precedent passage
                (preview_dir / f"{path.stem}.jpg").unlink(missing_ok=True)
                rep.empty += 1
        if progress:
            progress(i / max(len(images), 1), f"{i} / {len(images)}")
    return rep


# --- dataset d'entrainement -------------------------------------------------------------
@dataclass
class BuildReport:
    path: Path
    train: int
    val: int
    classes: int


def build_training_dataset(val_ratio: float = 0.2, seed: int = 0, out_dir: Path = DATASET_DIR,
                           train_dir: Path = TRAIN_DIR) -> BuildReport:
    """Copie les images labellisees dans dataset_train/ (train/val) + data.yaml."""
    pairs = [(p, out_dir / "labels" / f"{p.stem}.txt")
             for p in sorted((out_dir / "images").glob("*.png"))]
    pairs = [(p, lbl) for p, lbl in pairs if lbl.exists() and lbl.stat().st_size > 0]
    if len(pairs) < 2:
        raise ValueError("Il faut au moins 2 images labellisées (lancez l'auto-labellisation).")
    classes_file = out_dir / "classes.txt"
    names = [c for c in classes_file.read_text(encoding="utf-8").split("\n") if c] \
        if classes_file.exists() else []
    if not names:
        raise ValueError("classes.txt introuvable : relancez l'auto-labellisation.")

    random.Random(seed).shuffle(pairs)
    n_val = max(1, int(len(pairs) * val_ratio))
    splits = {"val": pairs[:n_val], "train": pairs[n_val:]}
    for sub in ("images", "labels"):  # dossier genere : reconstruit a chaque fois
        shutil.rmtree(train_dir / sub, ignore_errors=True)
    for split, items in splits.items():
        (train_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (train_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
        for img, lbl in items:
            shutil.copy2(img, train_dir / "images" / split / img.name)
            shutil.copy2(lbl, train_dir / "labels" / split / lbl.name)
    yaml = [f"path: {train_dir.as_posix()}", "train: images/train", "val: images/val", "names:"]
    yaml += [f"  {i}: {n}" for i, n in enumerate(names)]
    (train_dir / "data.yaml").write_text("\n".join(yaml) + "\n", encoding="utf-8")
    return BuildReport(train_dir, len(splits["train"]), len(splits["val"]), len(names))
