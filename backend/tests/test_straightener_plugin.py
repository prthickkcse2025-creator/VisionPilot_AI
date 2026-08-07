import unittest
import numpy as np
from backend.models.enhancement.straightener_plugin import ImageStraightenerPlugin

class TestStraightenerPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = ImageStraightenerPlugin()
        # Create solid gray image
        self.mock_image = np.ones((100, 100, 3), dtype=np.uint8) * 128

    def test_plugin_metadata(self):
        self.assertEqual(self.plugin.get_plugin_name(), "Image Straightener")
        self.assertEqual(self.plugin.get_plugin_version(), "ImageStraightener V1.0")
        self.assertIn("skew", self.plugin.get_plugin_description())

    def test_plugin_process(self):
        out_img, meta = self.plugin.process(self.mock_image, {})
        self.assertEqual(out_img.shape, self.mock_image.shape)
        self.assertIn("detected_angle_degrees", meta)
        self.assertIsInstance(meta["detected_angle_degrees"], float)

if __name__ == '__main__':
    unittest.main()
