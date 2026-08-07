import os
import json
import cv2
import time
import yaml
import numpy as np
from typing import List, Dict, Any

# Feature extractors
from backend.models.feature_extraction.brightness import extract_brightness
from backend.models.feature_extraction.contrast import extract_contrast
from backend.models.feature_extraction.blur import extract_blur
from backend.models.feature_extraction.noise import extract_noise
from backend.models.feature_extraction.color_cast import extract_color_cast
from backend.models.feature_extraction.dynamic_range import extract_dynamic_range
from backend.models.feature_extraction.perspective import extract_perspective_skew

class PolicyDatasetBuilder:
    """
    Downstream Performance-Aware Dataset Builder.
    Runs every preprocessing strategy on the input image, measures simulated
    downstream model performance, and labels the image with the strategy
    that yields the highest downstream accuracy based on configured weights.
    """
    def __init__(self, output_path: str = "E:/VisionPilot_AI/backend/models/policy/training/policy_dataset.json"):
        self.output_path = output_path
        self.dataset: List[Dict[str, Any]] = []

        # Load weights from configs/policy_config.yaml
        config_path = "E:/VisionPilot_AI/configs/policy_config.yaml"
        self.w_ocr = 0.45
        self.w_det = 0.40
        self.w_pack = 0.15
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = yaml.safe_load(f)
                    weights = cfg.get("evaluation_weights", {})
                    self.w_ocr = weights.get("ocr", 0.45)
                    self.w_det = weights.get("detection", 0.40)
                    self.w_pack = weights.get("packaging", 0.15)
            except Exception:
                pass

    def evaluate_strategy_downstream(self, strategy: str, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Simulates downstream AI performance on the image for a given strategy.
        """
        brightness = features["brightness"]
        contrast = features["contrast"]
        blur = features["blur"]
        noise = features["noise"]
        color_cast = features["color_cast"]
        dynamic_range = features["dynamic_range"]
        skew = features["perspective_skew"]
        
        # Determine dominant defects
        has_color_cast = color_cast > 0.40
        has_skew = skew > 0.08
        has_lighting_defect = brightness < 0.30

        # Base clean state
        is_clean = not (has_color_cast or has_skew or has_lighting_defect)

        ocr = 0.50
        det = 0.50
        pack = 0.50
        latency = 5.0

        if strategy == "skip":
            if is_clean:
                ocr, det, pack = 0.96, 0.95, 0.95
            else:
                ocr = 0.70 - 0.2 * color_cast - 0.3 * skew
                det = 0.68 - 0.2 * blur
                pack = 0.65 - 0.4 * skew
            latency = 1.2
        elif strategy == "white_balance":
            if has_color_cast and not (has_skew or has_lighting_defect):
                ocr, det, pack = 0.94, 0.92, 0.90
            else:
                ocr = 0.82 if has_color_cast else 0.70
                det = 0.75
                pack = 0.78
            latency = 14.0
        elif strategy == "hdr":
            if has_lighting_defect and not (has_color_cast or has_skew):
                ocr, det, pack = 0.93, 0.94, 0.91
            else:
                ocr = 0.88 if has_lighting_defect else 0.68
                det = 0.85
                pack = 0.82
            latency = 59.0
        elif strategy == "straighten":
            if has_skew and not (has_color_cast or has_lighting_defect):
                ocr, det, pack = 0.95, 0.93, 0.96
            else:
                ocr = 0.90 if has_skew else 0.65
                det = 0.88
                pack = 0.91 if has_skew else 0.60
            latency = 18.0
        elif strategy == "wb_hdr":
            if has_color_cast and has_lighting_defect and not has_skew:
                ocr, det, pack = 0.96, 0.95, 0.93
            else:
                ocr = 0.91 if (has_color_cast and has_lighting_defect) else 0.72
                det = 0.90
                pack = 0.88
            latency = 63.0

        ocr_score = float(np.clip(ocr, 0.0, 1.0))
        det_score = float(np.clip(det, 0.0, 1.0))
        pack_score = float(np.clip(pack, 0.0, 1.0))

        # Calculate final weighted score
        weighted_score = (
            self.w_ocr * ocr_score +
            self.w_det * det_score +
            self.w_pack * pack_score
        )

        return {
            "ocr_score": ocr_score,
            "detection_confidence": det_score,
            "packaging_score": pack_score,
            "latency_ms": latency,
            "weighted_score": float(weighted_score)
        }

    def build_dataset_from_folder(self, folder_path: str) -> List[Dict[str, Any]]:
        """Processes folder images, evaluates all 5 strategies, and records specs."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        self.dataset = []
        valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]
        
        strategy_keys = ["skip", "white_balance", "hdr", "straighten", "wb_hdr"]
        key_to_label = {
            "skip": 0,
            "white_balance": 1,
            "hdr": 2,
            "straighten": 3,
            "wb_hdr": 4
        }
        
        for file in files:
            full_path = os.path.join(folder_path, file)
            try:
                img = cv2.imread(full_path)
                if img is None:
                    continue
                
                # Extract features
                features = {
                    "brightness": extract_brightness(img),
                    "contrast": extract_contrast(img),
                    "blur": extract_blur(img),
                    "noise": extract_noise(img),
                    "color_cast": extract_color_cast(img),
                    "dynamic_range": extract_dynamic_range(img),
                    "perspective_skew": extract_perspective_skew(img)
                }
                
                # Evaluate all 5 strategies
                best_strategy = "skip"
                best_score = -1.0
                scores = {}
                latency_ms = {}
                
                for strat in strategy_keys:
                    eval_res = self.evaluate_strategy_downstream(strat, features)
                    # We evaluate best strategy based on weighted score
                    scores[strat] = eval_res["weighted_score"]
                    latency_ms[strat] = eval_res["latency_ms"]
                    
                    if eval_res["weighted_score"] > best_score:
                        best_score = eval_res["weighted_score"]
                        best_strategy = strat
                
                self.dataset.append({
                    "image_id": file,
                    "filename": file,  # preserve for backward compatibility
                    "filepath": full_path,
                    "features": features,
                    "scores": scores,
                    "latency_ms": latency_ms,
                    "best_strategy": best_strategy,
                    "label": key_to_label[best_strategy]
                })
            except Exception as e:
                print(f"Skipping {file} due to extraction error: {e}")
                
        # Save dataset
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(self.dataset, f, indent=2)
            
        return self.dataset
