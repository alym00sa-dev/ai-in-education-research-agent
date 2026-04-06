"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { GraphSession, ChatMessage } from "@/lib/types";

async function apiSave(session: GraphSession) {
  await fetch("/api/graph/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(session),
  });
}

async function apiDelete(id: string) {
  await fetch("/api/graph/sessions", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  });
}

export function useGraphSessions() {
  const [sessions, setSessions] = useState<GraphSession[]>([]);
  const sessionMap = useRef<Map<string, GraphSession>>(new Map());

  // Load all sessions from disk on mount
  useEffect(() => {
    fetch("/api/graph/sessions")
      .then(r => r.json())
      .then(({ sessions: loaded }) => {
        if (Array.isArray(loaded)) {
          setSessions(loaded);
          sessionMap.current = new Map(loaded.map((s: GraphSession) => [s.id, s]));
        }
      })
      .catch(() => {});
  }, []);

  const addSession = useCallback((session: GraphSession) => {
    sessionMap.current.set(session.id, session);
    setSessions(prev => [session, ...prev]);
    apiSave(session);
  }, []);

  const appendMessage = useCallback((id: string, message: ChatMessage) => {
    setSessions(prev => {
      const updated = prev.map(s => {
        if (s.id !== id) return s;
        const next = { ...s, messages: [...s.messages, message], updatedAt: Date.now() };
        sessionMap.current.set(id, next);
        apiSave(next);
        return next;
      });
      return updated;
    });
  }, []);

  // Save the full messages array in one shot — avoids stale-prev race conditions
  const saveMessages = useCallback((id: string, messages: ChatMessage[]) => {
    setSessions(prev => {
      const updated = prev.map(s => {
        if (s.id !== id) return s;
        const next = { ...s, messages, updatedAt: Date.now() };
        sessionMap.current.set(id, next);
        apiSave(next);
        return next;
      });
      return updated;
    });
  }, []);

  const removeSession = useCallback((id: string) => {
    sessionMap.current.delete(id);
    setSessions(prev => prev.filter(s => s.id !== id));
    apiDelete(id);
  }, []);

  const getSession = useCallback((id: string): GraphSession | undefined => {
    // Fast path: in-memory map (populated after load)
    if (sessionMap.current.has(id)) return sessionMap.current.get(id);
    // Fallback: linear scan of state
    return sessions.find(s => s.id === id);
  }, [sessions]);

  return { sessions, addSession, appendMessage, saveMessages, removeSession, getSession };
}
