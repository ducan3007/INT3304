import React from 'react';
import History from './History';

const BingoBoard = (props: any) => {
  const data = [
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 25]
  ];


  const [board, setBoard] = React.useState();

  React.useEffect(() => {
    setBoard(props?.board?.board);
  }, []);

  const myTurn = props?.board?.uid === props?.current ? true : false;

  return (
    <div className='bingo-board'>
      {props?.board?.uid && (
        <h2 className={`next_move ${myTurn ? 'text-secondary' : ''}`}>
          {myTurn ? 'ĐẾN LƯỢT ' : ''} ID: {props?.board?.uid}
        </h2>
      )}

      {props?.board?.board.map((row: any, index: number) => {
        return (
          <div className='row' key={index}>
            {row.map((column: number, index: number) => {
              return (
                <Square
                  board={props?.board?.board}
                  history={props?.board?.history || {}}
                  key={index}
                >
                  {column}
                </Square>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

export const Square = (props: any) => {
  // console.log(props?.history);

  const isSelect = React.useMemo(() => {
    for (const i in props?.history) {
      const x = props?.history[i][0];
      const y = props?.history[i][1];
      if (props?.children === props?.board[y][x]) {
        return true;
      }
    }
  }, [props?.history]);

  return (
    <div
      style={{ fontSize: '30px', fontWeight: 'bold' }}
      className={isSelect ? 'square selected' : 'square non-selected'}
    >
      {props.children}
    </div>
  );
};

export default BingoBoard;
