"use client";

import { useCallback, useMemo, useRef, useState } from "react";

import { createLiveVisionWebSocket, LiveDetection, LiveStreamEvent } from "@/lib/ai-client";

export function useLiveVisionAgent(sessionId: string, demoMode: string) {
  const socketRef = useRef<WebSocket | null>(null);
  const lastSentRef = useRef(0);
  const [connected, setConnected] = useState(false);
  const [detections, setDetections] = useState<LiveDetection[]>([]);
  const [reasoning, setReasoning] = useState("");
  const [tokens, setTokens] = useState<string[]>([]);
  const [events, setEvents] = useState<LiveStreamEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  const appendEvent = useCallback((event: LiveStreamEvent) => {
    setEvents((prev) => [...prev, event]);
    if (event.type === "detection" && event.detections) setDetections(event.detections);
    if (event.type === "reasoning") setReasoning(event.content);
    if (event.type === "token") setTokens((prev) => [...prev, event.content]);
    if (event.type === "error") setError(event.content);
  }, []);

  const connect = useCallback(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) return;
    const ws = createLiveVisionWebSocket();
    socketRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setError("Live websocket connection failed.");
    ws.onmessage = (message) => {
      try {
        appendEvent(JSON.parse(message.data) as LiveStreamEvent);
      } catch {
        setError("Malformed live websocket event.");
      }
    };
  }, [appendEvent]);

  const disconnect = useCallback(() => {
    socketRef.current?.close();
    socketRef.current = null;
    setConnected(false);
  }, []);

  const sendFrame = useCallback(
    (frameBase64: string, frameId: string, mimeType: "image/jpeg" | "image/png" = "image/jpeg") => {
      if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;
      const now = Date.now();
      if (now - lastSentRef.current < 100) return;
      lastSentRef.current = now;
      socketRef.current.send(
        JSON.stringify({
          type: "frame",
          payload: {
            session_id: sessionId,
            frame_id: frameId,
            image_base64: frameBase64,
            mime_type: mimeType,
            demo_mode: demoMode,
          },
        }),
      );
    },
    [demoMode, sessionId],
  );

  const askQuestion = useCallback(
    (question: string) => {
      if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;
      socketRef.current.send(
        JSON.stringify({
          type: "question",
          session_id: sessionId,
          question,
          demo_mode: demoMode,
        }),
      );
    },
    [demoMode, sessionId],
  );

  return useMemo(
    () => ({
      connected,
      detections,
      reasoning,
      tokens,
      events,
      error,
      connect,
      disconnect,
      sendFrame,
      askQuestion,
    }),
    [askQuestion, connect, connected, detections, disconnect, error, events, reasoning, sendFrame, tokens],
  );
}
