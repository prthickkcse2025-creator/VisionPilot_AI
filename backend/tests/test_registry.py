import unittest
from backend.models.plugins.registry import registry

class TestPluginRegistry(unittest.TestCase):
    def test_registry_has_active_plugins(self):
        # The registry should auto-register our two production wrappers
        plugins = registry.list_plugins()
        self.assertIn("HDR Fusion", plugins)
        self.assertIn("Image Straightener", plugins)

    def test_get_plugin(self):
        hdr = registry.get_plugin("HDR Fusion")
        self.assertIsNotNone(hdr)
        self.assertEqual(hdr.get_plugin_name(), "HDR Fusion")

    def test_health_check(self):
        health = registry.get_health_status()
        self.assertEqual(health.get("HDR Fusion"), "Healthy")
        self.assertEqual(health.get("Image Straightener"), "Healthy")

if __name__ == '__main__':
    unittest.main()
