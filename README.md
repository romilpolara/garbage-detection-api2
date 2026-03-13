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
python -m uvicorn app.main:app --reload
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

## Deploy on Azure

This project is now ready for Azure Container Apps using the included [`Dockerfile`](/c:/Users/ROMIL/Desktop/garbage-detection-api2/Dockerfile) and [`.dockerignore`](/c:/Users/ROMIL/Desktop/garbage-detection-api2/.dockerignore).

### Why Azure Container Apps

- Better fit for a YOLO API than a small free web instance
- Supports custom containers
- Works well with FastAPI
- Easier to scale memory for `torch` and `ultralytics`

### One-time setup

Install and sign in to Azure CLI:

```bash
az login
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

### Deploy from this folder

Run these commands from the project root:

```bash
az group create --name garbage-detection-rg --location centralindia
az containerapp up \
  --name garbage-detection-api \
  --resource-group garbage-detection-rg \
  --location centralindia \
  --ingress external \
  --target-port 8000 \
  --env-vars ALLOWED_ORIGINS=* \
  --source .
```

Azure will build the container from your local source and deploy it.

### Recommended Azure settings

After the first deploy, set your container resources high enough for YOLO inference:

- CPU: `1`
- Memory: `2Gi` or `4Gi`

### Test after deployment

Open:

- `https://YOUR-AZURE-URL/docs`

Use:

- `POST /analyze-waste`
- upload `file`
- set `include_annotated_image=true` if you want the output image with bounding boxes

## Connect your application

Frontend or mobile app flow:

1. User selects an image.
2. App sends a `multipart/form-data` POST request to:
   - `https://YOUR-AZURE-URL/analyze-waste`
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

const response = await fetch("https://YOUR-AZURE-URL/analyze-waste", {
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
  Uri.parse('https://YOUR-AZURE-URL/analyze-waste'),
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

### Why this API works well on Azure

- The YOLO model loads once and stays in memory
- `/health` is available for checks
- `annotated_image_data_url` can be shown directly in your app
- Ultralytics and matplotlib config paths are set to `/tmp`, which is safer for cloud containers
