```python
import asyncio
import websockets
import struct
a=[1,9,b'127.0.0.5',8081,4,b'game',10,b'bingo',4,b'copv']
pack=struct.pack(f'ii{a[1]}s',a[0],a[1],a[2])+struct.pack(f'ii{a[4]}s',a[3],a[4],a[5])+struct.pack(f'i{a[6]}s',a[6],a[7])+struct.pack(f'i{a[8]}s',a[8],a[9])
tt = pack
async def hello():
async with websockets.connect("104.194.240.16://localhost:8881") as websocket:
await websocket.send(tt)
msg = await websocket.recv()
print(msg)
asyncio.run(hello())
print(pack)
```
