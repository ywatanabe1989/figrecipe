/**
 * Chat wiring for FigRecipe — connects the shell AI chat UI to the backend.
 *
 * Uses scitex-ui's chat modules (stream handler, storage, history, markdown).
 * The SSE endpoint is figrecipe's `api/chat/stream` (POST, JSON body).
 */

import {
  processStream,
  renderMarkdown,
  highlightCodeBlocks,
  fixExternalLinks,
  saveMessage,
  loadMessages,
  clearMessages,
  loadHistory,
  pushHistory,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat";
import type {
  ChatAdapter,
  StreamContext,
  StoredMessage,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat";
import type { ImageInputManager } from "@scitex/ui/src/scitex_ui/static/scitex_ui/ts/shell/chat/_image-input";

/** Restore persisted messages into the messages container. */
function restoreMessages(messagesEl: HTMLElement): void {
  const stored = loadMessages();
  for (const msg of stored) {
    const el = document.createElement("div");
    el.className = `stx-shell-ai-msg ${msg.role}`;
    if (msg.role === "user") {
      el.textContent = msg.text;
    } else if (msg.role === "assistant") {
      el.innerHTML = renderMarkdown(msg.text);
      highlightCodeBlocks(el);
      fixExternalLinks(el);
    } else if (msg.role === "error") {
      el.textContent = msg.text;
    }
    messagesEl.appendChild(el);
  }
  // Scroll to bottom after restore
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

/** Create user message element and append to messages container. */
function appendUserMessage(messagesEl: HTMLElement, text: string): void {
  const el = document.createElement("div");
  el.className = "stx-shell-ai-msg user";
  el.textContent = text;
  messagesEl.appendChild(el);
  saveMessage({ role: "user", text });
}

/** Create assistant message element (empty, to be filled by stream). */
function createAssistantBubble(messagesEl: HTMLElement): HTMLElement {
  const el = document.createElement("div");
  el.className = "stx-shell-ai-msg assistant";
  messagesEl.appendChild(el);
  return el;
}

/** Build chat history array from stored messages for the API. */
function buildApiHistory(): { role: string; content: string }[] {
  const stored = loadMessages();
  return stored
    .filter((m) => m.role === "user" || m.role === "assistant")
    .map((m) => ({ role: m.role, content: m.text }));
}

/** Send message to figrecipe's SSE chat endpoint. */
async function sendToBackend(
  prompt: string,
  images?: string[],
): Promise<Response> {
  const history = buildApiHistory();
  const body: Record<string, unknown> = { prompt, history };
  if (images && images.length > 0) {
    body.images = images;
  }
  const resp = await fetch("api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`Chat API error: HTTP ${resp.status}`);
  }
  return resp;
}

/**
 * Initialize chat wiring.
 *
 * Call this once after DOM is ready. Binds Enter-to-send, C-p/C-n history,
 * restores persisted messages, and streams AI responses.
 */
export function initChatWiring(options?: {
  imageInput?: ImageInputManager | null;
}): void {
  const messagesEl = document.getElementById("stx-shell-ai-messages");
  const inputEl = document.getElementById(
    "stx-shell-ai-input",
  ) as HTMLTextAreaElement | null;

  if (!messagesEl || !inputEl) {
    console.warn(
      "[figrecipe] Chat elements not found (#stx-shell-ai-messages or #stx-shell-ai-input)",
    );
    return;
  }

  // Restore persisted conversation
  restoreMessages(messagesEl);

  // Command history state
  let history = loadHistory();
  let historyIdx = -1;
  let savedDraft = "";

  // Track whether a request is in flight
  let sending = false;

  /** Handle sending a chat message. */
  async function handleSend(): Promise<void> {
    const text = inputEl!.value.trim();
    if (!text || sending) return;

    sending = true;
    inputEl!.value = "";
    inputEl!.style.height = "auto";
    historyIdx = -1;
    savedDraft = "";

    // Push to command history
    history = pushHistory(history, text);

    // Collect attached images if any
    let images: string[] | undefined;
    if (options?.imageInput) {
      const attachments = options.imageInput.getAttachmentsAsBase64();
      if (attachments.length > 0) {
        images = attachments.map((a) => `data:${a.mime};base64,${a.base64}`);
        options.imageInput.clear();
      }
    }

    // Show user message
    appendUserMessage(messagesEl!, text);
    messagesEl!.scrollTop = messagesEl!.scrollHeight;

    // Create assistant bubble and stream response
    const assistantEl = createAssistantBubble(messagesEl!);
    const streamCtx: StreamContext = {
      messagesEl: messagesEl!,
      modelBadge: document.querySelector(".stx-shell-ai-model-badge"),
      speak: () => {}, // No auto-speak for figrecipe
      autoSpeak: false,
      scrollIfNeeded: () => {
        messagesEl!.scrollTop = messagesEl!.scrollHeight;
      },
    };

    try {
      const resp = await sendToBackend(text, images);
      await processStream(resp, assistantEl, streamCtx);
    } catch (err) {
      assistantEl.remove();
      const errEl = document.createElement("div");
      errEl.className = "stx-shell-ai-msg error";
      errEl.textContent = `Chat error: ${err instanceof Error ? err.message : String(err)}`;
      messagesEl!.appendChild(errEl);
      saveMessage({ role: "error", text: errEl.textContent });
    }

    // Final scroll
    messagesEl!.scrollTop = messagesEl!.scrollHeight;
    sending = false;
  }

  // Enter to send (Shift+Enter for newline)
  inputEl.addEventListener("keydown", (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
      return;
    }

    // C-p / ArrowUp — previous history
    if (
      (e.key === "ArrowUp" || (e.ctrlKey && e.key === "p")) &&
      inputEl!.selectionStart === 0
    ) {
      e.preventDefault();
      if (historyIdx === -1) {
        savedDraft = inputEl!.value;
      }
      if (historyIdx < history.length - 1) {
        historyIdx++;
        inputEl!.value = history[historyIdx];
      }
      return;
    }

    // C-n / ArrowDown — next history
    if (
      (e.key === "ArrowDown" || (e.ctrlKey && e.key === "n")) &&
      inputEl!.selectionEnd === inputEl!.value.length
    ) {
      e.preventDefault();
      if (historyIdx > 0) {
        historyIdx--;
        inputEl!.value = history[historyIdx];
      } else if (historyIdx === 0) {
        historyIdx = -1;
        inputEl!.value = savedDraft;
      }
      return;
    }
  });

  // Auto-resize textarea as user types
  inputEl.addEventListener("input", () => {
    inputEl!.style.height = "auto";
    inputEl!.style.height = Math.min(inputEl!.scrollHeight, 150) + "px";
  });

  // Clear chat on custom event (for toolbar clear button if it exists)
  document.addEventListener("stx-shell:clear-chat", () => {
    clearMessages();
    messagesEl!.innerHTML = "";
    history = loadHistory();
    historyIdx = -1;
  });

  console.log("[figrecipe] Chat wiring initialized");
}
