import os
import sys
from typing import Dict, Any, Type
from backend.models.interfaces.enhancement_plugin import EnhancementPlugin

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, EnhancementPlugin] = {}

    def register_plugin(self, name: str, plugin_instance: EnhancementPlugin):
        self._plugins[name] = plugin_instance

    def get_plugin(self, name: str) -> EnhancementPlugin:
        return self._plugins.get(name)

    def list_plugins(self) -> Dict[str, Any]:
        result = {}
        for name, plugin in self._plugins.items():
            result[name] = {
                "name": plugin.get_plugin_name(),
                "version": plugin.get_plugin_version(),
                "description": plugin.get_plugin_description(),
                "supported_formats": plugin.get_supported_formats(),
                "supports_batch_processing": plugin.supports_batch_processing()
            }
        return result

    def get_health_status(self) -> Dict[str, str]:
        health = {}
        for name, plugin in self._plugins.items():
            try:
                # Test basic properties or dummy process to ensure it is healthy
                _ = plugin.get_plugin_name()
                _ = plugin.get_plugin_version()
                health[name] = "Healthy"
            except Exception as e:
                health[name] = f"Unhealthy: {str(e)}"
        return health

# Global instance of PluginRegistry
registry = PluginRegistry()

# Register approved enhancement plugins
from backend.models.enhancement.hdr_plugin import HDRFusionPlugin
from backend.models.enhancement.straightener_plugin import ImageStraightenerPlugin

registry.register_plugin("HDR Fusion", HDRFusionPlugin())
registry.register_plugin("Image Straightener", ImageStraightenerPlugin())

