import unittest
import numpy as np
import os
from backend.models.enhancement.hdr_plugin import HDRFusionPlugin

class TestHDRPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = HDRFusionPlugin()
        # Create a mock BGR image (solid gray)
        self.mock_image = np.ones((100, 100, 3), dtype=np.uint8) * 128

    def test_plugin_metadata(self):
        self.assertEqual(self.plugin.get_plugin_name(), "HDR Fusion")
        self.assertEqual(self.plugin.get_plugin_version(), "MAWB-Net HDR Fusion V13.2")
        self.assertIn("MAWB-Net V13.2", self.plugin.get_plugin_description())
        self.assertIn("png", self.plugin.get_supported_formats())
        self.assertTrue(self.plugin.supports_batch_processing())

    def test_plugin_process(self):
        config = {"fusion_mode": "mertens"}
        out_img, meta = self.plugin.process(self.mock_image, config)
        self.assertEqual(out_img.shape, self.mock_image.shape)
        self.assertEqual(meta["version"], "MAWB-Net HDR Fusion V13.2")
        self.assertEqual(meta["fusion_mode"], "mertens")
        self.assertTrue(meta["simulated_brackets"])

if __name__ == '__main__':
    unittest.main()
