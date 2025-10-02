import { create } from 'zustand';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatStore {
  messages: Message[];
  model: string;
  addUserMessage: (content: string) => void;
  addAssistantMessage: (content: string) => void;
  updateLastMessage: (content: string) => void;
  clearMessages: () => void;
  setModel: (model: string) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  model: 'qwen3:1.7b',
  
  addUserMessage: (content) => {
    set((state) => ({
      messages: [...state.messages, { role: 'user', content }],
    }));
  },
  
  addAssistantMessage: (content) => {
    set((state) => ({
      messages: [...state.messages, { role: 'assistant', content }],
    }));
  },
  
  updateLastMessage: (content) => {
    set((state) => {
      const newMessages = [...state.messages];
      if (newMessages.length > 0) {
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          content,
        };
      }
      return { messages: newMessages };
    });
  },
  
  clearMessages: () => {
    set({ messages: [] });
  },
  
  setModel: (model) => {
    set({ model });
  },
}));
