import unittest
from backend.models.policy.policy_network import InferenceAwarePolicyNetwork

class TestPolicyNetwork(unittest.TestCase):
    def setUp(self):
        self.network = InferenceAwarePolicyNetwork()

    def test_predict_no_action(self):
        features = {
            "brightness": 0.5,
            "contrast": 0.5,
            "blur": 0.02,
            "perspective_skew": 0.02,
            "dynamic_range": 0.3
        }
        res = self.network.predict_strategy(features)
        self.assertEqual(res["policy_decision"], "NO_ACTION")
        self.assertGreaterEqual(res["confidence_score"], 0.9)

    def test_predict_hdr(self):
        features = {
            "brightness": 0.2,
            "contrast": 0.5,
            "blur": 0.02,
            "perspective_skew": 0.02,
            "dynamic_range": 0.8
        }
        res = self.network.predict_strategy(features)
        self.assertEqual(res["policy_decision"], "HDR_FUSION")
        self.assertIn("High dynamic range", res["reasons"][0])

    def test_predict_straightening(self):
        features = {
            "brightness": 0.5,
            "contrast": 0.5,
            "blur": 0.02,
            "perspective_skew": 0.15,
            "dynamic_range": 0.3
        }
        res = self.network.predict_strategy(features)
        self.assertEqual(res["policy_decision"], "IMAGE_STRAIGHTENING")

if __name__ == '__main__':
    unittest.main()
