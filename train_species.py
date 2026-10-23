import torch
import torch.nn as nn
import torch.optim as optim

from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader


# =========================================================
# 1. DEVICE
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using:", device)


# =========================================================
# 2. IMAGE TRANSFORMATIONS
# =========================================================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),
    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# =========================================================
# 3. LOAD DATASET
# =========================================================

dataset = datasets.ImageFolder(
    root="dataset/train",
    transform=transform
)

print("Number of images:", len(dataset))
print("Number of plant species:", len(dataset.classes))

print("\nPlant classes:")

for plant in dataset.classes:
    print("-", plant)


# =========================================================
# 4. CREATE DATA LOADER
# =========================================================

train_loader = DataLoader(
    dataset,
    batch_size=16,
    shuffle=True,
    num_workers=0
)


# =========================================================
# 5. LOAD PRETRAINED RESNET18
# =========================================================

print("\nLoading pretrained ResNet18...")

model = models.resnet18(
    weights=models.ResNet18_Weights.DEFAULT
)


# =========================================================
# 6. FREEZE MOST OF THE MODEL
# =========================================================

for parameter in model.parameters():
    parameter.requires_grad = False


# Allow the final ResNet block to learn plant-specific features

for parameter in model.layer4.parameters():
    parameter.requires_grad = True


# =========================================================
# 7. REPLACE FINAL CLASSIFICATION LAYER
# =========================================================

model.fc = nn.Linear(
    model.fc.in_features,
    len(dataset.classes)
)

model = model.to(device)


# =========================================================
# 8. LOSS FUNCTION
# =========================================================

criterion = nn.CrossEntropyLoss()


# =========================================================
# 9. OPTIMIZER
# =========================================================

optimizer = optim.Adam(
    filter(
        lambda parameter: parameter.requires_grad,
        model.parameters()
    ),
    lr=0.0001
)


# =========================================================
# 10. TRAINING
# =========================================================

epochs = 8

print("\nStarting training...")
print("=" * 50)


for epoch in range(epochs):

    print(f"\nStarting Epoch {epoch + 1}/{epochs}")
    print("=" * 50)

    model.train()

    running_loss = 0.0

    for batch_number, (images, labels) in enumerate(train_loader):

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        if (batch_number + 1) % 20 == 0:

            print(
                f"Epoch {epoch + 1}/{epochs} | "
                f"Batch {batch_number + 1}/{len(train_loader)} | "
                f"Loss: {loss.item():.4f}"
            )

    average_loss = running_loss / len(train_loader)

    print()
    print("=" * 50)
    print(f"Epoch {epoch + 1}/{epochs} COMPLETE")
    print(f"Average Loss: {average_loss:.4f}")
    print("=" * 50)

    # Save after EVERY epoch
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "classes": dataset.classes,
        "epoch": epoch + 1
    }

    torch.save(
        checkpoint,
        "plant_species_model.pth"
    )

    print("Model saved successfully!")


# =========================================================
# 11. SAVE MODEL
# =========================================================

checkpoint = {
    "model_state_dict": model.state_dict(),
    "classes": dataset.classes
}

torch.save(
    checkpoint,
    "plant_species_model.pth"
)


# =========================================================
# 12. FINISHED
# =========================================================

print("\n" + "=" * 50)
print("🌿 LeafSense AI Training Complete!")
print("=" * 50)

print("Model saved as:")
print("plant_species_model.pth")