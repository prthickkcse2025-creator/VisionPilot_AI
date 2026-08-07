import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestRESTAPIs(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_api_login_fail(self):
        # Invalid credentials should raise 401
        response = self.client.post("/api/login", data={"username": "wrong", "password": "user"})
        self.assertEqual(response.status_code, 401)

    def test_extract_features_api(self):
        headers = {"Authorization": "Bearer mock_token_admin"}
        response = self.client.post("/extract_features", headers=headers, data={"image_id": 101})
        self.assertEqual(response.status_code, 200)
        self.assertIn("features", response.json())

    def test_predict_policy_api(self):
        headers = {"Authorization": "Bearer mock_token_admin"}
        response = self.client.post("/predict_policy", headers=headers, data={"image_id": 101})
        self.assertEqual(response.status_code, 200)
        self.assertIn("policy_decision", response.json())

    def test_policy_evaluate_api_untrained(self):
        headers = {"Authorization": "Bearer mock_token_admin"}
        response = self.client.post("/policy/evaluate", headers=headers)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "error")
        self.assertIn("not trained", json_data["message"])

if __name__ == '__main__':
    unittest.main()

