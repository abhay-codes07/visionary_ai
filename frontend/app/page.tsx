import { Navbar } from "@/components/layout/navbar";
import { Reveal } from "@/components/ui/reveal";
import { Section } from "@/components/ui/section";
import { siteConfig } from "@/lib/site";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Navbar />
      <Section className="pt-24 sm:pt-32">
        <Reveal className="glass-card rounded-3xl p-8 sm:p-12">
          <div className="space-y-5">
            <p className="text-xs uppercase tracking-[0.35em] text-white/60">Phase 2 in Progress</p>
            <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">{siteConfig.name}</h1>
            <p className="max-w-3xl text-base text-white/70 sm:text-lg">{siteConfig.description}</p>
          </div>
        </Reveal>
      </Section>
    </main>
  );
}
