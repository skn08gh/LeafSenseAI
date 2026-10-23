# recommendations.py


# -----------------------------------------
# Plant care profiles
# -----------------------------------------

CARE_PROFILES = {

    "Aloe Vera": {
        "watering": "Water only when the soil has dried out well. Avoid overwatering.",
        "light": "Provide bright light. A few hours of direct sunlight can be suitable.",
        "care": "Make sure the pot has good drainage and remove damaged leaves."
    },

    "Peace Lily": {
        "watering": "Keep the soil lightly moist, but do not leave it waterlogged.",
        "light": "Provide bright, indirect light. Avoid strong direct sunlight.",
        "care": "Check the leaves regularly and remove severely damaged leaves."
    },

    "Snake Plant (Sansevieria)": {
        "watering": "Allow the soil to dry completely between waterings.",
        "light": "Bright, indirect light is ideal, although it can tolerate lower light.",
        "care": "Avoid excess water and make sure the pot drains well."
    },

    "ZZ Plant (Zamioculcas zamiifolia)": {
        "watering": "Allow the soil to dry out between waterings.",
        "light": "Provide bright, indirect light. It can also tolerate lower light.",
        "care": "Avoid frequent watering because the plant stores water in its roots."
    },

    "Monstera Deliciosa (Monstera deliciosa)": {
        "watering": "Water when the upper layer of soil becomes dry.",
        "light": "Provide bright, indirect light.",
        "care": "Keep leaves clean and provide support as the plant grows."
    },

    "Rubber Plant (Ficus elastica)": {
        "watering": "Water when the upper layer of soil has dried.",
        "light": "Provide bright, indirect light.",
        "care": "Keep the leaves clean and avoid sudden environmental changes."
    },

    "Spider Plant": {
        "watering": "Water when the upper layer of soil becomes dry.",
        "light": "Provide bright, indirect light.",
        "care": "Avoid constantly wet soil and check the leaves for discoloration."
    },

    "Areca Palm": {
        "watering": "Keep the soil moderately moist but avoid waterlogging.",
        "light": "Provide bright, indirect light.",
        "care": "Maintain moderate humidity and remove dry or damaged leaves."
    },

    "Boston Fern (Nephrolepis exaltata)": {
        "watering": "Keep the soil consistently moist but not waterlogged.",
        "light": "Provide bright, indirect light.",
        "care": "Maintain good humidity and avoid letting the soil dry completely."
    },

    "Chinese Evergreen (Aglaonema)": {
        "watering": "Water when the upper layer of soil becomes dry.",
        "light": "Provide medium to bright indirect light.",
        "care": "Avoid overwatering and protect the plant from harsh direct sunlight."
    },

    "Chinese Money Plant (Pilea peperomioides)": {
        "watering": "Allow the upper layer of soil to dry before watering again.",
        "light": "Provide bright, indirect light.",
        "care": "Rotate the pot occasionally for balanced growth."
    },

    "Jade Plant (Crassula ovata)": {
        "watering": "Allow the soil to dry thoroughly between waterings.",
        "light": "Provide bright light.",
        "care": "Use well-draining soil and avoid excess moisture."
    },

    "Kalanchoe": {
        "watering": "Allow the soil to dry between waterings.",
        "light": "Provide bright light.",
        "care": "Avoid water sitting around the roots."
    },

    "Orchid": {
        "watering": "Water when the growing medium begins to dry, avoiding constantly wet roots.",
        "light": "Provide bright, indirect light.",
        "care": "Ensure good air circulation and avoid leaving water trapped in the leaves."
    },

    "Parlor Palm (Chamaedorea elegans)": {
        "watering": "Keep the soil lightly moist and allow the surface to dry slightly.",
        "light": "Provide bright, indirect light.",
        "care": "Maintain moderate humidity and remove dry leaves."
    },

    "Rattlesnake Plant (Calathea lancifolia)": {
        "watering": "Keep the soil evenly moist but avoid waterlogging.",
        "light": "Provide medium to bright indirect light.",
        "care": "Maintain humidity and avoid harsh direct sunlight."
    },

    "Birds Nest Fern (Asplenium nidus)": {
        "watering": "Keep the soil consistently moist but not saturated.",
        "light": "Provide bright, indirect light.",
        "care": "Maintain humidity and avoid harsh direct sunlight."
    },

    "Cast Iron Plant (Aspidistra elatior)": {
        "watering": "Allow the upper soil layer to dry slightly between waterings.",
        "light": "Provide indirect or low to medium light.",
        "care": "Avoid overwatering and remove damaged leaves."
    },

    "Asparagus Fern (Asparagus setaceus)": {
        "watering": "Keep the soil lightly moist and avoid letting it become completely dry.",
        "light": "Provide bright, indirect light.",
        "care": "Maintain moderate humidity and trim damaged foliage."
    },

    "Anthurium (Anthurium andraeanum)": {
        "watering": "Water when the upper soil layer becomes slightly dry.",
        "light": "Provide bright, indirect light.",
        "care": "Maintain humidity and avoid keeping the roots waterlogged."
    },

    "Tulip": {
        "watering": "Keep the soil lightly moist but avoid excessive watering.",
        "light": "Provide bright light.",
        "care": "Ensure good drainage and remove damaged foliage."
    },

    "Venus Flytrap": {
        "watering": "Keep the growing medium consistently moist using appropriate low-mineral water.",
        "light": "Provide strong light.",
        "care": "Avoid ordinary mineral-rich tap water and avoid disturbing the traps unnecessarily."
    },

    "Sago Palm (Cycas revoluta)": {
        "watering": "Allow the soil to dry between waterings.",
        "light": "Provide bright light.",
        "care": "Use well-draining soil and avoid excessive moisture."
    }
}


# -----------------------------------------
# Recommendation function
# -----------------------------------------

def get_recommendations(plant_name, severity):

    # Try exact plant match
    profile = CARE_PROFILES.get(plant_name)

    # Generic fallback
    if profile is None:
        profile = {
            "watering": "Check the soil moisture before watering and avoid overwatering.",
            "light": "Provide suitable indirect light and avoid sudden changes in lighting.",
            "care": "Inspect the leaves regularly and remove severely damaged foliage."
        }

    severity = severity.lower()

    # -----------------------------------------
    # Severity-specific advice
    # -----------------------------------------

    if severity == "healthy":

        urgency = (
            "The plant appears healthy. Continue its normal care routine "
            "and monitor it regularly."
        )

    elif severity == "mild":

        urgency = (
            "Mild stress was detected. Check the plant's watering, lighting, "
            "and leaf condition over the next few days."
        )

    elif severity == "moderate":

        urgency = (
            "Moderate stress was detected. Inspect the plant carefully and "
            "correct possible watering or lighting problems."
        )

    elif severity == "severe":

        urgency = (
            "Significant visible stress was detected. Inspect the plant "
            "carefully and address watering, lighting, drainage, and damaged "
            "leaves as appropriate."
        )

    else:

        urgency = (
            "Monitor the plant closely and check its watering, lighting, "
            "and leaf condition."
        )

    return {
        "watering": profile["watering"],
        "light": profile["light"],
        "care": profile["care"],
        "urgency": urgency
    }