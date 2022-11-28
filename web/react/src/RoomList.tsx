import React from 'react';

const RoomList = () => {
  return (
    <div>
      <h1>Room List</h1>
      <RoomItemInfo />
    </div>
  );
};

const RoomItemInfo = () => {
  return (
    <div className='room-info-item'>
      <h4>Room ID: asdfasdcvasdf</h4>
      <h4>Player ID1: 2</h4>
      <h4>Player ID2: 3</h4>
      
    </div>
  );
};

export default RoomList;
