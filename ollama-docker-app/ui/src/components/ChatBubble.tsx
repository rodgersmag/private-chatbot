import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { UserIcon, AiIcon } from './Icons';

interface ChatBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
}

const markdownComponents: Components = {
    p: ({ children, ...props }) => (
        <p {...props} className="mb-2 last:mb-0 leading-relaxed whitespace-pre-wrap">
            {children}
        </p>
    ),
    ul: ({ children, ...props }) => (
        <ul {...props} className="mb-2 last:mb-0 list-disc space-y-1 pl-5">
            {children}
        </ul>
    ),
    ol: ({ children, ...props }) => (
        <ol {...props} className="mb-2 last:mb-0 list-decimal space-y-1 pl-5">
            {children}
        </ol>
    ),
    blockquote: ({ children, ...props }) => (
        <blockquote
            {...props}
            className="mb-2 last:mb-0 border-l-4 border-slate-300 pl-3 text-slate-600"
        >
            {children}
        </blockquote>
    ),
    code: ({ className, children, ...props }) => {
        const { inline, ...rest } = props as { inline?: boolean } & React.HTMLAttributes<HTMLElement>;

        if (inline) {
            return (
                <code
                    {...rest}
                    className="rounded bg-slate-800/10 px-1 py-0.5 font-mono text-[0.95em]"
                >
                    {children}
                </code>
            );
        }

        return (
            <pre className="mb-2 last:mb-0 overflow-x-auto rounded-lg bg-slate-900/90 p-4 text-xs text-white">
                <code {...rest} className={className}>
                    {children}
                </code>
            </pre>
        );
    },
    a: ({ children, ...props }) => (
        <a
            {...props}
            className="font-semibold text-sky-600 underline-offset-2 hover:underline"
            target="_blank"
            rel="noreferrer"
        >
            {children}
        </a>
    ),
    hr: (props) => <hr {...props} className="my-3 border-slate-300/60" />
};

const ChatBubble: React.FC<ChatBubbleProps> = ({ role, content, isStreaming }) => {
    const isUser = role === 'user';

    return (
        <div className={`flex items-start gap-2 my-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && <AiIcon />}
            <div
                className={`max-w-4xl p-3 rounded-2xl text-sm ${
                    isUser
                        ? 'bg-slate-700 text-white rounded-br-none'
                        : isStreaming
                        ? 'text-gray-800'
                        : 'bg-gray-100 text-gray-800 rounded-bl-none'
                }`}
            >
                {content ? (
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkBreaks]}
                        components={markdownComponents}
                    >
                        {content}
                    </ReactMarkdown>
                ) : (
                    isStreaming ? '…' : null
                )}
            </div>
            {isUser && <UserIcon />}
        </div>
    );
};

export default ChatBubble;