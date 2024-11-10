// src/Chatbot.js
import React, { useState } from 'react';
import './Chatbot.css'; // Import the updated CSS for styling

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = () => {
    if (input.trim() === '') return;

    // Add the user's message to the message list
    setMessages([...messages, { role: 'user', text: input }]);

    // Clear the input field
    setInput('');

    // Simulate bot response (you can replace this with an API call)
    setTimeout(() => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'bot', text: 'Hello! How can I assist you?' },
      ]);
    }, 1000);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbox">
        <div className="messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              {message.text}
            </div>
          ))}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Type a message..."
            className="chat-input"
          />
          <button onClick={handleSendMessage} className="send-button">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;