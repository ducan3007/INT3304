import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import BingoBoard from './Bingo';
import { URL } from './App';

type RoomProps = {
  game_state: any;
};

const Room = (props: any) => {
  const { id } = useParams();
  const webSocket = useRef<WebSocket>(new WebSocket(URL));

  const [message, setMessage] = useState<string>('');
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

    if (webSocket.current.readyState !== WebSocket.CLOSED) {
      pingPongInterval = setInterval(() => {
        console.log(new Date().toLocaleTimeString(), 'detail');
        webSocket.current.send(JSON.stringify({ msg: 'detail', room_id: id }));
      }, 1000);

      webSocket.current.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data?.msg) {
          case 'pong':
            console.log(new Date().toLocaleTimeString(), 'pong', event.data);
          case 'get':
            console.log(new Date().toLocaleTimeString(), 'get', data);
          case 'detail':
            console.log(new Date().toLocaleTimeString(), 'detail', data);
        }
      };
    }

    // Handle close and Reconnect every 2 seconds
    webSocket.current.onclose = () => {
      console.log(new Date().toLocaleString(), 'closed');
      setConnected(false);
      clearInterval(pingPongInterval);

      const reconnectInterval = setInterval(() => {
        console.log(new Date().toLocaleString(), 'reconnecting');
        webSocket.current = new WebSocket(URL);
        webSocket.current.onopen = () => {
          console.log(new Date().toLocaleString(), 'connected');
          setConnected(true);
          clearInterval(reconnectInterval);
        };
      }, 2000);
    };

    return () => {
      clearInterval(pingPongInterval);
    };
  }, [webSocket.current]);

  return (
    <div className='room-wrapper'>
      <h3>Room {id}</h3>
      <div className='room'>
        <BingoBoard />
        <BingoBoard />
      </div>
    </div>
  );
};

export default Room;
