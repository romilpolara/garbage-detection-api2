import io
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

from app.analysis import analyze_waste
from app.detector import detect_objects


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Left coordinate")
    y1: float = Field(..., description="Top coordinate")
    x2: float = Field(..., description="Right coordinate")
    y2: float = Field(..., description="Bottom coordinate")


class DetectionResult(BaseModel):
    class_name: str = Field(..., alias="class")
    confidence: float
    bounding_box: BoundingBox
    biodegradable: bool
    estimated_weight: float
    energy_production: float
    severity: str

    model_config = {
        "populate_by_name": True,
    }


class SummaryResult(BaseModel):
    total_objects: int
    total_weight: float
    total_energy: float
    counts_by_class: Dict[str, int]


class WasteReport(BaseModel):
    biodegradable_count: int
    non_biodegradable_count: int
    highest_severity: str
    recommendation: str


class AnalyzeWasteResponse(BaseModel):
    detections: List[DetectionResult]
    summary: SummaryResult
    waste_report: WasteReport
    annotated_image_base64: Optional[str] = None
    annotated_image_data_url: Optional[str] = None


app = FastAPI(
    title="Garbage Detection AI API",
    description="Detect waste from an image and estimate biodegradability, weight, energy, and severity.",
    version="1.0.0",
)


def _get_allowed_origins() -> List[str]:
    raw_value = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if raw_value == "*":
        return ["*"]
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_image(file_bytes: bytes) -> Image.Image:
    try:
        return Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.") from exc


@app.get("/")
def home() -> Dict[str, str]:
    return {
        "message": "Garbage Detection API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze-waste", response_model=AnalyzeWasteResponse)
async def analyze_waste_endpoint(
    file: UploadFile = File(...),
    include_annotated_image: bool = Form(False),
) -> AnalyzeWasteResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    image = _load_image(file_bytes)

    detections, annotated_image_base64 = detect_objects(
        image=image,
        include_annotated_image=include_annotated_image,
    )
    analyzed_output = analyze_waste(detections)

    return AnalyzeWasteResponse(
        detections=analyzed_output["detections"],
        summary=analyzed_output["summary"],
        waste_report=analyzed_output["waste_report"],
        annotated_image_base64=annotated_image_base64,
        annotated_image_data_url=(
            f"data:image/jpeg;base64,{annotated_image_base64}" if annotated_image_base64 else None
        ),
    )
