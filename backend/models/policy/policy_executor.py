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
        processed_image = image.copy()
        
        # Query global registry
        from backend.models.plugins.registry import registry as global_registry
        
        # Execution loop
        if "STRAIGHTEN" in decision or decision == "IMAGE_STRAIGHTENING":
            plugin = self.registry.get("ImageStraightening") or global_registry.get_plugin("Image Straightener")
            if plugin:
                processed_image, _ = plugin.process(processed_image, context_config or {})
                
        if "HDR" in decision or decision == "HDR_FUSION":
            plugin = self.registry.get("HDRFusion") or global_registry.get_plugin("HDR Fusion")
            if plugin:
                processed_image, _ = plugin.process(processed_image, context_config or {})
                
        return processed_image

