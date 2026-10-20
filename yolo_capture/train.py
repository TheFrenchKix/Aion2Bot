"""Fine-tuning du modele sur le dataset construit depuis le menu (page Dataset).

    python train.py                       # dataset_train/data.yaml + dernier .pt de ./models
    python train.py --model models/best.pt --epochs 80

A la fin, le meilleur modele est copie dans ./models (finetune_AAAAMMJJ_HHMM.pt) : il apparait
automatiquement dans la liste du menu. Necessite : pip install ultralytics"""
import argparse
import shutil
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
MODELS_DIR = APP_DIR / "models"


def latest_model() -> str | None:
    pts = sorted(MODELS_DIR.glob("*.pt"), key=lambda p: p.stat().st_mtime)
    return str(pts[-1]) if pts else None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--data", default=str(APP_DIR / "dataset_train" / "data.yaml"))
    p.add_argument("--model", default=latest_model(), help="poids de depart (.pt) ou .yaml")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--device", default=None, help="ex. 0, cpu (defaut : auto)")
    p.add_argument("--workers", type=int, default=0, help="0 recommande sous Windows")
    args = p.parse_args()

    if not args.model:
        raise SystemExit("Aucun .pt dans ./models : indiquez --model (poids de depart).")
    if not Path(args.data).exists():
        raise SystemExit(f"{args.data} introuvable : construisez le dataset depuis le menu (Dataset).")
    from ultralytics import YOLO

    model = YOLO(args.model)
    results = model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz, batch=args.batch,
                          device=args.device, workers=args.workers,
                          project=str(APP_DIR / "runs"), name="finetune", exist_ok=False)
    best = Path(results.save_dir) / "weights" / "best.pt"
    MODELS_DIR.mkdir(exist_ok=True)
    dest = MODELS_DIR / f"finetune_{datetime.now():%Y%m%d_%H%M}.pt"
    shutil.copy2(best, dest)
    print(f"\nModele copie dans {dest} : selectionnez-le dans le menu.")


if __name__ == "__main__":
    main()
