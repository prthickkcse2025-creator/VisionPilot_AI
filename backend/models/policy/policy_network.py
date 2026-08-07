import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, List

class PolicyMLP(nn.Module):
    """
    Lightweight MLP Architecture for Preprocessing Strategy Prediction.
    Input Features (7) -> Dense (32) -> ReLU -> Dense (16) -> ReLU -> Dense (5)
    """
    def __init__(self, input_dim: int = 7, hidden_dim1: int = 32, hidden_dim2: int = 16, num_classes: int = 5):
        super(PolicyMLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim1)
        self.fc2 = nn.Linear(hidden_dim1, hidden_dim2)
        self.fc3 = nn.Linear(hidden_dim2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class InferenceAwarePolicyNetwork:
    """
    Policy Network responsible for evaluating extracted image features
    and predicting the optimal preprocessing strategy.
    
    CRITICAL: This network only PREDICTS; it never directly executes enhancement plugins.
    """
    def __init__(self, model_config: Dict[str, Any] = None):
        self.config = model_config or {}
        self.model = PolicyMLP()
        self.model.eval()
        
        # Load weights if available
        self.weights_path = self.config.get(
            "best_model_path", 
            "E:/VisionPilot_AI/backend/models/policy/checkpoints/policy_best.pth"
        )
        self.is_trained = False
        if os.path.exists(self.weights_path):
            try:
                self.model.load_state_dict(torch.load(self.weights_path, map_location="cpu"))
                self.is_trained = True
            except Exception:
                # Fallback if checkpoint load fails
                pass

    def predict_strategy(self, features: Dict[str, float], evaluation_mode: bool = False) -> Dict[str, Any]:
        """
        Predicts optimal strategy based on extracted metrics.
        Returns:
            Dict[str, Any]: Policy decision prediction details
        """
        if evaluation_mode and not self.is_trained:
            return {
                "status": "error",
                "message": "Policy model not trained. Evaluation unavailable."
            }

        # Feature order matches configs/policy_config.yaml
        feature_keys = [
            "brightness", "contrast", "blur", "noise", 
            "color_cast", "dynamic_range", "perspective_skew"
        ]
        
        feature_vector = [features.get(key, 0.5) for key in feature_keys]
        
        if self.is_trained:
            # Real Inference Mode using PyTorch MLP
            with torch.no_grad():
                tensor_input = torch.tensor([feature_vector], dtype=torch.float32)
                logits = self.model(tensor_input)
                probs = F.softmax(logits, dim=-1).squeeze(0).numpy()
                
            predicted_class = int(np.argmax(probs))
            confidence = float(probs[predicted_class])
        else:
            # Heuristic Rule-Based Mock Inference Mode (Trained weights don't exist yet)
            brightness = features.get("brightness", 0.5)
            contrast = features.get("contrast", 0.5)
            blur = features.get("blur", 0.0)
            color_cast = features.get("color_cast", 0.0)
            dynamic_range = features.get("dynamic_range", 0.5)
            skew = features.get("perspective_skew", 0.0)
            
            # Predict default Skip (Class 0)
            predicted_class = 0
            confidence = 0.95
            
            if dynamic_range > 0.7 or brightness < 0.3:
                if color_cast > 0.4:
                    predicted_class = 4  # WB + HDR
                    confidence = 0.88
                else:
                    predicted_class = 2  # HDR
                    confidence = 0.92
            elif skew > 0.08:
                predicted_class = 3  # Straighten
                confidence = 0.91
            elif color_cast > 0.5:
                predicted_class = 1  # WB
                confidence = 0.89

        # Class maps to strategies
        class_to_strategy = {
            0: "NO_ACTION",
            1: "WHITE_BALANCE",
            2: "HDR_FUSION",
            3: "IMAGE_STRAIGHTENING",
            4: "WHITE_BALANCE_AND_HDR"
        }
        
        strategy_reasons = {
            0: ["All features are within nominal operational bounds."],
            1: ["High color cast detected, requiring temperature balancing."],
            2: ["High dynamic range or under-exposure detected; exposure fusion required."],
            3: ["Significant rotational skew detected, requiring alignment."],
            4: ["Multiple visual degradations (exposure + color cast) detected."]
        }
        
        decision = class_to_strategy.get(predicted_class, "NO_ACTION")
        reasons = strategy_reasons.get(predicted_class, ["Fallback default decision."])
        
        return {
            "policy_decision": decision,
            "selected_strategy": f"{decision}_Ensemble_v1",
            "confidence_score": confidence,
            "reasons": reasons
        }
