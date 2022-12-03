import React from 'react';
import { Square } from './Bingo';

const History = (props: any) => {
  console.log('props', props);

  return (
    <>
      {props?.history?.map((item: any, index: number) => {
        const matchTime = new Date(item?.time);
        return (
          <div>
            <div>
              Thời gian: {matchTime.getDate()}/{matchTime.getMonth()}/{matchTime.getFullYear()}
              {' - '}
              {matchTime.getHours()}:{matchTime.getMinutes()}:{matchTime.getSeconds()}
            </div>

            <div>Match ID : {item?.data?.match_id}</div>
            <div>Winner ID : {item?.data?.winner}</div>

            <div style={{ display: 'flex', gap: '20px', border: '1px solid black' }}>
              <div>
                Player 1: {item?.data?.uid_1}
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
              <div>
                Player 2: {item?.data?.uid_2}
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
