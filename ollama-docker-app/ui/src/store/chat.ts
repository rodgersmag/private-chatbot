import { create } from 'zustand';
import { selfDBAPI, type Chat } from '../lib/selfdb';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatStore {
  messages: Message[];
  chats: Chat[];
  currentChatId: string | null;
  model: string;
  addUserMessage: (content: string) => void;
  addAssistantMessage: (content: string) => void;
  updateLastMessage: (content: string) => void;
  clearMessages: () => void;
  setModel: (model: string) => void;
  // New async actions
  loadChats: (userId: string) => Promise<void>;
  setCurrentChat: (chatId: string) => Promise<void>;
  createNewChat: (userId: string, title?: string) => Promise<string>;
  saveUserMessage: (content: string, userId: string) => Promise<void>;
  saveAssistantMessage: (content: string, userId: string) => Promise<void>;
  loadMessages: (chatId: string) => Promise<void>;
  deleteChat: (chatId: string) => Promise<void>;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  chats: [],
  currentChatId: null,
  model: import.meta.env.VITE_DEFAULT_MODEL,
  
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

  loadChats: async (userId: string) => {
    try {
      const chats = await selfDBAPI.fetchUserChats(userId);
      const filteredChats = chats.filter((chat) => chat.user_id === userId);
      set({ chats: filteredChats, currentChatId: filteredChats.length ? filteredChats[0].id : null, messages: [] });
    } catch (error) {
      console.error('Failed to load chats:', error);
    }
  },

  setCurrentChat: async (chatId: string) => {
    console.log('Setting current chat to:', chatId);
    const chat = get().chats.find((item) => item.id === chatId);
    if (!chat) {
      console.warn('Attempted to access chat not owned by user:', chatId);
      return;
    }

    set({ currentChatId: chatId, messages: [] }); // Clear messages immediately
    await get().loadMessages(chatId);
  },

  createNewChat: async (userId: string, title = 'New Chat') => {
    try {
      const chat = await selfDBAPI.createChat(userId, title);
      if (!chat) {
        throw new Error('Chat creation returned no data');
      }
      set((state) => ({
        chats: [chat, ...state.chats.filter((existingChat) => existingChat.user_id === userId)],
        currentChatId: chat.id,
        messages: [],
      }));
      return chat.id;
    } catch (error) {
      console.error('Failed to create chat:', error);
      throw error;
    }
  },

  saveUserMessage: async (content: string, userId: string) => {
    const { currentChatId } = get();
    if (!currentChatId) return;
    try {
      await selfDBAPI.saveMessage(currentChatId, userId, 'user', content);

      const state = get();
      const currentChat = state.chats.find((chat) => chat.id === currentChatId);
      const proposedTitle = content.trim().slice(0, 50);

      if (currentChat && proposedTitle && (!currentChat.title || currentChat.title === 'New Chat')) {
        try {
          await selfDBAPI.updateChatTitle(currentChatId, proposedTitle);
          set(({ chats }) => ({
            chats: chats.map((chat) =>
              chat.id === currentChatId ? { ...chat, title: proposedTitle } : chat
            ),
          }));
        } catch (titleError) {
          console.error('Failed to update chat title:', titleError);
        }
      }
    } catch (error) {
      console.error('Failed to save user message:', error);
    }
  },

  saveAssistantMessage: async (content: string, userId: string) => {
    const { currentChatId } = get();
    if (!currentChatId) return;
    try {
      await selfDBAPI.saveMessage(currentChatId, userId, 'assistant', content);
    } catch (error) {
      console.error('Failed to save assistant message:', error);
    }
  },

  loadMessages: async (chatId: string) => {
    console.log('Loading messages for chat:', chatId);
    try {
      const dbMessages = await selfDBAPI.fetchMessages(chatId);
      console.log('DB messages:', dbMessages);
      const messages: Message[] = dbMessages.map(m => ({ role: m.role, content: m.content }));
      console.log('Mapped messages:', messages);
      set({ messages });
      console.log('Store messages after set:', get().messages);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  },

  deleteChat: async (chatId: string) => {
    const { currentChatId } = get();
    const chat = get().chats.find((item) => item.id === chatId);
    if (!chat) {
      console.warn('Attempted to delete chat not owned by user:', chatId);
      return;
    }

    try {
      await selfDBAPI.deleteMessagesByChatId(chatId);
    } catch (error) {
      console.error('Failed to delete chat messages:', error);
    }

    try {
      await selfDBAPI.deleteChat(chatId);
    } catch (error) {
      console.error('Failed to delete chat:', error);
      throw error;
    }

    set((state) => {
  const remainingChats = state.chats.filter((chatItem) => chatItem.id !== chatId);
      let nextChatId = state.currentChatId;
      let nextMessages = state.messages;

      if (state.currentChatId === chatId) {
        nextChatId = remainingChats.length > 0 ? remainingChats[0].id : null;
        nextMessages = [];
      }

      return {
        chats: remainingChats,
        currentChatId: nextChatId,
        messages: nextMessages,
      };
    });

    const { currentChatId: updatedChatId } = get();
    if (currentChatId === chatId && updatedChatId) {
      await get().loadMessages(updatedChatId);
    }
  },
}));
