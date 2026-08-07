import unittest
import os
import json
import numpy as np
import cv2
from backend.models.policy.training.dataset_builder import PolicyDatasetBuilder
from backend.models.policy.training.policy_dataset import PolicyPyTorchDataset

class TestDatasetFramework(unittest.TestCase):
    def setUp(self):
        self.temp_json = "E:/VisionPilot_AI/backend/models/policy/training/temp_test_dataset.json"
        self.builder = PolicyDatasetBuilder(self.temp_json)
        self.mock_dir = "E:/VisionPilot_AI/uploads/test_mock"
        os.makedirs(self.mock_dir, exist_ok=True)
        
        # Save a valid mock image
        self.mock_img_path = os.path.join(self.mock_dir, "mock_item.png")
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        cv2.imwrite(self.mock_img_path, img)

    def tearDown(self):
        if os.path.exists(self.mock_img_path):
            os.remove(self.mock_img_path)
        if os.path.exists(self.mock_dir):
            os.rmdir(self.mock_dir)
        if os.path.exists(self.temp_json):
            os.remove(self.temp_json)

    def test_builder_runs_and_saves(self):
        dataset = self.builder.build_dataset_from_folder(self.mock_dir)
        self.assertEqual(len(dataset), 1)
        self.assertEqual(dataset[0]["filename"], "mock_item.png")
        self.assertIn("brightness", dataset[0]["features"])
        self.assertTrue(os.path.exists(self.temp_json))

    def test_pytorch_dataset_loads(self):
        # Build first
        self.builder.build_dataset_from_folder(self.mock_dir)
        
        # Parse via PyTorch dataset loader
        ds = PolicyPyTorchDataset(self.temp_json)
        self.assertEqual(len(ds), 1)
        features, label = ds[0]
        self.assertEqual(features.shape[0], 7)
        self.assertIsInstance(label.item(), int)

if __name__ == '__main__':
    unittest.main()
