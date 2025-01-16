import unittest
from app.hello_world import hello_world

class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(hello_world(), "hello world")

if __name__ == '__main__':
    unittest.main()
