import unittest
import numpy as np
from backend.models.policy.policy_inference import PolicyInferencePipeline

class TestPolicyInferencePipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = PolicyInferencePipeline()
        self.mock_image = np.ones((50, 50, 3), dtype=np.uint8) * 128

    def test_pipeline_runs_end_to_end(self):
        enhanced, meta = self.pipeline.run_pipeline(self.mock_image)
        self.assertEqual(enhanced.shape, self.mock_image.shape)
        self.assertEqual(meta["pipeline_status"], "success")
        self.assertIn("extracted_features", meta)
        self.assertIn("policy_decision", meta)
        self.assertIn("brightness", meta["extracted_features"])

    def test_pipeline_evaluation_mode_missing_weights(self):
        # In evaluation mode without trained weights, it must fail with error pipeline_status
        self.pipeline.policy_network.is_trained = False
        enhanced, meta = self.pipeline.run_pipeline(self.mock_image, evaluation_mode=True)
        self.assertEqual(meta["pipeline_status"], "error")
        self.assertIn("not trained", meta["message"])

if __name__ == '__main__':
    unittest.main()
