from typing import Dict, List


WASTE_DATA = {
    "plastic": {"biodegradable": False, "weight": 0.30, "energy": 1.20},
    "paper": {"biodegradable": True, "weight": 0.10, "energy": 0.50},
    "glass": {"biodegradable": False, "weight": 0.50, "energy": 0.00},
    "metal": {"biodegradable": False, "weight": 0.40, "energy": 0.20},
    "cardboard": {"biodegradable": True, "weight": 0.20, "energy": 0.80},
    "biodegradable": {"biodegradable": True, "weight": 0.25, "energy": 0.60},
}

DEFAULT_WASTE_PROFILE = {"biodegradable": False, "weight": 0.20, "energy": 0.30}


def calculate_severity(weight: float) -> str:
    if weight < 0.2:
        return "low"
    if weight < 0.5:
        return "medium"
    return "high"


def build_recommendation(total_weight: float, highest_severity: str, biodegradable_count: int) -> str:
    if highest_severity == "high":
        return "Immediate cleanup is recommended because the waste load is high."
    if biodegradable_count and total_weight < 1:
        return "Segregate biodegradable waste for composting and recycle the rest."
    return "Sort the waste by type and send recyclable material for further processing."


def analyze_waste(detections: List[Dict]) -> Dict:
    analyzed_detections = []
    counts_by_class: Dict[str, int] = {}
    total_weight = 0.0
    total_energy = 0.0
    biodegradable_count = 0
    non_biodegradable_count = 0
    highest_severity_rank = 0
    severity_order = {"low": 1, "medium": 2, "high": 3}

    for detection in detections:
        class_name = detection["class"]
        waste_profile = WASTE_DATA.get(class_name.lower(), DEFAULT_WASTE_PROFILE)

        weight = waste_profile["weight"]
        energy = waste_profile["energy"]
        severity = calculate_severity(weight)

        total_weight += weight
        total_energy += energy
        counts_by_class[class_name] = counts_by_class.get(class_name, 0) + 1
        highest_severity_rank = max(highest_severity_rank, severity_order[severity])

        if waste_profile["biodegradable"]:
            biodegradable_count += 1
        else:
            non_biodegradable_count += 1

        analyzed_detections.append(
            {
                "class": class_name,
                "confidence": detection["confidence"],
                "bounding_box": detection["bounding_box"],
                "biodegradable": waste_profile["biodegradable"],
                "estimated_weight": round(weight, 2),
                "energy_production": round(energy, 2),
                "severity": severity,
            }
        )

    severity_lookup = {1: "low", 2: "medium", 3: "high"}
    highest_severity = severity_lookup.get(highest_severity_rank, "low")

    return {
        "detections": analyzed_detections,
        "summary": {
            "total_objects": len(analyzed_detections),
            "total_weight": round(total_weight, 2),
            "total_energy": round(total_energy, 2),
            "counts_by_class": counts_by_class,
        },
        "waste_report": {
            "biodegradable_count": biodegradable_count,
            "non_biodegradable_count": non_biodegradable_count,
            "highest_severity": highest_severity,
            "recommendation": build_recommendation(
                total_weight=round(total_weight, 2),
                highest_severity=highest_severity,
                biodegradable_count=biodegradable_count,
            ),
        },
    }
