import React from 'react';

const BingoBoard = () => {
  const data = [
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 25]
  ];
  return (
    <div className='bingo-board'>
      {data.map((row, index) => {
        return (
          <div className='row' key={index}>
            {row.map((column, index) => {
              return <Square key={index}>{column}</Square>;
            })}
          </div>
        );
      })}
    </div>
  );
};

const Square = (props: any) => {
  return (
    <div className={props?.selected ? 'square selected' : 'square non-selected'}>
      {props.children}
    </div>
  );
};

export default BingoBoard;
