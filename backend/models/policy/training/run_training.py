import os
import sys
import yaml
import json
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import numpy as np
import random

# Add project root to path
sys.path.insert(0, "E:/VisionPilot_AI")
from backend.models.policy.policy_network import PolicyMLP

class PolicyPreSplitDataset(Dataset):
    """
    Subclass of PyTorch Dataset for feeding pre-split lists of samples.
    """
    def __init__(self, samples: list):
        self.samples = samples
        self.feature_order = [
            "brightness", "contrast", "blur", "noise",
            "color_cast", "dynamic_range", "perspective_skew"
        ]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        sample = self.samples[idx]
        features = sample["features"]
        feature_vector = [features.get(key, 0.5) for key in self.feature_order]
        label = sample["label"]
        return (
            torch.tensor(feature_vector, dtype=torch.float32),
            torch.tensor(label, dtype=torch.long),
            sample.get("image_id", sample.get("filename", "unknown"))
        )

def compute_metrics(y_true, y_pred, num_classes=5):
    """
    Computes precision, recall, F1, and confusion matrix manually.
    """
    conf_matrix = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        conf_matrix[t, p] += 1

    precision = {}
    recall = {}
    f1_score = {}
    
    for c in range(num_classes):
        tp = conf_matrix[c, c]
        fp = sum(conf_matrix[:, c]) - tp
        fn = sum(conf_matrix[c, :]) - tp
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        
        precision[c] = prec
        recall[c] = rec
        f1_score[c] = f1

    # Macro averages
    macro_prec = sum(precision.values()) / num_classes
    macro_rec = sum(recall.values()) / num_classes
    macro_f1 = sum(f1_score.values()) / num_classes

    return {
        "confusion_matrix": conf_matrix.tolist(),
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "macro": {
            "precision": macro_prec,
            "recall": macro_rec,
            "f1_score": macro_f1
        }
    }

