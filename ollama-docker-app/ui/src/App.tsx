import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useChatStore } from './store/chat';
import { ollamaAPI } from './lib/api';
import ChatBubble from './components/ChatBubble';
import MessageInput from './components/MessageInput';
import { AiIcon } from './components/Icons';
import { useAuth } from './store/auth';
import Login from './components/Login';
import { MdLogout, MdMenu } from 'react-icons/md';
import Sidebar from './components/Sidebar';

const App: React.FC = () => {
    const { user, loading, logout } = useAuth();
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [inputValue, setInputValue] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const { messages, model, addUserMessage, addAssistantMessage, updateLastMessage, currentChatId, createNewChat, saveUserMessage, saveAssistantMessage } = useChatStore();
    const abortControllerRef = useRef<AbortController | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load chats on login
    useEffect(() => {
        if (user) {
            useChatStore.getState().loadChats(user.id);
        }
    }, [user]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = useCallback(async () => {
        const currentInput = inputValue.trim();
        if (!currentInput) return;

        setInputValue('');
        addUserMessage(currentInput);

        // Ensure we have a chat
        let chatId = currentChatId;
        if (!chatId && user) {
            try {
                chatId = await createNewChat(user.id, currentInput.slice(0, 50));
            } catch (error) {
                console.error('Failed to create chat:', error);
                return;
            }
        }

        // Save user message
        if (chatId && user) {
            await saveUserMessage(currentInput, user.id);
        }

        addAssistantMessage('');
        setIsLoading(true);

        try {
            abortControllerRef.current = new AbortController();
            let fullContent = '';

            const stream = ollamaAPI.streamChat(
                {
                    model,
                    messages: [...messages, { role: 'user', content: currentInput }],
                },
                abortControllerRef.current.signal
            );

            for await (const { content: chunk } of stream) {
                if (chunk) {
                    fullContent += chunk;
                    updateLastMessage(fullContent);
                }
            }

            // Save assistant message
            if (chatId && user) {
                await saveAssistantMessage(fullContent, user.id);
            }
        } catch (error) {
            if (error instanceof DOMException && error.name === 'AbortError') {
                return;
            }

            if (error instanceof Error) {
                console.error('Stream error:', error);
                updateLastMessage(`Error: ${error.message}`);
            } else {
                console.error('Stream error:', error);
                updateLastMessage('Error: An unexpected issue occurred.');
            }
        } finally {
            setIsLoading(false);
            abortControllerRef.current = null;
        }
    }, [inputValue, messages, model, addUserMessage, addAssistantMessage, updateLastMessage, currentChatId, createNewChat, saveUserMessage, saveAssistantMessage, user]);

    const handleStop = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
        setIsLoading(false);
    };

    const messageInputComponent = (
        <MessageInput
            inputValue={inputValue}
            onInputChange={(e) => setInputValue(e.target.value)}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onStop={handleStop}
        />
    );

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-lg">Loading...</div>
            </div>
        );
    }

    if (!user) {
        return <Login />;
    }

    return (
        <div className="flex flex-col h-screen bg-slate-50 font-sans text-gray-800">
            <header className="flex items-center justify-between px-3 py-2 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
                <div className="flex items-center">
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className="p-2 mr-2 text-slate-600 hover:text-slate-800"
                        aria-label="Toggle chat list"
                    >
                        <MdMenu size={20} />
                    </button>
                    <AiIcon />
                    <div className="ml-3">
                        <h1 className="text-lg font-semibold text-gray-800 m-0 leading-tight">Private Chat</h1>
                        <p className="text-xs text-gray-500 m-0 leading-tight">{model}</p>
                    </div>
                </div>
                <button
                    onClick={logout}
                    className="p-2 text-gray-600 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500 rounded"
                    title="Logout"
                >
                    <MdLogout size={20} />
                </button>
            </header>

            <div className="flex flex-1 overflow-hidden relative">
                <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

                <div className="flex-1 flex flex-col overflow-hidden">
                    <main className="flex-1 overflow-y-auto p-4 md:p-6">
                        <div className="max-w-5xl mx-auto">
                            {messages.length === 0 ? (
                                <div className="text-center mt-20">
                                    <h2 className="text-4xl font-bold text-gray-700">What can I help with?</h2>
                                    <p className="text-gray-500 mt-2">Start a conversation and watch the response stream in real time.</p>
                                    <div className="mt-12">
                                        {messageInputComponent}
                                    </div>
                                </div>
                            ) : (
                                <>
                                    {messages.map((msg, index) => (
                                        <ChatBubble
                                            key={index}
                                            role={msg.role}
                                            content={msg.content}
                                            isStreaming={isLoading && index === messages.length - 1 && msg.role === 'assistant'}
                                        />
                                    ))}
                                    <div ref={messagesEndRef} />
                                </>
                            )}
                        </div>
                    </main>

                    {messages.length > 0 && (
                        <div className="border-t border-slate-200 bg-white/80 backdrop-blur-sm p-3">
                            {messageInputComponent}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default App;
