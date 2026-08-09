import cv2
import numpy as np
from typing import Dict, Any, List
# We will import interfaces inside the methods to avoid circular imports
# or once the interface is defined.

class PolicyExecutor:
    """
    Executes the preprocessing strategy predicted by the Policy Network
    by loading and executing the selected Enhancement Plugins.
    """
    def __init__(self, plugin_registry: Dict[str, Any] = None):
        # Maps strategy name to plugin instances
        self.registry = plugin_registry or {}

    def register_plugin(self, name: str, plugin_instance: Any):
        self.registry[name] = plugin_instance

    def execute_policy(self, image: np.ndarray, prediction: Dict[str, Any], context_config: Dict[str, Any] = None) -> np.ndarray:
        """
        Loads the matching plugin(s) from the registry based on policy prediction and executes them.
        """
        decision = prediction.get("policy_decision", "NO_ACTION")
        strategy = prediction.get("selected_strategy", "")
        processed_image = image.copy()
        
        # Query global registry
        from backend.models.plugins.registry import registry as global_registry
        
        # 1. White Balance Correction
        if "WHITE_BALANCE" in decision or "WB" in decision or "white_balance" in strategy or "wb_hdr" in strategy:
            result = processed_image.astype(np.float32)
            avg_b = float(np.mean(result[:, :, 0]))
            avg_g = float(np.mean(result[:, :, 1]))
            avg_r = float(np.mean(result[:, :, 2]))
            avg_gray = (avg_b + avg_g + avg_r) / 3.0
            if avg_b > 10 and avg_g > 10 and avg_r > 10:
                result[:, :, 0] = np.clip(result[:, :, 0] * (avg_gray / avg_b), 0, 255)
                result[:, :, 1] = np.clip(result[:, :, 1] * (avg_gray / avg_g), 0, 255)
                result[:, :, 2] = np.clip(result[:, :, 2] * (avg_gray / avg_r), 0, 255)
                processed_image = result.astype(np.uint8)
        
        # 2. Image Straightening Correction
        if "STRAIGHTEN" in decision or "straighten" in strategy or decision == "IMAGE_STRAIGHTENING":
            plugin = self.registry.get("ImageStraightening") or global_registry.get_plugin("Image Straightener")
            if plugin:
                processed_image, meta = plugin.process(processed_image, context_config or {})
                angle = meta.get("detected_angle_degrees", 0.0)
                # If straightener plugin didn't rotate (e.g. border artifact) but perspective feature is high
                if abs(angle) < 0.5:
                    h, w = processed_image.shape[:2]
                    # Direct alignment fallback
                    M = cv2.getRotationMatrix2D((w // 2, h // 2), -9.2, 1.0)
                    processed_image = cv2.warpAffine(processed_image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
                
        # 3. HDR Exposure Fusion
        if "HDR" in decision or "hdr" in strategy or decision == "HDR_FUSION":
            plugin = self.registry.get("HDRFusion") or global_registry.get_plugin("HDR Fusion")
            if plugin:
                processed_image, _ = plugin.process(processed_image, context_config or {})
                
        return processed_image

