import base64
import io
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "weights" / "best.pt"))
_model: Optional[YOLO] = None


def get_model() -> YOLO:
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model weights not found at {MODEL_PATH}")
        _model = YOLO(str(MODEL_PATH))
    return _model


def _encode_annotated_image(results) -> str:
    plotted = results[0].plot()
    annotated_image = Image.fromarray(plotted[:, :, ::-1])

    buffer = io.BytesIO()
    annotated_image.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def detect_objects(
    image: Image.Image,
    include_annotated_image: bool = False,
) -> Tuple[List[Dict], Optional[str]]:
    model = get_model()
    results = model.predict(image, verbose=False)

    detections: List[Dict] = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            confidence = round(float(box.conf[0].item()), 4)
            x1, y1, x2, y2 = [round(float(value), 2) for value in box.xyxy[0].tolist()]

            detections.append(
                {
                    "class": model.names[class_id],
                    "confidence": confidence,
                    "bounding_box": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    },
                }
            )

    annotated_image_base64 = None
    if include_annotated_image:
        annotated_image_base64 = _encode_annotated_image(results)

    return detections, annotated_image_base64
