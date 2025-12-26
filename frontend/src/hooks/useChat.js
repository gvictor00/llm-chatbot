import { useState, useCallback, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [documentsLoaded, setDocumentsLoaded] = useState(null);
  const [error, setError] = useState(null);
  const initializationRef = useRef(false);

  const checkConnection = useCallback(async () => {
    try {
      const response = await chatAPI.checkHealth();
      console.log('Health check response:', response);
      setIsConnected(true);
      setError(null);
      return true;
    } catch (err) {
      console.error('Health check failed:', err);
      setIsConnected(false);
      setError('Failed to connect to backend');
      return false;
    }
  }, []);

  const loadDocuments = useCallback(async () => {
    try {
      console.log('Loading documents...');
      const response = await chatAPI.loadDocuments();
      console.log('Documents loaded:', response);
      setDocumentsLoaded(response.document_count);
      return response;
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to load documents');
      throw err;
    }
  }, []);

  const sendMessage = useCallback(async (messageText, options = {}) => {
    if (!messageText.trim()) return;

    const userMessage = {
      content: messageText,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      console.log('Sending message:', messageText);
      const response = await chatAPI.sendMessage(messageText, options);
      console.log('Received response:', response);
      
      const botMessage = {
        content: response.response || 'I apologize, but I received an empty response.',
        isUser: false,
        timestamp: new Date().toISOString(),
        metadata: response.metadata,
        contextUsed: response.context_used || [],
        success: response.success,
        isError: !response.success,
      };

      setMessages(prev => [...prev, botMessage]);

      if (!response.success) {
        if (response.error_message) {
          setError(`Response error: ${response.error_message}`);
        }
      } else {
    setError(null);
      }

      return response;
      } catch (err) {
      console.error('Error sending message:', err);

      const errorMessage = {
        content: `Sorry, I encountered an error while processing your message: ${err.response?.data?.detail || err.message || 'Unknown error'}`,
        isUser: false,
        timestamp: new Date().toISOString(),
        isError: true,
        contextUsed: [],
      };

      setMessages(prev => [...prev, errorMessage]);
      setError(err.response?.data?.detail || err.message || 'An error occurred while sending the message');
      throw err;
    } finally {
      setIsLoading(false);
      }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  useEffect(() => {
    const initialize = async () => {
      if (initializationRef.current) return;
      initializationRef.current = true;

      console.log('Initializing chat...');
      const connected = await checkConnection();

      if (connected) {
        try {
          await loadDocuments();
        } catch (err) {
          console.warn('Could not load documents on initialization:', err);
        }
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
