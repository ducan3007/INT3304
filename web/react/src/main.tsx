import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import Room from './Room';
import './index.css';

import { createBrowserRouter, RouterProvider, Route } from 'react-router-dom';
import History from './History';

const router = createBrowserRouter([
  {
    path: '/game/history',
    element: <History />
  },
  {
    path: '/:id',
    element: <Room />
  },
  {
    path: '/',
    element: <App />
  }
]);

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
