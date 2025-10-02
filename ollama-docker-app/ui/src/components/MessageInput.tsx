import React, { useRef, useEffect } from 'react';
import { SendIcon, StopIcon } from './Icons';

interface MessageInputProps {
    inputValue: string;
    onInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    onSendMessage: () => void;
    isLoading: boolean;
    onStop: () => void;
}

const MessageInput: React.FC<MessageInputProps> = ({ inputValue, onInputChange, onSendMessage, isLoading, onStop }) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            const scrollHeight = textarea.scrollHeight;
            textarea.style.height = `${scrollHeight}px`;
        }
    }, [inputValue]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isLoading && inputValue.trim()) {
                onSendMessage();
            }
        }
    };

    return (
        <div className="w-full max-w-3xl mx-auto p-4 bg-slate-50">
            <div className="relative flex items-center bg-white border border-gray-300 rounded-full shadow-sm pr-2">
                <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={onInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything..."
                    className="w-full p-4 pl-6 pr-16 bg-transparent border-none rounded-full resize-none focus:outline-none focus:ring-0 max-h-40 overflow-y-auto"
                    rows={1}
                    disabled={isLoading}
                />
                <button
                    onClick={isLoading ? onStop : onSendMessage}
                    disabled={!inputValue.trim() && !isLoading}
                    className={`absolute right-2 top-1/2 -translate-y-1/2 flex items-center justify-center w-10 h-10 rounded-full transition-colors ${isLoading ? 'bg-red-500 hover:bg-red-600' : 'bg-slate-800 hover:bg-slate-900'} text-white disabled:bg-gray-300 disabled:cursor-not-allowed`}
                    aria-label={isLoading ? 'Stop generating' : 'Send message'}
                >
                    {isLoading ? <StopIcon className="w-5 h-5" /> : <SendIcon className="w-5 h-5" />}
                </button>
            </div>
            <p className="text-center text-xs text-gray-500 mt-2">
                Responses may be inaccurate. Verify important information.
            </p>
        </div>
    );
};

export default MessageInput;