import pandas as pd




def load_plant_data():
    """Load the plant database."""
    return pd.read_csv("plants.csv")




def check_range(value, minimum, maximum):
    """Check whether a value is inside a preferred range."""
    return minimum <= value <= maximum




def temperature_score(temperature, minimum, maximum):
    """Give 2 points for ideal temperature, 1 for close, 0 for far."""


    if minimum <= temperature <= maximum:
        return 2


    if minimum - 3 <= temperature <= maximum + 3:
        return 1


    return 0




def humidity_score(humidity, minimum, maximum):
    """Give 2 points for ideal humidity, 1 for close, 0 for far."""


    if minimum <= humidity <= maximum:
        return 2


    if minimum - 10 <= humidity <= maximum + 10:
        return 1


    return 0




def light_score(user_light, plant_light):
    """Give 2 points for ideal light, 1 for acceptable, 0 for unsuitable."""


    if user_light == plant_light:
        return 2


    if (
        (user_light == "low" and plant_light == "medium")
        or
        (user_light == "medium" and plant_light in ["low", "bright"])
        or
        (user_light == "bright" and plant_light == "medium")
    ):
        return 1


    return 0




def check_light(user_light, plant_light):
    """Check whether the user's light level matches the plant."""
    return user_light == plant_light




def check_soil_moisture(user_moisture, plant_moisture):
    """Check whether the user's soil moisture matches the plant."""
    return user_moisture == plant_moisture




def soil_moisture_score(user_moisture, plant_moisture):
    """Give 2 points for ideal moisture, 1 for close, 0 for unsuitable."""


    levels = ["dry", "moderate", "moist"]


    user_index = levels.index(user_moisture)
    plant_index = levels.index(plant_moisture)


    difference = abs(user_index - plant_index)


    if difference == 0:
        return 2
    elif difference == 1:
        return 1
    else:
        return 0




def calculate_score(
    temperature_points,
    light_points,
    humidity_points,
    soil_moisture_points
):
    score = 0


    score += temperature_points
    score += light_points
    score += humidity_points
    score += soil_moisture_points


    return score




def generate_explanation(result):
    """Create a simple explanation of why a plant was recommended."""


    reasons = []


    if result["temperature_points"] == 2:
        reasons.append("temperature is ideal")
    elif result["temperature_points"] == 1:
        reasons.append("temperature is close")
    else:
        reasons.append("temperature is unsuitable")


    if result["light_points"] == 2:
        reasons.append("light is ideal")
    elif result["light_points"] == 1:
        reasons.append("light is close")
    else:
        reasons.append("light is unsuitable")


    if result["humidity_points"] == 2:
        reasons.append("humidity is ideal")
    elif result["humidity_points"] == 1:
        reasons.append("humidity is close")
    else:
        reasons.append("humidity is unsuitable")


    if result["soil_moisture_points"] == 2:
        reasons.append("soil moisture is ideal")
    elif result["soil_moisture_points"] == 1:
        reasons.append("soil moisture is close")
    else:
        reasons.append("soil moisture is unsuitable")


    return "Best suited because " + ", ".join(reasons) + "."




def recommend_plants(temperature, user_light, humidity, soil_moisture):
    plants = load_plant_data()


    results = []


    for index, plant in plants.iterrows():


        temperature_points = temperature_score(
            temperature,
            plant["min_temperature_c"],
            plant["max_temperature_c"]
        )


        temperature_match = temperature_points > 0


        humidity_points = humidity_score(
            humidity,
            plant["min_humidity"],
            plant["max_humidity"]
        )


        humidity_match = humidity_points > 0


        light_points = light_score(
            user_light,
            plant["light_level"]
        )


        light_match = light_points > 0


        soil_moisture_points = soil_moisture_score(
            soil_moisture,
            plant["soil_moisture"]
        )


        soil_moisture_match = soil_moisture_points > 0


        score = calculate_score(
            temperature_points,
            light_points,
            humidity_points,
            soil_moisture_points
        )


        percentage = (score / 8) * 100


        result = {
            "plant": plant["plant_name"],
            "score": score,
            "percentage": percentage,
            "temperature_match": temperature_match,
            "temperature_points": temperature_points,
            "light_match": light_match,
            "light_points": light_points,
            "humidity_match": humidity_match,
            "humidity_points": humidity_points,
            "soil_moisture_match": soil_moisture_match,
            "soil_moisture_points": soil_moisture_points
        }


        result["explanation"] = generate_explanation(result)


        results.append(result)


    results.sort(
    key=lambda x: (
        x["score"],
        x["temperature_points"] == 2,
        x["light_points"] == 2,
        x["humidity_points"] == 2,
        x["soil_moisture_points"] == 2
    ),
    reverse=True
)


    return results

