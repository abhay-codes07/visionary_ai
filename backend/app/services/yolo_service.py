from __future__ import annotations

import base64
import logging
from typing import Any

import cv2
import numpy as np

from app.core.config import Settings, get_settings
from app.schemas.live import BoundingBox, LiveDetection

logger = logging.getLogger(__name__)


class YoloService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._model: Any | None = None

    # ------------------------------------------------------------------
    # Public API – called from a thread-pool executor so it may block.
    # ------------------------------------------------------------------
    def detect_from_base64(self, image_base64: str) -> list[LiveDetection]:
        frame = self._decode_frame(image_base64)
        if frame is None:
            logger.warning("[yolo] failed to decode frame (base64 length=%d)", len(image_base64))
            return []

        model = self._get_model()
        results = model.predict(frame, conf=self._settings.yolo_confidence_threshold, verbose=False)
        if not results:
            logger.debug("[yolo] model returned no results")
            return []

        detections: list[LiveDetection] = []
        for row in results[0].boxes:
            xyxy = row.xyxy[0].tolist()
            x1, y1, x2, y2 = xyxy
            cls_index = int(row.cls[0].item())
            label = model.names.get(cls_index, f"class-{cls_index}")
            confidence = float(row.conf[0].item())
            detections.append(
                LiveDetection(
                    label=label,
                    confidence=confidence,
                    box=BoundingBox(x=x1, y=y1, width=max(0.0, x2 - x1), height=max(0.0, y2 - y1)),
                )
            )

        logger.info("[yolo] detected %d objects: %s", len(detections), [d.label for d in detections])
        return detections

    def _get_model(self):
        if self._model is None:
            import os
            from pathlib import Path

            from ultralytics import YOLO

            model_name = self._settings.yolo_model  # e.g. "yolov8n.pt"
            # Search order: CWD, backend/ dir, /app/ (Docker workdir)
            candidates = [
                Path(model_name),
                Path(__file__).resolve().parents[2] / model_name,  # backend/
                Path("/app") / model_name,
            ]
            model_path = model_name  # fallback (lets ultralytics try download)
            for p in candidates:
                if p.is_file():
                    model_path = str(p)
                    break

            logger.info("[yolo] loading model from %s \u2026", model_path)
            self._model = YOLO(model_path)
            logger.info("[yolo] model loaded successfully")
        return self._model

    @staticmethod
    def _decode_frame(image_base64: str):
        try:
            raw = base64.b64decode(image_base64)
            array = np.frombuffer(raw, dtype=np.uint8)
            return cv2.imdecode(array, cv2.IMREAD_COLOR)
        except Exception:
            return None
