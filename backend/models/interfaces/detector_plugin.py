from abc import ABC, abstractmethod
from typing import Any, Dict, List
import numpy as np

class DetectorPlugin(ABC):
    """
    Abstract Interface for VisionPilot Product/Label Bounding Box Detectors.
    Swappable modules (e.g. YOLO, SSD, or custom contour finders).
    """
    @abstractmethod
    def get_plugin_name(self) -> str:
        pass

    @abstractmethod
    def get_plugin_version(self) -> str:
        pass

    @abstractmethod
    def detect(self, image: np.ndarray, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detects objects in the input image.
        Returns:
            List[Dict[str, Any]]: A list of detections, where each detection contains:
                {
                    "class_name": str,
                    "confidence": float,
                    "box": [x, y, w, h]  # Normalized coordinates [0, 1]
                }
        """
        pass
