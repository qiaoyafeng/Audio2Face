
import os
import sys
import time
from os.path import abspath, dirname, join
import codecs
import json

import asyncio
import websockets

package_path = "./"

# *******************************************
# load config file
path_config = join(package_path, "config.json")

try:
    with codecs.open(path_config, 'r', 'utf-8-sig') as fconfig:
        ServiceConfig = json.load(fconfig)
except Exception as err:
    print("Read file failed,",path_config,".Error is :",err)
    os.system("pause")
    # exit(1)



# *******************************************
# read parsing config data
productId = ServiceConfig['api_key']['productId']
publicKey = ServiceConfig['api_key']['publicKey']
secretkey = ServiceConfig['api_key']['secretKey']
productIdChat = ServiceConfig['api_key']['productIdChat']
SPEAKER = ServiceConfig['api_key']['speaker']

BA_URL = ServiceConfig['api_ba']['url']
WSURL = ServiceConfig['api_websocket']['url']+productId + "&token="
request_body_json=json.dumps(ServiceConfig['api_websocket']['request_body_first'])

info_print = ServiceConfig['config']['print']
ID_SESSION = ServiceConfig['config']['session']
FPS = ServiceConfig['config']['fps']
SPEED_PLAY = float(1.0 / FPS)

# *******************************************
# *******************************************

# read server and client config data
SERVER_ADDR = (ServiceConfig['config']['server']['ip'], ServiceConfig['config']['server']['port'])
CLIENT_ADDR = (ServiceConfig['config']['client']['ip'], ServiceConfig['config']['client']['port'])


async def hello(websocket):
    name = await websocket.recv()
    print(f"<<< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f">>> {greeting}")


async def main():
    async with websockets.serve(hello, SERVER_ADDR[0], SERVER_ADDR[1]):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
