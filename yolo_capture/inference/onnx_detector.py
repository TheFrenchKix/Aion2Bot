"""Detecteur YOLO ONNX avec choix automatique du meilleur provider disponible.

Gere deux formats de sortie :
  - end-to-end sans NMS (YOLO26 par defaut) : (1, N, 6) = x1, y1, x2, y2, score, classe
  - classique (YOLOv8/11) : (1, 4+nc, anchors) -> decodage + NMS ici
"""
import ast

import cv2
import numpy as np
import onnxruntime as ort

from .base import Detection, Detector

PROVIDER_PRIORITY = (
    "TensorrtExecutionProvider",
    "CUDAExecutionProvider",
    "DmlExecutionProvider",
    "OpenVINOExecutionProvider",
    "CPUExecutionProvider",
)


class OnnxDetector(Detector):
    def __init__(self, model_path: str, imgsz: int = 640, conf: float = 0.25,
                 iou: float = 0.45, provider: str = "auto",
                 names: dict[int, str] | None = None) -> None:
        available = ort.get_available_providers()
        if provider == "auto":
            chain = [p for p in PROVIDER_PRIORITY if p in available]
        else:
            chain = [provider]
        if "CPUExecutionProvider" not in chain:
            chain.append("CPUExecutionProvider")  # filet de securite final

        self.conf, self.iou, self.imgsz = conf, iou, imgsz
        self.sess, self.provider = self._open_first_working(model_path, chain)
        print(f"[inference] provider retenu : {self.provider} | entree {self.in_w}x{self.in_h}"
              f"{' (fp16)' if self.fp16 else ''}")
        self.names = names or self._names_from_metadata()
        task = self.sess.get_modelmeta().custom_metadata_map.get("task", "detect")
        if task != "detect":
            raise ValueError(f"Modele de type '{task}' non supporte : seule la detection "
                             "(boites) est geree. Adapter _postprocess pour ce type.")

    def _open_first_working(self, model_path: str, chain: list[str]):
        """Essaie chaque provider (creation + inference de test) jusqu'a un qui marche :
        une DLL CUDA manquante ou un GPU incompatible ne bloque donc jamais le projet."""
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        errors = []
        for p in chain:
            try:
                sess = ort.InferenceSession(model_path, so, providers=[p, "CPUExecutionProvider"]
                                            if p != "CPUExecutionProvider" else [p])
                if p not in sess.get_providers():
                    raise RuntimeError("provider non active (repli silencieux sur CPU)")
                inp = sess.get_inputs()[0]
                shape = inp.shape  # [1, 3, H, W] ; H/W peuvent etre dynamiques (str/None)
                self.input_name = inp.name
                self.in_h = shape[2] if isinstance(shape[2], int) else self.imgsz
                self.in_w = shape[3] if isinstance(shape[3], int) else self.imgsz
                self.fp16 = "float16" in inp.type
                dummy = np.zeros((1, 3, self.in_h, self.in_w),
                                 np.float16 if self.fp16 else np.float32)
                sess.run(None, {self.input_name: dummy})  # warmup + validation
                return sess, p
            except Exception as e:
                errors.append(f"{p}: {str(e).splitlines()[0][:120]}")
                print(f"[inference] {p} indisponible -> {errors[-1]}")
        raise RuntimeError("Aucun provider ONNX utilisable :\n  " + "\n  ".join(errors))

    def _names_from_metadata(self) -> dict[int, str]:
        meta = self.sess.get_modelmeta().custom_metadata_map
        try:
            return {int(k): v for k, v in ast.literal_eval(meta["names"]).items()}
        except Exception:
            return {}

    def _letterbox(self, img: np.ndarray):
        h, w = img.shape[:2]
        r = min(self.in_h / h, self.in_w / w)
        nh, nw = round(h * r), round(w * r)
        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((self.in_h, self.in_w, 3), 114, np.uint8)
        top, left = (self.in_h - nh) // 2, (self.in_w - nw) // 2
        canvas[top:top + nh, left:left + nw] = resized
        return canvas, r, left, top

    def predict(self, frame_bgr: np.ndarray) -> list[Detection]:
        canvas, r, left, top = self._letterbox(frame_bgr)
        blob = canvas[:, :, ::-1].transpose(2, 0, 1)[None]  # BGR->RGB, HWC->CHW
        blob = np.ascontiguousarray(blob, dtype=np.float16 if self.fp16 else np.float32)
        blob /= 255.0
        out = self.sess.run(None, {self.input_name: blob})[0]
        return self._postprocess(out, r, left, top, frame_bgr.shape[1], frame_bgr.shape[0])

    def _postprocess(self, out, r, left, top, w, h) -> list[Detection]:
        out = out[0].astype(np.float32)
        end2end = out.shape[-1] == 6 and out.shape[0] != 6
        if end2end:                                          # (N, 6)
            boxes, scores, cls = out[:, :4], out[:, 4], out[:, 5].astype(int)
        else:                                                # classique (4+nc, A)
            out = out.T
            cls_scores = out[:, 4:]
            cls = cls_scores.argmax(1)
            scores = cls_scores.max(1)
            cx, cy, bw, bh = out[:, 0], out[:, 1], out[:, 2], out[:, 3]
            boxes = np.stack([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], 1)
        keep = scores >= self.conf
        boxes, scores, cls = boxes[keep], scores[keep], cls[keep]
        if not end2end and len(boxes):                       # NMS seulement en mode classique
            xywh = np.stack([boxes[:, 0], boxes[:, 1],
                             boxes[:, 2] - boxes[:, 0], boxes[:, 3] - boxes[:, 1]], 1)
            idx = cv2.dnn.NMSBoxes(xywh.tolist(), scores.tolist(), self.conf, self.iou)
            idx = np.asarray(idx).flatten().astype(int)
            boxes, scores, cls = boxes[idx], scores[idx], cls[idx]
        # repere letterbox -> repere frame d'origine
        boxes[:, [0, 2]] = ((boxes[:, [0, 2]] - left) / r).clip(0, w)
        boxes[:, [1, 3]] = ((boxes[:, [1, 3]] - top) / r).clip(0, h)
        return [Detection(*b.tolist(), float(s), int(c), self.names.get(int(c), str(int(c))))
                for b, s, c in zip(boxes, scores, cls)]
