import { useState, useCallback } from 'react';
import apiClient from '../services/api';

export const useChat = () => {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingStep, setProcessingStep] = useState('');

  // 🔧 HELPER FUNCTION - Tạo thành regular function thay vì useCallback
  const createValidMessage = (role, text, additionalProps = {}) => {
    return {
      role,
      text: text || '',
      created_at: new Date().toISOString(),
      id: Math.random().toString(36).substr(2, 9),
      ...additionalProps
    };
  };

  // Fetch conversations
  const fetchConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const conversationList = await apiClient.fetchConversations();
      setConversations(conversationList);
    } catch (error) {
      setError('Không thể tải danh sách cuộc hội thoại');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load conversation
  const loadConversation = useCallback(async (conversationId) => {
    setError(null);
    setIsProcessing(false);
    setProcessingStep('');
    try {
      setCurrentConversationId(conversationId);
      const conversationMessages = await apiClient.fetchMessages(conversationId);
      setMessages(conversationMessages || []);
    } catch (error) {
      setError('Không thể tải cuộc hội thoại');
      setMessages([]);
      setCurrentConversationId(null);
    }
  }, []);

  // Create new conversation
  const createNewConversation = useCallback(() => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
    setIsProcessing(false);
    setProcessingStep('');
  }, []);

  // Delete conversation
  const deleteConversation = useCallback(async (conversationId) => {
    try {
      const success = await apiClient.deleteConversation(conversationId);
      if (success) {
        setConversations(prev => prev.filter(conv => conv.conversation_id !== conversationId));
        if (currentConversationId === conversationId) {
          createNewConversation();
        }
        return true;
      }
      return false;
    } catch (error) {
      setError('Không thể xóa cuộc hội thoại');
      return false;
    }
  }, [currentConversationId, createNewConversation]);

  // Finalize message
  const finalizeMessage = useCallback((text) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      
      if (newMessages[lastIndex] && newMessages[lastIndex].isStreaming) {
        newMessages[lastIndex] = {
          ...newMessages[lastIndex],
          text: text || '',
          isStreaming: false
        };
      } else {
        const newMessage = createValidMessage('assistant', text);
        newMessages.push(newMessage);
      }
      return newMessages;
    });
    setIsProcessing(false);
    setProcessingStep('');
  }, []); // 🔧 Loại bỏ createValidMessage khỏi dependency

  // Start complete processing - Improved streaming
  const startCompleteProcessing = useCallback(async (conversationId, userMessage) => {
    setIsProcessing(true);
    setProcessingStep('🔍 Đang phân tích truy vấn...');

    try {
      // 1. Gọi API analyze
      const analysisResult = await apiClient.analyzeUserQuery(userMessage, conversationId);
      console.log('🔍 Analysis result:', analysisResult);
      
      // 2. Hiển thị analysis result
      if (analysisResult) {
        const analysisMessage = createValidMessage('analysis', '', {
          analysis: analysisResult.analysis,
          actions: analysisResult.actions,
          finalAnswer: analysisResult.final_answer
        });
        setMessages(prev => [...prev, analysisMessage]);
      }

      // 3. Kiểm tra final_answer ngay lập tức
      if (analysisResult.final_answer && (!analysisResult.actions || analysisResult.actions.length === 0)) {
        console.log('✅ Có final_answer và không có tool nào');
        setProcessingStep('✅ Đã có câu trả lời trực tiếp');
        
        const finalMessage = createValidMessage('assistant', analysisResult.final_answer);
        setMessages(prev => [...prev, finalMessage]);
        
        setIsProcessing(false);
        setProcessingStep('');
        return;
      }

      // 4. Stream final answer với hiệu ứng typing
      console.log('📝 Streaming final answer...');
      setProcessingStep('🤖 Đang tạo câu trả lời...');
      
      // Tạo streaming message placeholder
      const streamingMessage = createValidMessage('assistant', '', { isStreaming: true });
      setMessages(prev => [...prev, streamingMessage]);
      
      let accumulatedText = '';
      let updateTimeout = null;
      
      // 🔧 Debounced update function for smoother UI
      const debouncedUpdate = (newText) => {
        if (updateTimeout) clearTimeout(updateTimeout);
        updateTimeout = setTimeout(() => {
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIndex = newMessages.length - 1;
            if (newMessages[lastIndex] && newMessages[lastIndex].isStreaming) {
              newMessages[lastIndex] = {
                ...newMessages[lastIndex],
                text: newText
              };
            }
            return newMessages;
          });
        }, 16); // 🔧 60fps update rate
      };
      
      // Stream final answer
      await apiClient.streamAnswer(
        conversationId,
        (chunk) => {
          // onChunk - Smooth text accumulation
          accumulatedText += chunk;
          debouncedUpdate(accumulatedText);
        },
        () => {
          // onComplete - Finalize message
          console.log('✅ Stream completed');
          if (updateTimeout) clearTimeout(updateTimeout);
          
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIndex = newMessages.length - 1;
            if (newMessages[lastIndex] && newMessages[lastIndex].isStreaming) {
              newMessages[lastIndex] = {
                ...newMessages[lastIndex],
                text: accumulatedText,
                isStreaming: false
              };
            }
            return newMessages;
          });
          setProcessingStep('✅ Hoàn thành');
          setIsProcessing(false);
        },
        (error) => {
          // onError
          console.error('❌ Stream error:', error);
          if (updateTimeout) clearTimeout(updateTimeout);
          
          setProcessingStep('❌ Lỗi khi stream câu trả lời');
          const errorMessage = createValidMessage('assistant', 'Đã xảy ra lỗi khi tạo câu trả lời. Vui lòng thử lại.');
          setMessages(prev => {
            const newMessages = prev.slice(0, -1);
            return [...newMessages, errorMessage];
          });
          setIsProcessing(false);
        }
      );

    } catch (error) {
      console.error('❌ Error in processing:', error);
      setProcessingStep('❌ Lỗi xử lý! Vui lòng thử lại.');
      
      const errorMessage = createValidMessage('assistant', 'Đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại.');
      setMessages(prev => [...prev, errorMessage]);
      
      setIsProcessing(false);
    }
  }, []); // 🔧 Loại bỏ createValidMessage khỏi dependency

  // Send message
  const sendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || isProcessing) return;

    console.log('🚀 Starting message flow:', messageText);

    const userMessage = createValidMessage('user', messageText);
    setMessages(prev => [...prev, userMessage]);
    setError(null);
    setIsProcessing(true);
    setProcessingStep('Đang gửi tin nhắn...');

    try {
      const response = await apiClient.sendMessage(messageText, currentConversationId);

      if (response && response.conversation_id) {
        const conversationId = response.conversation_id;
        if (!currentConversationId) {
          setCurrentConversationId(conversationId);
          fetchConversations();
        }

        if (response.status === "reused" && response.answer) {
          setProcessingStep('Sử dụng câu trả lời có sẵn');
          const assistantMessage = createValidMessage('assistant', response.answer);
          setMessages(prev => [...prev, assistantMessage]);
          setIsProcessing(false);
          setProcessingStep('');
          return;
        }

        await startCompleteProcessing(conversationId, messageText);
      } else {
        throw new Error('No conversation ID received');
      }
    } catch (error) {
      setError('Không thể gửi tin nhắn. Vui lòng thử lại.');
      setIsProcessing(false);
      setProcessingStep('');
      setMessages(prev => prev.slice(0, -1));
    }
  }, [currentConversationId, isProcessing, fetchConversations, startCompleteProcessing]); // 🔧 Loại bỏ createValidMessage

  // Update conversation title
  const updateConversationTitle = useCallback(async (conversationId, title) => {
    try {
      await apiClient.updateConversationTitle(conversationId, title);
      setConversations(prev => 
        prev.map(conv => 
          conv.conversation_id === conversationId 
            ? { ...conv, title, updated_at: new Date().toISOString() }
            : conv
        )
      );
      return true;
    } catch (error) {
      setError('Không thể cập nhật tên cuộc trò chuyện');
      return false;
    }
  }, []);
  console.info('Conversation title updated:', messages);

  return {
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
  };
};