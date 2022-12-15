import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import BingoBoard from './Bingo';
import { URL } from './App';

type RoomProps = {
  game_state: any;
};

export let webSocket = new WebSocket('ws://localhost:8081');

const Room = (props: any) => {
  const nextMoveRef = useRef('');
  const gameEndRef = useRef(false);

  const { id } = useParams();

  const [data, setData] = useState<any>([]);
  const [messages, setMessages] = useState<string[]>([]);
  const [connected, setConnected] = useState<boolean>(false);

  // const players = React.useMemo(() => {
  //   for (const i in props?.game_state) {
  //     if (props?.game_state[i].room_id === id) {
  //       return props?.game_state[i]?.data?.players;
  //     }
  //   }
  // }, []);

  // console.log(players);

  useEffect(() => {
    // Handle ping pong interval every 2 seconds
    let pingPongInterval: any;

    if (webSocket.readyState !== WebSocket.CLOSED) {
      pingPongInterval = setInterval(() => {
        console.log(
          new Date().toLocaleTimeString(),
          JSON.stringify({ msg: 'detail', room_id: id })
        );

        webSocket.send(JSON.stringify({ msg: 'detail', room_id: id }));
      }, 100);

      webSocket.onmessage = (event) => {
        const message = JSON.parse(event.data);

        console.log('message', message);
        console.log('dataRef', nextMoveRef.current);

        if ('' === nextMoveRef.current) {
          nextMoveRef.current = message?.next_move;
        }

        if (nextMoveRef.current && '' === message?.next_move) {
          gameEndRef.current = true;
          const endText = document.getElementById('abc1');
          if (endText) {
            endText.style.display = 'block';
          }
          setTimeout(() => {
            console.log('reload');
            window.location.reload();
          }, 5000);
        }

        if (!gameEndRef.current) {
          setData({
            boards: message?.res,
            next_move: message?.next_move
          });
        }
      };
    }

    // Handle close and Reconnect every 2 seconds
    webSocket.onclose = () => {
      console.log(new Date().toLocaleString(), 'closed');
      setConnected(false);
      clearInterval(pingPongInterval);

      const reconnectInterval = setInterval(() => {
        console.log(new Date().toLocaleString(), 'reconnecting');
        webSocket = new WebSocket(URL);
        webSocket.onopen = () => {
          console.log(new Date().toLocaleString(), 'connected');
          setConnected(true);
          clearInterval(reconnectInterval);
        };
      }, 2000);
    };

    return () => {
      clearInterval(pingPongInterval);
    };
  }, [webSocket]);

  console.log('data', data);

  return (
    <div className='room-wrapper'>
      <h1 className='bold'>Room {id}</h1>
      <h1 id='abc1' style={{ display: 'none' }}>
        Trận đấu kết thúc
      </h1>
      {/* <h2 className='bold'>Current turn {data?.next_move?.toString()}</h2> */}
      <div style={{ display: 'flex', gap: '200px' }}>
        {data?.boards?.map((board: any, index: number) => {
          return (
            <div key={index} className='room-board'>
              <BingoBoard board={board} current={data?.next_move?.toString()} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Room;
