import React from 'react';
import ReactMarkdown from 'react-markdown';
import { UserIcon, AiIcon } from './Icons';

interface ChatBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ role, content, isStreaming }) => {
    const isUser = role === 'user';

    return (
        <div className={`flex items-start gap-2 my-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && <AiIcon />}
            <div className={`max-w-4xl p-3 rounded-2xl text-sm ${isUser ? 'bg-slate-700 text-white rounded-br-none' : (isStreaming ? 'text-gray-800' : 'bg-gray-100 text-gray-800 rounded-bl-none')}`}>
                {content ? (
                    isUser ? (
                        <div className="whitespace-pre-wrap">{content}</div>
                    ) : (
                        <div className="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-800 prose-strong:text-gray-800 prose-code:text-gray-800 prose-pre:bg-gray-200 prose-pre:text-gray-800">
                            <ReactMarkdown>{content}</ReactMarkdown>
                        </div>
                    )
                ) : (
                    isStreaming ? '…' : ''
                )}
            </div>
            {isUser && <UserIcon />}
        </div>
    );
};

export default ChatBubble;