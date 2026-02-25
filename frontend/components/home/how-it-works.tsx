import { Broadcast, Camera, Cpu, Sparkle } from "@phosphor-icons/react/dist/ssr";

import { Reveal } from "@/components/ui/reveal";
import { Section } from "@/components/ui/section";

const steps = [
  {
    title: "Capture",
    description: "Ingest image uploads, live webcam streams, or video files into a unified analysis session.",
    icon: Camera,
  },
  {
    title: "Analyze",
    description: "Vision agents interpret scenes, detect objects, and generate grounded contextual insights.",
    icon: Cpu,
  },
  {
    title: "Stream",
    description: "Responses stream in real-time so teams can act immediately on evolving visual conditions.",
    icon: Broadcast,
  },
  {
    title: "Orchestrate",
    description: "Route insights into workflows, alerts, and operational decisions across the organization.",
    icon: Sparkle,
  },
] as const;

export function HowItWorksSection() {
  return (
    <Section id="how-it-works">
      <Reveal className="mb-8">
        <p className="text-xs uppercase tracking-[0.32em] text-white/55">How It Works</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">From Camera Input to Intelligent Action</h2>
      </Reveal>

      <div className="grid gap-4 md:grid-cols-2">
        {steps.map((step, idx) => (
          <Reveal
            key={step.title}
            delay={idx * 0.07}
            className="glass-card group relative overflow-hidden rounded-2xl p-6"
          >
            <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full bg-cyan-400/10 blur-2xl transition group-hover:bg-cyan-300/20" />
            <p className="text-xs uppercase tracking-[0.22em] text-white/55">Step {idx + 1}</p>
            <div className="mt-3 inline-flex rounded-xl border border-white/15 bg-white/[0.03] p-2.5">
              <step.icon size={20} className="text-cyan-300" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-white/95">{step.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-white/68">{step.description}</p>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
