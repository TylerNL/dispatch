export interface Citation {
  item_id: string;
  title: string;
  url: string;
  source: string;
  published_at: string | null;
  snippet: string | null;
}

export type TimeWindow = 'today' | 'week' | 'month' | 'year' | 'all';

export type Topic =
  | 'research'
  | 'labs'
  | 'startups'
  | 'community'
  | 'security'
  | 'signal';

export interface AskRequest {
  question: string;
  window?: TimeWindow;
  topic?: Topic | null;
  sources?: string[] | null;
}

export interface DeltaEvent {
  type: 'delta';
  text: string;
}

export interface CitationsEvent {
  type: 'citations';
  citations: Citation[];
}

export type SSEEvent = DeltaEvent | CitationsEvent;

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  isStreaming?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
}
