import unittest

from config.ailingxin import ailingxin_settings
from lib.ailingxin.api_ailingxin import AiLingXin


class MyTestCase(unittest.TestCase):

    def test_conn(self):
        ailingxin = AiLingXin(ailingxin_settings.app_name, ailingxin_settings.client_id, ailingxin_settings.client_secret)
        chat = ailingxin.chat("苏轼是谁？。")
        print(f"test chat: {chat}")
        self.assertIsNotNone(chat)


if __name__ == '__main__':
    unittest.main()
