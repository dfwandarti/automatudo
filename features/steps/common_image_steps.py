import re
from pathlib import Path
from typing import Any
from venv import logger

import cv2
import numpy as np
from behave import then
from cv2 import Mat
from numpy import dtype, floating, integer, ndarray
from playwright.sync_api import Page  # type: ignore[import-untyped]
from ultralytics import YOLO

from python.page_field.page_field import PageField
from python.config.browser_config import BrowserConfig
from python.page_field.from_display_name import PageFieldFactory

SNAPSHOTS_DIR = Path(__file__).parents[2] / "static" / "snapshots"
DIFF_THRESHOLD = 0.05  # allow up to 5% of pixels to differ
YOLO_MODEL_PATH = Path(__file__).parents[2] / "yolo_models" / "logos-2026-06-24.pt"
_yolo_model: YOLO | None = None


@then("Imagem {display_name} é como esperada")  # type: ignore[misc]
def assert_same_image(context: Any, display_name: str) -> None:
    page: Page = context.page  # type: ignore
    field = PageFieldFactory.from_display_name(page, display_name)

    actual_image, actual_snapshot_path = get_actual_image(display_name, field, page)
    expected_image: cv2.typing.MatLike = get_expected_image(display_name, actual_snapshot_path)

    if actual_image.shape != expected_image.shape:
        expected_size = (actual_image.shape[1], actual_image.shape[0])  # (width, height)
        expected_image = cv2.resize(expected_image, expected_size, interpolation=cv2.INTER_LINEAR)

    diff = cv2.absdiff(actual_image, expected_image)
    differing_pixels = np.count_nonzero(diff.any(axis=2))
    total_pixels = actual_image.shape[0] * actual_image.shape[1]
    diff_ratio = differing_pixels / total_pixels

    assert diff_ratio <= DIFF_THRESHOLD, (
        f"Image '{display_name}' differs from reference by "
        f"{diff_ratio:.2%} ({differing_pixels}/{total_pixels} pixels). "
    )


def get_expected_image(display_name: str, actual_snapshot_path: str) -> cv2.typing.MatLike:
    expected_snapshot_path = _display_name_to_filepath(display_name, "expected")
    if not expected_snapshot_path.exists():
        logger.info(f"[Tip] if image is correct fix with 'cp {actual_snapshot_path} {expected_snapshot_path}'")
        raise AssertionError(f"No expected image found for '{display_name}' at {expected_snapshot_path}.")

    expected_image = cv2.imread(str(expected_snapshot_path))
    if expected_image is None:
        logger.info(f"[Tip] if image is correct fix with 'cp {actual_snapshot_path} {expected_snapshot_path}'")
        raise AssertionError(f"Could not read reference image at {expected_snapshot_path}.")

    return expected_image


def get_actual_image(display_name: str, field: PageField, page: Page) -> [cv2.typing.MatLike, str]:
    bounding_box = field.locator.bounding_box()
    if bounding_box is None or bounding_box["width"] == 0 or bounding_box["height"] == 0:
        raise AssertionError(f"Element '{display_name}' is not visible for image comparison.")

    screenshot_bytes: bytes = page.screenshot(clip=bounding_box)
    actual_image: cv2.typing.MatLike = cv2.imdecode(np.frombuffer(screenshot_bytes, np.uint8), cv2.IMREAD_COLOR)
    if actual_image is None:
        raise AssertionError(f"Could not decode actual screenshot for '{display_name}'.")
    actual_image_path = _display_name_to_filepath(display_name, "actual")
    cv2.imwrite(str(actual_image_path), actual_image)
    return actual_image, str(actual_image_path)


def _sanitize(text: str) -> str:
    return re.sub(r"[^\w\-]", "_", text)


def _display_name_to_filepath(display_name: str, actual_or_expected: str) -> Path:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    device_type = BrowserConfig.get_device_type()
    filename = f"{_sanitize(display_name)}__{_sanitize(device_type)}__{actual_or_expected}.png"
    return SNAPSHOTS_DIR / filename

