# crop_disease_model.py
# CLEANED & FLASK-READY

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import json
import os

# ------------------------
# Device
# ------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ------------------------
# Image Transform
# ------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ------------------------
# Model Architecture (MUST match training)
# ------------------------
class CropDiseaseCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()

        self.block1 = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.block2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.block3 = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.block4 = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 14 * 14, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        return self.classifier(x)

# ------------------------
# Load model + class map
# ------------------------
def load_model(
    model_path="models/best_model.pth",
    class_map_path="models/class_mapping.json"
):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    if not os.path.exists(class_map_path):
        raise FileNotFoundError(f"Class map not found: {class_map_path}")

    with open(class_map_path, "r") as f:
        idx_to_class = json.load(f)

    model = CropDiseaseCNN(num_classes=len(idx_to_class))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    return model, idx_to_class

# ------------------------
# Prediction
# ------------------------
@torch.no_grad()
def predict(image_path, model, idx_to_class, threshold=0.5):
    if not os.path.exists(image_path):
        raise FileNotFoundError("Image does not exist")

    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    logits = model(image)
    probs = F.softmax(logits, dim=1)

    confidence, pred_idx = torch.max(probs, dim=1)
    confidence = confidence.item()

    if confidence < threshold:
        return {
            "prediction": "unknown",
            "confidence": round(confidence, 4)
        }

    return {
        "prediction": idx_to_class[str(pred_idx.item())],
        "confidence": round(confidence, 4)
    }
