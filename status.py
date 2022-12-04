import asyncio
import websockets
import struct
import json

data = {
    "result": 2,
    "match": 8, # id của ván game
    "status": 1,
    "id1": 1000,
    "id2": 100
}

async def hello():
    async with websockets.connect("ws://104.194.240.16/ws/channels/") as websocket:
        await websocket.send(json.dumps(data))
        msg = await websocket.recv()
        print(msg)
asyncio.run(hello())

