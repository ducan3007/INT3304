from bingo import Bingo
import protocol
import redis
import json


if __name__ == '__main__':
    redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")

    bingo = Bingo(5)
    a = bingo.to_json("1234")
    # print(json.dumps(a))

    c = dict()
    c['players'] = []
    c['players'].append('1234')

    # redisClient.ping()
    redisClient.set('id:1', a['id'])
    redisClient.set('game_board:1', a['board'])
    redisClient.set('history:1', a['history'])
    redisClient.set('c:1', json.dumps(c))

    print(redisClient.get('id:1').decode())
    print(protocol.deserialize_matrix(redisClient.get('game_board:1'))[1])
    print(json.loads(redisClient.get('history:1')))
    print(json.loads(redisClient.get('c:1')))

    redisClient.keys()
