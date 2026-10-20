import argparse
import time

import cv2

from capture import make_capture
from capture.winapi import list_windows, set_dpi_aware
from inference import make_detector, resolve_model
from pipeline import Pipeline, draw
from settings import Settings
from user_logic import on_result


def parse_args():
    p = argparse.ArgumentParser(
        description="Capture de fenetre + detection YOLO. Sans --window : menu de configuration.")
    p.add_argument("--window", help="Partie du titre de la fenetre (lance sans menu)")
    p.add_argument("--list-windows", action="store_true", help="Lister les fenetres et quitter")
    p.add_argument("--no-menu", action="store_true",
                   help="Utiliser la derniere configuration sauvegardee, sans menu")
    p.add_argument("--model", help=".onnx ou .pt (sinon detecte dans ./models ou ./)")
    p.add_argument("--capture", default="auto", choices=["auto", "wgc", "dxcam", "mss"])
    p.add_argument("--provider", default="auto",
                   help="auto | TensorrtExecutionProvider | CUDAExecutionProvider | "
                        "DmlExecutionProvider | OpenVINOExecutionProvider | CPUExecutionProvider")
    p.add_argument("--imgsz", type=int, default=640, help="Utilise si l'ONNX est dynamique")
    p.add_argument("--conf", type=float, default=0.25)
    p.add_argument("--iou", type=float, default=0.45, help="NMS (modeles non end-to-end)")
    p.add_argument("--no-display", action="store_true", help="Pas de fenetre d'apercu")
    p.add_argument("--display-fps", type=int, default=30)
    return p.parse_args()


def get_settings(args) -> Settings | None:
    if args.window:  # mode ligne de commande : le modele est detecte si --model absent
        return Settings(window=args.window, model=args.model or resolve_model(None) or "",
                        capture=args.capture,
                        provider=args.provider, conf=args.conf, iou=args.iou,
                        imgsz=args.imgsz, preview=not args.no_display,
                        display_fps=args.display_fps)
    saved = Settings.load()
    if args.no_menu:
        if not saved.window:
            raise SystemExit("Aucune configuration sauvegardee : lancer sans --no-menu.")
        return saved
    from config_ui import run_menu
    return run_menu(saved)


def run(s: Settings) -> None:
    capture = make_capture(s.window, s.capture)
    # --model non fourni en CLI : recherche automatique ; via le menu, "" = capture seule
    detector = make_detector(s.model, discover=False, imgsz=s.imgsz, conf=s.conf,
                             iou=s.iou, provider=s.provider)
    pipe = Pipeline(capture, detector, on_result=on_result)
    pipe.start()
    try:
        period = 1.0 / max(s.display_fps, 1)
        last_print = 0.0
        while True:
            t0 = time.perf_counter()
            res = pipe.get_result()
            if res is not None and s.preview:
                cv2.imshow("Aion2Bot", draw(res, pipe.fps.fps))
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
            elif not s.preview and time.perf_counter() - last_print > 1.0:
                last_print = time.perf_counter()
                n = len(res.detections) if res else 0
                print(f"{pipe.fps.fps:6.1f} FPS | {n} detection(s)")
            time.sleep(max(0.0, period - (time.perf_counter() - t0)))
    except KeyboardInterrupt:
        pass
    finally:
        pipe.stop()
        cv2.destroyAllWindows()


def main():
    args = parse_args()
    set_dpi_aware()
    if args.list_windows:
        for hwnd, title in list_windows():
            print(f"{hwnd:>10}  {title}")
        return
    settings = get_settings(args)
    if settings is None:  # menu ferme sans lancer
        return
    try:
        run(settings)
    except (RuntimeError, LookupError, FileNotFoundError, ValueError) as e:
        raise SystemExit(f"Erreur : {e}")


if __name__ == "__main__":
    main()
