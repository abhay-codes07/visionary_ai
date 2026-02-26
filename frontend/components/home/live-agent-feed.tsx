"use client";

import React from "react";
import { FormEvent, useMemo, useRef, useState } from "react";

import { createVisionWebSocket, MediaType } from "@/lib/ai-client";

import { Section } from "@/components/ui/section";

type FeedEvent = {
  type: string;
  content: string;
  request_id?: string;
  timestamp?: string;
};

const mediaOptions: MediaType[] = ["image", "video", "webcam"];

export function LiveAgentFeedSection() {
  const socketRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [prompt, setPrompt] = useState("Describe this live scene.");
  const [question, setQuestion] = useState("What is the main object?");
  const [mediaType, setMediaType] = useState<MediaType>("image");
  const [uiError, setUiError] = useState<string | null>(null);

  const orderedEvents = useMemo(() => [...events].slice(-12).reverse(), [events]);

  const appendEvent = (event: FeedEvent) => setEvents((prev) => [...prev, event]);

  const connect = () => {
    if (socketRef.current && connected) return;
    setUiError(null);
    const socket = createVisionWebSocket();
    socketRef.current = socket;

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => {
      setUiError("WebSocket transport error. Check backend connectivity.");
      appendEvent({ type: "error", content: "WebSocket transport error." });
    };
    socket.onmessage = (message) => {
      try {
        const parsed = JSON.parse(message.data) as FeedEvent;
        appendEvent(parsed);
      } catch {
        appendEvent({ type: "error", content: "Failed to parse server event." });
      }
    };
  };

  const disconnect = () => {
    socketRef.current?.close();
    socketRef.current = null;
    setConnected(false);
  };

  const send = (payload: object) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setUiError("Connect to realtime gateway before sending events.");
      return;
    }
    setUiError(null);
    socketRef.current.send(JSON.stringify(payload));
  };

  const onAnalyze = (event: FormEvent) => {
    event.preventDefault();
    if (!prompt.trim()) {
      setUiError("Prompt cannot be empty.");
      return;
    }
    send({ type: "analyze", media_type: mediaType, prompt });
  };

  const onQuestion = (event: FormEvent) => {
    event.preventDefault();
    if (!question.trim()) {
      setUiError("Question cannot be empty.");
      return;
    }
    send({ type: "question", request_id: "ui-question", question });
  };

  return (
    <Section id="live-agent-feed">
      <div className="mb-8 text-center">
        <p className="text-xs uppercase tracking-[0.32em] text-white/55">Realtime Console</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">WebSocket Live Agent Feed</h2>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="glass-card rounded-2xl p-6">
          <div className="mb-4 flex gap-2">
            <button
              type="button"
              onClick={connect}
              className="rounded-lg bg-emerald-300/90 px-3 py-2 text-xs font-semibold text-slate-900"
            >
              Connect
            </button>
            <button
              type="button"
              onClick={disconnect}
              className="rounded-lg border border-white/20 px-3 py-2 text-xs font-semibold text-white/80"
            >
              Disconnect
            </button>
            <button
              type="button"
              onClick={() => send({ type: "ping", request_id: "ui-ping" })}
              className="rounded-lg border border-cyan-300/40 px-3 py-2 text-xs font-semibold text-cyan-100"
            >
              Ping
            </button>
          </div>
          <p className="text-xs uppercase tracking-[0.22em] text-white/50">
            Status: <span className={connected ? "text-emerald-200" : "text-rose-200"}>{connected ? "Connected" : "Offline"}</span>
          </p>

          <form onSubmit={onAnalyze} className="mt-5 space-y-3">
            <div className="flex flex-wrap gap-2">
              {mediaOptions.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setMediaType(option)}
                  className={`rounded-lg px-3 py-1.5 text-xs uppercase tracking-[0.16em] ${
                    mediaType === option ? "bg-cyan-300 text-slate-900" : "border border-white/20 text-white/70"
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-white/20 bg-white/[0.02] p-3 text-sm text-white/85"
            />
            <button className="rounded-lg bg-cyan-300/90 px-4 py-2 text-sm font-medium text-slate-900" type="submit">
              Send Analyze
            </button>
          </form>

          <form onSubmit={onQuestion} className="mt-4 space-y-3">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full rounded-lg border border-white/20 bg-white/[0.02] p-3 text-sm text-white/85"
            />
            <button className="rounded-lg border border-white/20 px-4 py-2 text-sm font-medium text-white/85" type="submit">
              Ask Question
            </button>
          </form>
        </div>

        <div className="glass-card rounded-2xl p-6">
          <p className="text-xs uppercase tracking-[0.22em] text-white/50">Event Stream</p>
          <div className="mt-4 space-y-2">
            {uiError && <p className="rounded-lg border border-rose-300/40 bg-rose-500/10 p-2 text-sm text-rose-100">{uiError}</p>}
            {orderedEvents.length === 0 && <p className="text-sm text-white/55">No events yet.</p>}
            {orderedEvents.map((event, idx) => (
              <div key={`${event.type}-${idx}`} className="rounded-lg border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-cyan-200/90">{event.type}</p>
                <p className="mt-1 text-sm text-white/85">{event.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Section>
  );
}
