import { PageShell } from "@/components/layout/page-shell";
import { Reveal } from "@/components/ui/reveal";
import { Section } from "@/components/ui/section";

const principles = [
  "Design for real-time decision loops.",
  "Expose model reasoning transparently.",
  "Ship production systems, not prototypes.",
] as const;

export default function AboutPage() {
  return (
    <PageShell
      title="About Visionary"
      subtitle="We build high-trust vision intelligence products for teams operating in high-speed, high-stakes environments."
    >
      <Section className="pt-2">
        <div className="grid gap-4 md:grid-cols-3">
          {principles.map((principle, idx) => (
            <Reveal key={principle} delay={idx * 0.06} className="glass-card rounded-2xl p-6">
              <p className="text-xs uppercase tracking-[0.2em] text-white/50">Principle {idx + 1}</p>
              <p className="mt-3 text-sm text-white/80">{principle}</p>
            </Reveal>
          ))}
        </div>
      </Section>
    </PageShell>
  );
}
