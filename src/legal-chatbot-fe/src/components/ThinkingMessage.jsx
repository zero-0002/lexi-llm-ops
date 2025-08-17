import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, ChevronDown, ChevronRight, Brain, Eye, EyeOff } from 'lucide-react';

const ThinkingMessage = ({ 
  thinkingProcess, 
  finalAnswer, 
  timestamp, 
  isStreaming = false 
}) => {
  const [showThinking, setShowThinking] = useState(false);
  
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return '';
    }
  };

  return (
    <div style={{
      display: 'flex',
      gap: '16px',
      padding: '20px 16px',
      maxWidth: '100%'
    }}>
      {/* Avatar */}
      <div style={{
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        backgroundColor: '#8b5cf6',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        flexShrink: 0,
        boxShadow: '0 4px 8px rgba(139, 92, 246, 0.3)',
        border: '2px solid rgba(255,255,255,0.1)',
        position: 'relative'
      }}>
        <Bot size={20} />
        
        {/* Streaming indicator */}
        {isStreaming && (
          <div style={{
            position: 'absolute',
            bottom: '-2px',
            right: '-2px',
            width: '12px',
            height: '12px',
            backgroundColor: '#10b981',
            borderRadius: '50%',
            border: '2px solid #1e293b',
            animation: 'pulse 1.5s infinite'
          }}>
            <Brain size={8} style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              animation: 'spin 1s linear infinite'
            }} />
          </div>
        )}
      </div>

      {/* Message content */}
      <div style={{ 
        maxWidth: '75%', 
        minWidth: 0,
        width: '100%'
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '12px'
        }}>
          <span style={{ 
            fontSize: '14px', 
            fontWeight: '600', 
            color: '#a855f7'
          }}>
            AI Assistant
          </span>
          
          {isStreaming && (
            <span style={{
              fontSize: '12px',
              color: '#10b981',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <div style={{
                width: '6px',
                height: '6px',
                backgroundColor: '#10b981',
                borderRadius: '50%',
                animation: 'pulse 1s infinite'
              }}></div>
              Đang suy nghĩ...
            </span>
          )}
          
          {timestamp && !isStreaming && (
            <span style={{ 
              fontSize: '12px', 
              color: '#64748b',
              opacity: 0.8
            }}>
              {formatTime(timestamp)}
            </span>
          )}
        </div>

        {/* Thinking Process Toggle Button */}
        {thinkingProcess && (
          <button
            onClick={() => setShowThinking(!showThinking)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: 'rgba(139, 92, 246, 0.1)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '8px',
              color: '#c4b5fd',
              fontSize: '13px',
              fontWeight: '500',
              cursor: 'pointer',
              marginBottom: '12px',
              transition: 'all 0.2s ease',
              width: 'fit-content'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'rgba(139, 92, 246, 0.2)';
              e.target.style.borderColor = 'rgba(139, 92, 246, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'rgba(139, 92, 246, 0.1)';
              e.target.style.borderColor = 'rgba(139, 92, 246, 0.3)';
            }}
          >
            {showThinking ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <Brain size={14} />
            <span>{showThinking ? 'Ẩn' : 'Xem'} quá trình suy nghĩ</span>
            {showThinking ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        )}

        {/* Thinking Process - Collapsible */}
        {showThinking && thinkingProcess && (
          <div style={{
            marginBottom: '16px',
            padding: '16px',
            backgroundColor: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '12px',
            fontSize: '13px',
            lineHeight: '1.6',
            maxHeight: '400px',
            overflowY: 'auto',
            animation: 'slideDown 0.3s ease-out'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '12px',
              paddingBottom: '8px',
              borderBottom: '1px solid #334155'
            }}>
              <Brain size={16} style={{ color: '#8b5cf6' }} />
              <span style={{ 
                color: '#8b5cf6', 
                fontWeight: '600',
                fontSize: '14px'
              }}>
                Quá trình tư duy AI
              </span>
            </div>
            
            <div className="thinking-content" style={{ color: '#94a3b8' }}>
              <ReactMarkdown
                components={{
                  p: ({ children }) => (
                    <p style={{ 
                      margin: '0 0 12px 0', 
                      lineHeight: '1.6',
                      fontSize: '13px'
                    }}>
                      {children}
                    </p>
                  ),
                  strong: ({ children }) => (
                    <strong style={{ color: '#e5e7eb', fontWeight: '600' }}>
                      {children}
                    </strong>
                  ),
                  code: ({ children, inline }) => (
                    <code style={{
                      backgroundColor: 'rgba(139, 92, 246, 0.2)',
                      color: '#c4b5fd',
                      padding: inline ? '2px 6px' : '0',
                      borderRadius: '4px',
                      fontSize: '12px'
                    }}>
                      {children}
                    </code>
                  )
                }}
              >
                {thinkingProcess}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Final Answer - Main display */}
        <div style={{
          padding: '16px 20px',
          borderRadius: '16px',
          backgroundColor: '#1e293b',
          color: '#e5e7eb',
          border: '1px solid #334155',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          wordWrap: 'break-word',
          overflowWrap: 'break-word',
          position: 'relative',
          minHeight: isStreaming ? '60px' : 'auto'
        }}>
          {/* Message tail */}
          <div style={{
            position: 'absolute',
            width: 0,
            height: 0,
            left: '-8px',
            top: '16px',
            borderTop: '8px solid transparent',
            borderBottom: '8px solid transparent',
            borderRight: '8px solid #1e293b'
          }}></div>

          {/* Final Answer Content */}
          <div className="markdown-content">
            {/* Streaming cursor for final answer */}
            {isStreaming && !finalAnswer && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#94a3b8',
                fontSize: '14px'
              }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #8b5cf6',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Đang tạo câu trả lời...
              </div>
            )}
            
            {(finalAnswer || isStreaming) && (
              <ReactMarkdown
                components={{
                  p: ({ children }) => (
                    <p style={{ 
                      margin: '0 0 16px 0', 
                      lineHeight: '1.7',
                      fontSize: '15px',
                      color: '#e5e7eb'
                    }}>
                      {children}
                    </p>
                  ),
                  h1: ({ children }) => (
                    <h1 style={{ 
                      fontSize: '18px', 
                      fontWeight: 'bold', 
                      margin: '16px 0 12px 0',
                      color: '#f1f5f9',
                      borderBottom: '2px solid #8b5cf6',
                      paddingBottom: '8px'
                    }}>
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 style={{ 
                      fontSize: '16px', 
                      fontWeight: 'bold', 
                      margin: '14px 0 10px 0',
                      color: '#f1f5f9',
                      borderLeft: '4px solid #3b82f6',
                      paddingLeft: '12px'
                    }}>
                      {children}
                    </h2>
                  ),
                  ul: ({ children }) => (
                    <ul style={{ 
                      margin: '12px 0', 
                      paddingLeft: '20px',
                      color: '#e5e7eb'
                    }}>
                      {children}
                    </ul>
                  ),
                  li: ({ children }) => (
                    <li style={{ 
                      marginBottom: '8px',
                      lineHeight: '1.6'
                    }}>
                      {children}
                    </li>
                  ),
                  strong: ({ children }) => (
                    <strong style={{ 
                      color: '#f1f5f9', 
                      fontWeight: '600'
                    }}>
                      {children}
                    </strong>
                  ),
                  code: ({ children, inline }) => (
                    <code style={{
                      backgroundColor: inline ? 'rgba(139, 92, 246, 0.2)' : '#0f172a',
                      color: inline ? '#c4b5fd' : '#e2e8f0',
                      padding: inline ? '3px 8px' : '16px',
                      borderRadius: inline ? '6px' : '8px',
                      fontSize: '13px',
                      fontFamily: 'Monaco, Consolas, "Courier New", monospace',
                      border: inline ? '1px solid rgba(139, 92, 246, 0.3)' : '1px solid #334155',
                      display: inline ? 'inline' : 'block',
                      margin: inline ? '0' : '16px 0'
                    }}>
                      {children}
                    </code>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote style={{
                      borderLeft: '4px solid #8b5cf6',
                      paddingLeft: '16px',
                      margin: '16px 0',
                      color: '#94a3b8',
                      backgroundColor: 'rgba(139, 92, 246, 0.1)',
                      padding: '12px 16px',
                      borderRadius: '0 8px 8px 0'
                    }}>
                      {children}
                    </blockquote>
                  )
                }}
              >
                {finalAnswer || ''}
              </ReactMarkdown>
            )}
            
            {/* Streaming cursor */}
            {isStreaming && finalAnswer && (
              <span style={{
                display: 'inline-block',
                width: '2px',
                height: '20px',
                backgroundColor: '#10b981',
                marginLeft: '2px',
                animation: 'blink 1s infinite',
                verticalAlign: 'text-bottom'
              }}></span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThinkingMessage;