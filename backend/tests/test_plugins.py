import unittest
from backend.models.interfaces.enhancement_plugin import EnhancementPlugin
from backend.models.interfaces.detector_plugin import DetectorPlugin
from backend.models.interfaces.ocr_plugin import OCRPlugin

class MockEnhancement(EnhancementPlugin):
    def get_plugin_name(self) -> str:
        return "mock_enhancer"
    def get_plugin_version(self) -> str:
        return "1.0.0"
    def get_plugin_description(self) -> str:
        return "Mock enhancement plugin for testing interface compatibility."
    def get_supported_formats(self) -> list:
        return ["jpg", "png"]
    def supports_batch_processing(self) -> bool:
        return True
    def process(self, image, config):
        return image, {}

class MockDetector(DetectorPlugin):
    def get_plugin_name(self) -> str:
        return "mock_detector"
    def get_plugin_version(self) -> str:
        return "1.0.0"
    def detect(self, image, config):
        return []

class TestPluginInterfaces(unittest.TestCase):
    def test_enhancement_plugin_subclass(self):
        plugin = MockEnhancement()
        self.assertEqual(plugin.get_plugin_name(), "mock_enhancer")
        self.assertEqual(plugin.get_plugin_version(), "1.0.0")

    def test_detector_plugin_subclass(self):
        plugin = MockDetector()
        self.assertEqual(plugin.get_plugin_name(), "mock_detector")
        self.assertEqual(plugin.get_plugin_version(), "1.0.0")

if __name__ == '__main__':
    unittest.main()
