import time
import numpy as np
from typing import Dict, Any, Tuple

# Import feature extractors
from backend.models.feature_extraction.brightness import extract_brightness
from backend.models.feature_extraction.contrast import extract_contrast
from backend.models.feature_extraction.blur import extract_blur
from backend.models.feature_extraction.noise import extract_noise
from backend.models.feature_extraction.color_cast import extract_color_cast
from backend.models.feature_extraction.dynamic_range import extract_dynamic_range
from backend.models.feature_extraction.perspective import extract_perspective_skew

# Import policy models
from backend.models.policy.policy_network import InferenceAwarePolicyNetwork
from backend.models.policy.policy_executor import PolicyExecutor

class PolicyInferencePipeline:
    """
    End-to-end Inference Pipeline coordinating feature extraction,
    policy network decision-making, and plugin execution.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.policy_network = InferenceAwarePolicyNetwork(self.config.get("model_config"))
        self.policy_executor = PolicyExecutor()

    def run_pipeline(self, image: np.ndarray, context_config: Dict[str, Any] = None, evaluation_mode: bool = False) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Runs the complete optimization pipeline:
        Image -> Feature Extraction -> Policy Decision -> Policy Execution -> Enhanced Image
        """
        start_time = time.time()
        
        # Step 1: Feature Extraction
        features = {
            "brightness": extract_brightness(image),
            "contrast": extract_contrast(image),
            "blur": extract_blur(image),
            "noise": extract_noise(image),
            "color_cast": extract_color_cast(image),
            "dynamic_range": extract_dynamic_range(image),
            "perspective_skew": extract_perspective_skew(image)
        }
        
        # Step 2: Policy network prediction
        policy_res = self.policy_network.predict_strategy(features, evaluation_mode=evaluation_mode)
        
        if policy_res.get("status") == "error":
            elapsed = time.time() - start_time
            return image, {
                "pipeline_status": "error",
                "message": policy_res["message"],
                "total_latency_sec": elapsed,
                "extracted_features": features
            }
        
        # Step 3: Policy Execution
        enhanced_image = self.policy_executor.execute_policy(
            image=image, 
            prediction=policy_res, 
            context_config=context_config
        )
        
        elapsed = time.time() - start_time
        
        pipeline_meta = {
            "pipeline_status": "success",
            "total_latency_sec": elapsed,
            "extracted_features": features,
            "policy_decision": policy_res["policy_decision"],
            "selected_strategy": policy_res["selected_strategy"],
            "confidence_score": policy_res["confidence_score"],
            "reasons": policy_res["reasons"]
        }
        
        return enhanced_image, pipeline_meta

