import json
import os
from datetime import datetime

HISTORY_FILE = "data/history.json"


def save_analysis(
    plant_name,
    confidence,
    health,
    severity,
    explanation,
    watering,
    light
):
    analysis = {
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "plant": plant_name,
        "confidence": confidence,
        "health": health,
        "severity": severity,
        "explanation": explanation,
        "watering": watering,
        "light": light
    }

    # Create data folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Load existing history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
        except:
            history = []
    else:
        history = []

    # Add new analysis
    history.append(analysis)

    # Save history
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)

    return analysis


def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []