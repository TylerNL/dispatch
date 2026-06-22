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
  conversation_id?: string;
  title?: string | null;
}

export interface MetaEvent {
  type: 'meta';
  conversation_id: string;
}

export interface DeltaEvent {
  type: 'delta';
  text: string;
}

export interface CitationsEvent {
  type: 'citations';
  citations: Citation[];
}

export interface TitleEvent {
  type: 'title';
  title: string;
}

export interface ErrorEvent {
  type: 'error';
  error: string;
}

export type SSEEvent =
  | MetaEvent
  | DeltaEvent
  | CitationsEvent
  | TitleEvent
  | ErrorEvent;

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

export interface ConversationSummary {
  id: string;
  title: string | null;
  updated_at: string;
}

export interface MessageOut {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[] | null;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string | null;
  messages: MessageOut[];
}
