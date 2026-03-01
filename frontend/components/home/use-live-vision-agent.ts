"use client";

import { useCallback, useMemo, useRef, useState } from "react";

import { createLiveVisionWebSocket, LiveDetection, LiveStreamEvent } from "@/lib/ai-client";

export type BrainState = "FOCUSED" | "DISTRACTED" | "AWAY" | "SUSPICIOUS" | "ACTIVE" | "IDLE" | "INITIALIZING";

export type StateTransition = {
  previous: string;
  new: string;
  reason: string;
  confidence: number;
  timestamp: string;
};

export type AlertEvent = {
  level: string;
  title: string;
  message: string;
  state: string;
  timestamp: string;
};

export function useLiveVisionAgent(sessionId: string, demoMode: string) {
  const socketRef = useRef<WebSocket | null>(null);
  const lastSentRef = useRef(0);
  const [connected, setConnected] = useState(false);
  const [detections, setDetections] = useState<LiveDetection[]>([]);
  const [reasoning, setReasoning] = useState("");
  const [tokens, setTokens] = useState<string[]>([]);
  const [events, setEvents] = useState<LiveStreamEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Cognitive state
  const [brainState, setBrainState] = useState<BrainState>("INITIALIZING");
  const [stateConfidence, setStateConfidence] = useState(0);
  const [stateReason, setStateReason] = useState("");
  const [stateSince, setStateSince] = useState<number>(Date.now());
  const [transitions, setTransitions] = useState<StateTransition[]>([]);
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [summary, setSummary] = useState("");
  const [behaviorLabel, setBehaviorLabel] = useState("");

  const appendEvent = useCallback((event: LiveStreamEvent) => {
    // Only keep last 50 events to avoid memory bloat
    setEvents((prev) => [...prev.slice(-49), event]);

    if (event.type === "detection" && event.detections) {
      setDetections(event.detections);
    }
    if (event.type === "reasoning") {
      setReasoning(event.content);
    }
    if (event.type === "token") {
      setTokens((prev) => [...prev, event.content]);
    }
    if (event.type === "error") {
      setError(event.content);
    }

    // Cognitive events
    if (event.type === "state_change" && event.data) {
      const d = event.data as Record<string, unknown>;
      setBrainState((d.new_state as BrainState) ?? "INITIALIZING");
      setStateConfidence((d.confidence as number) ?? 0);
      setStateReason((d.reason as string) ?? "");
      setStateSince(Date.now());
      setTransitions((prev) => [
        ...prev.slice(-9),
        {
          previous: (d.previous_state as string) ?? "",
          new: (d.new_state as string) ?? "",
          reason: (d.reason as string) ?? "",
          confidence: (d.confidence as number) ?? 0,
          timestamp: (d.timestamp as string) ?? new Date().toISOString(),
        },
      ]);
    }
    if (event.type === "alert" && event.data) {
      const d = event.data as Record<string, unknown>;
      setAlerts((prev) => [
        ...prev.slice(-9),
        {
          level: (d.level as string) ?? "info",
          title: (d.title as string) ?? "Alert",
          message: (d.message as string) ?? event.content,
          state: (d.state as string) ?? "",
          timestamp: (d.timestamp as string) ?? new Date().toISOString(),
        },
      ]);
    }
    if (event.type === "summary" && event.data) {
      const d = event.data as Record<string, unknown>;
      setSummary((d.text as string) ?? event.content);
      setBrainState((d.state as BrainState) ?? brainState);
      setStateConfidence((d.confidence as number) ?? stateConfidence);
      setBehaviorLabel((d.state as string) ?? "");
    }
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
      // Cognitive state
      brainState,
      stateConfidence,
      stateReason,
      stateSince,
      transitions,
      alerts,
      summary,
      behaviorLabel,
    }),
    [
      askQuestion, connect, connected, detections, disconnect, error, events,
      reasoning, sendFrame, tokens,
      brainState, stateConfidence, stateReason, stateSince, transitions, alerts,
      summary, behaviorLabel,
    ],
  );
}
