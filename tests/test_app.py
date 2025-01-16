import os
import unittest
from fastapi.testclient import TestClient
from app.sample.app import app, MOUNT_PATH

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_file = os.path.join(MOUNT_PATH, "test.txt")
        if not os.path.exists(MOUNT_PATH):
            os.makedirs(MOUNT_PATH)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_write_file(self):
        response = self.client.post("/write", json={"filename": "test.txt", "content": "Hello, world!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "File written successfully"})
        with open(self.test_file, "r") as file:
            self.assertEqual(file.read(), "Hello, world!")

    def test_read_file(self):
        with open(self.test_file, "w") as file:
            file.write("Hello, world!")
        response = self.client.get("/read/test.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"filename": "test.txt", "content": "Hello, world!"})

    def test_read_file_not_found(self):
        response = self.client.get("/read/nonexistent.txt")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "File not found"})

    def test_write_file_error(self):
        response = self.client.post("/write", json={"filename": "", "content": "Hello, world!"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())

if __name__ == "__main__":
    unittest.main()
