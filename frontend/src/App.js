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
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">RAG Chatbot</h1>
                <p className="text-sm text-gray-500">Ask questions about your documents</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleLoadDocuments}
                className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors duration-200"
              >
                Reload Docs
              </button>
              <button
                onClick={clearChat}
                className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors duration-200"
              >
                Clear Chat
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

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat History */}
      <ChatHistory 
        messages={messages} 
        isTyping={isLoading}
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
