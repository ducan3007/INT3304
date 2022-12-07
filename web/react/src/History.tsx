import React from 'react';
import { Square } from './Bingo';

const History = (props: any) => {
  console.log('props', props);

  const style = {
    fontSize: '30px',
    fontWeight: 'bold',
    margin: '20px',
    padding: '10px',
    lineHeight: '34px',
  };
  const style_winner = Object.assign({}, style, { color: '#f1852d' });

  return (
    <>
      {props?.history?.map((item: any, index: number) => {
        const matchTime = new Date(item?.time);
        return (
          <div>
            <div style={style}>
              Thời gian: {matchTime.getDate()}/{matchTime.getMonth()}/{matchTime.getFullYear()}
              {' - '}
              {matchTime.getHours()}:{matchTime.getMinutes()}:{matchTime.getSeconds()}
            </div>

            <div style={style}>{`Match ID: ${item?.data?.match_id}`}</div>
            <div style={style}>{`Winner ID: ${item?.data?.winner}`}</div>

            <div style={{ display: 'flex', gap: '20px', border: '1px solid black' }}>
              <span style={item?.data?.winner == item?.data?.uid_1 ? style_winner : style}>
                Player 1: {item?.data?.uid_1}
              </span>
              <div>
                {item?.data?.game_board_1.map((row: any, index: number) => {
                  return (
                    <div className='row' key={index}>
                      {row.map((column: number, index: number) => {
                        return (
                          <Square
                            board={item?.data?.game_board_1}
                            history={item?.data?.history_1 || {}}
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
              <span style={item?.data?.winner == item?.data?.uid_2 ? style_winner : style}>
                Player 2: {item?.data?.uid_2}
              </span>
              <div>
                {item?.data?.game_board_2.map((row: any, index: number) => {
                  return (
                    <div className='row' key={index}>
                      {row.map((column: number, index: number) => {
                        return (
                          <Square
                            board={item?.data?.game_board_2}
                            history={item?.data?.history_2 || {}}
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
            </div>
          </div>
        );
      })}
    </>
  );
};

export default History;
