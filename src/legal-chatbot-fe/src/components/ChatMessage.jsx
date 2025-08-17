import React from 'react';
import AnalysisMessage from './AnalysisMessage';

const ChatMessage = ({ message, isUser }) => {
  // 🔧 VALIDATION - Kiểm tra message tồn tại
  if (!message) {
    console.warn('ChatMessage: message is undefined or null');
    return null;
  }

  // 🔧 VALIDATION - Kiểm tra message có role
  if (typeof message !== 'object' || !message.role) {
    console.warn('ChatMessage: message does not have role property', message);
    return null;
  }

  // Handle analysis message type
  if (message.role === 'analysis') {
    return (
      <div style={{ marginBottom: '16px' }}>
        <AnalysisMessage 
          analysis={message.analysis}
          actions={message.actions}
          finalAnswer={message.finalAnswer}
        />
      </div>
    );
  }

  // Handle user/assistant messages
  const isUserMessage = message.role === 'user' || isUser;

  return (
    <div style={{
      display: 'flex',
      justifyContent: isUserMessage ? 'flex-end' : 'flex-start',
      marginBottom: '16px',
      alignItems: 'flex-end',
      gap: '8px'
    }}>
      {/* Avatar cho assistant */}
      {!isUserMessage && (
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: '#374151',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          color: '#10b981',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          🤖
        </div>
      )}

      {/* Message content */}
      <div style={{
        maxWidth: '70%',
        padding: '12px 16px',
        borderRadius: '12px',
        backgroundColor: isUserMessage ? '#3b82f6' : '#374151',
        color: 'white',
        fontSize: '14px',
        lineHeight: '1.6', // 🔧 Tăng line-height cho dễ đọc
        wordWrap: 'break-word',
        wordBreak: 'break-word',
        whiteSpace: 'pre-wrap', // 🔧 QUAN TRỌNG: Giữ nguyên xuống dòng và spaces
        overflowWrap: 'break-word' // 🔧 Wrap từ dài
      }}>
        {/* 🔧 SAFE TEXT RENDERING với xử lý xuống dòng */}
        {(message.text || message.content || 'Message không có nội dung')}
        
        {/* 🔧 STREAMING INDICATOR */}
        {message.isStreaming && (
          <span style={{
            display: 'inline-block',
            width: '8px',
            height: '8px',
            backgroundColor: '#10b981',
            borderRadius: '50%',
            marginLeft: '8px',
            animation: 'pulse 1.5s infinite'
          }} />
        )}
      </div>

      {/* Avatar cho user */}
      {isUserMessage && (
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: '#3b82f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          color: 'white',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          👤
        </div>
      )}
    </div>
  );
};

export default ChatMessage;