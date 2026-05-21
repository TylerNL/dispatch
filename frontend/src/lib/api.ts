import type { AskRequest, Citation, SSEEvent } from '../types/ask';

export const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface StreamCallbacks {
  onDelta: (text: string) => void;
  onCitations: (citations: Citation[]) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

/**
 * Stream an answer from the /ask/stream endpoint.
 * Returns an AbortController so the caller can cancel mid-stream.
 */
export function streamAsk(
  request: AskRequest,
  callbacks: StreamCallbacks,
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_URL}/ask/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
