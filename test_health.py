from PIL import Image
from health_analyzer import analyze_health


image = Image.open(
    "dataset/train/Aloe Vera/1.jpg"
)

result = analyze_health(image)

print("\n🌿 LeafSense AI Health Test")
print("---------------------------")

print("Health:", result["health"])
print("Severity:", result["severity"])
print("Explanation:", result["explanation"])

print("\nVisual Analysis:")
print("Green:", result["green_ratio"], "%")
print("Yellow:", result["yellow_ratio"], "%")
print("Brown:", result["brown_ratio"], "%")