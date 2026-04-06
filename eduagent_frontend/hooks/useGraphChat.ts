"use client";
import { useState, useCallback, useRef, useEffect } from "react";
import { ChatMessage } from "@/lib/types";

interface UseGraphChatOptions {
  sessionId: string;
  model: string;
  initialMessages?: ChatMessage[];
  onMessageComplete?: (message: ChatMessage) => void;
}

export function useGraphChat({
  sessionId,
  model,
  initialMessages = [],
  onMessageComplete,
}: UseGraphChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const seededRef = useRef(false);

  // When sessions load from disk, seed messages once (only if not yet streaming/populated)
  useEffect(() => {
    if (!seededRef.current && initialMessages.length > 0 && messages.length === 0) {
      seededRef.current = true;
      setMessages(initialMessages);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialMessages.length]);

  const sendMessage = useCallback(async (text: string) => {
    if (isStreaming || !text.trim()) return;

    // Add user message
    const userMsg: ChatMessage = {
      role: "user",
      content: text.trim(),
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, userMsg]);

    // Placeholder AI message for streaming into
    const aiMsg: ChatMessage = {
      role: "assistant",
      content: "",
      timestamp: Date.now(),
    };
    setMessages(prev => [...prev, aiMsg]);
    setIsStreaming(true);

    abortRef.current = new AbortController();
    let accumulated = "";
    let currentMsgId: string | null = null;

    try {
      const res = await fetch("/api/graph/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, message: text.trim(), model }),
        signal: abortRef.current.signal,
      });

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw || raw === "[DONE]") continue;

          try {
            const parsed = JSON.parse(raw);
            // LangGraph messages/partial format: [message_chunk] (single-element array)
            const chunk = Array.isArray(parsed) ? parsed[0] : parsed;
            if (
              chunk &&
              (chunk.type === "AIMessageChunk" || chunk.type === "ai") &&
              typeof chunk.content === "string" &&
              chunk.content
            ) {
              // Reset accumulator when a new LLM message starts (e.g. intent
              // classification vs. synthesis are separate streamed messages).
              // The synthesis message is always last so we always end up with prose.
              if (chunk.id && chunk.id !== currentMsgId) {
                currentMsgId = chunk.id;
                accumulated = "";
              }
              // LangGraph messages/partial sends CUMULATIVE content, not deltas
              accumulated = chunk.content;
              // Don't display internal JSON (classification step) — only show prose
              if (!accumulated.startsWith("{")) {
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = { ...aiMsg, content: accumulated };
                  return updated;
                });
              }
            }
          } catch {
            // Non-JSON line — skip
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        // Cancelled — leave partial content
      } else {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...aiMsg,
            content: accumulated || "Something went wrong. Please try again.",
          };
          return updated;
        });
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;

      // Notify parent with the completed message
      if (accumulated && onMessageComplete) {
        onMessageComplete({ ...aiMsg, content: accumulated });
      }
    }
  }, [sessionId, model, isStreaming, onMessageComplete]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { messages, isStreaming, sendMessage, cancel };
}
