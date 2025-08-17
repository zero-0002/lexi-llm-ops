import React, { memo, useCallback } from 'react';
import { MessageSquare, Edit3, Copy, Trash2 } from 'lucide-react';

// 🆕 Memoized dropdown menu component để prevent unnecessary re-renders
const OptimizedDropdownMenu = memo(({ 
  conversation, 
  selectedIndex, 
  hoveredIndex, 
  onAction, 
  onMouseEnter, 
  onMouseLeave,
  dropdownRef 
}) => {
  const menuItems = [
    {
      action: 'select',
      label: 'Mở cuộc trò chuyện',
      icon: MessageSquare,
      color: '#8b5cf6'
    },
    {
      action: 'rename',
      label: 'Đổi tên',
      icon: Edit3,
      color: '#3b82f6'
    },
    {
      action: 'copy',
      label: 'Sao chép ID',
      icon: Copy,
      color: '#10b981'
    },
    {
      action: 'delete',
      label: 'Xóa cuộc trò chuyện',
      icon: Trash2,
      color: '#ef4444',
      isDanger: true
    }
  ];

  // 🆕 Memoized click handler
  const handleItemClick = useCallback((e, action) => {
    e.stopPropagation();
    onAction(action, conversation.conversation_id);
  }, [onAction, conversation.conversation_id]);

  // 🆕 Memoized mouse handlers
  const handleMouseEnter = useCallback((index) => {
    onMouseEnter(index);
  }, [onMouseEnter]);

  const handleMouseLeave = useCallback(() => {
    onMouseLeave();
  }, [onMouseLeave]);

  return (
    <div
      ref={dropdownRef}
      className="dropdown-menu-content"
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
        overflow: 'hidden',
        backdropFilter: 'blur(10px)',
        animation: 'dropdownSlideIn 0.15s ease-out'
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

      {/* Menu items */}
      <div style={{ padding: '4px 0' }}>
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          const isKeyboardSelected = hoveredIndex === null && selectedIndex === index;
          const isMouseHovered = hoveredIndex === index;
          const isSelected = isKeyboardSelected || isMouseHovered;
          const isDanger = item.isDanger;
          
          return (
            <button
              key={item.action}
              className="dropdown-item"
              onClick={(e) => handleItemClick(e, item.action)}
              onMouseEnter={() => handleMouseEnter(index)}
              onMouseLeave={handleMouseLeave}
              style={{
                width: '100%',
                padding: '8px 12px',
                backgroundColor: isSelected 
                  ? (isDanger ? 'rgba(239, 68, 68, 0.1)' : '#334155')
                  : 'transparent',
                border: 'none',
                color: isDanger ? '#ef4444' : '#e5e7eb',
                fontSize: '13px',
                textAlign: 'left',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                outline: 'none',
                boxShadow: isKeyboardSelected ? `inset 2px 0 0 ${item.color}` : 'none',
                // 🆕 Stable transition để avoid flickering
                transition: 'background-color 0.1s ease'
              }}
            >
              <Icon size={14} style={{ color: item.color }} />
              {item.label}
              {isKeyboardSelected && (
                <div style={{
                  marginLeft: 'auto',
                  fontSize: '10px',
                  color: '#64748b'
                }}>
                  ⏎
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer hint */}
      <div style={{
        padding: '6px 12px',
        borderTop: '1px solid #334155',
        backgroundColor: '#0f172a',
        fontSize: '10px',
        color: '#64748b'
      }}>
        ↑↓ điều hướng • ⏎ chọn • Esc đóng
      </div>
    </div>
  );
});

OptimizedDropdownMenu.displayName = 'OptimizedDropdownMenu';

export default OptimizedDropdownMenu;