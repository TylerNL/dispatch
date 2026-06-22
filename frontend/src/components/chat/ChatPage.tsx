import { useCallback, useEffect, useRef, useState } from 'react';
import { Navigate, useNavigate, useParams } from 'react-router-dom';
import { Menu, Sparkles } from 'lucide-react';
import { chips } from '../../lib/chips';
import {
  deleteConversation,
  getConversation,
  listConversations,
  streamAsk,
} from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import type {
  ChatMessage,
  Citation,
  ConversationSummary,
  TimeWindow,
} from '../../types/ask';
import Sidebar from './Sidebar';
import MessageList from './MessageList';
import ChatInput from './ChatInput';

const TIME_WINDOWS: { label: string; value: TimeWindow }[] = [
  { label: 'Today', value: 'today' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'Year', value: 'year' },
  { label: 'All', value: 'all' },
];

function createId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

// Replace the last assistant message in the list via an updater.
function patchLastAssistant(
  messages: ChatMessage[],
  patch: (m: ChatMessage) => ChatMessage,
): ChatMessage[] {
  const msgs = [...messages];
  const last = msgs[msgs.length - 1];
  if (last?.role === 'assistant') msgs[msgs.length - 1] = patch(last);
  return msgs;
}

export default function ChatPage() {
  const { user, loading, session } = useAuth();
  const token = session?.access_token;
  const { id: routeId } = useParams();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('all');
  const abortRef = useRef<AbortController | null>(null);
  const loadedRef = useRef<string | null>(null); 

  useEffect(() => {
    if (!token) return;
    listConversations(token).then(setConversations).catch(() => {});
  }, [token]);

  useEffect(() => {
    if (!token) return;
    if (!routeId) {
      setMessages([]);
      loadedRef.current = null;
      return;
    }
    if (loadedRef.current === routeId) return;
    getConversation(routeId, token)
      .then((detail) => {
        setMessages(
          detail.messages.map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            citations: m.citations ?? undefined,
          })),
        );
        loadedRef.current = routeId;
      })
      .catch(() => navigate('/chat'));
  }, [routeId, token, navigate]);

  const handleSend = useCallback(
    (text: string) => {
      if (isStreaming || !token) return;

      const convId = routeId ?? crypto.randomUUID();
      const title = text.length > 60 ? text.slice(0, 60) + '...' : text;

      if (!routeId) {
        loadedRef.current = convId;
        setConversations((prev) => [
          { id: convId, title, updated_at: new Date().toISOString() },
          ...prev,
        ]);
        navigate(`/chat/${convId}`);
      }

      const userMsg: ChatMessage = { id: createId(), role: 'user', content: text };
      const assistantMsg: ChatMessage = {
        id: createId(),
        role: 'assistant',
        content: '',
        isStreaming: true,
      };
      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsStreaming(true);

      abortRef.current = streamAsk(
        { question: text, window: timeWindow, conversation_id: convId, title },
        token,
        {
          onDelta: (chunk) =>
            setMessages((prev) =>
              patchLastAssistant(prev, (m) => ({ ...m, content: m.content + chunk })),
            ),
          onCitations: (citations: Citation[]) =>
            setMessages((prev) => patchLastAssistant(prev, (m) => ({ ...m, citations }))),
          onTitle: (newTitle) =>
            setConversations((prev) =>
              prev.map((c) => (c.id === convId ? { ...c, title: newTitle } : c)),
            ),
          onDone: () => {
            setMessages((prev) =>
              patchLastAssistant(prev, (m) => ({ ...m, isStreaming: false })),
            );
            setIsStreaming(false);
            abortRef.current = null;
          },
          onError: (error) => {
            setMessages((prev) =>
              patchLastAssistant(prev, (m) => ({
                ...m,
                content: error,
                isStreaming: false,
              })),
            );
            setIsStreaming(false);
            abortRef.current = null;
          },
        },
      );
    },
    [isStreaming, token, routeId, timeWindow, navigate],
  );

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const handleNewChat = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
    navigate('/chat');
  }, [navigate]);

  const handleSelect = useCallback(
    (id: string) => {
      if (id === routeId) return;
      abortRef.current?.abort();
      abortRef.current = null;
      setIsStreaming(false);
      navigate(`/chat/${id}`);
    },
    [routeId, navigate],
  );

  const handleDelete = useCallback(
    (id: string) => {
      if (!token) return;
      deleteConversation(id, token)
        .then(() => {
          setConversations((prev) => prev.filter((c) => c.id !== id));
          if (routeId === id) navigate('/chat');
        })
        .catch(() => {});
    },
    [token, routeId, navigate],
  );

  if (loading) return null;
  if (!user) return <Navigate to="/" replace />;

  const conversationTitle =
    conversations.find((c) => c.id === routeId)?.title ?? 'New conversation';

  return (
    <div className="flex h-screen bg-bg text-text overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={routeId ?? null}
        onSelect={handleSelect}
        onNew={handleNewChat}
        onDelete={handleDelete}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <div className="flex items-center gap-3 px-4 sm:px-6 h-[56px] border-b border-border shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="flex items-center justify-center w-8 h-8 rounded-lg text-text-dim hover:text-text hover:bg-bg-elev transition-colors md:hidden"
            aria-label="Open sidebar"
          >
            <Menu className="w-4.5 h-4.5" />
          </button>

          <h1 className="text-[14px] font-medium text-text truncate">
            {conversationTitle}
          </h1>

          <div className="ml-auto flex items-center gap-1">
            {TIME_WINDOWS.map((tw) => (
              <button
                key={tw.value}
                onClick={() => setTimeWindow(tw.value)}
                className={`
                  px-2.5 py-1 rounded-md text-[11.5px] font-medium transition-colors duration-150
                  ${
                    timeWindow === tw.value
                      ? 'bg-accent/15 text-accent'
                      : 'text-text-mute hover:text-text-dim hover:bg-bg-elev'
                  }
                `}
              >
                {tw.label}
              </button>
            ))}
          </div>
        </div>

        {/* Messages or empty state */}
        {messages.length === 0 ? (
          <EmptyState onPrompt={handleSend} />
        ) : (
          <MessageList messages={messages} />
        )}

        {/* Input bar */}
        <ChatInput onSend={handleSend} onStop={handleStop} isStreaming={isStreaming} />
      </div>
    </div>
  );
}

function EmptyState({ onPrompt }: { onPrompt: (text: string) => void }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
      <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-accent/10 mb-5">
        <Sparkles className="w-5 h-5 text-accent" />
      </div>
      <h2 className="text-[20px] font-medium text-text tracking-tight">
        Ask dispatch anything
      </h2>
      <p className="mt-2 text-[14px] text-text-dim max-w-[400px] text-center leading-relaxed">
        Search and ask questions across thousands of indexed tech news articles,
        papers, and discussions.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-2 max-w-[560px]">
        {chips.map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => onPrompt(chip)}
            className="rounded-full bg-bg-elev border border-border px-3.5 py-2 text-[12.5px] text-text-dim hover:border-border-hover hover:text-text transition-colors duration-150"
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  );
}