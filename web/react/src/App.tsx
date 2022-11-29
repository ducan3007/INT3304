import { useState, useRef, useEffect } from 'react';
import Login from './Login';
import BingoBoard from './Bingo';
import Room from './Room';
import RoomList from './RoomList';
import './App.css';

const URL = 'ws://localhost:8081';

function App() {
  const webSocket = useRef<WebSocket>(new WebSocket(URL));

  const [message, setMessage] = useState<string>('');
  const [messages, setMessages] = useState<string[]>([]);
  const [connected, setConnected] = useState<boolean>(false);

  useEffect(() => {
    // Handle ping pong interval
    let pingPongInterval: any;

    if (webSocket.current.readyState !== WebSocket.CLOSED) {
      pingPongInterval = setInterval(() => {
        console.log(new Date().toLocaleTimeString(), 'ping');
        webSocket.current.send('ping');
      }, 2000);

      webSocket.current.onmessage = (event) => {
        console.log('Rcv: ', event.data);
      };
    }

    // Handle close and Reconnect
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

      {/* <Room />
      <RoomList /> */}
    </div>
  );
}

export default App;
