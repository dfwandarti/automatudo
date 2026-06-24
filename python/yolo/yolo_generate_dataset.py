import random
import re
import uuid
from pathlib import Path

import cv2
import numpy as np
from playwright.sync_api import Page, Locator

TRAIN_RATIO = 0.7
VAL_RATIO = 0.9
OUTPUT_DIR = Path("yolo_dataset")

# IMPORTANT:
# Every time you add a new yolo class, update custom.yaml on yolo_datasets folder.
display_name_to_yolo_class = {
    # "login - logo wesayso": 0,
    # "login - logo acme": 1,
}


class YoloDataset:

    @classmethod
    def get_yolo_class(cls, display_name: str) -> int | None:
        return display_name_to_yolo_class.get(display_name)

    @classmethod
    def generate_dataset(cls, display_name: str, page: Page, locator: Locator) -> None:
        yolo_class: int | None = cls.get_yolo_class(display_name)
        if yolo_class is None:
            return

        bbox = locator.bounding_box()
        if bbox is None or bbox['width'] == 0 or bbox['height'] == 0:
            return

        screenshot_bytes = page.screenshot()
        img = cv2.imdecode(np.frombuffer(screenshot_bytes, np.uint8), cv2.IMREAD_COLOR)

        x_r = bbox['x']
        y_r = bbox['y']
        w_r = bbox['width']
        h_r = bbox['height']

        img_h, img_w = img.shape[:2]
        x_center = (x_r + w_r / 2) / img_w
        y_center = (y_r + h_r / 2) / img_h
        norm_w = w_r / img_w
        norm_h = h_r / img_h

        split = cls.get_split()

        images_dir = OUTPUT_DIR / 'images' / split
        labels_dir = OUTPUT_DIR / 'labels' / split
        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)

        name = f"{re.sub(r'[^a-zA-Z0-9]', '_', display_name)}_{uuid.uuid4()}"
        cv2.imwrite(str(images_dir / f"{name}.jpg"), img)

        label = f"{yolo_class} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}"
        (labels_dir / f"{name}.txt").write_text(label + '\n')

    @classmethod
    def get_split(cls):
        train_val_or_test = random.random()
        if train_val_or_test < TRAIN_RATIO:
            split = 'train'
        elif train_val_or_test < VAL_RATIO:
            split = 'val'
        else:
            split = 'test'
        return split
