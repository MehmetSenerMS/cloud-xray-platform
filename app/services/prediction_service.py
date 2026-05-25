import base64
import io
import os
from typing import Dict, Any

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "chestmnist_224_torch_model.pt"
)


LABELS = [
    "Atelectasis",
    "Cardiomegaly",
    "Effusion",
    "Infiltration",
    "Mass",
    "Nodule",
    "Pneumonia",
    "Pneumothorax",
    "Consolidation",
    "Edema",
    "Emphysema",
    "Fibrosis",
    "Pleural_Thickening",
    "Hernia"
]


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model():
    model = models.resnet18(num_classes=14)

    model.fc = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(512, 14)
    )

    return model


def load_model():
    model = build_model()

    state_dict = torch.load(
        MODEL_PATH,
        map_location=device
    )

    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    return model


model = load_model()


preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def run_prediction(image_base64: str) -> Dict[str, Any]:
    try:
        img_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(img_data)).convert("RGB")

        input_tensor = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            logits = model(input_tensor)
            probs = torch.sigmoid(logits).squeeze().tolist()

        sorted_indices = sorted(
            range(len(probs)),
            key=lambda i: probs[i],
            reverse=True
        )

        sorted_predictions = {
            LABELS[i]: round(float(probs[i]), 4)
            for i in sorted_indices
        }

        top_label = LABELS[sorted_indices[0]]
        top_confidence = round(float(probs[sorted_indices[0]]), 4)

        return {
            "status": "success",
            "model_name": "ChestMNIST ResNet18",
            "device": str(device),
            "top_prediction": {
                "label": top_label,
                "confidence": top_confidence
            },
            "predictions": sorted_predictions
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }