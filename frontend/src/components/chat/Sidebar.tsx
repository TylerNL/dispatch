import { Link } from 'react-router-dom';
import { Plus, MessageSquare, X } from 'lucide-react';
import type { Conversation } from '../../types/ask';

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  isOpen,
  onClose,
}: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed md:relative z-50 md:z-auto
          top-0 left-0 h-full
          w-[280px] shrink-0
          bg-bg-card border-r border-border
          flex flex-col
          transition-transform duration-200 ease-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 h-[56px] border-b border-border shrink-0">
          <Link to="/" className="flex items-center gap-2 group">
            <span className="text-[15px] font-medium tracking-[-0.015em] text-text">
              dispatch
            </span>
          </Link>
          <div className="flex items-center gap-1">
            <button
              onClick={onNew}
              className="flex items-center justify-center w-8 h-8 rounded-lg text-text-dim hover:text-text hover:bg-bg-elev transition-colors"
              aria-label="New chat"
            >
              <Plus className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="flex items-center justify-center w-8 h-8 rounded-lg text-text-dim hover:text-text hover:bg-bg-elev transition-colors md:hidden"
              aria-label="Close sidebar"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto py-2 px-2">
          {conversations.length === 0 && (
            <p className="px-3 py-6 text-[12.5px] text-text-mute text-center">
              No conversations yet
            </p>
          )}
          {conversations.map((conv) => {
            const isActive = conv.id === activeId;
            return (
              <button
                key={conv.id}
                onClick={() => {
                  onSelect(conv.id);
                  onClose();
                }}
                className={`
                  w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left
                  transition-colors duration-100 group
                  ${
                    isActive
                      ? 'bg-bg-elev border-l-2 border-accent text-text'
                      : 'text-text-dim hover:text-text hover:bg-bg-elev/50 border-l-2 border-transparent'
                  }
                `}
              >
                <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-50" />
                <span className="text-[13px] truncate">{conv.title}</span>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-border shrink-0">
          <p className="font-mono text-[10px] text-text-mute tracking-wide uppercase">
            dispatch chat &middot; beta
          </p>
        </div>
      </aside>
    </>
  );
}
