from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import numpy as np

class OCRPlugin(ABC):
    """
    Abstract Interface for VisionPilot text readers (EasyOCR, Tesseract).
    """
    @abstractmethod
    def get_plugin_name(self) -> str:
        pass

    @abstractmethod
    def get_plugin_version(self) -> str:
        pass

    @abstractmethod
    def read_text(self, image: np.ndarray, bounding_boxes: List[Tuple[float, float, float, float]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts alphanumeric data from specified bounding box regions.
        Returns:
            List[Dict[str, Any]]: A list of OCR results, where each result contains:
                {
                    "text": str,
                    "confidence": float,
                    "box": [x, y, w, h]  # Coordinates inside original image
                }
        """
        pass
