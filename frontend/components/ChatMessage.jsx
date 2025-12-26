import React from 'react';

const ChatMessage = ({ message, isUser, timestamp, isTyping = false }) => {
  if (isTyping) {
    return (
      <div className="flex justify-start mb-4">
        <div className="message-bubble bot-message">
          <div className="typing-indicator">
            <div className="typing-dot" style={{ animationDelay: '0ms' }}></div>
            <div className="typing-dot" style={{ animationDelay: '150ms' }}></div>
            <div className="typing-dot" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`message-bubble ${isUser ? 'user-message' : 'bot-message'}`}>
        <p className="text-sm leading-relaxed">{message}</p>
        {timestamp && (
          <p className={`text-xs mt-1 opacity-70 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
            {new Date(timestamp).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
