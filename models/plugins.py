from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import numpy as np

class EnhancementPlugin(ABC):
    """
    Abstract Interface for VisionPilot Image Enhancement Plugins.
    Enables custom filters, local adjustments, or pseudo-exposure calculations.
    """
    @abstractmethod
    def get_plugin_name(self) -> str:
        """Returns unique plugin identifier."""
        pass

    @abstractmethod
    def get_plugin_version(self) -> str:
        """Returns plugin version."""
        pass

    @abstractmethod
    def process(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Enhances the input image (BGR format).
        Returns:
            Tuple[np.ndarray, Dict[str, Any]]: Enhanced image, diagnostic/telemetry dict
        """
        pass


class DetectorPlugin(ABC):
    """
    Abstract Interface for VisionPilot Bounding Box Bounding & Detection Plugins.
    Enables custom object models (e.g. YOLO, SSD, custom contour finders).
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


class OCRPlugin(ABC):
    """
    Abstract Interface for VisionPilot Text extraction / OCR Plugins.
    Enables custom text readers (e.g. Tesseract, EasyOCR, PaddleOCR).
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
