# NOTE: Not fully tested with production setup due to environment limits
import unittest
import app_config

class TestSecretKey(unittest.TestCase):
    def test_secret_key_not_default(self):
        self.assertNotEqual(app_config.SECRET_KEY, 'string')

if __name__ == '__main__':
    unittest.main()
