import React from 'react';
import ChatHistory from './components/ChatHistory';
import ChatInput from './components/ChatInput';
import StatusBar from './components/StatusBar';
import { useChat } from './hooks/useChat';
import './App.css';

function App() {
  const {
    messages,
    isLoading,
    isConnected,
    documentsLoaded,
    error,
    sendMessage,
    clearChat,
    loadDocuments,
  } = useChat();

  const handleSendMessage = async (message) => {
    try {
      await sendMessage(message, {
        model: 'gpt-4o',
        agentName: 'llm-chatbot-ui',
        maxTokens: 1000,
        temperature: 0.7,
        topK: 3,
      });
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleLoadDocuments = async () => {
    try {
      await loadDocuments();
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  return (
    <div className="App h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-sm">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">RAG Chatbot</h1>
                <p className="text-sm text-gray-500">Intelligent document-based conversations</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handleLoadDocuments}
                disabled={isLoading}
                className="px-4 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Reload Docs</span>
              </button>
              <button
                onClick={clearChat}
                disabled={isLoading}
                className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Clear Chat</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Status Bar */}
      <StatusBar 
        isConnected={isConnected}
        documentsLoaded={documentsLoaded}
        isLoading={isLoading}
      />

      {/* Chat History with Error Handling */}
      <ChatHistory 
        messages={messages} 
        isTyping={isLoading}
        error={error}
      />

      {/* Chat Input */}
      <ChatInput 
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={!isConnected}
      />
    </div>
  );
}

export default App;
