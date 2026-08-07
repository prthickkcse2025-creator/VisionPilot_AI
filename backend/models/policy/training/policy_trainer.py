import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from backend.models.policy.policy_network import PolicyMLP
from backend.models.policy.training.policy_dataset import PolicyPyTorchDataset

class PolicyNetworkTrainer:
    """
    Trainer framework for compiling and optimizing the Inference-Aware Policy Network.
    """
    def __init__(self, dataset_path: str, checkpoint_dir: str = "E:/VisionPilot_AI/backend/models/policy/checkpoints"):
        self.dataset_path = dataset_path
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        self.model = PolicyMLP()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.005, weight_decay=1e-4)

    def train_model(self, epochs: int = 10, batch_size: int = 4, val_split: float = 0.2) -> dict:
        """
        Runs the training framework loop.
        Integrates dataset loading, splits, and early stopping.
        """
        dataset = PolicyPyTorchDataset(self.dataset_path)
        if len(dataset) < 2:
            return {"status": "failed", "reason": "Insufficient dataset size for training."}

        # Train/Val Split
        val_len = int(len(dataset) * val_split)
        train_len = len(dataset) - val_len
        train_set, val_set = random_split(dataset, [train_len, val_len])

        train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)

        best_val_loss = float('inf')
        patience = 5
        patience_counter = 0
        
        history = {"train_loss": [], "val_loss": []}

        for epoch in range(epochs):
            # Training loop
            self.model.train()
            total_train_loss = 0.0
            for features, labels in train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(features)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                total_train_loss += loss.item() * features.size(0)

            mean_train_loss = total_train_loss / len(train_set)
            history["train_loss"].append(mean_train_loss)

            # Validation loop
            self.model.eval()
            total_val_loss = 0.0
            with torch.no_grad():
                for features, labels in val_loader:
                    outputs = self.model(features)
                    loss = self.criterion(outputs, labels)
                    total_val_loss += loss.item() * features.size(0)

            mean_val_loss = total_val_loss / len(val_set) if len(val_set) > 0 else 0.0
            history["val_loss"].append(mean_val_loss)

            # Early Stopping and Checkpoint Check
            if mean_val_loss < best_val_loss:
                best_val_loss = mean_val_loss
                patience_counter = 0
                # Save best checkpoint
                torch.save(self.model.state_dict(), os.path.join(self.checkpoint_dir, "policy_best.pth"))
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping triggered at epoch {epoch}")
                    break

        return {
            "status": "success",
            "epochs_run": len(history["train_loss"]),
            "best_val_loss": best_val_loss,
            "history": history
        }
