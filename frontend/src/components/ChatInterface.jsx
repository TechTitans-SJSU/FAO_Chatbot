import React, { useState, useRef, useEffect } from 'react';

const ChatMessage = ({ text, sender }) => (
  <div className={`flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
    <div
      className={`max-w-[80%] p-3 rounded-lg ${
        sender === 'user' 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-100 text-gray-900'
      }`}
    >
      {text}
    </div>
  </div>
);

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    try {
      setIsLoading(true);
      setMessages(prev => [...prev, { text: input, sender: 'user' }]);
      
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input }),
      });

      const data = await response.json();
      setMessages(prev => [...prev, { text: data.answer, sender: 'bot' }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        text: 'Sorry, there was an error processing your message.', 
        sender: 'bot' 
      }]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  return (
    <div className="container mx-auto max-w-3xl h-screen py-4">
      <div className="flex flex-col h-full space-y-4">
        <div
          className="flex-1 w-full overflow-y-auto border border-gray-200 rounded-lg p-4"
        >
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              text={message.text}
              sender={message.sender}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className={`px-6 py-2 rounded-lg text-white ${
              isLoading 
                ? 'bg-blue-300 cursor-not-allowed' 
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;