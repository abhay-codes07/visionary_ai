"use client";

import React from "react";
import { useMemo, useState } from "react";

import { AgentStreamPanel } from "@/components/AgentStreamPanel";
import { BoundingBoxOverlay } from "@/components/BoundingBoxOverlay";
import { WebcamStream } from "@/components/WebcamStream";
import { Section } from "@/components/ui/section";
import { useLiveVisionAgent } from "@/components/home/use-live-vision-agent";

const demoModes = ["security", "workspace", "objects", "custom"] as const;

export function LiveVisionLabSection() {
  const sessionId = useMemo(() => `live-${Date.now()}`, []);
  const [demoMode, setDemoMode] = useState<(typeof demoModes)[number]>("workspace");
  const [question, setQuestion] = useState("What is the person doing?");
  const [active, setActive] = useState(false);

  const agent = useLiveVisionAgent(sessionId, demoMode);

  return (
    <Section id="live-lab">
      <div className="mb-8 text-center">
        <p className="text-xs uppercase tracking-[0.32em] text-white/55">Live Vision Lab</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Real-Time Vision Agent</h2>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="glass-card rounded-xl p-4">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  agent.connect();
                  setActive(true);
                }}
                className="rounded-lg bg-emerald-300/90 px-3 py-2 text-xs font-semibold text-slate-900"
              >
                Connect Live Agent
              </button>
              <button
                type="button"
                onClick={() => {
                  agent.disconnect();
                  setActive(false);
                }}
                className="rounded-lg border border-white/20 px-3 py-2 text-xs text-white/80"
              >
                Disconnect
              </button>
              <span className="text-xs text-white/65">Status: {agent.connected ? "Connected" : "Offline"}</span>
            </div>
            <div className="relative">
              <WebcamStream
                active={active}
                fps={8}
                onFrame={(base64) => agent.sendFrame(base64, `${Date.now()}`)}
              />
              <BoundingBoxOverlay detections={agent.detections} sourceWidth={960} sourceHeight={540} />
            </div>
          </div>

          <div className="glass-card rounded-xl p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-white/55">Demo Mode</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {demoModes.map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setDemoMode(mode)}
                  className={`rounded-lg px-3 py-1.5 text-xs uppercase ${
                    demoMode === mode ? "bg-cyan-300 text-slate-900" : "border border-white/20 text-white/75"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <form
            className="glass-card rounded-xl p-4"
            onSubmit={(e) => {
              e.preventDefault();
              agent.askQuestion(question);
            }}
          >
            <p className="text-xs uppercase tracking-[0.2em] text-white/55">Ask Live Video Question</p>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="mt-3 w-full rounded-lg border border-white/20 bg-white/[0.02] p-3 text-sm text-white/85"
            />
            <button type="submit" className="mt-3 w-full rounded-lg border border-cyan-300/40 py-2.5 text-sm text-cyan-100">
              Ask Agent
            </button>
            {agent.error && <p className="mt-2 text-sm text-rose-200">{agent.error}</p>}
          </form>
        </div>
        <AgentStreamPanel detections={agent.detections} reasoning={agent.reasoning} tokens={agent.tokens} events={agent.events} />
      </div>
    </Section>
  );
}
