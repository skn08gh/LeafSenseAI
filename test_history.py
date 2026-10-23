from history import save_analysis, get_history

save_analysis(
    plant_name="Aloe Vera",
    confidence=99.22,
    health="Plant appears visually healthy.",
    severity="Healthy",
    explanation="The leaves appear mostly green with little visible discoloration.",
    watering="Water when the soil is completely dry.",
    light="Provide bright, indirect to direct sunlight."
)

print("\n🌿 LeafSense AI History")
print("======================")

history = get_history()

for item in history:
    print("\nDate:", item["date"])
    print("Plant:", item["plant"])
    print("Confidence:", item["confidence"], "%")
    print("Health:", item["health"])
    print("Severity:", item["severity"])