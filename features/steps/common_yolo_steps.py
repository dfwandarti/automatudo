# import re
from pathlib import Path
from typing import Any
from venv import logger

import cv2
import numpy as np
from behave import then
# from cv2 import Mat
# from numpy import dtype, floating, integer, ndarray
from playwright.sync_api import Page  # type: ignore[import-untyped]
from ultralytics import YOLO

from python.page_field.page_field import PageField
from python.config.browser_config import BrowserConfig
from python.page_field.from_display_name import PageFieldFactory

YOLO_MODEL_PATH = Path(__file__).parents[2] / "yolo_models" / "logos-2026-06-24.pt"
_yolo_model: YOLO | None = None


@then("A imagem {class_name} é encontrada {expectedCount:d} vez") # type: ignore[misc]
@then("A imagem {class_name} é encontrada {expectedCount:d} vezes") # type: ignore[misc]
def assert_single_logo_image(context: Any, class_name: str, expectedCount: int) -> None:
    detected_objects: dict[str, Any] = _detect_page_objects(context.page)

    logger.info(f"[YOLO] Detectados: {_format_detection_summary(detected_objects)}")
    
    assert detected_objects is not None, "Não foi possível detectar objetos na página."
    actualCount = detected_objects.get(class_name, {}).get("count", 0)
    logger.info(f"expectedCount: {expectedCount} {type(expectedCount)}, actualCount: {actualCount} {type(actualCount)}")
    assert actualCount == expectedCount, f"Esperado {expectedCount} ocorrência(s) de '{class_name}', mas YOLO encontrou {actualCount} > {expectedCount == actualCount}. Resumo: {_format_detection_summary(detected_objects)}"

def _detect_page_objects(page: Page) -> dict[str, Any]:
    screenshot_bytes: bytes = page.screenshot()
    image = cv2.imdecode(np.frombuffer(screenshot_bytes, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise AssertionError("Não foi possível decodificar screenshot para inferência YOLO.")

    results = _get_yolo_model().predict(image, verbose=False)
    if not results:
        return dict()

    result = results[0]
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        return dict()

    detections: dict[str, Any] = dict()
    names = result.names

    for idx in range(len(boxes)):
        class_id = int(boxes.cls[idx].item())
        confidence = float(boxes.conf[idx].item())
        bbox = [float(v) for v in boxes.xyxy[idx].tolist()]

        if isinstance(names, dict):
            class_name = str(names.get(class_id, class_id))
        else:
            class_name = str(names[class_id]) if names and class_id < len(names) else str(class_id)

        count = detections.get(class_name, {}).get("count", 0)
        detections[class_name] = {
            "class_id": class_id,
            "class_name": class_name,
            "confidence": confidence,
            "bbox": bbox,
            "count": count + 1,
        }        

    return detections


def _format_detection_summary(detections: dict[str, Any]) -> str:
    if not detections:
        return "nenhum objeto"

    counts: dict[str, int] = {}
    for det in detections.values():
        class_name = str(det["class_name"])
        counts[class_name] = counts.get(class_name, 0) + 1

    return ", ".join(f"{class_name}={count}" for class_name, count in sorted(counts.items()))
    
def _get_yolo_model() -> YOLO:
    global _yolo_model
    if _yolo_model is None:
        _yolo_model = YOLO(str(YOLO_MODEL_PATH))
    return _yolo_model
