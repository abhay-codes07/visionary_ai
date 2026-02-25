import { Check } from "@phosphor-icons/react/dist/ssr";

import { Reveal } from "@/components/ui/reveal";
import { Section } from "@/components/ui/section";

const pricingPlans = [
  {
    name: "Free",
    price: "$0",
    period: "/month",
    highlighted: false,
    features: ["Image analysis", "Basic scene descriptions", "Community support"],
    cta: "Start Free",
  },
  {
    name: "Pro",
    price: "$99",
    period: "/month",
    highlighted: true,
    features: ["Real-time stream analysis", "WebSocket live responses", "Priority support", "Advanced insights"],
    cta: "Choose Pro",
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    highlighted: false,
    features: ["Dedicated infrastructure", "Security controls", "SLA guarantees", "Custom integrations"],
    cta: "Contact Sales",
  },
] as const;

export function PricingSection() {
  return (
    <Section id="pricing">
      <Reveal className="mb-8 text-center">
        <p className="text-xs uppercase tracking-[0.32em] text-white/55">Pricing</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Plans for Every Growth Stage</h2>
      </Reveal>

      <div className="grid gap-5 lg:grid-cols-3">
        {pricingPlans.map((plan, idx) => (
          <Reveal
            key={plan.name}
            delay={idx * 0.08}
            className={`rounded-2xl p-6 ${
              plan.highlighted ? "neon-ring glass-card border border-cyan-300/40" : "glass-card border border-white/12"
            }`}
          >
            {plan.highlighted && (
              <p className="mb-3 inline-flex rounded-full border border-cyan-200/35 bg-cyan-300/10 px-3 py-1 text-xs font-medium text-cyan-200">
                Recommended
              </p>
            )}
            <h3 className="text-xl font-semibold text-white/95">{plan.name}</h3>
            <p className="mt-3 text-3xl font-semibold text-white">
              {plan.price}
              <span className="ml-1 text-sm font-normal text-white/60">{plan.period}</span>
            </p>
            <ul className="mt-6 space-y-3">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-center gap-2 text-sm text-white/75">
                  <Check size={14} className="text-cyan-300" weight="bold" />
                  {feature}
                </li>
              ))}
            </ul>
            <button
              type="button"
              className={`mt-7 w-full rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                plan.highlighted
                  ? "bg-cyan-300/90 text-slate-950 hover:bg-cyan-200"
                  : "border border-white/20 bg-white/[0.02] text-white hover:border-white/35 hover:bg-white/[0.06]"
              }`}
            >
              {plan.cta}
            </button>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
