import React from 'react';
import { UserIcon, AiIcon } from './Icons';

interface ChatBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ role, content, isStreaming }) => {
    const isUser = role === 'user';

    return (
        <div className={`flex items-start gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && <AiIcon />}
            <div className={`max-w-2xl p-4 rounded-2xl whitespace-pre-wrap ${isUser ? 'bg-slate-700 text-white rounded-br-none' : (isStreaming ? 'text-gray-800' : 'bg-gray-100 text-gray-800 rounded-bl-none')}`}>
                {content || (isStreaming ? '…' : '')}
            </div>
            {isUser && <UserIcon />}
        </div>
    );
};

export default ChatBubble;