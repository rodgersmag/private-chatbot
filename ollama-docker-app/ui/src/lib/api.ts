import type { OllamaChatRequest, OllamaChatChunk, OllamaModelsResponse, StreamStats } from '../types';

const OLLAMA_BASE_URL = import.meta.env.VITE_OLLAMA_URL || '/ollama';

export class OllamaAPI {
  private baseUrl: string;

  constructor(baseUrl: string = OLLAMA_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async *streamChat(
    request: OllamaChatRequest,
    signal?: AbortSignal
  ): AsyncGenerator<{ chunk: OllamaChatChunk; content: string }, StreamStats> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ...request, stream: true }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body reader available');
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let totalTokens = 0;
    const startTime = Date.now();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const chunk: OllamaChatChunk = JSON.parse(line);
            const content = chunk.message?.content || '';
            
            console.log('Received chunk:', { content, done: chunk.done });
            
            if (content) {
              totalTokens += content.split(/\s+/).length;
            }

            yield { chunk, content };

            if (chunk.done) {
              const duration = (Date.now() - startTime) / 1000;
              console.log('Stream finished:', { tokens: totalTokens, duration, tokensPerSecond: totalTokens / duration });
              return {
                tokens: totalTokens,
                duration,
                tokensPerSecond: duration > 0 ? totalTokens / duration : 0,
              };
            }
          } catch (e) {
            console.error('Failed to parse chunk:', line, e);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    const duration = (Date.now() - startTime) / 1000;
    return {
      tokens: totalTokens,
      duration,
      tokensPerSecond: duration > 0 ? totalTokens / duration : 0,
    };
  }

  async listModels(): Promise<OllamaModelsResponse> {
    const response = await fetch(`${this.baseUrl}/api/tags`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch models: ${response.status}`);
    }

    return response.json();
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const ollamaAPI = new OllamaAPI();
