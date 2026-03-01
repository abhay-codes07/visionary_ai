"use client";

import React, { useEffect, useState } from "react";
import { LiveDetection, LiveStreamEvent } from "@/lib/ai-client";
import { AlertEvent, BrainState, StateTransition } from "@/components/home/use-live-vision-agent";

type AgentStreamPanelProps = {
  detections: LiveDetection[];
  reasoning: string;
  tokens: string[];
  events: LiveStreamEvent[];
  // Cognitive extensions
  brainState?: BrainState;
  stateConfidence?: number;
  stateReason?: string;
  stateSince?: number;
  transitions?: StateTransition[];
  alerts?: AlertEvent[];
  summary?: string;
  behaviorLabel?: string;
  demoMode?: string;
};

const STATE_COLORS: Record<string, string> = {
  FOCUSED: "bg-emerald-400 text-slate-900",
  DISTRACTED: "bg-amber-400 text-slate-900",
  AWAY: "bg-slate-500 text-white",
  SUSPICIOUS: "bg-red-500 text-white",
  ACTIVE: "bg-cyan-400 text-slate-900",
  IDLE: "bg-zinc-600 text-white",
  INITIALIZING: "bg-zinc-700 text-white/70",
};

const STATE_ICONS: Record<string, string> = {
  FOCUSED: "\uD83C\uDFAF",
  DISTRACTED: "\uD83D\uDCF1",
  AWAY: "\uD83D\uDEAA",
  SUSPICIOUS: "\u26A0\uFE0F",
  ACTIVE: "\uD83C\uDFC3",
  IDLE: "\u23F8\uFE0F",
  INITIALIZING: "\u23F3",
};

function useElapsedTime(since: number) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => setElapsed(Math.floor((Date.now() - since) / 1000)), 1000);
    return () => clearInterval(id);
  }, [since]);
  return elapsed;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

export function AgentStreamPanel({
  detections,
  reasoning,
  tokens,
  events,
  brainState = "INITIALIZING",
  stateConfidence = 0,
  stateReason = "",
  stateSince = Date.now(),
  transitions = [],
  alerts = [],
  summary = "",
  behaviorLabel = "",
  demoMode = "workspace",
}: AgentStreamPanelProps) {
  const elapsed = useElapsedTime(stateSince);

  return (
    <div className="grid gap-4">
      {/* Brain State Badge */}
      <div className="glass-card rounded-xl p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Brain State</p>
        <div className="mt-3 flex items-center gap-4">
          <span
            className={`inline-flex items-center gap-2 rounded-xl px-5 py-3 text-lg font-bold tracking-wide ${STATE_COLORS[brainState] ?? "bg-zinc-700 text-white"}`}
          >
            <span className="text-xl">{STATE_ICONS[brainState] ?? ""}</span>
            {brainState}
          </span>
          <div className="text-sm text-white/70">
            <p>{formatDuration(elapsed)} in state</p>
            <p>Confidence: {(stateConfidence * 100).toFixed(0)}%</p>
          </div>
        </div>
        {stateReason && <p className="mt-2 text-sm text-white/60">{stateReason}</p>}
        <div className="mt-2 flex items-center gap-2">
          <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs text-white/60">
            Mode: {demoMode.toUpperCase()}
          </span>
          {behaviorLabel && behaviorLabel !== brainState && (
            <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs text-white/60">
              Behavior: {behaviorLabel}
            </span>
          )}
        </div>
      </div>

      {/* Live Context Summary */}
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Live Context</p>
        <p className="mt-2 text-sm text-cyan-100/85">
          {summary || reasoning || "Observing scene..."}
        </p>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="glass-card rounded-xl p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-white/55">Alerts</p>
          <div className="mt-2 space-y-2">
            {[...alerts].reverse().slice(0, 5).map((a, idx) => (
              <div
                key={`alert-${idx}`}
                className={`rounded-lg px-3 py-2 text-sm ${
                  a.level === "critical"
                    ? "border border-red-400/40 bg-red-500/15 text-red-200"
                    : a.level === "warning"
                      ? "border border-amber-400/40 bg-amber-500/15 text-amber-200"
                      : "border border-cyan-400/30 bg-cyan-500/10 text-cyan-200"
                }`}
              >
                <span className="font-semibold">{a.title}</span> — {a.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live Detections */}
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Live Detections</p>
        <div className="mt-2 space-y-1 text-sm text-white/80">
          {detections.length === 0 && <p>No objects detected yet.</p>}
          {detections.map((d, idx) => (
            <p key={`${d.label}-${idx}`}>
              {d.label} ({(d.confidence * 100).toFixed(0)}%)
            </p>
          ))}
        </div>
      </div>

      {/* Session Timeline */}
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Session Timeline</p>
        <div className="mt-2 max-h-48 space-y-1.5 overflow-auto text-sm text-white/70">
          {transitions.length === 0 && <p>No state transitions yet.</p>}
          {[...transitions].reverse().slice(0, 10).map((t, idx) => (
            <div key={`t-${idx}`} className="flex items-center gap-2">
              <span className={`inline-block h-2 w-2 rounded-full ${STATE_COLORS[t.new]?.split(" ")[0] ?? "bg-zinc-500"}`} />
              <span className="font-medium text-white/85">{t.previous} → {t.new}</span>
              <span className="text-xs text-white/50">{t.reason}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Event Stream (compact) */}
      <div className="glass-card rounded-xl p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-white/55">Event Stream</p>
        <div className="mt-2 max-h-40 space-y-1 overflow-auto text-xs text-white/60">
          {events.length === 0 && <p>No events yet.</p>}
          {[...events].reverse().slice(0, 20).map((event, idx) => (
            <p key={`${event.type}-${idx}`}>
              <span className="text-white/40">[{event.type}]</span> {event.content.slice(0, 120)}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
