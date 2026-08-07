import time
import os
import sys
import importlib.util
import numpy as np
from typing import Dict, Any, Tuple
from backend.models.interfaces.enhancement_plugin import EnhancementPlugin

# Dynamically load the approved read-only production model
engine_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "..", 
    "models", "production", "ImageStraightener_VisionPilot.py"
))

if not os.path.exists(engine_path):
    raise FileNotFoundError(f"Production Image Straightener Engine not found at {engine_path}")

spec = importlib.util.spec_from_file_location("straightener_engine", engine_path)
straightener_engine = importlib.util.module_from_spec(spec)
sys.modules["straightener_engine"] = straightener_engine
spec.loader.exec_module(straightener_engine)

class ImageStraightenerPlugin(EnhancementPlugin):
    def get_plugin_name(self) -> str:
        return "Image Straightener"

    def get_plugin_version(self) -> str:
        return "ImageStraightener V1.0"

    def get_plugin_description(self) -> str:
        return "Detects and corrects rotational skew in industrial camera frames."

    def get_supported_formats(self) -> list:
        return ["jpg", "jpeg", "png", "tiff", "bmp"]

    def supports_batch_processing(self) -> bool:
        return True

    def process(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Straightens rotation of input BGR image.
        """
        start_time = time.time()

        # Validation
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Input image must be a valid numpy array.")
        if len(image.shape) != 3:
            raise ValueError("Input image must be a 3-channel BGR image.")

        # Detect rotation angle
        angle, debug_info = straightener_engine.detect_rotation_angle(image)

        # Rotate the image
        final_image = straightener_engine.rotate_image(image, angle)

        elapsed = time.time() - start_time
        metadata = {
            "version": self.get_plugin_version(),
            "detected_angle_degrees": angle,
            "debug_metrics": debug_info,
            "processing_time_sec": elapsed,
            "input_dimensions": f"{image.shape[1]}x{image.shape[0]}",
            "output_dimensions": f"{final_image.shape[1]}x{final_image.shape[0]}"
        }

        return final_image, metadata
