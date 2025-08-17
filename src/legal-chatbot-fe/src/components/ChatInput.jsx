import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Square } from 'lucide-react';

const ChatInput = ({ onSendMessage, isProcessing = false, isMobile = false }) => {
  const [message, setMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const maxHeight = isMobile ? 120 : 150;
      const scrollHeight = Math.min(textareaRef.current.scrollHeight, maxHeight);
      textareaRef.current.style.height = `${scrollHeight}px`;
    }
  }, [message, isMobile]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'vi-VN';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setMessage(prev => prev + ' ' + transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isProcessing) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (isMobile || e.shiftKey) {
        // On mobile or with Shift, allow new line
        return;
      } else {
        // On desktop without Shift, send message
        e.preventDefault();
        handleSubmit(e);
      }
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  return (
    <div style={{
      backgroundColor: '#1e293b',
      borderTop: '1px solid #334155',
      padding: isMobile ? '12px' : '16px 24px',
      boxShadow: '0 -2px 8px rgba(0,0,0,0.3)'
    }}>
      <form onSubmit={handleSubmit}>
        <div style={{
          display: 'flex',
          gap: isMobile ? '8px' : '12px',
          alignItems: 'flex-end',
          maxWidth: isMobile ? '100%' : '1000px',
          margin: '0 auto'
        }}>
          {/* Voice input button - Mobile responsive */}
          {recognitionRef.current && (
            <button
              type="button"
              onClick={toggleListening}
              disabled={isProcessing}
              style={{
                padding: isMobile ? '10px' : '12px',
                backgroundColor: isListening ? '#ef4444' : '#374151',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                cursor: isProcessing ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                opacity: isProcessing ? 0.6 : 1,
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                if (!isProcessing && !isMobile) {
                  e.target.style.backgroundColor = isListening ? '#dc2626' : '#4b5563';
                }
              }}
              onMouseLeave={(e) => {
                if (!isProcessing && !isMobile) {
                  e.target.style.backgroundColor = isListening ? '#ef4444' : '#374151';
                }
              }}
            >
              {isListening ? <Square size={isMobile ? 16 : 18} /> : <Mic size={isMobile ? 16 : 18} />}
            </button>
          )}

          {/* Text input - Mobile responsive */}
          <div style={{
            flex: 1,
            position: 'relative',
            backgroundColor: '#0f172a',
            borderRadius: '12px',
            border: '1px solid #334155',
            overflow: 'hidden'
          }}>
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isMobile ? "Nhập câu hỏi..." : "Nhập câu hỏi pháp luật của bạn..."}
              disabled={isProcessing}
              style={{
                width: '100%',
                minHeight: isMobile ? '44px' : '50px',
                maxHeight: isMobile ? '120px' : '150px',
                padding: isMobile ? '12px 16px' : '16px 20px',
                backgroundColor: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#f1f5f9',
                fontSize: isMobile ? '14px' : '16px',
                fontFamily: 'inherit',
                lineHeight: '1.5',
                resize: 'none',
                overflow: 'auto',
                scrollbarWidth: 'thin',
                scrollbarColor: '#475569 transparent'
              }}
              rows={1}
            />
            
            {/* Character counter for mobile */}
            {isMobile && message.length > 100 && (
              <div style={{
                position: 'absolute',
                bottom: '4px',
                right: '8px',
                fontSize: '10px',
                color: '#64748b',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                padding: '2px 6px',
                borderRadius: '4px'
              }}>
                {message.length}
              </div>
            )}
          </div>

          {/* Send button - Mobile responsive */}
          <button
            type="submit"
            disabled={!message.trim() || isProcessing}
            style={{
              padding: isMobile ? '10px' : '12px',
              backgroundColor: (!message.trim() || isProcessing) 
                ? '#374151' 
                : 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
              background: (!message.trim() || isProcessing) 
                ? '#374151' 
                : 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              cursor: (!message.trim() || isProcessing) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              opacity: (!message.trim() || isProcessing) ? 0.6 : 1,
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: (!message.trim() || isProcessing) 
                ? 'none' 
                : '0 4px 12px rgba(139, 92, 246, 0.3)'
            }}
            onMouseEnter={(e) => {
              if (message.trim() && !isProcessing && !isMobile) {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 6px 20px rgba(139, 92, 246, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (message.trim() && !isProcessing && !isMobile) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 12px rgba(139, 92, 246, 0.3)';
              }
            }}
          >
            <Send size={isMobile ? 16 : 18} />
          </button>
        </div>

        {/* Mobile helper text */}
        {isMobile && (
          <p style={{
            fontSize: '12px',
            color: '#64748b',
            margin: '8px 0 0 0',
            textAlign: 'center',
            lineHeight: '1.4'
          }}>
            {isListening 
              ? '🎤 Đang nghe... Nói câu hỏi của bạn' 
              : 'Nhấn Enter để xuống dòng, nhấn Send để gửi'}
          </p>
        )}
      </form>
    </div>
  );
};

export default ChatInput;