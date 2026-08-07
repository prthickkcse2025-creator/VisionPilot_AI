import unittest
import io
import os
from fastapi.testclient import TestClient
from backend.main import app

class TestEnhancementAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {"Authorization": "Bearer mock_token_admin"}
        import cv2
        import numpy as np
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        _, buf = cv2.imencode(".png", img)
        self.dummy_image_data = buf.tobytes()

    def test_list_plugins(self):
        response = self.client.get("/plugins", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("HDR Fusion", data)
        self.assertIn("Image Straightener", data)

    def test_plugins_health(self):
        response = self.client.get("/plugins/health", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("HDR Fusion"), "Healthy")
        self.assertEqual(data.get("Image Straightener"), "Healthy")

    def test_enhance_manual_hdr(self):
        files = {"file": ("test.png", io.BytesIO(self.dummy_image_data), "image/png")}
        data = {"enhancement": "HDR Fusion"}
        response = self.client.post("/enhance", headers=self.headers, files=files, data=data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["plugin"], "HDR Fusion")
        self.assertEqual(json_data["status"], "success")
        self.assertIn("uploads", json_data["input_image"])
        self.assertIn("outputs", json_data["output_image"])
        self.assertIn("version", json_data["metadata"])

    def test_enhance_batch_placeholder(self):
        files = [
            ("files", ("test1.png", io.BytesIO(self.dummy_image_data), "image/png")),
            ("files", ("test2.png", io.BytesIO(self.dummy_image_data), "image/png"))
        ]
        data = {"enhancement": "policy"}
        response = self.client.post("/enhance/batch", headers=self.headers, files=files, data=data)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["status"], "batch_processing_queued")
        self.assertEqual(json_data["total_images"], 2)

if __name__ == '__main__':
    unittest.main()
