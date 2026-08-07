import unittest
import numpy as np
from backend.models.feature_extraction.brightness import extract_brightness
from backend.models.feature_extraction.contrast import extract_contrast
from backend.models.feature_extraction.blur import extract_blur
from backend.models.feature_extraction.noise import extract_noise
from backend.models.feature_extraction.color_cast import extract_color_cast
from backend.models.feature_extraction.dynamic_range import extract_dynamic_range
from backend.models.feature_extraction.perspective import extract_perspective_skew

class TestFeatureExtraction(unittest.TestCase):
    def setUp(self):
        # Create a mock black image
        self.mock_image = np.zeros((100, 100, 3), dtype=np.uint8)

    def test_brightness(self):
        val = extract_brightness(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

    def test_contrast(self):
        val = extract_contrast(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

    def test_blur(self):
        val = extract_blur(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

    def test_noise(self):
        val = extract_noise(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

    def test_color_cast(self):
        val = extract_color_cast(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

    def test_dynamic_range(self):
        val = extract_dynamic_range(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

    def test_perspective_skew(self):
        val = extract_perspective_skew(self.mock_image)
        self.assertIsInstance(val, float)
        self.assertTrue(0.0 <= val <= 1.0)

if __name__ == '__main__':
    unittest.main()
