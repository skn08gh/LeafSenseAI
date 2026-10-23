import torch
from torchvision import transforms, models


# =========================================================
# DEVICE
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using:", device)


# =========================================================
# LOAD TRAINED MODEL
# =========================================================

checkpoint = torch.load(
    "plant_species_model.pth",
    map_location=device
)

plant_names = checkpoint["classes"]

print("Number of plant classes:", len(plant_names))


# =========================================================
# CREATE RESNET18
# =========================================================

model = models.resnet18(weights=None)

model.fc = torch.nn.Linear(
    model.fc.in_features,
    len(plant_names)
)


# =========================================================
# LOAD OUR TRAINED WEIGHTS
# =========================================================

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# =========================================================
# PLANT IDENTIFICATION
# =========================================================

def identify_plant(image):

    image = image.convert("RGB")

    image = transform(image)

    image = image.unsqueeze(0)

    image = image.to(device)

    with torch.no_grad():

        outputs = model(image)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

    # Get top 5 predictions
    top_scores, top_indices = torch.topk(
        probabilities,
        5,
        dim=1
    )

    results = []

    for score, index in zip(
        top_scores[0],
        top_indices[0]
    ):

        results.append({
            "label": plant_names[index.item()],
            "score": score.item()
        })

    return results