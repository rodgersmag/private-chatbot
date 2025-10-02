export type MessageRole = 'user' | 'assistant' | 'system' | 'error';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: number;
  tokens?: number;
  meta?: Record<string, unknown>;
}

export interface Session {
  id: string;
  title: string;
  model: string;
  systemPrompt?: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  archived?: boolean;
}

export interface OllamaMessage {
  role: string;
  content: string;
}

export interface OllamaChatRequest {
  model: string;
  messages: OllamaMessage[];
  stream?: boolean;
}

export interface OllamaChatChunk {
  model?: string;
  created_at?: string;
  message?: {
    role: string;
    content: string;
  };
  done?: boolean;
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  eval_count?: number;
  eval_duration?: number;
}

export interface OllamaModel {
  name: string;
  modified_at: string;
  size: number;
  digest: string;
  details?: {
    format?: string;
    family?: string;
    parameter_size?: string;
  };
}

export interface OllamaModelsResponse {
  models: OllamaModel[];
}

export interface StreamStats {
  tokens: number;
  duration: number;
  tokensPerSecond: number;
}

export interface Settings {
  model: string;
  temperature: number;
  systemPrompt: string;
  theme: 'light' | 'dark' | 'system';
  showThinkingTags: boolean;
}
