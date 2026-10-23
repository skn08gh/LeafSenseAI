from PIL import Image
import numpy as np


def analyze_health(image, plant_name=None):
    """
    Lightweight visual plant-health screening.

    Uses visible colour patterns to estimate whether
    the plant appears Healthy, Mild, Moderate, or Severe.

    This is a visual screening system, not a medical/
    botanical disease diagnosis.
    """

    # ------------------------------------------------
    # 1. Prepare image
    # ------------------------------------------------

    image = image.convert("RGB")
    image = image.resize((224, 224))

    img = np.array(image).astype(float)

    red = img[:, :, 0]
    green = img[:, :, 1]
    blue = img[:, :, 2]

    # ------------------------------------------------
    # 2. Detect likely leaf pixels
    # ------------------------------------------------

    # Strong green areas
    green_pixels = (
        (green > red * 1.10) &
        (green > blue * 1.05) &
        (green > 55)
    )

    # Yellow/green areas
    yellow_pixels = (
        (red > 100) &
        (green > 90) &
        (red > blue * 1.15) &
        (green > blue * 1.05)
    )

    # Brown areas
    brown_pixels = (
        (red > 60) &
        (red > blue * 1.20) &
        (green > blue * 1.05) &
        (green < red * 1.05) &
        (green < 145)
    )

    # ------------------------------------------------
    # 3. Calculate colour ratios
    # ------------------------------------------------

    green_ratio = np.mean(green_pixels)
    yellow_ratio = np.mean(yellow_pixels)
    brown_ratio = np.mean(brown_pixels)

    # ------------------------------------------------
    # 4. Plant-specific adjustment
    # ------------------------------------------------

    plant = str(plant_name).lower() if plant_name else ""

    # Some plants naturally contain yellow/cream patterns.
    # Do not treat all yellow pixels as stress for these plants.

    naturally_variegated = [
        "snake plant",
        "sansevieria",
        "pothos",
        "money plant",
        "chinese evergreen"
    ]

    if any(name in plant for name in naturally_variegated):
        yellow_stress = yellow_ratio * 20
    else:
        yellow_stress = yellow_ratio * 35

    # ------------------------------------------------
    # 5. Calculate visual stress score
    # ------------------------------------------------

    stress_score = (
        yellow_stress
        + brown_ratio * 70
        - green_ratio * 18
    )

    # Prevent strange negative values
    stress_score = max(0, stress_score)

    # ------------------------------------------------
    # 6. Determine severity
    # ------------------------------------------------

    if stress_score < 7:

        severity = "Healthy"

        health_status = (
            "Plant appears visually healthy."
        )

        explanation = (
            "The image contains a strong proportion of "
            "green plant areas with relatively little "
            "visible discoloration."
        )

    elif stress_score < 15:

        severity = "Mild"

        health_status = (
            "Possible mild plant stress detected."
        )

        explanation = (
            "A small amount of yellowish or brown "
            "discoloration is visible. Monitor the plant "
            "and check its watering and lighting conditions."
        )

    elif stress_score < 25:

        severity = "Moderate"

        health_status = (
            "Possible moderate plant stress detected."
        )

        explanation = (
            "Noticeable discoloration or darker areas "
            "are visible. The plant's watering, lighting, "
            "and growing conditions should be checked."
        )

    else:

        severity = "Severe"

        health_status = (
            "Significant visible stress detected."
        )

        explanation = (
            "A relatively large amount of visible "
            "discoloration or darkened plant area was "
            "detected. The plant should be inspected carefully."
        )

    # ------------------------------------------------
    # 7. Return results
    # ------------------------------------------------

    return {
        "health": health_status,
        "severity": severity,
        "explanation": explanation,

        "green_ratio": round(green_ratio * 100, 2),
        "yellow_ratio": round(yellow_ratio * 100, 2),
        "brown_ratio": round(brown_ratio * 100, 2),

        "stress_score": round(stress_score, 2)
    }