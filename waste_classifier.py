"""
waste_classifier.py
Lightweight YOLOv8n ONNX inference using onnxruntime only (no PyTorch/ultralytics).
Model:  models/yolov8n.onnx
Labels: models/class_names.txt  (one class name per line, in training index order)
Install: pip install onnxruntime opencv-python-headless numpy
"""
import logging, os
import numpy as np

logger = logging.getLogger(__name__)

try:
    import onnxruntime as ort
    import cv2
    ORT_AVAILABLE = True
except ImportError:
    logger.warning("onnxruntime/opencv not found - classifier in simulation mode.")
    ORT_AVAILABLE = False

# Model class name -> recycling category
COCO_TO_WASTE = {
    "plastic": "plastic",
    "glass":   "glass",
    "can":     "can",
    "paper":   "paper",
    "general": "general",
}
CATEGORY_BOX_COLOR = {   # BGR for drawing
    "plastic": (255, 150, 30), "glass": (110, 200, 30), "can": (30, 120, 230),
    "paper": (30, 200, 230), "general": (150, 150, 150),
}

CONFIDENCE_THRESHOLD = 0.40
IOU_THRESHOLD        = 0.45
INPUT_SIZE           = 480

_BASE = os.path.dirname(__file__)
MODEL_PATH  = os.path.join(_BASE, "models", "yolov8n.onnx")
LABELS_PATH = os.path.join(_BASE, "models", "class_names.txt")


class WasteClassifier:
    def __init__(self):
        self._session = None
        self._names = []
        if not ORT_AVAILABLE:
            logger.info("WasteClassifier: simulation mode.")
            return
        if not os.path.exists(MODEL_PATH):
            logger.error(f"{MODEL_PATH} not found - simulation mode.")
            return
        try:
            with open(LABELS_PATH) as f:
                self._names = [ln.strip() for ln in f if ln.strip()]
            logger.info(f"Loading ONNX: {MODEL_PATH}  ({len(self._names)} classes)")
            self._session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
            self._input_name = self._session.get_inputs()[0].name
            logger.info("YOLO ONNX loaded (onnxruntime).")
        except Exception as exc:
            logger.error(f"ONNX load failed: {exc}")
            self._session = None

    # ── public ────────────────────────────────────────────────
    def classify(self, frame):
        """frame (BGR ndarray) -> (category, confidence, annotated_frame)."""
        if self._session is None:
            label, conf = self._simulate()
            return label, conf, frame
        try:
            inp, scale, pad = self._preprocess(frame)
            out = self._session.run(None, {self._input_name: inp})[0]
            boxes = self._postprocess(out, scale, pad, frame.shape)
        except Exception as exc:
            logger.error(f"Inference error: {exc}")
            return None, 0.0, frame

        best_label, best_conf = None, 0.0
        annotated = frame.copy()
        for (x1, y1, x2, y2, conf, cls_id) in boxes:
            name = self._names[cls_id] if cls_id < len(self._names) else str(cls_id)
            category = COCO_TO_WASTE.get(name, "general")
            color = CATEGORY_BOX_COLOR.get(category, (150, 150, 150))
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, category, (x1, max(y1 - 8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)   # class only, no confidence
            if conf > best_conf:
                best_conf, best_label = conf, category

        if best_label:
            logger.info(f"Classified as {best_label} ({best_conf:.1%})")
        else:
            logger.info("No waste item detected above threshold.")
        return best_label, best_conf, annotated

    # ── helpers ───────────────────────────────────────────────
    def _preprocess(self, frame):
        h, w = frame.shape[:2]
        scale = INPUT_SIZE / max(h, w)
        nw, nh = int(round(w * scale)), int(round(h * scale))
        resized = cv2.resize(frame, (nw, nh))
        canvas = np.full((INPUT_SIZE, INPUT_SIZE, 3), 114, dtype=np.uint8)
        px, py = (INPUT_SIZE - nw) // 2, (INPUT_SIZE - nh) // 2
        canvas[py:py + nh, px:px + nw] = resized
        img = canvas.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))[None]   # (1,3,640,640)
        return np.ascontiguousarray(img), scale, (px, py)

    def _postprocess(self, out, scale, pad, shape):
        # out: (1, 4+num_classes, N) -> (N, 4+num_classes)
        pred = np.squeeze(out, 0).T
        ncls = pred.shape[1] - 4
        scores = pred[:, 4:]
        cls_ids = np.argmax(scores, axis=1)
        confs = scores[np.arange(scores.shape[0]), cls_ids]
        keep = confs > CONFIDENCE_THRESHOLD
        pred, cls_ids, confs = pred[keep], cls_ids[keep], confs[keep]
        if pred.shape[0] == 0:
            return []

        px, py = pad
        cx, cy, bw, bh = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
        x1 = (cx - bw / 2 - px) / scale
        y1 = (cy - bh / 2 - py) / scale
        x2 = (cx + bw / 2 - px) / scale
        y2 = (cy + bh / 2 - py) / scale
        H, W = shape[:2]
        rects = [[int(max(0, a)), int(max(0, b)),
                  int(min(W, c) - max(0, a)), int(min(H, d) - max(0, b))]
                 for a, b, c, d in zip(x1, y1, x2, y2)]
        idxs = cv2.dnn.NMSBoxes(rects, confs.tolist(), CONFIDENCE_THRESHOLD, IOU_THRESHOLD)
        if len(idxs) == 0:
            return []
        idxs = np.array(idxs).flatten()
        res = []
        for i in idxs:
            a, b, c, d = rects[i]
            res.append((a, b, a + c, b + d, float(confs[i]), int(cls_ids[i])))
        return res

    @staticmethod
    def _simulate():
        import random
        cats = ["bottle", "can", "paper", "glass", "food", "general"]
        label = random.choice(cats)
        conf = random.uniform(0.55, 0.95)
        logger.info(f"[SIM] {label} ({conf:.1%})")
        return label, conf
