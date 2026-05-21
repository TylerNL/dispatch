import { useCallback, useRef, useState } from 'react';
import { Menu, Sparkles } from 'lucide-react';
import { chips } from '../../lib/chips';
import { streamAsk } from '../../lib/api';
import type {
  ChatMessage,
  Citation,
  Conversation,
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

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('all');
  const abortRef = useRef<AbortController | null>(null);

  const activeConv = conversations.find((c) => c.id === activeId) ?? null;
  const messages = activeConv?.messages ?? [];


  const ensureConversation = useCallback(
    (firstMessage: string): string => {
      if (activeId) return activeId;
      const id = createId();
      const title =
        firstMessage.length > 60
          ? firstMessage.slice(0, 60) + '...'
          : firstMessage;
      const newConv: Conversation = {
        id,
        title,
        messages: [],
        createdAt: Date.now(),
      };
      setConversations((prev) => [newConv, ...prev]);
      setActiveId(id);
      return id;
    },
    [activeId],
  );

  const handleSend = useCallback(
    (text: string) => {
      if (isStreaming) return;

      const convId = ensureConversation(text);
      const userMsg: ChatMessage = {
        id: createId(),
        role: 'user',
        content: text,
      };
      const assistantMsg: ChatMessage = {
        id: createId(),
        role: 'assistant',
        content: '',
        isStreaming: true,
      };

      setConversations((prev) =>
        prev.map((c) =>
          c.id === convId
            ? { ...c, messages: [...c.messages, userMsg, assistantMsg] }
            : c,
        ),
      );

      setIsStreaming(true);

      const controller = streamAsk(
        { question: text, window: timeWindow },
        {
          onDelta: (chunk) => {
            setConversations((prev) =>
              prev.map((c) => {
                if (c.id !== convId) return c;
                const msgs = [...c.messages];
                const last = msgs[msgs.length - 1];
                if (last.role === 'assistant') {
                  msgs[msgs.length - 1] = {
                    ...last,
                    content: last.content + chunk,
                  };
                }
                return { ...c, messages: msgs };
              }),
            );
          },
          onCitations: (citations: Citation[]) => {
            setConversations((prev) =>
              prev.map((c) => {
                if (c.id !== convId) return c;
                const msgs = [...c.messages];
                const last = msgs[msgs.length - 1];
                if (last.role === 'assistant') {
                  msgs[msgs.length - 1] = { ...last, citations };
                }
                return { ...c, messages: msgs };
              }),
            );
          },
          onDone: () => {
            setConversations((prev) =>
              prev.map((c) => {
                if (c.id !== convId) return c;
                const msgs = [...c.messages];
                const last = msgs[msgs.length - 1];
                if (last.role === 'assistant') {
                  msgs[msgs.length - 1] = { ...last, isStreaming: false };
                }
                return { ...c, messages: msgs };
              }),
            );
            setIsStreaming(false);
            abortRef.current = null;
          },
          onError: (error) => {
            setConversations((prev) =>
              prev.map((c) => {
                if (c.id !== convId) return c;
                const msgs = [...c.messages];
                const last = msgs[msgs.length - 1];
                if (last.role === 'assistant') {
                  msgs[msgs.length - 1] = {
                    ...last,
                    content: error,
                    isStreaming: false,
                  };
                }
                return { ...c, messages: msgs };
              }),
            );
            setIsStreaming(false);
            abortRef.current = null;
          },
        },
      );

      abortRef.current = controller;
    },
    [isStreaming, ensureConversation, timeWindow],
  );

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const handleNewChat = useCallback(() => {
    setActiveId(null);
    setIsStreaming(false);
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const handleSelectConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const conversationTitle = activeConv?.title ?? 'New conversation';

  return (
    <div className="flex h-screen bg-bg text-text overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelectConversation}
        onNew={handleNewChat}
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
        <ChatInput
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
        />
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
