import React, { useEffect, useRef, useState } from 'react';
import ConversationSidebar from './components/ConversationSidebar';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { useChat } from './hooks/useChat';
import { MessageSquare, AlertCircle, Zap, Search, Brain, FileText, Send, Menu, X } from 'lucide-react';
import { useToast } from './components/Toast';

function App() {
  const {
    conversations,
    currentConversationId,
    messages,
    isProcessing,
    isLoading,
    error,
    processingStep,
    fetchConversations,
    loadConversation,
    createNewConversation,
    deleteConversation,
    updateConversationTitle,
    sendMessage
  } = useChat();

  const { ToastContainer } = useToast();

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  
  // 🆕 Mobile responsive state
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // 🆕 Check screen size
  useEffect(() => {
    const checkScreenSize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) {
        setSidebarOpen(false); // Close sidebar on desktop
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  // 🆕 Scroll to top when conversation changes
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = 0;
    }
  }, [currentConversationId]);

  // Get processing icon based on step
  const getProcessingIcon = (step) => {
    if (step.includes('phân tích')) return <Brain size={16} />;
    if (step.includes('tìm kiếm')) return <Search size={16} />;
    if (step.includes('tạo')) return <FileText size={16} />;
    return <Zap size={16} />;
  };

  // Example questions for quick start
  const exampleQuestions = [
    "Quyền lợi của người lao động khi bị sa thải?",
    "Điều kiện mua bán nhà đất mới nhất?",
    "Thủ tục khởi kiện dân sự như thế nào?",
    "Quy định về hợp đồng lao động 2024?"
  ];

  // Handle example question click
  const handleExampleClick = (question) => {
    if (!isProcessing) {
      sendMessage(question);
      if (isMobile) {
        setSidebarOpen(false); // Close sidebar after sending message on mobile
      }
    }
  };

  // 🆕 Handle conversation selection on mobile
  const handleSelectConversation = (conversationId) => {
    loadConversation(conversationId);
    if (isMobile) {
      setSidebarOpen(false); // Close sidebar after selection
    }
  };

  // 🆕 Handle new conversation on mobile
  const handleCreateNewConversation = () => {
    createNewConversation();
    if (isMobile) {
      setSidebarOpen(false); // Close sidebar after creation
    }
  };

  // 🆕 Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl/Cmd + N: New conversation
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        createNewConversation();
      }
      
      // Escape: Close sidebar on mobile
      if (e.key === 'Escape' && isMobile && sidebarOpen) {
        setSidebarOpen(false);
      }
      
      // Ctrl/Cmd + K: Focus search (future feature)
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focus search input if available
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [createNewConversation, isMobile, sidebarOpen]);

  return (
    <div style={{ 
      display: 'flex', 
      height: '100vh', 
      width: '100vw',
      backgroundColor: '#0f172a',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
      overflow: 'hidden',
      position: 'relative'
    }}>
      {/* 🆕 Mobile Overlay */}
      {isMobile && sidebarOpen && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 998,
            backdropFilter: 'blur(4px)'
          }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Responsive */}
      <div style={{
        position: isMobile ? 'fixed' : 'relative',
        left: isMobile ? (sidebarOpen ? '0' : '-100%') : '0',
        top: 0,
        height: '100%',
        width: isMobile ? '280px' : '320px',
        zIndex: 999,
        transition: isMobile ? 'left 0.3s ease-in-out' : 'none',
        transform: isMobile ? 'translateZ(0)' : 'none' // Hardware acceleration
      }}>
        <ConversationSidebar
          conversations={conversations}
          selectedConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onCreateNewConversation={handleCreateNewConversation}
          onDeleteConversation={deleteConversation}
          onRefreshConversations={fetchConversations}
          onUpdateTitle={updateConversationTitle}
          isLoading={isLoading}
          isMobile={isMobile}
          onCloseSidebar={() => setSidebarOpen(false)}
        />
      </div>

      {/* Main chat area */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        minWidth: 0,
        width: isMobile ? '100%' : 'auto'
      }}>
        {/* Header - Mobile responsive */}
        <div style={{
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
          padding: isMobile ? '12px 16px' : '16px 24px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
          position: 'relative'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* 🆕 Mobile menu button */}
            {isMobile && (
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                style={{
                  padding: '8px',
                  backgroundColor: 'transparent',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#94a3b8',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Menu size={20} />
              </button>
            )}

            <div style={{
              width: isMobile ? '32px' : '40px',
              height: isMobile ? '32px' : '40px',
              background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
              position: 'relative',
              flexShrink: 0
            }}>
              <MessageSquare size={isMobile ? 16 : 20} />
              
              {/* Processing indicator */}
              {isProcessing && (
                <div style={{
                  position: 'absolute',
                  bottom: '-2px',
                  right: '-2px',
                  width: isMobile ? '10px' : '12px',
                  height: isMobile ? '10px' : '12px',
                  backgroundColor: '#10b981',
                  borderRadius: '50%',
                  border: '2px solid #1e293b',
                  animation: 'pulse 1.5s infinite'
                }}>
                  <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    animation: 'spin 1s linear infinite'
                  }}>
                    {getProcessingIcon(processingStep)}
                  </div>
                </div>
              )}
            </div>
            
            <div style={{ flex: 1, minWidth: 0 }}>
              <h1 style={{ 
                fontSize: isMobile ? '16px' : '20px', 
                fontWeight: '600', 
                color: '#f1f5f9', 
                margin: 0,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                flexWrap: 'wrap'
              }}>
                🤖 Legal AI Assistant
                {isProcessing && processingStep && (
                  <span style={{
                    fontSize: isMobile ? '10px' : '12px',
                    color: '#10b981',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    whiteSpace: 'nowrap'
                  }}>
                    <div style={{
                      width: '6px',
                      height: '6px',
                      backgroundColor: '#10b981',
                      borderRadius: '50%',
                      animation: 'pulse 1s infinite'
                    }}></div>
                    {isMobile ? 'Đang xử lý...' : processingStep}
                  </span>
                )}
              </h1>
              <p style={{ 
                fontSize: isMobile ? '12px' : '14px', 
                color: '#94a3b8', 
                margin: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                {currentConversationId 
                  ? `Conversation: ${currentConversationId.substring(0, 8)}...` 
                  : 'Hỗ trợ tư vấn pháp luật Việt Nam với AI'}
              </p>
            </div>
          </div>
        </div>

        {/* Messages area - Responsive */}
        <div 
          ref={chatContainerRef}
          style={{ 
            flex: 1, 
            overflowY: 'auto',
            backgroundColor: '#0f172a',
            backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.05) 1px, transparent 0)',
            backgroundSize: '20px 20px',
            WebkitOverflowScrolling: 'touch' // Smooth scrolling on iOS
          }}
        >
          <div style={{ 
            maxWidth: isMobile ? '100%' : '1000px', 
            margin: '0 auto', 
            padding: isMobile ? '8px' : '16px', 
            minHeight: '100%' 
          }}>
            {/* Error message */}
            {error && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 16px',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                color: '#fca5a5',
                borderRadius: '8px',
                marginBottom: '16px',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                fontSize: isMobile ? '14px' : '16px'
              }}>
                <AlertCircle size={16} />
                <span style={{ fontSize: '14px' }}>{error}</span>
              </div>
            )}

            {/* Welcome message - Mobile responsive */}

            {messages.length === 0 && !isProcessing && !error && (
              <div style={{ 
                textAlign: 'center', 
                padding: isMobile ? '32px 16px' : '64px 16px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: isMobile ? 'calc(100vh - 150px)' : 'calc(100vh - 200px)'
              }}>
                <div style={{
                  width: isMobile ? '60px' : '80px',
                  height: isMobile ? '60px' : '80px',
                  background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  margin: '0 auto 24px',
                  boxShadow: '0 8px 32px rgba(139, 92, 246, 0.3)',
                  animation: 'pulse 2s infinite'
                }}>
                  <MessageSquare size={isMobile ? 30 : 40} />
                </div>
                <h2 style={{ 
                  fontSize: isMobile ? '24px' : '32px', 
                  fontWeight: '700', 
                  color: '#f1f5f9', 
                  marginBottom: '12px',
                  background: 'linear-gradient(135deg, #f1f5f9, #cbd5e1)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textAlign: 'center'
                }}>
                  Chào mừng đến với Legal AI!
                </h2>
                <p style={{ 
                  color: '#94a3b8', 
                  marginBottom: '32px', 
                  maxWidth: isMobile ? '100%' : '600px', 
                  margin: '0 auto 32px',
                  lineHeight: '1.6',
                  fontSize: isMobile ? '14px' : '16px',
                  textAlign: 'center'
                }}>
                  Tôi có thể giúp bạn tư vấn các vấn đề pháp luật Việt Nam với pipeline AI hoàn chỉnh.
                </p>
                
                {/* Info card - Mobile responsive */}
                <div style={{
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '12px',
                  padding: isMobile ? '16px' : '24px',
                  maxWidth: isMobile ? '100%' : '600px',
                  margin: '0 auto 32px',
                  textAlign: 'left',
                  backdropFilter: 'blur(10px)'
                }}>
                  <p style={{ 
                    fontSize: isMobile ? '13px' : '15px', 
                    color: '#93c5fd', 
                    margin: '0 0 16px 0',
                    lineHeight: '1.6'
                  }}>
                    <strong style={{ color: '#dbeafe' }}>🚀 Pipeline AI hoàn chỉnh:</strong><br/>
                    💬 Phân tích truy vấn → 🌐 Tìm kiếm web → 📝 Tổng hợp kết quả
                  </p>
                </div>

                {/* Clickable example questions - Mobile responsive */}
                <div style={{
                  backgroundColor: 'rgba(139, 92, 246, 0.1)',
                  border: '1px solid rgba(139, 92, 246, 0.3)',
                  borderRadius: '12px',
                  padding: isMobile ? '16px' : '24px',
                  maxWidth: isMobile ? '100%' : '700px',
                  margin: '0 auto',
                  textAlign: 'left',
                  backdropFilter: 'blur(10px)'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '16px',
                    color: '#c4b5fd'
                  }}>
                    <MessageSquare size={16} />
                    <strong style={{ fontSize: isMobile ? '14px' : '15px' }}>Thử các câu hỏi mẫu:</strong>
                  </div>
                  
                  <div style={{ 
                    display: 'grid', 
                    gap: isMobile ? '8px' : '12px' 
                  }}>
                    {exampleQuestions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => handleExampleClick(question)}
                        disabled={isProcessing}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          gap: '12px',
                          padding: isMobile ? '10px 14px' : '12px 16px',
                          backgroundColor: isProcessing 
                            ? 'rgba(139, 92, 246, 0.1)' 
                            : 'rgba(139, 92, 246, 0.2)',
                          border: '1px solid rgba(139, 92, 246, 0.4)',
                          borderRadius: '8px',
                          color: isProcessing ? '#94a3b8' : '#e5e7eb',
                          fontSize: isMobile ? '13px' : '14px',
                          fontWeight: '500',
                          cursor: isProcessing ? 'not-allowed' : 'pointer',
                          transition: 'all 0.2s ease',
                          textAlign: 'left',
                          opacity: isProcessing ? 0.6 : 1,
                          width: '100%'
                        }}
                        onMouseEnter={(e) => {
                          if (!isProcessing && !isMobile) {
                            e.target.style.backgroundColor = 'rgba(139, 92, 246, 0.3)';
                            e.target.style.borderColor = 'rgba(139, 92, 246, 0.6)';
                            e.target.style.transform = 'translateY(-1px)';
                            e.target.style.boxShadow = '0 4px 12px rgba(139, 92, 246, 0.2)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!isProcessing && !isMobile) {
                            e.target.style.backgroundColor = 'rgba(139, 92, 246, 0.2)';
                            e.target.style.borderColor = 'rgba(139, 92, 246, 0.4)';
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = 'none';
                          }
                        }}
                      >
                        <span style={{ 
                          flex: 1,
                          lineHeight: '1.4'
                        }}>
                          {question}
                        </span>
                        <Send size={isMobile ? 12 : 14} style={{ 
                          color: isProcessing ? '#64748b' : '#8b5cf6',
                          flexShrink: 0
                        }} />
                      </button>
                    ))}
                  </div>
                  
                  <div style={{
                    marginTop: '16px',
                    padding: '12px',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '8px',
                    border: '1px solid rgba(59, 130, 246, 0.2)'
                  }}>
                    <p style={{
                      fontSize: isMobile ? '12px' : '13px',
                      color: '#93c5fd',
                      margin: 0,
                      lineHeight: '1.4',
                      fontStyle: 'italic'
                    }}>
                      💡 <strong>Mẹo:</strong> Click vào câu hỏi để gửi ngay, hoặc nhập câu hỏi tùy chỉnh của bạn ở phía dưới.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Chat messages */}
            <div style={{ marginBottom: '20px' }}>
              {/* 🔧 SAFE MESSAGE RENDERING */}
              {/* {console.log('Current messages:', messages, messages.length)} */}
              {messages && messages.length > 0 && messages
                .filter(message => message && typeof message === 'object' && message.role) // Filter out invalid messages
                .map((message, index) => (
                  <ChatMessage
                    key={message.id || index}
                    message={message}
                    isUser={message.role === 'user'}
                  />
                ))
              }
            </div>

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        <ChatInput
          onSendMessage={sendMessage}
          isProcessing={isProcessing}
          isMobile={isMobile}
        />
      </div>

      {/* 🆕 Toast Container */}
      <ToastContainer />
    </div>
  );
}

export default App;
