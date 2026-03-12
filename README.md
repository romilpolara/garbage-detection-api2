# Garbage Detection API

FastAPI API for garbage detection using a YOLO model stored at `weights/best.pt`.

## Features

- Waste detection with YOLO
- Bounding box output
- Biodegradable vs non-biodegradable analysis
- Estimated weight and energy output
- Severity report
- Optional annotated image as base64
- Optional annotated image as a ready-to-show data URL
- Swagger UI at `/docs`

## Project structure

```text
garbage-detection-api2/
|-- app/
|   |-- analysis.py
|   |-- detector.py
|   `-- main.py
|-- weights/
|   `-- best.pt
`-- requirements.txt
```

## Install

```bash
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`

## Main endpoint

`POST /analyze-waste`

Form fields:

- `file`: image file
- `include_annotated_image`: `true` or `false`

If `include_annotated_image=true`, the API returns both:

- `annotated_image_base64`
- `annotated_image_data_url`

You can use `annotated_image_data_url` directly inside an `<img>` tag or in your mobile/web app image component.

## Example response

```json
{
  "detections": [
    {
      "class": "plastic",
      "confidence": 0.9123,
      "bounding_box": {
        "x1": 25.4,
        "y1": 62.7,
        "x2": 180.1,
        "y2": 240.8
      },
      "biodegradable": false,
      "estimated_weight": 0.3,
      "energy_production": 1.2,
      "severity": "medium"
    }
  ],
  "summary": {
    "total_objects": 1,
    "total_weight": 0.3,
    "total_energy": 1.2,
    "counts_by_class": {
      "plastic": 1
    }
  },
  "waste_report": {
    "biodegradable_count": 0,
    "non_biodegradable_count": 1,
    "highest_severity": "medium",
    "recommendation": "Sort the waste by type and send recyclable material for further processing."
  },
  "annotated_image_base64": null,
  "annotated_image_data_url": null
}
```

## Deploy on Render

Render's current FastAPI docs show a Python web service with:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn ... --host 0.0.0.0 --port $PORT`

This repo already includes [`render.yaml`](/c:/Users/ROMIL/Desktop/garbage-detection-api2/render.yaml) with the correct settings and pins Python to `3.12.2` so Render matches your local environment more closely.

### Steps

1. Push this project to GitHub.
2. Open Render Dashboard.
3. Click `New` -> `Blueprint`.
4. Connect your GitHub repository.
5. Render will read `render.yaml` automatically.
6. After deploy finishes, open:
   - `https://YOUR-SERVICE.onrender.com/docs`

### Important note about speed

Render free services can spin down after inactivity, which makes the first request slower. For faster repeated responses, keep the service warm with traffic or use a paid plan.

## Connect your application

Frontend or mobile app flow:

1. User selects an image.
2. App sends a `multipart/form-data` POST request to:
   - `https://YOUR-SERVICE.onrender.com/analyze-waste`
3. App reads JSON response.
4. Show:
   - `detections`
   - `summary`
   - `waste_report`
   - `annotated_image_data_url`

### JavaScript example

```javascript
const formData = new FormData();
formData.append("file", imageFile);
formData.append("include_annotated_image", "true");

const response = await fetch("https://YOUR-SERVICE.onrender.com/analyze-waste", {
  method: "POST",
  body: formData,
});

const data = await response.json();

console.log(data.summary);
document.getElementById("result-image").src = data.annotated_image_data_url;
```

### Flutter example

```dart
final request = http.MultipartRequest(
  'POST',
  Uri.parse('https://YOUR-SERVICE.onrender.com/analyze-waste'),
);

request.fields['include_annotated_image'] = 'true';
request.files.add(await http.MultipartFile.fromPath('file', imagePath));

final streamedResponse = await request.send();
final responseBody = await streamedResponse.stream.bytesToString();
final data = jsonDecode(responseBody);

final imageDataUrl = data['annotated_image_data_url'];
final base64String = imageDataUrl.split(',').last;
final imageBytes = base64Decode(base64String);
```

## Official Render references

- Render FastAPI deploy docs: https://render.com/docs/deploy-fastapi
- Render web services docs: https://render.com/docs/web-services
- Render Python version docs: https://render.com/docs/python-version

## Render start command

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
