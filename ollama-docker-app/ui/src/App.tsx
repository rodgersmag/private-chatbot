import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useChatStore } from './store/chat';
import { ollamaAPI } from './lib/api';
import ChatBubble from './components/ChatBubble';
import MessageInput from './components/MessageInput';
import { AiIcon } from './components/Icons';

const App: React.FC = () => {
    const [inputValue, setInputValue] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const { messages, model, addUserMessage, addAssistantMessage, updateLastMessage } = useChatStore();
    const abortControllerRef = useRef<AbortController | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

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
        } catch (error: any) {
            if (error.name !== 'AbortError') {
                console.error('Stream error:', error);
                updateLastMessage('Error: ' + error.message);
            }
        } finally {
            setIsLoading(false);
            abortControllerRef.current = null;
        }
    }, [inputValue, messages, model, addUserMessage, addAssistantMessage, updateLastMessage]);

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

    return (
        <div className="flex flex-col h-screen bg-slate-50 font-sans text-gray-800">
            <header className="flex items-center p-4">
                <AiIcon />
                <div className="ml-3">
                    <h1 className="text-lg font-semibold text-gray-800">Private Chat</h1>
                    <p className="text-sm text-gray-500">{model}</p>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6">
                <div className="max-w-3xl mx-auto">
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
                <footer className="sticky bottom-0">
                    {messageInputComponent}
                </footer>
            )}
        </div>
    );
};

export default App;
