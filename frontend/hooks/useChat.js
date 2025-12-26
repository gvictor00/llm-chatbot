import { useState, useCallback, useEffect } from 'react';
import { chatAPI } from '../../src/services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [documentsLoaded, setDocumentsLoaded] = useState(null);
  const [error, setError] = useState(null);

  // Check connection status
  const checkConnection = useCallback(async () => {
    try {
      await chatAPI.checkHealth();
      setIsConnected(true);
      setError(null);
    } catch (err) {
      setIsConnected(false);
      setError('Failed to connect to backend');
    }
  }, []);

  // Load documents
  const loadDocuments = useCallback(async () => {
    try {
      const response = await chatAPI.loadDocuments();
      setDocumentsLoaded(response.document_count);
      return response;
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to load documents');
      throw err;
    }
  }, []);

  // Send message
  const sendMessage = useCallback(async (messageText, options = {}) => {
    if (!messageText.trim()) return;

    // Add user message to chat
    const userMessage = {
      content: messageText,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatAPI.sendMessage(messageText, options);
      
      // Add bot response to chat
      const botMessage = {
        content: response.response,
        isUser: false,
        timestamp: new Date().toISOString(),
        metadata: response.metadata,
        contextUsed: response.context_used,
        success: response.success,
      };

      setMessages(prev => [...prev, botMessage]);

      if (!response.success && response.error_message) {
        setError(response.error_message);
      }

      return response;
    } catch (err) {
      const errorMessage = {
        content: 'Sorry, I encountered an error while processing your message. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString(),
        isError: true,
      };

      setMessages(prev => [...prev, errorMessage]);
      setError(err.response?.data?.detail || err.message || 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Clear chat
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  // Initialize connection and load documents on mount
  useEffect(() => {
    const initialize = async () => {
      await checkConnection();
      try {
        await loadDocuments();
      } catch (err) {
        console.warn('Could not load documents on initialization:', err);
      }
    };

    initialize();
  }, [checkConnection, loadDocuments]);

  return {
    messages,
    isLoading,
    isConnected,
    documentsLoaded,
    error,
    sendMessage,
    clearChat,
    checkConnection,
    loadDocuments,
  };
};
