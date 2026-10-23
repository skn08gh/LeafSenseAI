from PIL import Image
from models import identify_plant

# =========================================================
# TEST IMAGE
# =========================================================

image = Image.open(
    r"C:\Users\Shahzia Khwaja Nawaz\OneDrive\Desktop\Python AI Project\ill money plant.png"
)

# =========================================================
# RUN AI
# =========================================================

result = identify_plant(image)

# =========================================================
# DISPLAY RESULTS
# =========================================================

print("\n🌿 LeafSense AI")
print("========================")

print("\nTop predictions:")

for prediction in result:
    print(
        prediction["label"],
        "-",
        round(prediction["score"] * 100, 2),
        "%"
    )
    