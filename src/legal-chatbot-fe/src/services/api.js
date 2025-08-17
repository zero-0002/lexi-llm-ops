// filepath: d:\Data\Legal-Retrieval\legal-chatbot-fe\src\services\api.js
import axios from 'axios';
const HOST = "localhost:8000"
// const HOST = "nutten-gnu-termination-jennifer.trycloudflare.com"
const API_BASE = `http://${HOST}/api/legal-chat`;
const RAG_BASE = `http://${HOST}/api/rag`;
const USER_ID = 'tinh123';
const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  constructor() {
    this.axios = axios.create({
      baseURL: API_BASE,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    this.baseURL = API_BASE_URL;
  }

  // 🆕 Enhanced fetchConversations with title support
  async fetchConversations(userId = 'tinh123') {
    try {
      console.log('📋 Fetching conversations with titles...');
      
      const response = await fetch(`${API_BASE}/conversations?user_id=${userId}`, {
        method: 'GET',
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const conversations = await response.json();
      
      // Sort by updated_at (most recent first)
      const sortedConversations = conversations.sort((a, b) => 
        new Date(b.updated_at) - new Date(a.updated_at)
      );
      
      console.log('✅ Conversations fetched:', sortedConversations);
      return sortedConversations;
      
    } catch (error) {
      console.error('❌ Error fetching conversations:', error);
      throw error;
    }
  }

  // 🆕 Update conversation title
  async updateConversationTitle(conversationId, title, userId = 'tinh123') {
    try {
      console.log(`📝 Updating conversation title: ${conversationId} -> ${title}`);
    
    const response = await axios.put(
      `${API_BASE}/conversations/${conversationId}/title`,
      { title }, // <-- body JSON, đúng format BE yêu cầu
      {
        params: { user_id: userId }, // query param
        headers: this.defaultHeaders // nếu cần token hoặc custom header
      }
    );

    if (response.status < 200 || response.status >= 300) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

      const result = response.data;
      console.log('✅ Title updated successfully');
      return result;
      
    } catch (error) {
      console.error('❌ Error updating title:', error);
      throw error;
    }
  }

async fetchMessages(conversationId) {
  try {
    const response = await this.axios.get(`/conversation-history/${conversationId}`, {
      params: { limit: 20 }
    });
    console.info('fetching messages:', response.data);
    // Trả về đúng mảng messages, nếu không có thì trả mảng rỗng
    return response.data?.messages || [];
  } catch (error) {
    console.error('Error fetching messages:', error);
    return [];
  }
}

  async sendMessage(message, conversationId = null) {
    try {
      const payload = { 
        user_id: USER_ID, 
        message: message.trim()
      };
      
      if (conversationId) {
        payload.conversation_id = conversationId;
      }
      
      const response = await this.axios.post('/send-query', payload);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  // 🆕 Stream query analyze
  async streamQueryAnalyze(conversationId, userMessage, onChunk, onComplete, onError) {
    try {
      console.log('📊 Starting query analyze stream for:', conversationId);
      
      const response = await fetch(`${API_BASE}/query/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          user_id: USER_ID,
          query: userMessage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('📊 Query analyze stream completed');
          onComplete(buffer); // Pass full text to complete handler
          break;
        }
        
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        
        // Send chunk to UI for real-time display
        onChunk(chunk);
      }
    } catch (error) {
      console.error('❌ Error in stream query analyze:', error);
      onError(error);
    }
  }

  // 🆕 Extract tool and input from LLM response
  extractToolAndInput(text) {
    const toolMatch = text.match(/Action:\s*\[(\w+)\]/);
    const inputMatch = text.match(/Action Input:\s*\[(.*?)\]/);

    const tool = toolMatch ? toolMatch[1] : null;
    const inputStr = inputMatch ? inputMatch[1] : null;

    let inputs = [];
    if (inputStr) {
      inputs = inputStr.split(',').map(s => s.trim().replace(/"/g, ''));
    }

    return { tool, inputs };
  }

  // 🆕 Check for final answer
  checkFinalAnswer(text) {
    const match = text.match(/Final Answer:\s*(.*)/is);
    return match ? match[1].trim() : null;
  }

  // 🆕 Web search API
  async triggerWebSearch(query) {
    try {
      console.log('🌐 Triggering web search for:', query);
      
      const response = await fetch(`${RAG_BASE}/web_search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query
        })
      });

      if (!response.ok) {
        throw new Error(`Web search failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('🌐 Web search completed:', result);
      return result;
    } catch (error) {
      console.error('❌ Error in web search:', error);
      throw error;
    }
  }



  // 🆕 Generate response
  async triggerGenerateResponse(query, conversationId, tools = []) {
    try {
      // Xác định có dùng tool nào không
      const useWebSearch = tools.some(t => t.type === 'web_search');
      const useLawsRetrieval = tools.some(t => t.type === 'laws_retrieval');

      console.log('🔄 Triggering generate response for:', conversationId, {
        useWebSearch,
        useLawsRetrieval,
        query,
        tools
      });

      const response = await this.axios.post('/generate_response', {
        rewrite_query: query,
        use_web_search: useWebSearch,
        use_retrieval: true,
        user_id: USER_ID,
        conversation_id: conversationId
      });

      console.log('🔄 Generate response triggered:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error triggering generate response:', error);
      throw error;
    }
  }

  // 🆕 Stream final answer
// 🆕 Stream final answer with timeout
async streamAnswer(conversationId, onChunk, onComplete, onError, timeoutMs = 60000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort(); // Hủy request khi hết thời gian
  }, timeoutMs);

  try {
    console.log('📝 Starting answer stream for:', conversationId);

  const response = await fetch(
    `${API_BASE}/stream-legal-response?conversation_id=${conversationId}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
      },
      signal: controller.signal
    }
  );

    if (!response.ok) {
      throw new Error(`Answer stream failed: ${response.status}`);
    }


    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // Don't send buffer again - chunks already sent
        console.log('📝 Answer stream completed');
        onComplete();
        break;
      }

      const chunk = decoder.decode(value, { stream: true });

      // Kiểm tra end markers
      if (chunk.includes('[DONE]')) {
        // Don't send buffer again - final chunk already processed
        console.log('📝 Found [DONE] marker, stopping stream');
        onComplete();
        break;
      }

      if (chunk.includes('[TIMEOUT]') || chunk.includes('[ERROR')) {
        console.log('📝 Found error marker:', chunk);
        onError(new Error(chunk));
        break;
      }

      // 🔧 Only send individual chunks, don't accumulate
      if (chunk) {
        onChunk(chunk);
      }
    }


  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('⏳ Stream request timed out');
      onError(new Error('[TIMEOUT] Stream request timed out'));
    } else {
      console.error('❌ Error in stream answer:', error);
      onError(error);
    }
  } finally {
    clearTimeout(timeoutId);
  }
}

  async deleteConversation(conversationId) {
    try {
      const response = await this.axios.delete('/conversations', {
        params: { 
          user_id: USER_ID, 
          conversation_id: conversationId 
        }
      });
      return response.status === 200;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      return false;
    }
  }

  // 🆕 TRIGGER LAWS RETRIEVAL
  async triggerLawsRetrieval(retrievalQuery) {
    try {
      console.log('⚖️ Triggering laws retrieval API:', retrievalQuery);
      
      const response = await fetch(`${RAG_BASE}/retrieve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: retrievalQuery
        })
      });

      if (!response.ok) {
        throw new Error(`Laws retrieval failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('⚖️ Laws retrieval response:', result);
      
      return result;
    } catch (error) {
      console.error('❌ Laws retrieval error:', error);
      throw error;
    }
  }

  // 🆕 ENHANCED TOOL DETECTION from response
  extractToolAndInput(responseText) {
    if (!responseText || typeof responseText !== 'string') {
      return { tool: null, inputs: [] };
    }

    const text = responseText.toLowerCase();
    
    // Check for web_search
    if (text.includes('web_search') || text.includes('search_web')) {
      const searchQuery = this.extractSearchQuery(responseText);
      return {
        tool: 'web_search',
        inputs: searchQuery ? [searchQuery] : []
      };
    }

    // Check for laws_retrieval
    if (text.includes('laws_retrieval') || text.includes('legal_retrieval')) {
      const retrievalQuery = this.extractRetrievalQuery(responseText);
      return {
        tool: 'laws_retrieval',
        inputs: retrievalQuery ? [retrievalQuery] : []
      };
    }

    return { tool: null, inputs: [] };
  }

  // 🆕 EXTRACT SEARCH QUERY
  extractSearchQuery(text) {
    const patterns = [
      /web_search\s*\(\s*["']([^"']+)["']\s*\)/i,
      /search\s*:\s*["']([^"']+)["']/i,
      /query\s*:\s*["']([^"']+)["']/i,
      /search_query\s*:\s*["']([^"']+)["']/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1].trim();
      }
    }

    return null;
  }

  // 🆕 EXTRACT RETRIEVAL QUERY
  extractRetrievalQuery(text) {
    const patterns = [
      /laws_retrieval\s*\(\s*["']([^"']+)["']\s*\)/i,
      /legal_retrieval\s*\(\s*["']([^"']+)["']\s*\)/i,
      /retrieve_laws\s*:\s*["']([^"']+)["']/i,
      /legal_query\s*:\s*["']([^"']+)["']/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1].trim();
      }
    }

    return null;
  }

  // 🆕 ENHANCED FINAL ANSWER CHECK
  checkFinalAnswer(responseText) {
    if (!responseText || typeof responseText !== 'string') {
      return null;
    }

    const text = responseText.toLowerCase();
    
    // Patterns indicating final answer
    const finalAnswerPatterns = [
      'final_answer',
      'câu trả lời cuối cùng',
      'kết luận',
      'đây là câu trả lời',
      'answer:',
      'trả lời:'
    ];
    
    const hasFinalAnswer = finalAnswerPatterns.some(pattern => text.includes(pattern));
    
    if (hasFinalAnswer) {
      // Try to extract the actual answer part
      for (const pattern of finalAnswerPatterns) {
        const index = text.indexOf(pattern);
        if (index !== -1) {
          const answerPart = responseText.slice(index + pattern.length).trim();
          if (answerPart.length > 10) { // Ensure it's a substantial answer
            return answerPart;
          }
        }
      }
      
      return responseText; // Return full text if can't extract specific part
    }

    return null;
  }

  extractAllToolsAndInputs(responseText) {
    if (!responseText || typeof responseText !== 'string') {
      return { tools: [], hasFinalAnswer: false, finalAnswer: null };
    }
    const text = responseText.toLowerCase();
    let tools = [];

    // 1. Detect JSON array/object tool format
    try {
      // Tìm tất cả object dạng { "tool": "...", "input": "..." }
      const jsonToolRegex = /{[^{}]*"tool"\s*:\s*"([^"]+)"[^{}]*"input"\s*:\s*"([^"]+)"[^{}]*}/gi;
      let match;
      while ((match = jsonToolRegex.exec(responseText)) !== null) {
        const type = match[1].trim();
        const query = match[2].trim();
        if (type === 'web_search' || type === 'laws_retrieval') {
          tools.push({ type, query });
        }
      }
      // Nếu là mảng JSON
      if (tools.length === 0 && text.includes('"tool":')) {
        try {
          // Tìm đoạn JSON array trong text
          const arrMatch = responseText.match(/\[[\s\S]*?"tool"\s*:\s*".+?"[\s\S]*?\]/);
          if (arrMatch) {
            const arr = JSON.parse(arrMatch[0]);
            arr.forEach(obj => {
              if (
                obj.tool &&
                (obj.tool === 'web_search' || obj.tool === 'laws_retrieval') &&
                obj.input
              ) {
                tools.push({ type: obj.tool, query: obj.input });
              }
            });
          }
        } catch (e) { /* ignore */ }
      }
    } catch (e) { /* ignore */ }

    // 2. Detect legacy pattern web_search("...")
    const webSearchMatches = [...text.matchAll(/web_search\s*\(\s*["']([^"']+)["']\s*\)/gi)];
    webSearchMatches.forEach(match => {
      tools.push({ type: 'web_search', query: match[1] });
    });

    // 3. Detect legacy pattern laws_retrieval("...")
    const retrievalMatches = [...text.matchAll(/laws_retrieval\s*\(\s*["']([^"']+)["']\s*\)/gi)];
    retrievalMatches.forEach(match => {
      tools.push({ type: 'laws_retrieval', query: match[1] });
    });

    // Only final_answer if NO tool detected
    let hasFinalAnswer = false;
    let finalAnswer = null;
    if (tools.length === 0) {
      const finalAnswerMatch = text.match(/final_answer\s*[:：-]?\s*(.*)$/i);
      if (finalAnswerMatch) {
        hasFinalAnswer = true;
        finalAnswer = finalAnswerMatch[1] || responseText;
      } else if (/câu trả lời cuối cùng|kết luận|answer:/i.test(text)) {
        hasFinalAnswer = true;
        finalAnswer = responseText;
      }
    }

    return { tools, hasFinalAnswer, finalAnswer };
  }

  async analyzeUserQuery(query, conversationId) {
    try {
      const response = await this.axios.post('/analyze-legal-query', {
        query: query,
        conversation_id: conversationId,
        user_id: USER_ID
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error analyzing query:', error);
      throw error;
    }
  }

  async waitForFinalResponse(conversationId) {
    try {
      const response = await this.axios.get(`/generate_response/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Error getting final response:', error);
      throw error;
    }
  }
}

const apiClient = new ApiClient();
export default apiClient;