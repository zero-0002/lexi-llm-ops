import React, { useState, useEffect } from 'react';
import { Check, X, AlertCircle, Info, Copy } from 'lucide-react';

const Toast = ({ message, type = 'info', duration = 3000, onClose }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300); // Allow fade-out animation
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success': return <Check size={16} />;
      case 'error': return <X size={16} />;
      case 'warning': return <AlertCircle size={16} />;
      case 'copy': return <Copy size={16} />;
      default: return <Info size={16} />;
    }
  };

  const getColors = () => {
    switch (type) {
      case 'success': 
        return {
          bg: 'rgba(16, 185, 129, 0.1)',
          border: 'rgba(16, 185, 129, 0.3)',
          icon: '#10b981',
          text: '#10b981'
        };
      case 'error':
        return {
          bg: 'rgba(239, 68, 68, 0.1)',
          border: 'rgba(239, 68, 68, 0.3)',
          icon: '#ef4444',
          text: '#ef4444'
        };
      case 'warning':
        return {
          bg: 'rgba(245, 158, 11, 0.1)',
          border: 'rgba(245, 158, 11, 0.3)',
          icon: '#f59e0b',
          text: '#f59e0b'
        };
      case 'copy':
        return {
          bg: 'rgba(139, 92, 246, 0.1)',
          border: 'rgba(139, 92, 246, 0.3)',
          icon: '#8b5cf6',
          text: '#8b5cf6'
        };
      default:
        return {
          bg: 'rgba(59, 130, 246, 0.1)',
          border: 'rgba(59, 130, 246, 0.3)',
          icon: '#3b82f6',
          text: '#3b82f6'
        };
    }
  };

  const colors = getColors();

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        backgroundColor: colors.bg,
        border: `1px solid ${colors.border}`,
        borderRadius: '8px',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        zIndex: 1000,
        maxWidth: '400px',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(-20px)',
        transition: 'all 0.3s ease'
      }}
    >
      <div style={{ color: colors.icon, flexShrink: 0 }}>
        {getIcon()}
      </div>
      <span style={{ 
        color: colors.text, 
        fontSize: '14px',
        fontWeight: '500'
      }}>
        {message}
      </span>
      <button
        onClick={() => {
          setVisible(false);
          setTimeout(onClose, 300);
        }}
        style={{
          background: 'transparent',
          border: 'none',
          color: colors.text,
          cursor: 'pointer',
          padding: '2px',
          borderRadius: '4px',
          flexShrink: 0
        }}
      >
        <X size={14} />
      </button>
    </div>
  );
};

// Toast Manager
export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'info', duration = 3000) => {
    const id = Date.now();
    const toast = { id, message, type, duration };
    
    setToasts(prev => [...prev, toast]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const ToastContainer = () => (
    <div style={{ position: 'fixed', top: 0, right: 0, zIndex: 1000 }}>
      {toasts.map((toast, index) => (
        <div
          key={toast.id}
          style={{
            marginBottom: '8px',
            transform: `translateY(${index * 60}px)`
          }}
        >
          <Toast
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
    </div>
  );

  return { showToast, ToastContainer };
};

export default Toast;