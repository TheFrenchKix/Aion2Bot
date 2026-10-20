# Aion2Bot

Capture d'une fenêtre Windows à FPS maximum, détection YOLO (ONNX) et outils pour agrandir le
dataset puis réentraîner le modèle. Tout fonctionne avec un repli automatique selon la
configuration de la machine. Le projet est dans le dossier `yolo_capture/`.

## Installation
```
cd yolo_capture
python install.py
```
Détecte le GPU (NVIDIA → `onnxruntime-gpu`, sinon DirectML sous Windows, sinon CPU) et installe
les dépendances, dont PySide6 pour le menu. `ultralytics` est nécessaire pour utiliser un `.pt`
et pour l'entraînement (`pip install ultralytics`).

## Utilisation
Déposer le modèle (`.pt` ou `.onnx`) dans `yolo_capture/models/`, puis :
```
python main.py              # ouvre le menu de configuration
python main.py --no-menu    # relance avec la dernière configuration (config.json)
python main.py --window "titre" [--model ...] [--capture ...]   # sans menu
```
Quitter : `q` / `Échap` dans l'aperçu, ou `Ctrl+C`.

## Le menu (PySide6 + QML)
Navigation latérale ; le backend est `config_ui.py`, l'interface et le thème sont dans `ui/`.

| Page | Contenu |
|---|---|
| **Général** | Fenêtre cible, modèle (liste du dossier `models/`), méthode de capture, accélération d'inférence, seuil de confiance, aperçu. |
| **Debug** | Auto-trainer : enregistre des images pour agrandir le dataset. |
| **Dataset** | Auto-labellisation, contrôle, construction du dataset d'entraînement, fine-tuning. |
| **Instances** | À venir (plusieurs fenêtres en parallèle). |

Les options incompatibles avec la machine sont **grisées avec la raison** (paquet manquant,
session RDP, Windows trop ancien, GPU absent, modèle autre que détection…). Les choix sont
sauvegardés dans `config.json`.

## Agrandir le dataset et réentraîner
1. **Debug → Auto-trainer** (ou `--auto-trainer [--auto-interval N]`) : enregistre une image
   toutes les N images (1000 par défaut) où le modèle détecte au moins un objet, dans
   `dataset_auto/images/`. Les images sont brutes. Les prédictions du modèle sont une option
   (`pre_labels/`), jamais utilisées pour l'entraînement. L'écriture se fait dans un thread dédié.
2. **Dataset → Auto-labellisation** : génère les labels YOLO dans `dataset_auto/labels/` et des
   aperçus annotés dans `dataset_auto/preview/`.
   - *Images de référence* (recommandé) : déposer une image par objet dans `references/` (le nom du
     fichier donne la classe, `boss.png`, `boss__2.png`…). Recherche par correspondance multi-échelle,
     indépendante du modèle. Un PNG transparent est recadré automatiquement.
   - *Modèle actuel* : pré-annotation par le modèle sélectionné, à relire attentivement.
3. **Contrôle** : ouvrir les aperçus. Corriger un label en éditant `dataset_auto/labels/<nom>.txt`
   (CVAT, Label Studio, labelImg…), l'exclure en supprimant ce fichier. Les images sans détection
   restent sans label : les labelliser à la main si elles contiennent l'objet.
4. **Construire le dataset** : copie les images labellisées dans `dataset_train/` (80 % train /
   20 % validation) avec son `data.yaml`.
5. **Intégrer au modèle** :
   ```
   python train.py                          # dernier .pt de models/, dataset_train/data.yaml
   python train.py --model models/best.pt --epochs 80 --imgsz 640
   ```
   Le meilleur modèle est copié dans `models/` (`finetune_AAAAMMJJ_HHMM.pt`) et apparaît
   automatiquement dans le menu.

Limites : la correspondance de modèle est fiable si l'objet garde le même aspect, moins s'il change
d'angle ou d'éclairage (réglable avec le seuil). Les classes viennent des noms de fichiers de
`references/` : si elles diffèrent de celles du modèle actuel, réentraîner sur un dataset qui
contient toutes les classes.

## Mode automatique
- capture : meilleur backend disponible (`wgc` > `dxcam` > `mss`), repli automatique
- inférence : meilleur provider disponible (TensorRT > CUDA > DirectML > OpenVINO > CPU)
- taille d'entrée, FP16/FP32, noms de classes, format de sortie (YOLO26 end-to-end ou classique) : lus depuis le modèle
- un `.pt` est exporté en ONNX une seule fois ; sans modèle, capture seule (benchmark)

Options pour forcer un choix : `--capture`, `--provider`, `--model`, `--conf`, `--no-display`.
Seuls les modèles de **détection** sont gérés (pas segmentation/pose/obb).

## Structure (`yolo_capture/`)
- `main.py` : point d'entrée (menu ou CLI).
- `config_ui.py`, `ui/` : menu PySide6 + QML (`Theme.qml` : couleurs, rayons, police).
- `capture/` : backends de capture et vérification de compatibilité (`compat.py`).
- `inference/` : détecteur ONNX, providers, vérification des modèles (`compat.py`).
- `pipeline.py` : capture, inférence et affichage dans des threads séparés, toujours la dernière frame.
- `autotrainer.py` : enregistrement automatique d'images (Debug).
- `autolabel.py` : auto-labellisation et construction du dataset.
- `train.py` : fine-tuning.
- `user_logic.py` : **votre code** : `on_result(frame, detections)` est appelé à chaque frame.
- `settings.py` : réglages sauvegardés dans `config.json`.

## Pour aller plus loin
- Ajouter un sous-menu : une entrée dans `pages` (`ui/Main.qml`) et une page `ui/XxxPage.qml` ajoutée au `StackLayout` dans le même ordre (`ComingSoonPage` sert de gabarit).
- Ajouter une méthode de capture ou un provider : l'ajouter à `BACKENDS` / `PROVIDERS` et écrire sa fonction `check_*` (`compat.py`).
- Si l'inférence est le goulot : modèle plus petit, `--imgsz` plus bas, ONNX FP16.
- Si `dxcam` renvoie du noir sur portable hybride : tester un autre `device_idx` dans `capture/dxcam_backend.py`.
