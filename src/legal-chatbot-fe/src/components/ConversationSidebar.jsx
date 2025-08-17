import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Trash2, 
  RefreshCw, 
  Clock,
  Edit3,
  Check,
  X,
  MessageCircle,
  Copy,
  ChevronDown
} from 'lucide-react';

const ConversationSidebar = ({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onCreateNewConversation,
  onDeleteConversation,
  onRefreshConversations,
  onUpdateTitle,
  isLoading = false,
  isMobile = false,
  onCloseSidebar = null
}) => {
  const [editingTitleId, setEditingTitleId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(null);
  const [selectedDropdownIndex, setSelectedDropdownIndex] = useState(0);
  
  const dropdownRefs = useRef({});

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffHours / 24);

      if (diffDays > 0) {
        return `${diffDays} ngày trước`;
      } else if (diffHours > 0) {
        return `${diffHours} giờ trước`;
      } else {
        return 'Vừa xong';
      }
    } catch (error) {
      return '';
    }
  };

  // Toggle dropdown menu
  const toggleDropdown = (e, conversationId) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (dropdownOpen === conversationId) {
      setDropdownOpen(null);
    } else {
      setDropdownOpen(conversationId);
      setSelectedDropdownIndex(0);
    }
  };

  // Handle conversation click
  const handleConversationClick = (conversationId) => {
    if (editingTitleId !== conversationId && dropdownOpen !== conversationId) {
      onSelectConversation(conversationId);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownOpen && dropdownRefs.current[dropdownOpen]) {
        if (!dropdownRefs.current[dropdownOpen].contains(event.target)) {
          setDropdownOpen(null);
        }
      }
    };

    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('scroll', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('scroll', handleClickOutside);
    };
  }, [dropdownOpen]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!dropdownOpen) return;

      switch (e.key) {
        case 'Escape':
          setDropdownOpen(null);
          break;
        case 'ArrowDown':
          e.preventDefault();
          setSelectedDropdownIndex(prev => prev < 3 ? prev + 1 : 0);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedDropdownIndex(prev => prev > 0 ? prev - 1 : 3);
          break;
        case 'Enter':
          e.preventDefault();
          const actions = ['select', 'rename', 'copy', 'delete'];
          handleDropdownAction(actions[selectedDropdownIndex], dropdownOpen);
          break;
      }
    };

    if (dropdownOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [dropdownOpen, selectedDropdownIndex]);

  // Handle title editing
  const handleStartEdit = (conversation) => {
    setEditingTitleId(conversation.conversation_id);
    setEditTitle(conversation.title);
    setDropdownOpen(null);
  };

  const handleSaveTitle = async (conversationId) => {
    if (editTitle.trim() && onUpdateTitle) {
      try {
        await onUpdateTitle(conversationId, editTitle.trim());
        setEditingTitleId(null);
        setEditTitle('');
      } catch (error) {
        console.error('Error updating title:', error);
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingTitleId(null);
    setEditTitle('');
  };

  // Handle dropdown actions
  const handleDropdownAction = async (action, conversationId) => {
    const conversation = conversations.find(c => c.conversation_id === conversationId);
    
    try {
      switch (action) {
        case 'rename':
          handleStartEdit(conversation);
          break;
        case 'delete':
          if (window.confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) {
            await onDeleteConversation(conversationId);
          }
          break;
        case 'copy':
          await navigator.clipboard.writeText(conversationId);
          console.log('Copied conversation ID:', conversationId);
          break;
        case 'select':
          onSelectConversation(conversationId);
          break;
      }
    } catch (error) {
      console.error('Dropdown action error:', error);
    }
    
    setDropdownOpen(null);
  };

  return (
    <div style={{
      width: isMobile ? '280px' : '320px',
      backgroundColor: '#1e293b',
      borderRight: '1px solid #334155',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden',
      position: 'relative'
    }}>
      {/* Header */}
      <div style={{
        padding: isMobile ? '16px' : '20px',
        borderBottom: '1px solid #334155',
        backgroundColor: '#0f172a'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <h2 style={{
            fontSize: isMobile ? '16px' : '18px',
            fontWeight: '600',
            color: '#f1f5f9',
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <MessageCircle size={isMobile ? 18 : 20} style={{ color: '#8b5cf6' }} />
            Cuộc trò chuyện
          </h2>
          
          <div style={{ display: 'flex', gap: '8px' }}>
            {/* Mobile close button */}
            {isMobile && onCloseSidebar && (
              <button
                onClick={onCloseSidebar}
                style={{
                  padding: '8px',
                  backgroundColor: 'transparent',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#94a3b8',
                  cursor: 'pointer'
                }}
              >
                <X size={16} />
              </button>
            )}
            
            <button
              onClick={onRefreshConversations}
              disabled={isLoading}
              style={{
                padding: '8px',
                backgroundColor: 'transparent',
                border: '1px solid #334155',
                borderRadius: '6px',
                color: '#94a3b8',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1
              }}
            >
              <RefreshCw size={16} style={{
                animation: isLoading ? 'spin 1s linear infinite' : 'none'
              }} />
            </button>
          </div>
        </div>

        {/* New Conversation Button */}
        <button
          onClick={onCreateNewConversation}
          style={{
            width: '100%',
            padding: isMobile ? '10px 14px' : '12px 16px',
            background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
            border: 'none',
            borderRadius: '8px',
            color: 'white',
            fontSize: isMobile ? '13px' : '14px',
            fontWeight: '500',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
        >
          <Plus size={isMobile ? 14 : 16} />
          Cuộc trò chuyện mới
        </button>
      </div>

      {/* Conversations List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 0'
      }}>
        {isLoading ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '40px 20px',
            color: '#94a3b8'
          }}>
            <RefreshCw size={20} style={{ animation: 'spin 1s linear infinite' }} />
            <span style={{ marginLeft: '8px' }}>Đang tải...</span>
          </div>
        ) : conversations.length === 0 ? (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: '#64748b'
          }}>
            <MessageSquare size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
            <p style={{ fontSize: '14px', margin: 0, lineHeight: '1.5' }}>
              Chưa có cuộc trò chuyện nào.<br />
              Tạo cuộc trò chuyện mới để bắt đầu!
            </p>
          </div>
        ) : (
          <div style={{ padding: '0 16px' }}>
            {conversations.map((conversation) => (
              <div
                key={conversation.conversation_id}
                style={{
                  marginBottom: '8px',
                  padding: '12px',
                  backgroundColor: selectedConversationId === conversation.conversation_id 
                    ? 'rgba(139, 92, 246, 0.2)' 
                    : 'transparent',
                  border: selectedConversationId === conversation.conversation_id 
                    ? '1px solid rgba(139, 92, 246, 0.5)' 
                    : '1px solid transparent',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  position: 'relative',
                  userSelect: 'none'
                }}
                onClick={() => handleConversationClick(conversation.conversation_id)}
              >
                {/* Title editing or display */}
                {editingTitleId === conversation.conversation_id ? (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '8px'
                  }}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleSaveTitle(conversation.conversation_id);
                        } else if (e.key === 'Escape') {
                          handleCancelEdit();
                        }
                      }}
                      style={{
                        flex: 1,
                        padding: '4px 8px',
                        backgroundColor: '#0f172a',
                        border: '1px solid #334155',
                        borderRadius: '4px',
                        color: '#f1f5f9',
                        fontSize: '14px'
                      }}
                      autoFocus
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSaveTitle(conversation.conversation_id);
                      }}
                      style={{
                        padding: '4px',
                        backgroundColor: '#10b981',
                        border: 'none',
                        borderRadius: '4px',
                        color: 'white',
                        cursor: 'pointer'
                      }}
                    >
                      <Check size={12} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCancelEdit();
                      }}
                      style={{
                        padding: '4px',
                        backgroundColor: '#ef4444',
                        border: 'none',
                        borderRadius: '4px',
                        color: 'white',
                        cursor: 'pointer'
                      }}
                    >
                      <X size={12} />
                    </button>
                  </div>
                ) : (
                  <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    marginBottom: '8px'
                  }}>
                    <h3 style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      color: selectedConversationId === conversation.conversation_id 
                        ? '#c4b5fd' 
                        : '#e5e7eb',
                      margin: 0,
                      lineHeight: '1.4',
                      flex: 1,
                      marginRight: '8px'
                    }}>
                      {conversation.title || `Cuộc trò chuyện ${conversation.conversation_id.substring(0, 8)}`}
                    </h3>
                    
                    {/* 🆕 Simplified dropdown trigger - no hover effects */}
                    <div style={{ position: 'relative' }}>
                      <button
                        onClick={(e) => toggleDropdown(e, conversation.conversation_id)}
                        style={{
                          padding: '6px',
                          backgroundColor: dropdownOpen === conversation.conversation_id 
                            ? '#334155' 
                            : 'transparent',
                          border: 'none',
                          borderRadius: '6px',
                          color: dropdownOpen === conversation.conversation_id 
                            ? '#f1f5f9' 
                            : '#94a3b8',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          minWidth: isMobile ? '32px' : '28px',
                          minHeight: isMobile ? '32px' : '28px',
                          transform: dropdownOpen === conversation.conversation_id ? 'rotate(180deg)' : 'rotate(0deg)',
                          transition: 'transform 0.2s ease'
                        }}
                        title={dropdownOpen === conversation.conversation_id ? 'Đóng menu' : 'Mở menu tùy chọn'}
                      >
                        <ChevronDown size={isMobile ? 16 : 14} />
                      </button>

                      {/* 🆕 Simple Dropdown Menu - no hover flickering */}
                      {dropdownOpen === conversation.conversation_id && (
                        <div
                          ref={el => dropdownRefs.current[conversation.conversation_id] = el}
                          style={{
                            position: 'absolute',
                            top: '100%',
                            right: '0',
                            marginTop: '4px',
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
                            zIndex: 1000,
                            minWidth: '180px',
                            overflow: 'hidden'
                          }}
                        >
                          {/* Header */}
                          <div style={{
                            padding: '8px 12px',
                            borderBottom: '1px solid #334155',
                            backgroundColor: '#0f172a'
                          }}>
                            <div style={{
                              fontSize: '10px',
                              color: '#64748b',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              Tùy chọn
                            </div>
                          </div>

                          {/* Menu items - simplified, no hover effects */}
                          <div style={{ padding: '4px 0' }}>
                            {/* Select conversation */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDropdownAction('select', conversation.conversation_id);
                              }}
                              style={{
                                width: '100%',
                                padding: '10px 12px',
                                backgroundColor: selectedDropdownIndex === 0 ? '#334155' : 'transparent',
                                border: 'none',
                                color: '#e5e7eb',
                                fontSize: '13px',
                                textAlign: 'left',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                              }}
                            >
                              <MessageSquare size={14} style={{ color: '#8b5cf6' }} />
                              Mở cuộc trò chuyện
                            </button>

                            {/* Rename */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDropdownAction('rename', conversation.conversation_id);
                              }}
                              style={{
                                width: '100%',
                                padding: '10px 12px',
                                backgroundColor: selectedDropdownIndex === 1 ? '#334155' : 'transparent',
                                border: 'none',
                                color: '#e5e7eb',
                                fontSize: '13px',
                                textAlign: 'left',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                              }}
                            >
                              <Edit3 size={14} style={{ color: '#3b82f6' }} />
                              Đổi tên
                            </button>

                            {/* Copy ID */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDropdownAction('copy', conversation.conversation_id);
                              }}
                              style={{
                                width: '100%',
                                padding: '10px 12px',
                                backgroundColor: selectedDropdownIndex === 2 ? '#334155' : 'transparent',
                                border: 'none',
                                color: '#e5e7eb',
                                fontSize: '13px',
                                textAlign: 'left',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                              }}
                            >
                              <Copy size={14} style={{ color: '#10b981' }} />
                              Sao chép ID
                            </button>

                            {/* Divider */}
                            <div style={{
                              height: '1px',
                              backgroundColor: '#334155',
                              margin: '4px 0'
                            }} />

                            {/* Delete */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDropdownAction('delete', conversation.conversation_id);
                              }}
                              style={{
                                width: '100%',
                                padding: '10px 12px',
                                backgroundColor: selectedDropdownIndex === 3 ? 'rgba(239, 68, 68, 0.1)' : 'transparent',
                                border: 'none',
                                color: '#ef4444',
                                fontSize: '13px',
                                textAlign: 'left',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                              }}
                            >
                              <Trash2 size={14} />
                              Xóa cuộc trò chuyện
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Conversation info */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  fontSize: '12px',
                  color: '#64748b'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} />
                    <span>{formatTime(conversation.updated_at)}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MessageSquare size={12} />
                    <span>{conversation.message_count || 0}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationSidebar;