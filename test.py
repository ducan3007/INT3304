from bingo import Bingo
import protocol
import redis
import json
import time
obj = time.gmtime(0)


if __name__ == '__main__':
    redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")

    get_history = redisClient.zrange("game_history", 0, -1, desc=True, withscores=True)

    # Sau khi chơi xong, gọi thằng này để Lịch sử chơi
    protocol.redis_decode_history(get_history[0][0])

    # bingo = Bingo(5)
    # a = bingo.to_json()
    # test = dict()
    # test['1'] = 1

    # f = json.dumps(test).encode()

    # print(json.loads(f.decode()))

    # c = dict()8
    # c['players'] = []
    # c['players'].append('1234')

    # redisClient.ping()
    # redisClient.set('game_board:1', a['board'])
    # redisClient.set('history:1', a['history'])
    # redisClient.set('c:1', json.dumps(c))

    # print(redisClient.get('id:1').decode())
    # print(protocol.deserialize_matrix(redisClient.get('game_board:1'))[1])
    # print(json.loads(redisClient.get('history:1')))
    # print(json.loads(redisClient.get('c:1')))

    # curr_time = round(time.time()*1000)

    # dict = {}
    # dict[protocol.game_draw()] = curr_time

    # redisClient.zadd("history", dict)
