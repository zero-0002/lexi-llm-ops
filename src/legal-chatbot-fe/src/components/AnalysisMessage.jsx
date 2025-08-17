import React from 'react';
import { Brain, Search, FileText, MessageCircle } from 'lucide-react';

const AnalysisMessage = ({ analysis, actions, finalAnswer }) => {
  return (
    <div style={{
      backgroundColor: '#1e293b',
      border: '1px solid #334155',
      borderRadius: '12px',
      padding: '16px',
      marginBottom: '12px',
      color: '#e2e8f0'
    }}>
      {/* Analysis Section */}
      {analysis && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }}>
            <Brain size={16} style={{ color: '#8b5cf6' }} />
            <span style={{ fontWeight: '600', color: '#f1f5f9' }}>🔍 Phân tích</span>
          </div>
          
          <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
            <div style={{ marginBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Câu hỏi chuẩn hóa:</span>
              <span style={{ marginLeft: '8px', color: '#f1f5f9' }}>
                "{analysis.rewritten_query}"
              </span>
            </div>
            
            <div style={{ marginBottom: '4px' }}>
              <span style={{ color: '#94a3b8' }}>Loại:</span>
              <span style={{ 
                marginLeft: '8px',
                padding: '2px 8px',
                backgroundColor: '#3b82f6',
                borderRadius: '4px',
                fontSize: '12px',
                color: '#ffffff'
              }}>
                {analysis.query_type}
              </span>
            </div>
            
            <div>
              <span style={{ color: '#94a3b8' }}>Lý do:</span>
              <span style={{ marginLeft: '8px', color: '#e2e8f0' }}>
                {analysis.reasoning}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Actions Section */}
      {actions && actions.length > 0 && (
        <div style={{ marginBottom: finalAnswer ? '16px' : '0' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }}>
            <Search size={16} style={{ color: '#10b981' }} />
            <span style={{ fontWeight: '600', color: '#f1f5f9' }}>🛠️ Công cụ sử dụng</span>
          </div>
          
          <div style={{ fontSize: '14px' }}>
            {actions.map((action, idx) => (
              <div key={idx} style={{ 
                marginBottom: '8px',
                padding: '8px',
                backgroundColor: '#0f172a',
                borderRadius: '6px',
                border: '1px solid #334155'
              }}>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  marginBottom: '4px'
                }}>
                  {action.tool === 'web_search' ? (
                    <Search size={14} style={{ color: '#3b82f6' }} />
                  ) : action.tool === 'laws_retrieval' ? (
                    <FileText size={14} style={{ color: '#f59e0b' }} />
                  ) : (
                    <div style={{ width: '14px', height: '14px' }} />
                  )}
                  <span style={{ 
                    fontWeight: '500',
                    color: action.tool === 'web_search' ? '#3b82f6' : '#f59e0b'
                  }}>
                    {idx + 1}. {action.tool === 'web_search' ? '🌐 Tìm kiếm web' : '⚖️ Tra cứu pháp luật'}
                  </span>
                </div>
                
                <div style={{ marginLeft: '20px', fontSize: '13px' }}>
                  <div style={{ color: '#e2e8f0', marginBottom: '2px' }}>
                    <strong>Đầu vào:</strong> "{action.input}"
                  </div>
                  <div style={{ color: '#94a3b8' }}>
                    <strong>Lý do:</strong> {action.reason}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Final Answer Section */}
      {finalAnswer && (
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }}>
            <MessageCircle size={16} style={{ color: '#10b981' }} />
            <span style={{ fontWeight: '600', color: '#f1f5f9' }}>🤖 Câu trả lời mẫu</span>
          </div>
          
          <div style={{ 
            fontSize: '14px',
            lineHeight: '1.6',
            color: '#e2e8f0',
            padding: '8px',
            backgroundColor: '#0f172a',
            borderRadius: '6px',
            border: '1px solid #334155'
          }}>
            {finalAnswer}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisMessage;