import unittest
import numpy as np
from backend.models.evaluation.evaluation_runner import EvaluationRunner

class TestEvaluationRunner(unittest.TestCase):
    def setUp(self):
        mock_images = [np.ones((40, 40, 3), dtype=np.uint8) * 128]
        self.runner = EvaluationRunner(mock_images)
        self.runner.pipeline.policy_network.is_trained = True

    def test_runner_executes_successfully(self):
        res = self.runner.run_evaluations()
        self.assertEqual(res["status"], "complete")
        self.assertEqual(res["images_evaluated"], 1)
        self.assertIn("comparison", res)
        comparison = res["comparison"]
        self.assertIn("raw", comparison)
        self.assertIn("fixed", comparison)
        self.assertIn("policy", comparison)
        self.assertGreater(comparison["policy"]["mean_accuracy"], 0.0)

if __name__ == '__main__':
    unittest.main()
