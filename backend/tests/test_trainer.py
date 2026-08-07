import unittest
import os
import json
from backend.models.policy.training.policy_trainer import PolicyNetworkTrainer

class TestTrainerFramework(unittest.TestCase):
    def setUp(self):
        self.temp_json = "E:/VisionPilot_AI/backend/models/policy/training/temp_train_data.json"
        self.checkpoint_dir = "E:/VisionPilot_AI/backend/models/policy/checkpoints/test_checkpoints"
        
        # Write dummy samples to the JSON file
        dummy_data = [
            {"filename": "img1.png", "filepath": "img1.png", "features": {"brightness": 0.5, "contrast": 0.5, "blur": 0.0, "noise": 0.0, "color_cast": 0.0, "dynamic_range": 0.5, "perspective_skew": 0.0}, "label": 0},
            {"filename": "img2.png", "filepath": "img2.png", "features": {"brightness": 0.1, "contrast": 0.2, "blur": 0.1, "noise": 0.1, "color_cast": 0.1, "dynamic_range": 0.8, "perspective_skew": 0.0}, "label": 2},
            {"filename": "img3.png", "filepath": "img3.png", "features": {"brightness": 0.5, "contrast": 0.5, "blur": 0.0, "noise": 0.0, "color_cast": 0.0, "dynamic_range": 0.5, "perspective_skew": 0.8}, "label": 3},
            {"filename": "img4.png", "filepath": "img4.png", "features": {"brightness": 0.5, "contrast": 0.5, "blur": 0.0, "noise": 0.0, "color_cast": 0.8, "dynamic_range": 0.5, "perspective_skew": 0.0}, "label": 1}
        ]
        with open(self.temp_json, "w") as f:
            json.dump(dummy_data, f)
            
        self.trainer = PolicyNetworkTrainer(self.temp_json, self.checkpoint_dir)

    def tearDown(self):
        if os.path.exists(self.temp_json):
            os.remove(self.temp_json)
        best_pth = os.path.join(self.checkpoint_dir, "policy_best.pth")
        if os.path.exists(best_pth):
            os.remove(best_pth)
        if os.path.exists(self.checkpoint_dir):
            os.rmdir(self.checkpoint_dir)

    def test_trainer_initializes_and_runs(self):
        # Run a short 2 epoch training test
        res = self.trainer.train_model(epochs=2, batch_size=2, val_split=0.25)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["epochs_run"], 2)
        self.assertTrue(os.path.exists(os.path.join(self.checkpoint_dir, "policy_best.pth")))

if __name__ == '__main__':
    unittest.main()
