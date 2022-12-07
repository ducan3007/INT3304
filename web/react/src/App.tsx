import { useState, useRef, useEffect } from 'react';
import Login from './Login';
import BingoBoard from './Bingo';
import Room from './Room';
import RoomList from './RoomList';
import History from './History';
import { Link, NavLink } from 'react-router-dom';

import './App.css';

export const URL = 'ws://localhost:8081';

export let webSocket = new WebSocket(URL);

console.log('APP run');

function App() {
  const [gameState, setGameState] = useState<any>();
  const [history, setHistory] = useState<any>();
  const [messages, setMessages] = useState<string[]>([]);
  const [connected, setConnected] = useState<boolean>(false);

  useEffect(() => {
    // Handle ping pong interval every 2 seconds
    let pingPongInterval: any;

    // console.log('run');

    if (webSocket.readyState !== WebSocket.CLOSED) {
      pingPongInterval = setInterval(() => {
        console.log(new Date().toLocaleTimeString(), 'ping');

        webSocket.send(JSON.stringify({ msg: 'ping' }));
      }, 1000);

      webSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data?.msg) {
          case 'get':
            // console.log(new Date().toLocaleTimeString(), 'get', data?.game_state);
            var result = [];

            for (var i in data?.game_state) result.push({ room_id: i, data: data?.game_state[i] });
            setGameState(result);
            setHistory(data?.game_history);
            // console.log(result);
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

  let activeStyle = {
    textDecoration: 'underline'
  };

  console.log(gameState);

  if (!gameState) {
    return (
      <div className='logo'>
        <h2>Loading ...</h2>
      </div>
    );
  }

  return (
    <div className='App'>
      <div className='logo'>
        <h1>Nhóm 8 Bingo</h1>
      </div>
      <div className='room-grid'>
        {gameState?.map((room: any) => {
          return (
            <Link className='room-item' to={`/${room.room_id}`}>
              <div>
                <h2>Room: {room?.room_id}</h2>
                <h2>Turn: {room?.data?.next_move}</h2>
                <h2>Player 1 ID: {room?.data?.players[0]}</h2>
                <h2>Player 2 ID: {room?.data?.players[1]}</h2>
              </div>
            </Link>
          );
        })}
      </div>
      <div className='logo'>
        <h1>Lịch sử</h1>
      </div>
      <History history={history} />
    </div>
  );
}

export default App;
