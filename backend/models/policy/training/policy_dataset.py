import json
import os
import torch
from torch.utils.data import Dataset
from typing import Tuple, List

class PolicyPyTorchDataset(Dataset):
    """
    Custom PyTorch Dataset class that parses the JSON training dataset
    and returns features and labels as tensors.
    """
    def __init__(self, json_dataset_path: str):
        self.json_path = json_dataset_path
        self.samples: List[dict] = []
        
        if os.path.exists(json_dataset_path):
            with open(json_dataset_path, "r") as f:
                self.samples = json.load(f)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        sample = self.samples[idx]
        features = sample["features"]
        
        # Order must be aligned with configs/policy_config.yaml
        feature_order = [
            "brightness", "contrast", "blur", "noise",
            "color_cast", "dynamic_range", "perspective_skew"
        ]
        
        feature_vector = [features.get(key, 0.5) for key in feature_order]
        label = sample["label"]
        
        return (
            torch.tensor(feature_vector, dtype=torch.float32),
            torch.tensor(label, dtype=torch.long)
        )
