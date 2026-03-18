/**
 * DjangoChatBackend — connects to figrecipe's Django SSE chat endpoint.
 * Implements ChatBackend interface from scitex-ui workspace shell.
 */

import type {
  ChatBackend,
  ChatChunk,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/shell/workspace/types";

export class DjangoChatBackend implements ChatBackend {
  private baseUrl: string;

  constructor(baseUrl: string = "") {
    this.baseUrl = baseUrl;
  }

  async *sendMessage(
    prompt: string,
    context?: Record<string, unknown>,
  ): AsyncIterable<ChatChunk> {
    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, context, history: [] }),
      });
    } catch (err) {
      yield {
        type: "error",
        text: `Chat unavailable: ${err instanceof Error ? err.message : "network error"}`,
      };
      return;
    }

    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: "Chat failed" }));
      yield { type: "error", text: err.error || `HTTP ${response.status}` };
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      yield { type: "error", text: "No response body" };
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = line.slice(6);
        if (data === "[DONE]") {
          yield { type: "done" };
          return;
        }
        try {
          const parsed = JSON.parse(data);
          if (parsed.type === "chunk") {
            yield { type: "text", text: parsed.text };
          } else if (parsed.type === "error") {
            yield { type: "error", text: parsed.error };
          }
        } catch {
          // skip malformed SSE
        }
      }
    }

    yield { type: "done" };
  }
}
