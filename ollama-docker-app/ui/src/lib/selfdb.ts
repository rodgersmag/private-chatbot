import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
const ANON_KEY = import.meta.env.VITE_ANON_KEY || '';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add request interceptor to include auth token and anon key
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (config.headers && ANON_KEY) {
      config.headers['apikey'] = ANON_KEY;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

interface Chat {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
}

interface Message {
  id: string;
  chat_id: string;
  user_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

const extractArray = <T,>(payload: any): T[] => {
  if (Array.isArray(payload?.data)) {
    return payload.data;
  }
  if (Array.isArray(payload)) {
    return payload;
  }
  if (payload?.data && Array.isArray(payload.data?.data)) {
    return payload.data.data;
  }
  if (payload && typeof payload === 'object') {
    return [payload as T];
  }
  return [];
};

class SelfDBAPI {
  async fetchUserChats(userId: string): Promise<Chat[]> {
    const response = await api.get(`/tables/chats/data?user_id=eq.${userId}&order=created_at.desc`);
    console.log('fetchUserChats response:', response.data);
    return extractArray<Chat>(response.data);
  }

  async createChat(userId: string, title: string): Promise<Chat> {
    const response = await api.post('/tables/chats/data', { user_id: userId, title });
    console.log('createChat response:', response.data);
    const [chat] = extractArray<Chat>(response.data);
    return chat;
  }

  async saveMessage(chatId: string, userId: string, role: 'user' | 'assistant', content: string): Promise<Message> {
    const response = await api.post('/tables/messages/data', { chat_id: chatId, user_id: userId, role, content });
    console.log('saveMessage response:', response.data);
    const [message] = extractArray<Message>(response.data);
    return message;
  }

  async fetchMessages(chatId: string): Promise<Message[]> {
    const response = await api.get(`/tables/messages/data?chat_id=eq.${chatId}&order=created_at.asc`);
    console.log('fetchMessages response:', response.data);
    const data = extractArray<Message>(response.data).filter((message) => message.chat_id === chatId);
    console.log('Parsed data:', data);
    return data;
  }

  async deleteMessagesByChatId(chatId: string): Promise<void> {
    const messages = await this.fetchMessages(chatId);
    if (messages.length === 0) {
      return;
    }
    await Promise.all(
      messages.map((message) =>
        api.delete(`/tables/messages/data/${message.id}?id_column=id`).catch((error) => {
          console.error(`Failed to delete message ${message.id}:`, error);
        })
      )
    );
  }

  async deleteChat(chatId: string): Promise<void> {
    await api.delete(`/tables/chats/data/${chatId}?id_column=id`);
  }

  async updateChatTitle(chatId: string, title: string): Promise<void> {
    await api.put(`/tables/chats/data/${chatId}?id_column=id`, { title });
  }
}

export const selfDBAPI = new SelfDBAPI();
export type { Chat, Message };