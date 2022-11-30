import { useState, useRef, useEffect } from 'react';
import Login from './Login';
import BingoBoard from './Bingo';
import Room from './Room';
import RoomList from './RoomList';

import './App.css';

export const URL = 'ws://localhost:8081';

function App() {
  const webSocket = useRef<WebSocket>(new WebSocket(URL));

  const [gameState, setGameState] = useState<any>();
  const [messages, setMessages] = useState<string[]>([]);
  const [connected, setConnected] = useState<boolean>(false);

  useEffect(() => {
    // Handle ping pong interval every 2 seconds
    let pingPongInterval: any;

    if (webSocket.current.readyState !== WebSocket.CLOSED) {
      pingPongInterval = setInterval(() => {
        console.log(new Date().toLocaleTimeString(), 'ping');
        webSocket.current.send(JSON.stringify({ msg: 'ping' }));
      }, 1000);

      webSocket.current.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data?.msg) {
          case 'get':
            // console.log(new Date().toLocaleTimeString(), 'get', data?.game_state);
            var result = [];

            for (var i in data?.game_state) result.push({ room_id: i, data: data?.game_state[i] });
            setGameState(result);
            console.log(result);
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
    <div className='App'>
      <a className='logo' href='https://vitejs.dev' target='_blank'>
        <img src='/vite.svg' alt='Vite logo' />
      </a>
      {/* <Login /> */}
      {gameState?.map((room: any) => {
        return (
          <div style={{ border: '1px solid black' }}>
            <h3>room id: {room?.room_id}</h3>
            <h3>next_move: {room?.data?.next_move}</h3>
            <h3>player 1: {room?.data?.players[0]}</h3>
            <h3>Player 2: {room?.data?.players[1]}</h3>
          </div>
        );
      })}
      <Room game_state={gameState} />
      <RoomList />
    </div>
  );
}

export default App;
