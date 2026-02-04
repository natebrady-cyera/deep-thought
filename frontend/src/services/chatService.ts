import api from './api';

export interface Chat {
  id: number;
  name: string;
  canvas_id: number;
  chat_type: 'sales_assistant' | 'whats_next';
  created_at: string;
  message_count: number;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  token_count?: number;
}

export interface CreateChatRequest {
  canvas_id: number;
  name: string;
  chat_type: 'sales_assistant' | 'whats_next';
  node_id?: number;
}

export interface SendMessageRequest {
  content: string;
  include_canvas_context?: boolean;
}

export const chatService = {
  // List all chats for a canvas
  listChats: async (canvasId: number): Promise<Chat[]> => {
    const response = await api.get(`/chats/canvas/${canvasId}`);
    return response.data;
  },

  // List all chats for a specific node
  listNodeChats: async (nodeId: number): Promise<Chat[]> => {
    const response = await api.get(`/chats/node/${nodeId}`);
    return response.data;
  },

  // Create a new chat
  createChat: async (data: CreateChatRequest): Promise<Chat> => {
    const response = await api.post('/chats/', data);
    return response.data;
  },

  // Get messages for a chat
  getMessages: async (chatId: number): Promise<Message[]> => {
    const response = await api.get(`/chats/${chatId}/messages`);
    return response.data;
  },

  // Send a message
  sendMessage: async (chatId: number, data: SendMessageRequest): Promise<Message> => {
    const response = await api.post(`/chats/${chatId}/messages`, data);
    return response.data;
  },

  // Delete a chat
  deleteChat: async (chatId: number): Promise<void> => {
    await api.delete(`/chats/${chatId}`);
  },

  // Rename a chat
  renameChat: async (chatId: number, name: string): Promise<void> => {
    await api.put(`/chats/${chatId}/rename`, null, { params: { name } });
  },
};
