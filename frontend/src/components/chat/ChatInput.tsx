import { useRef, useCallback, type KeyboardEvent } from 'react';
import { Send, Square } from 'lucide-react';

interface ChatInputProps {
  onSend: (text: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export default function ChatInput({
  onSend,
  onStop,
  isStreaming,
  disabled = false,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const resetHeight = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, []);

  const handleSend = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    const text = el.value.trim();
    if (!text || disabled) return;
    onSend(text);
    el.value = '';
    el.style.height = 'auto';
    el.focus();
  }, [onSend, disabled]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (isStreaming) return;
        handleSend();
      }
    },
    [handleSend, isStreaming],
  );

  return (
    <div className="border-t border-border bg-bg px-4 py-3 sm:px-6">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-end gap-3 rounded-xl bg-bg-card border border-border px-4 py-3 focus-within:border-accent transition-colors duration-200">
          <textarea
            ref={textareaRef}
            rows={1}
            placeholder="Ask dispatch anything..."
            disabled={disabled}
            onInput={resetHeight}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none bg-transparent text-[15px] text-text placeholder:text-text-mute outline-none leading-relaxed max-h-[200px]"
          />
          {isStreaming ? (
            <button
              type="button"
              onClick={onStop}
              className="flex items-center justify-center w-8 h-8 rounded-lg bg-red-500/15 text-red-400 hover:bg-red-500/25 transition-colors shrink-0"
              aria-label="Stop generating"
            >
              <Square className="w-3.5 h-3.5" fill="currentColor" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSend}
              disabled={disabled}
              className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent text-bg hover:bg-accent-hover transition-colors disabled:opacity-40 shrink-0"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>
        <p className="mt-2 text-center font-mono text-[10.5px] text-text-mute tracking-wide">
          dispatch &middot; AI-powered tech news
        </p>
      </div>
    </div>
  );
}
