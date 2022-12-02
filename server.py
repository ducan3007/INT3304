import asyncio
import websockets
import json

HOST = "127.0.0.1"
PORT = 65432

msg1 = {"result": 1, "ip": "localhost", "port": 10010, "path": "path"}

msg2 = {"result": 0}

data = {
    "action": 1,
    "match": 11,
    "id1": 3,
    "id2": 5,
    "passwd": 123
}

async def create(websocket):
    async for message in websocket:
        data = json.loads(message)
        print(data)
        if data["action"] == 1:
            await websocket.send(json.dumps(msg1))
        else:
            await websocket.send(json.dumps(msg2))

async def server():
    async with websockets.serve(create, "localhost", 8881):
        await asyncio.Future()
    asyncio.run(server())

