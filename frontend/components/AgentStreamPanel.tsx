"use client";

import React from "react";
import { LiveDetection, LiveStreamEvent } from "@/lib/ai-client";

type AgentStreamPanelProps = {
  detections: LiveDetection[];
  reasoning: string;
  tokens: string[];
  events: LiveStreamEvent[];
};

export function AgentStreamPanel({ detections, reasoning, tokens, events }: AgentStreamPanelProps) {
  return (
    <div className="grid gap-4">
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Live Detections</p>
        <div className="mt-2 space-y-1 text-sm text-white/80">
          {detections.length === 0 && <p>No objects detected yet.</p>}
          {detections.map((d, idx) => (
            <p key={`${d.label}-${idx}`}>
              {d.label} detected ({(d.confidence * 100).toFixed(0)}%)
            </p>
          ))}
        </div>
      </div>
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Reasoning</p>
        <p className="mt-2 text-sm text-cyan-100/85">{reasoning || "Waiting for reasoning..."}</p>
      </div>
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Token Stream</p>
        <p className="mt-2 text-sm text-white/80">{tokens.join(" ") || "No tokens yet."}</p>
      </div>
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Event Stream</p>
        <div className="mt-2 max-h-64 space-y-2 overflow-auto text-sm text-white/78">
          {events.length === 0 && <p>No events yet.</p>}
          {[...events].reverse().slice(0, 15).map((event, idx) => (
            <p key={`${event.type}-${idx}`}>
              [{event.type}] {event.content}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
