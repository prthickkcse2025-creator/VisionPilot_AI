from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
import numpy as np

class EnhancementPlugin(ABC):
    """
    Abstract Interface for VisionPilot Image Enhancement Plugins.
    Enables custom blenders, alignment scripts, or exposure compensators.
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
    def get_plugin_description(self) -> str:
        """Returns plugin description."""
        pass

    @abstractmethod
    def get_supported_formats(self) -> list:
        """Returns list of supported image formats (e.g. ['jpg', 'png'])."""
        pass

    @abstractmethod
    def supports_batch_processing(self) -> bool:
        """Returns True if the plugin supports batch processing natively."""
        pass

    @abstractmethod
    def process(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Enhances the input BGR image.
        Returns:
            Tuple[np.ndarray, Dict[str, Any]]: Enhanced image, diagnostic/telemetry dict
        """
        pass