def main():
    config_path = "E:/VisionPilot_AI/configs/policy_config.yaml"
    dataset_path = "E:/VisionPilot_AI/backend/models/policy/training/policy_dataset.json"

    # 1. Load Configurations
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    hyper = cfg.get("hyperparameters", {})
    lr = hyper.get("learning_rate", 0.005)
    batch_size = hyper.get("batch_size", 16)
    epochs = hyper.get("epochs", 100)
    seed = hyper.get("random_seed", 42)
    weight_decay = hyper.get("weight_decay", 0.0001)

    checkpoint_cfg = cfg.get("checkpoints", {})
    checkpoint_dir = checkpoint_cfg.get("checkpoint_dir", "E:/VisionPilot_AI/backend/models/policy/checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)

    early_stopping_cfg = cfg.get("early_stopping", {})
    patience = early_stopping_cfg.get("patience", 10)
    min_delta = early_stopping_cfg.get("min_delta", 0.001)

    # 2. Fix Random Seeds for Reproducibility
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    # 3. Load Dataset
    with open(dataset_path, "r") as f:
        samples = json.load(f)

    # Train / Val Split (Grouped by base template to prevent data leakage)
    train_samples = [s for s in samples if not s["image_id"].startswith("shipping")]
    val_samples = [s for s in samples if s["image_id"].startswith("shipping")]

    train_dataset = PolicyPreSplitDataset(train_samples)
    val_dataset = PolicyPreSplitDataset(val_samples)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # 4. Instantiate Model
    model = PolicyMLP()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    # Metrics history
    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": []
    }

    best_val_loss = float("inf")
    best_val_acc = 0.0
    patience_counter = 0
    best_epoch = 0

    class_names = {
        0: "skip",
        1: "white_balance",
        2: "hdr",
        3: "straighten",
        4: "wb_hdr"
    }

    print(f"Starting training on {len(train_samples)} samples (Val: {len(val_samples)})...")

    # 5. Training Loop
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        correct_train = 0
        total_train = 0

        for feats, labels, _ in train_loader:
            optimizer.zero_grad()
            outputs = model(feats)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * feats.size(0)
            _, predicted = torch.max(outputs, 1)
            correct_train += (predicted == labels).sum().item()
            total_train += labels.size(0)

        mean_train_loss = train_loss / total_train
        train_acc = correct_train / total_train

        # Validation
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0
        with torch.no_grad():
            for feats, labels, _ in val_loader:
                outputs = model(feats)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * feats.size(0)
                _, predicted = torch.max(outputs, 1)
                correct_val += (predicted == labels).sum().item()
                total_val += labels.size(0)

        mean_val_loss = val_loss / total_val if total_val > 0 else 0.0
        val_acc = correct_val / total_val if total_val > 0 else 0.0

        history["train_loss"].append(mean_train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(mean_val_loss)
        history["val_acc"].append(val_acc)

        # Print progress
        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch {epoch:03d}/{epochs:03d} | Train Loss: {mean_train_loss:.4f} | Train Acc: {train_acc*100:.1f}% | Val Loss: {mean_val_loss:.4f} | Val Acc: {val_acc*100:.1f}%")

        # Save Best Checkpoint based on Validation Loss
        if mean_val_loss < (best_val_loss - min_delta):
            best_val_loss = mean_val_loss
            best_val_acc = val_acc
            best_epoch = epoch
            patience_counter = 0
            
            # Save Best Model Checkpoint
            best_checkpoint_path = os.path.join(checkpoint_dir, "policy_best.pth")
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "validation_accuracy": val_acc,
                "training_loss": mean_train_loss
            }, best_checkpoint_path)
        else:
            patience_counter += 1

        # Check early stopping patience
        if patience_counter >= patience:
            print(f"Early stopping triggered at epoch {epoch}. Best Epoch: {best_epoch}")
            break

    # Save Last Model Checkpoint
    last_checkpoint_path = os.path.join(checkpoint_dir, "policy_last.pth")
    torch.save({
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "validation_accuracy": val_acc,
        "training_loss": mean_train_loss
    }, last_checkpoint_path)

    # 6. Evaluation & Metrics Calculation (on Best Model)
    best_weights = torch.load(best_checkpoint_path)
    model.load_state_dict(best_weights["model_state_dict"])
    model.eval()

    y_true = []
    y_pred = []
    prediction_logs = []

    with torch.no_grad():
        for feats, labels, img_ids in val_loader:
            outputs = model(feats)
            probs = F.softmax(outputs, dim=-1)
            _, predicted = torch.max(outputs, 1)
            
            y_true.extend(labels.tolist())
            y_pred.extend(predicted.tolist())
            
            for f, pred, true, prob, img_id in zip(feats, predicted, labels, probs, img_ids):
                prediction_logs.append({
                    "image_id": img_id,
                    "features": f.tolist(),
                    "predicted_strategy": class_names[pred.item()],
                    "ground_truth_strategy": class_names[true.item()],
                    "confidence_score": float(prob[pred].item())
                })

    metrics = compute_metrics(y_true, y_pred)
    
    # Save Prediction Logs
    logs_output_path = "E:/VisionPilot_AI/backend/models/policy/training/prediction_logs.json"
    with open(logs_output_path, "w") as f:
        json.dump(prediction_logs, f, indent=2)

    # 7. ONNX Export
    onnx_path = os.path.join(checkpoint_dir, "policy_best.onnx")
    dummy_input = torch.randn(1, 7)
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"]
    )
    
    # Verify ONNX model loads
    onnx_verified = "failed"
    try:
        import onnx
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        onnx_verified = "success"
    except Exception as e:
        onnx_verified = f"error: {e}"

    # Compile Final Run Results
    results = {
        "train_acc": float(history["train_acc"][-1]),
        "val_acc": float(best_val_acc),
        "best_epoch": best_epoch,
        "early_stopped_epoch": epoch,
        "metrics": metrics,
        "onnx_status": onnx_verified,
        "history": history
    }

    # Save training run stats report JSON
    stats_path = "E:/VisionPilot_AI/backend/models/policy/training/training_stats.json"
    with open(stats_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\nTraining completed successfully!")
    print(f"Train Accuracy: {results['train_acc']*100:.2f}%")
    print(f"Val Accuracy: {results['val_acc']*100:.2f}%")
    print(f"Macro F1 Score: {metrics['macro']['f1_score']:.4f}")
    print(f"ONNX Status: {onnx_verified}")

if __name__ == "__main__":
    main()
