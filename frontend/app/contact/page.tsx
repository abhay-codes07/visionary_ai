import { EnvelopeSimple, MapPin, Phone } from "@phosphor-icons/react/dist/ssr";

import { PageShell } from "@/components/layout/page-shell";
import { Reveal } from "@/components/ui/reveal";
import { Section } from "@/components/ui/section";

const channels = [
  { label: "Email", value: "hello@visionaryagent.ai", icon: EnvelopeSimple },
  { label: "Phone", value: "+1 (415) 555-0143", icon: Phone },
  { label: "HQ", value: "San Francisco, California", icon: MapPin },
] as const;

export default function ContactPage() {
  return (
    <PageShell
      title="Contact"
      subtitle="Talk to our product engineering team about pilots, enterprise deployment, and integration strategy."
    >
      <Section className="pt-2">
        <div className="grid gap-5 lg:grid-cols-5">
          <Reveal className="glass-card rounded-2xl p-6 lg:col-span-3">
            <h2 className="text-xl font-semibold text-white/95">Start a Conversation</h2>
            <form className="mt-5 grid gap-4">
              <input
                placeholder="Your name"
                className="rounded-xl border border-white/15 bg-white/[0.03] px-4 py-3 text-sm text-white outline-none placeholder:text-white/45 focus:border-cyan-300/40"
              />
              <input
                placeholder="Work email"
                type="email"
                className="rounded-xl border border-white/15 bg-white/[0.03] px-4 py-3 text-sm text-white outline-none placeholder:text-white/45 focus:border-cyan-300/40"
              />
              <textarea
                rows={5}
                placeholder="Tell us what you are building..."
                className="rounded-xl border border-white/15 bg-white/[0.03] px-4 py-3 text-sm text-white outline-none placeholder:text-white/45 focus:border-cyan-300/40"
              />
              <button
                type="button"
                className="neon-ring rounded-xl bg-cyan-300/90 px-5 py-3 text-sm font-medium text-slate-950 transition hover:bg-cyan-200"
              >
                Send Inquiry
              </button>
            </form>
          </Reveal>

          <div className="grid gap-4 lg:col-span-2">
            {channels.map((channel, idx) => (
              <Reveal key={channel.label} delay={idx * 0.06} className="glass-card rounded-2xl p-5">
                <channel.icon size={20} className="text-cyan-300" />
                <p className="mt-3 text-xs uppercase tracking-[0.2em] text-white/52">{channel.label}</p>
                <p className="mt-2 text-sm text-white/82">{channel.value}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </Section>
    </PageShell>
  );
}
