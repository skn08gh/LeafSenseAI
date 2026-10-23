import torch
import torch.nn as nn
import torch.optim as optim

from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# -----------------------------
# 1. DEVICE
# -----------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Using:", device)


# -----------------------------
# 2. IMAGE TRANSFORM
# -----------------------------

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])


# -----------------------------
# 3. DATASET
# -----------------------------

dataset = datasets.ImageFolder(
    "dataset/train",
    transform=transform
)

print("Number of images:", len(dataset))
print("Number of plant species:", len(dataset.classes))

print("\nPlant classes:")

for plant in dataset.classes:
    print("-", plant)


# -----------------------------
# 4. DATA LOADER
# -----------------------------

train_loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,
    num_workers=0
)


# -----------------------------
# 5. LOAD RESNET18
# -----------------------------

print("\nLoading ResNet18...")

model = models.resnet18(
    weights=models.ResNet18_Weights.DEFAULT
)


# -----------------------------
# 6. FREEZE THE MODEL
# -----------------------------

for parameter in model.parameters():
    parameter.requires_grad = False


# -----------------------------
# 7. REPLACE FINAL LAYER
# -----------------------------

model.fc = nn.Linear(
    model.fc.in_features,
    len(dataset.classes)
)

model = model.to(device)


# -----------------------------
# 8. LOSS + OPTIMIZER
# -----------------------------

criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.fc.parameters(),
    lr=0.001
)


# -----------------------------
# 9. TRAIN
# -----------------------------

epochs = 2

print("\nStarting training...")
print("Total batches per epoch:", len(train_loader))
print()


for epoch in range(epochs):

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


        # Progress every 10 batches
        if (batch_number + 1) % 10 == 0:

            print(
                f"Epoch {epoch + 1}/{epochs} | "
                f"Batch {batch_number + 1}/{len(train_loader)} | "
                f"Loss: {loss.item():.4f}"
            )


    average_loss = running_loss / len(train_loader)

    print()
    print(
        f"Epoch {epoch + 1} complete | "
        f"Average Loss: {average_loss:.4f}"
    )
    print()


# -----------------------------
# 10. SAVE MODEL
# -----------------------------

torch.save(
    {
        "model_state_dict": model.state_dict(),
        "classes": dataset.classes
    },
    "plant_species_model.pth"
)

print("--------------------------------")
print("Training Complete!")
print("--------------------------------")
print("Model saved as:")
print("plant_species_model.pth")