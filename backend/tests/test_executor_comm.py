import unittest
import numpy as np
from backend.models.policy.policy_executor import PolicyExecutor

class TestExecutorCommunication(unittest.TestCase):
    def setUp(self):
        self.executor = PolicyExecutor()
        self.mock_image = np.ones((50, 50, 3), dtype=np.uint8) * 128

    def test_executor_calls_registry_hdr(self):
        prediction = {"policy_decision": "HDR_FUSION"}
        # Execute policy - should fetch and process via global registry
        res = self.executor.execute_policy(self.mock_image, prediction)
        self.assertEqual(res.shape, self.mock_image.shape)

    def test_executor_calls_registry_straighten(self):
        prediction = {"policy_decision": "IMAGE_STRAIGHTENING"}
        res = self.executor.execute_policy(self.mock_image, prediction)
        self.assertEqual(res.shape, self.mock_image.shape)

if __name__ == '__main__':
    unittest.main()
