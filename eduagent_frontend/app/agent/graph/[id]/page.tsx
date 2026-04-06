"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import Navbar from "@/components/layout/Navbar";
import { useGraphSessions } from "@/hooks/useGraphSessions";
import { useGraphChat } from "@/hooks/useGraphChat";
import { ChatMessage } from "@/lib/types";

export default function GraphChatPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { sessions, saveMessages } = useGraphSessions();
  // Derive session reactively — sessions load async from disk
  const session = sessions.find(s => s.id === id);

  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesRef = useRef<ChatMessage[]>([]); // live ref to current messages for saving

  // Save the full conversation (user + AI) in one shot after each AI response
  // messagesRef is already up-to-date with the final content — just filter out empty placeholders
  const handleMessageComplete = useCallback((_msg: ChatMessage) => {
    saveMessages(id, messagesRef.current.filter(m => m.content));
  }, [id, saveMessages]);

  const { messages, isStreaming, sendMessage, cancel } = useGraphChat({
    sessionId: id,
    model: session?.model ?? "openai:gpt-4.1-mini",
    initialMessages: session?.messages ?? [],
    onMessageComplete: handleMessageComplete,
  });

  // Keep messagesRef in sync for use in handleMessageComplete
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  // Auto-send firstQuery once session loads (fresh sessions only — 0 messages means never started)
  const didAutoSend = useRef(false);
  useEffect(() => {
    if (!didAutoSend.current && session && session.messages.length === 0 && session.firstQuery) {
      didAutoSend.current = true;
      sendMessage(session.firstQuery);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.id]);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput("");
    sendMessage(text);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, isStreaming, sendMessage]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleTextareaChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  }, []);

  // Still loading sessions from disk
  if (sessions.length === 0 && !session) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg)" }}>
        <p style={{ color: "var(--text-muted)" }}>Loading…</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg)" }}>
        <p style={{ color: "var(--text-muted)" }}>Session not found.</p>
      </div>
    );
  }

  const turnCount = Math.ceil(messages.filter(m => m.role === "user").length);

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--bg)" }}>
      <Navbar />

      {/* Back bar */}
      <div
        className="sticky top-0 z-10 flex items-center gap-3 px-6 py-3 border-b"
        style={{ background: "var(--bg)", borderColor: "var(--border)" }}
      >
        <button
          onClick={() => router.push("/agent?tab=graph-traversal")}
          className="flex items-center gap-1.5 text-sm transition-colors"
          style={{ color: "var(--text-muted)" }}
          onMouseEnter={e => (e.currentTarget.style.color = "var(--text-primary)")}
          onMouseLeave={e => (e.currentTarget.style.color = "var(--text-muted)")}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 5l-7 7 7 7" />
          </svg>
          Graph Traversal
        </button>
        <span style={{ color: "var(--border)" }}>·</span>
        <span className="text-sm truncate max-w-lg" style={{ color: "var(--text-secondary)" }}>
          {session.firstQuery}
        </span>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-6 py-8 space-y-6">
          {messages.map((msg, i) => (
            // Skip empty assistant placeholder — TypingIndicator handles that state
            msg.role === "assistant" && !msg.content ? null : (
              <ChatBubble key={i} message={msg} />
            )
          ))}

          {isStreaming && (
            messages[messages.length - 1]?.role === "assistant" && !messages[messages.length - 1]?.content
              ? <TypingIndicator />
              : null
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input area */}
      <div
        className="sticky bottom-0 border-t"
        style={{ background: "var(--bg)", borderColor: "var(--border)" }}
      >
        <div className="mx-auto max-w-3xl px-6 py-4">
          <div
            className="flex items-end gap-3 rounded-xl border px-4 py-3"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder={isStreaming ? "Thinking…" : "Ask a follow-up question…"}
              disabled={isStreaming}
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm outline-none"
              style={{
                color: "var(--text-primary)",
                minHeight: "24px",
                maxHeight: "160px",
              }}
            />
            {isStreaming ? (
              <button
                onClick={cancel}
                className="flex-shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors"
                style={{ background: "var(--surface-alt)", color: "var(--text-muted)" }}
              >
                Stop
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="flex-shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-40"
                style={{ background: "var(--text-primary)", color: "var(--bg)" }}
              >
                Send
              </button>
            )}
          </div>
          <p className="mt-2 text-center text-xs" style={{ color: "var(--text-muted)" }}>
            {turnCount > 0 ? `${turnCount} turn${turnCount !== 1 ? "s" : ""} · ` : ""}Model: {session.model}
          </p>
        </div>
      </div>
    </div>
  );
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`rounded-2xl px-4 py-3 text-sm max-w-[85%] ${isUser ? "rounded-tr-sm" : "rounded-tl-sm"}`}
        style={
          isUser
            ? { background: "var(--text-primary)", color: "var(--bg)" }
            : { background: "var(--surface)", color: "var(--text-primary)", border: "1px solid var(--border)" }
        }
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none" style={{ color: "inherit" }}>
            <ReactMarkdown
              components={{
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent, #3b82f6)" }}>
                    {children}
                  </a>
                ),
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="mb-2 ml-4 list-disc space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal space-y-1">{children}</ol>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                code: ({ children }) => (
                  <code className="rounded px-1 py-0.5 text-xs font-mono" style={{ background: "var(--surface-alt)" }}>
                    {children}
                  </code>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div
        className="rounded-2xl rounded-tl-sm px-4 py-3 border"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex gap-1 items-center h-4">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full animate-bounce"
              style={{
                background: "var(--text-muted)",
                animationDelay: `${i * 150}ms`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
