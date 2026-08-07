import unittest
import numpy as np
from backend.models.policy.policy_executor import PolicyExecutor

class DummyPlugin:
    def process(self, image, config):
        # Simply returns a modified version
        return image + 1, {"status": "SUCCESS"}

class TestPolicyExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = PolicyExecutor()
        self.executor.register_plugin("ImageStraightening", DummyPlugin())
        self.executor.register_plugin("HDRFusion", DummyPlugin())
        self.mock_image = np.zeros((10, 10, 3), dtype=np.uint8)

    def test_executor_no_action(self):
        prediction = {"policy_decision": "NO_ACTION"}
        res = self.executor.execute_policy(self.mock_image, prediction)
        np.testing.assert_array_equal(res, self.mock_image)

    def test_executor_straighten(self):
        prediction = {"policy_decision": "IMAGE_STRAIGHTENING"}
        res = self.executor.execute_policy(self.mock_image, prediction)
        # Dummy plugin adds 1
        np.testing.assert_array_equal(res, self.mock_image + 1)

if __name__ == '__main__':
    unittest.main()
