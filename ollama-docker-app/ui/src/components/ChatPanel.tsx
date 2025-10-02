import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../store/chat';
import { ollamaAPI } from '../lib/api';

const assistantBg = 'bg-[#1f1f24] text-gray-100';
const userBg = 'bg-[#3b3b42] text-white';

export function ChatPanel() {
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const { messages, model, addUserMessage, addAssistantMessage, updateLastMessage } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = input.trim();
    setInput('');

    addUserMessage(userMessage);
    addAssistantMessage('');
    setIsStreaming(true);

    try {
      abortControllerRef.current = new AbortController();
      let fullContent = '';

      const stream = ollamaAPI.streamChat(
        {
          model,
          messages: [...messages, { role: 'user', content: userMessage }],
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
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-[#050509] text-gray-100 flex flex-col">
      <header className="border-b border-white/10">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-emerald-500/90 text-lg font-semibold text-black grid place-items-center shadow-lg">
              AI
            </div>
            <div>
              <p className="text-base font-semibold tracking-tight">Private Chat</p>
              <p className="text-xs text-gray-400">{model}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto w-full max-w-3xl px-4 py-10 space-y-6">
          {messages.length === 0 ? (
            <div className="pt-24 text-center text-gray-400">
              <h1 className="text-3xl font-semibold tracking-tight text-gray-200">What can I help with?</h1>
              <p className="mt-4 text-sm text-gray-500">Start a conversation and watch the response stream in real time.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="h-8 w-8 flex-none rounded-full bg-emerald-500/90 text-sm font-semibold text-black grid place-items-center shadow-lg">
                    AI
                  </div>
                )}
                <div
                  className={`max-w-2xl rounded-2xl px-4 py-3 leading-relaxed shadow-lg shadow-black/20 ${
                    msg.role === 'user' ? userBg : assistantBg
                  }`}
                >
                  <div className="whitespace-pre-wrap text-[15px]">{msg.content || (msg.role === 'assistant' ? '…' : '')}</div>
                </div>
                {msg.role === 'user' && (
                  <div className="h-8 w-8 flex-none rounded-full bg-gray-700 text-sm font-semibold text-white grid place-items-center shadow-lg">
                    You
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="border-t border-white/10 bg-[#050509]/95 pb-10 pt-6">
        <div className="mx-auto w-full max-w-3xl px-4">
          <div className="rounded-3xl border border-white/10 bg-black/30 backdrop-blur-md shadow-[0_10px_40px_-20px_rgba(15,255,120,0.35)]">
            <div className="flex items-end gap-3 px-5 py-4">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask anything..."
                className="max-h-48 flex-1 resize-none bg-transparent text-base text-gray-100 placeholder-gray-500 focus:outline-none"
                rows={1}
                disabled={isStreaming}
              />
              <div className="flex flex-none items-center gap-2 pb-1">
                {isStreaming ? (
                  <button
                    onClick={handleStop}
                    className="rounded-full bg-red-500/90 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-500"
                  >
                    Stop
                  </button>
                ) : (
                  <button
                    onClick={handleSend}
                    disabled={!input.trim()}
                    className="group rounded-full bg-emerald-500/90 p-2 text-black shadow-lg transition hover:bg-emerald-400 disabled:opacity-40"
                  >
                    <span className="px-1 text-sm font-semibold">Send</span>
                  </button>
                )}
              </div>
            </div>
          </div>
          <p className="mt-4 text-center text-xs text-gray-500">Responses may be inaccurate. Verify important information.</p>
        </div>
      </footer>
    </div>
  );
}
