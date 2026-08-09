import time
import os
import sys
import importlib.util
import numpy as np
from typing import Dict, Any, Tuple
from backend.models.interfaces.enhancement_plugin import EnhancementPlugin

# Dynamically load the approved read-only production model to avoid import issues with hyphens and dots in filenames
engine_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "..", 
    "models", "production", "MAWB-Net_HDR_Fusion_V13.2_VisionPilot.py"
))

if not os.path.exists(engine_path):
    raise FileNotFoundError(f"Production HDR Fusion Engine not found at {engine_path}")

spec = importlib.util.spec_from_file_location("hdr_fusion_engine", engine_path)
hdr_fusion_engine = importlib.util.module_from_spec(spec)
sys.modules["hdr_fusion_engine"] = hdr_fusion_engine
spec.loader.exec_module(hdr_fusion_engine)

class HDRFusionPlugin(EnhancementPlugin):
    def get_plugin_name(self) -> str:
        return "HDR Fusion"

    def get_plugin_version(self) -> str:
        return "MAWB-Net HDR Fusion V13.2"

    def get_plugin_description(self) -> str:
        return "Multi-exposure fusion using approved production MAWB-Net V13.2 algorithms."

    def get_supported_formats(self) -> list:
        return ["jpg", "jpeg", "png", "tiff", "bmp"]

    def supports_batch_processing(self) -> bool:
        return True

    def process(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Processes image using approved HDR fusion.
        If a single image is provided, we simulate under- and over-exposure brackets.
        """
        start_time = time.time()
        
        # Validation
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Input image must be a valid numpy array.")
        if len(image.shape) != 3:
            raise ValueError("Input image must be a 3-channel BGR image.")

        # Simulate brackets if we don't have them
        brackets = config.get("brackets", [])
        if not brackets:
            # Create dynamic exposure brackets to recover shadows and balance contrast
            gamma_boost = np.clip(np.power(image.astype(np.float32) / 255.0, 0.40) * 255.0, 0, 255).astype(np.uint8)
            bright_boost = np.clip(image.astype(np.float32) * 3.5 + 40, 0, 255).astype(np.uint8)
            images_to_fuse = [image, bright_boost, gamma_boost]
        else:
            images_to_fuse = [image] + list(brackets)

        # Fusion logic selector
        fusion_mode = config.get("fusion_mode", "mertens")
        if fusion_mode == "pytorch":
            fused = hdr_fusion_engine.run_pytorch_weight_fusion(images_to_fuse)
        else:
            fused = hdr_fusion_engine.run_opencv_mertens(images_to_fuse)

        # Run refinement and QC
        refined = hdr_fusion_engine.apply_refinement_pass(fused)
        final_image = hdr_fusion_engine.apply_qc_pass(refined)

        elapsed = time.time() - start_time
        metadata = {
            "version": self.get_plugin_version(),
            "fusion_mode": fusion_mode,
            "simulated_brackets": len(brackets) == 0,
            "processing_time_sec": elapsed,
            "input_dimensions": f"{image.shape[1]}x{image.shape[0]}",
            "output_dimensions": f"{final_image.shape[1]}x{final_image.shape[0]}"
        }

        return final_image, metadata
