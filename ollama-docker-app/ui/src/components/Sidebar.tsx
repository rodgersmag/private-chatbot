import React from 'react';
import { useChatStore } from '../store/chat';
import { useAuth } from '../store/auth';
import { MdAdd } from 'react-icons/md';
import { RiDeleteBin5Line } from 'react-icons/ri';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const { chats, currentChatId, setCurrentChat, createNewChat, deleteChat } = useChatStore();
  const { user } = useAuth();

  const handleNewChat = async () => {
    if (!user) return;
    try {
      await createNewChat(user.id, 'New Chat');
    } catch (error) {
      console.error('Failed to create new chat:', error);
    }
  };

  const handleChatClick = async (chatId: string) => {
    try {
      await setCurrentChat(chatId);
      if (isOpen && typeof window !== 'undefined' && window.innerWidth < 768) {
        onToggle();
      }
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
  };

  const handleDeleteChat = async (event: React.MouseEvent, chatId: string) => {
    event.stopPropagation();
    try {
      await deleteChat(chatId);
    } catch (error) {
      console.error('Failed to delete chat:', error);
    }
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`absolute inset-y-0 left-0 z-50 w-64 bg-slate-100 border-r border-slate-200 transform transition-transform duration-300 flex flex-col ${
          isOpen ? 'translate-x-0 shadow-xl md:shadow-none' : '-translate-x-full'
        } md:relative md:inset-auto md:z-auto md:h-full md:flex-shrink-0 ${
          isOpen ? 'md:translate-x-0' : 'md:-translate-x-full'
        }`}
      >
        <div className="p-3 flex-1 overflow-y-auto">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center px-4 py-2 text-sm bg-slate-800 text-white rounded-lg hover:bg-slate-900 mb-3"
          >
            <MdAdd size={18} className="mr-2" />
            New Chat
          </button>

          <div className="space-y-1">
            {chats.map((chat) => {
              const isActive = currentChatId === chat.id;
              return (
                <div
                  key={chat.id}
                  className={`flex items-center justify-between rounded-lg transition-colors ${
                    isActive ? 'bg-slate-200 text-slate-900' : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <button
                    onClick={() => handleChatClick(chat.id)}
                    className="flex-1 text-left px-3 py-2 rounded-lg text-sm"
                  >
                    <div className="truncate">
                      {chat.title || 'Untitled Chat'}
                    </div>
                  </button>
                  <button
                    onClick={(event) => handleDeleteChat(event, chat.id)}
                    className="p-2 text-slate-500 hover:text-red-600"
                    aria-label="Delete chat"
                    title="Delete chat"
                  >
                    <RiDeleteBin5Line size={16} />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;