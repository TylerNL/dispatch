import type {
  AskRequest,
  Citation,
  ConversationDetail,
  ConversationSummary,
  SSEEvent,
} from '../types/ask';

export const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}

export async function listConversations(
  token: string,
): Promise<ConversationSummary[]> {
  const res = await fetch(`${API_URL}/conversations`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Failed to load conversations');
  return res.json();
}

export async function getConversation(
  id: string,
  token: string,
): Promise<ConversationDetail> {
  const res = await fetch(`${API_URL}/conversations/${id}`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Failed to load conversation');
  return res.json();
}

export async function deleteConversation(
  id: string,
  token: string,
): Promise<void> {
  const res = await fetch(`${API_URL}/conversations/${id}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Failed to delete conversation');
}

interface StreamCallbacks {
  onMeta?: (conversationId: string) => void;
  onDelta: (text: string) => void;
  onCitations: (citations: Citation[]) => void;
  onTitle?: (title: string) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

/**
 * Stream an answer from the /ask/stream endpoint.
 * Returns an AbortController so the caller can cancel mid-stream.
 */
export function streamAsk(
  request: AskRequest,
  token: string,
  callbacks: StreamCallbacks,
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_URL}/ask/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        callbacks.onError('Something went wrong — try again.');
        callbacks.onDone();
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() ?? '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6);
          if (payload === '[DONE]') {
            callbacks.onDone();
            return;
          }
          try {
            const event: SSEEvent = JSON.parse(payload);
            if (event.type === 'delta') {
              callbacks.onDelta(event.text);
            } else if (event.type === 'citations') {
              callbacks.onCitations(event.citations);
            } else if (event.type === 'meta') {
              callbacks.onMeta?.(event.conversation_id);
            } else if (event.type === 'title') {
              callbacks.onTitle?.(event.title);
            } else if (event.type === 'error') {
              callbacks.onError(
                event.error === 'forbidden'
                  ? "You don't have access to this conversation."
                  : 'Something went wrong — try again.',
              );
              callbacks.onDone();
              return;
            }
          } catch {
            // Malformed JSON line — skip it
          }
        }
      }

      callbacks.onDone();
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        callbacks.onDone();
        return;
      }
      callbacks.onError('Network error — check your connection.');
      callbacks.onDone();
    }
  })();

  return controller;
}
