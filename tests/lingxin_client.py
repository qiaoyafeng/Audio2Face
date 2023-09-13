import time

from config.ailingxin import ailingxin_settings
from lib.ailingxin.api_ailingxin import AiLingXin

app_name = ailingxin_settings.app_name
client_id = ailingxin_settings.client_id
client_secret = ailingxin_settings.client_secret


ailingxin = AiLingXin(app_name, client_id, client_secret)
print(f"ailingxin: {ailingxin}")
#
# access_token = ailingxin.create_token()
#
# print(f"access_token: {access_token}")

chat = ailingxin.chat("苏轼是谁？。")

print(f"chat: {chat}")

time.sleep(5)

chat = ailingxin.chat("李白是谁？。")

print(f"chat: {chat}")
