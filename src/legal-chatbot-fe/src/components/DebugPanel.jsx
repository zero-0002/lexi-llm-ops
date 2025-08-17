import React, { useState } from 'react';
import { Code, ChevronDown, ChevronUp } from 'lucide-react';

const DebugPanel = ({ 
  processingStep, 
  isProcessing, 
  lastToolDetection = null,
  lastApiCall = null 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isProcessing && !lastToolDetection && !lastApiCall) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      backgroundColor: '#1e293b',
      border: '1px solid #334155',
      borderRadius: '8px',
      padding: '12px',
      maxWidth: '300px',
      zIndex: 1000,
      fontSize: '12px',
      color: '#e2e8f0'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: isExpanded ? '8px' : '0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <Code size={14} style={{ color: '#8b5cf6' }} />
          <span style={{ fontWeight: '500' }}>Debug</span>
          {isProcessing && (
            <div style={{
              width: '6px',
              height: '6px',
              backgroundColor: '#10b981',
              borderRadius: '50%',
              animation: 'pulse 2s infinite'
            }} />
          )}
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: '2px'
          }}
        >
          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* Compact status */}
      {!isExpanded && (
        <div style={{ color: '#94a3b8', fontSize: '11px' }}>
          {processingStep || 'Idle'}
        </div>
      )}

      {/* Expanded details */}
      {isExpanded && (
        <div style={{ fontSize: '11px', lineHeight: '1.4' }}>
          {/* Current step */}
          <div style={{ marginBottom: '8px' }}>
            <strong style={{ color: '#f1f5f9' }}>Status:</strong>
            <div style={{ color: isProcessing ? '#10b981' : '#64748b' }}>
              {processingStep || 'Idle'}
            </div>
          </div>

          {/* Tool detection */}
          {lastToolDetection && (
            <div style={{ marginBottom: '8px' }}>
              <strong style={{ color: '#f1f5f9' }}>Last Tool:</strong>
              <div style={{ color: '#8b5cf6' }}>
                {lastToolDetection.tool || 'none'}
              </div>
              {lastToolDetection.hasFinalAnswer && (
                <div style={{ color: '#10b981', fontSize: '10px' }}>
                  ✓ Final answer detected
                </div>
              )}
            </div>
          )}

          {/* Last API call */}
          {lastApiCall && (
            <div>
              <strong style={{ color: '#f1f5f9' }}>Last API:</strong>
              <div style={{ color: '#3b82f6' }}>
                {lastApiCall.endpoint}
              </div>
              <div style={{ 
                color: lastApiCall.success ? '#10b981' : '#ef4444',
                fontSize: '10px'
              }}>
                {lastApiCall.success ? '✓ Success' : '✗ Failed'}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DebugPanel;