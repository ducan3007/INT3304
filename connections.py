import asyncio
import websockets
import struct

a = [1, 9, b'localhost', 27003, 5, b'bingo', 7, b'doan_so', 4, b'nh08']
pack = struct.pack(f'ii{a[1]}s', a[0], a[1], a[2])+struct.pack(f'ii{a[4]}s', a[3], a[4], a[5]
                                                               )+struct.pack(f'i{a[6]}s', a[6], a[7])+struct.pack(f'i{a[8]}s', a[8], a[9])


async def hello():
    async with websockets.connect("ws://104.194.240.16:8881") as websocket:
        await websocket.send(pack)
        msg = await websocket.recv()
        print(msg)

asyncio.run(hello())

print(pack)
