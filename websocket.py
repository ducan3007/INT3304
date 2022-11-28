
import socket_server as socketServer
import os
import sys
import json
import websockets
import asyncio
import time
from datetime import datetime
import redis


redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


def log(*args, **kwargs):
    print(f'{datetime.now().strftime("%H:%M:%S")} :', *args, **kwargs)


async def main(ws, path):
    # ping pong
    while True:
        msg = await ws.recv()

        if msg == 'ping':
            ganme_state = redisClient.get('game_state')
            data = json.loads(ganme_state)

            print('data', data)

            await ws.send(json.dumps(data))


if __name__ == '__main__':
    start_server = websockets.serve(main, "localhost", 8081)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
