import React from 'react';

const ChatMessage = ({ message, isUser, timestamp, metadata, contextUsed, isError, isTyping = false }) => {
  if (isTyping) {
    return (
      <div className="flex justify-start mb-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </div>
          <div className="message-bubble bot-message">
            <div className="typing-indicator">
              <div className="typing-dot" style={{ animationDelay: '0ms' }}></div>
              <div className="typing-dot" style={{ animationDelay: '150ms' }}></div>
              <div className="typing-dot" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className="flex items-start space-x-3 max-w-4xl">
        {!isUser && (
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              isError ? 'bg-red-100' : 'bg-blue-100'
            }`}>
              {isError ? (
                <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              )}
            </div>
          </div>
        )}

        <div className="flex-1">
          <div className={`message-bubble ${
            isUser
              ? 'user-message'
              : isError
                ? 'error-message'
                : 'bot-message'
          }`}>
            <div className="message-content">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
            </div>

            {/* Metadata for bot responses */}
            {!isUser && metadata && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>
                    {metadata.documents_retrieved} documents • {metadata.model_used}
                  </span>
                  {metadata.query_length && (
                    <span>{metadata.query_length} chars</span>
                  )}
                </div>
              </div>
            )}

            {/* Context sources for bot responses */}
            {!isUser && contextUsed && contextUsed.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <details className="group">
                  <summary className="cursor-pointer text-xs text-gray-500 hover:text-gray-700 flex items-center">
                    <svg className="w-3 h-3 mr-1 transform group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    Sources ({contextUsed.length})
                  </summary>
                  <div className="mt-2 space-y-2">
                    {contextUsed.map((context, index) => (
                      <div key={index} className="bg-gray-50 rounded p-2 text-xs">
                        <div className="font-medium text-gray-700 mb-1">
                          📄 {context.file_name}
                          <span className="ml-2 text-gray-500">
                            (similarity: {(context.similarity_score * 100).toFixed(1)}%)
                          </span>
                        </div>
                        <div className="text-gray-600 italic">
                          "{context.content_preview}"
                        </div>
                      </div>
                    ))}
                  </div>
                </details>
              </div>
            )}
          </div>

          {/* Timestamp */}
          {timestamp && (
            <div className={`text-xs mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
              <span className="text-gray-400">
                {new Date(timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          )}
        </div>

        {isUser && (
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
