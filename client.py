#!/usr/bin/env python

import asyncio
import websockets


WS_SERVER_URL = "http://172.16.35.149:8000"


async def hello():
    uri = "ws://172.16.35.149:8765"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f">>> {name}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")


async def send_message_to_server(message):
    uri = "ws://172.16.35.149:8765"
    async with websockets.connect(uri) as websocket:

        await websocket.send(message)
        print(f">>> {message}")


if __name__ == "__main__":
    asyncio.run(hello())
