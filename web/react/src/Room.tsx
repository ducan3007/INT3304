import React from 'react';
import BingoBoard from './Bingo';

const Room = () => {
  return (
    <div className='room-wrapper'>
      <h1>Room</h1>
      <div className='room'>
        <BingoBoard />
        <BingoBoard />
      </div>
    </div>
  );
};

export default Room;
