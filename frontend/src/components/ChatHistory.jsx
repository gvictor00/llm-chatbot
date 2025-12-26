import React, { useEffect, useRef, useState, useCallback } from 'react';
import ChatMessage from './ChatMessage';

const ChatHistory = ({ messages, isTyping, error }) => {
  const messagesEndRef = useRef(null);
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true);
  const chatContainerRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    if (isAutoScrollEnabled) {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [isAutoScrollEnabled]);
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, scrollToBottom]);

  const handleScroll = () => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop <= clientHeight + 100;
      setIsAutoScrollEnabled(isAtBottom);
    }
};

  if (messages.length === 0 && !isTyping) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Welcome to RAG Chatbot</h3>
          <p className="text-gray-600 mb-4">
            I can help you find information from your documents. Ask me anything!
          </p>
          <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800">
            <p className="font-medium mb-2">💡 Try asking:</p>
            <ul className="text-left space-y-1">
              <li>• "What are the main topics in the documents?"</li>
              <li>• "Summarize the key points about contracts"</li>
              <li>• "What information do you have about bankruptcy?"</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col relative">
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 chat-history"
        onScroll={handleScroll}
      >
        <div className="max-w-4xl mx-auto">
          {messages.map((msg, index) => (
            <ChatMessage
              key={`${index}-${msg.timestamp}`}
              message={msg.content}
              isUser={msg.isUser}
              timestamp={msg.timestamp}
              metadata={msg.metadata}
              contextUsed={msg.contextUsed}
              isError={msg.isError}
            />
          ))}
          {isTyping && <ChatMessage isTyping={true} />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {!isAutoScrollEnabled && (
        <div className="absolute bottom-20 right-8">
          <button
            onClick={() => {
              setIsAutoScrollEnabled(true);
              scrollToBottom();
            }}
            className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full shadow-lg transition-colors duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border-t border-red-200 p-3">
          <div className="max-w-4xl mx-auto flex items-center">
            <svg className="w-4 h-4 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-red-700">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
