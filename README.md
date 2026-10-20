# yolo_capture

Base : capture d'une fenetre Windows a FPS maximum + inference YOLO (ONNX), avec repli
automatique selon la configuration de la machine.

## Installation (adaptee a la machine)
```
python install.py
```
Detecte le GPU (NVIDIA -> onnxruntime-gpu, sinon DirectML sous Windows, sinon CPU).

## Utilisation
Deposer le modele (`.pt` ou `.onnx`) dans `./models`, puis :
```
python main.py              # ouvre le menu de configuration
python main.py --no-menu    # relance avec la derniere configuration (config.json)
python main.py --window "titre" [--model ...] [--capture ...]   # sans menu
```
Le **menu** (PySide6 + QML : backend `config_ui.py`, interface et theme dans `ui/`) permet de choisir la fenetre, le modele, la methode de capture,
l'acceleration d'inference, le seuil de confiance et l'apercu. Les options incompatibles avec
la machine sont **grisees avec la raison** (paquet manquant, session RDP, Windows trop ancien,
GPU absent, modele non-detection...). Les choix sont sauvegardes dans `config.json`.

Compatibilite verifiee dans `capture/compat.py` et `inference/compat.py` : pour ajouter une
methode ou un provider, l'ajouter a `BACKENDS`/`PROVIDERS` et ecrire sa fonction `check_*`.

### Mode automatique (CLI)
- fenetre : choisie dans une liste (ou `--window "titre"`)
- modele : detecte automatiquement ; un `.pt` est exporte en ONNX une seule fois
- capture : meilleur backend disponible (wgc > dxcam > mss), repli automatique
- inference : meilleur provider disponible (TensorRT > CUDA > DirectML > OpenVINO > CPU), repli automatique
- taille d'entree, FP16/FP32, noms de classes, format de sortie (YOLO26 end-to-end ou classique) : lus depuis le modele

Options facultatives pour forcer un choix : `--capture`, `--provider`, `--model`, `--conf`, `--no-display`.
Sans modele : capture seule (benchmark). Quitter : `q`/`Echap` ou `Ctrl+C`.

Limite : seuls les modeles de **detection** sont geres (pas segmentation/pose/obb).

## Structure
- `capture/` : backends `wgc` > `dxcam` > `mss` (repli auto, test de vraie frame), interface commune.
- `inference/` : `OnnxDetector` (TensorRT > CUDA > DirectML > OpenVINO > CPU), formats end-to-end (YOLO26) et classique.
- `pipeline.py` : capture, inference et affichage dans des threads separes, toujours la derniere frame.
- `user_logic.py` : **votre code** : `on_result(frame, detections)` est appele a chaque frame.

## Pour aller plus loin
- Ajouter un backend : heriter de `CaptureBackend`, appeler `_publish(frame_bgr)`, l'ajouter dans `capture/__init__.py`.
- Si l'inference est le goulot : modele plus petit, `--imgsz` plus bas, ONNX FP16.
- Si `dxcam` renvoie du noir sur portable hybride : tester un autre `device_idx` dans `dxcam_backend.py`.
