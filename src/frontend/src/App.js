import React from 'react';
import logo from './logo.svg';
import { Counter } from './features/counter/Counter';
import MainPage from './components/MainPage';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
function App() {
  return (
    <div className="App">
      <MainPage />
    </div>
  );
}

export default App;
