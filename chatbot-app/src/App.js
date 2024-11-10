// src/App.js
import React from 'react';
import Chatbot from './Chatbot';
import './App.css'; // Optional CSS for styling

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot</h1>
        <h3>Type Hi to Start the conversation</h3>
        <Chatbot />
      </header>
    </div>
  );
}

export default App;