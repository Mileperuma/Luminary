import { useEffect, useRef, useState } from "react";

import Button from "./Button";
import { sendChatMessage, startChat } from "../lib/chat";
import type { ChatSessionType } from "../lib/chat";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  sessionType: ChatSessionType;
  onFinished?: (capturedPreferences: number) => void;
}

/** A simple, accessible chat panel. Works for both onboarding and general chat. */
export default function ChatPanel({ sessionType, onFinished }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finished, setFinished] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  // Bootstrap a session on mount.
  useEffect(() => {
    let cancelled = false;
    async function init() {
      try {
        const start = await startChat(sessionType);
        if (cancelled) return;
        setSessionId(start.session_id);
        setMessages([{ role: "assistant", content: start.opening_message }]);
      } catch {
        if (!cancelled) setError("Could not start the chat. Refresh and try again.");
      }
    }
    void init();
    return () => {
      cancelled = true;
    };
  }, [sessionType]);

  // Auto-scroll the log on every new message.
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages]);

  async function send() {
    if (!sessionId || !input.trim() || loading || finished) return;
    const content = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content }]);
    setLoading(true);
    setError(null);
    try {
      const reply = await sendChatMessage({ session_id: sessionId, content });
      setMessages((m) => [...m, { role: "assistant", content: reply.assistant_message }]);
      if (reply.finished) {
        setFinished(true);
        onFinished?.(reply.captured_preferences);
      }
    } catch {
      setError("Could not send that message. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-card border border-line rounded-lg shadow-soft flex flex-col h-[500px] max-h-[60vh]">
      <div ref={logRef} className="flex-1 overflow-y-auto p-4 space-y-3" role="log" aria-live="polite">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              "max-w-[85%] px-3 py-2 rounded-lg text-sm leading-relaxed " +
              (m.role === "assistant"
                ? "bg-line/40 text-ink mr-auto"
                : "bg-ink text-cream ml-auto")
            }
          >
            {m.content}
          </div>
        ))}
        {loading && (
          <div className="text-xs text-muted italic">Luminary is thinking…</div>
        )}
      </div>

      {error && (
        <p role="alert" className="text-sm text-ink bg-line/40 px-4 py-2 border-t border-line">
          {error}
        </p>
      )}

      <form
        onSubmit={(e) => { e.preventDefault(); void send(); }}
        className="flex gap-2 border-t border-line p-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={finished ? "This chat is complete." : "Type a message…"}
          disabled={finished || loading}
          aria-label="Your message"
          className="flex-1 px-3 py-2 bg-card text-ink border border-line rounded-lg
                     focus:border-accent focus:ring-1 focus:ring-accent outline-none
                     placeholder:text-muted/70 disabled:opacity-50"
        />
        <div className="w-24">
          <Button type="submit" loading={loading} disabled={finished || !input.trim()}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
}
