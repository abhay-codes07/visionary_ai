import { PropsWithChildren } from "react";

import { Footer } from "@/components/layout/footer";
import { Navbar } from "@/components/layout/navbar";

type PageShellProps = PropsWithChildren<{
  title: string;
  subtitle: string;
}>;

export function PageShell({ title, subtitle, children }: PageShellProps) {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Navbar />
      <section className="mx-auto w-full max-w-6xl px-6 pb-8 pt-12 sm:pt-16">
        <div className="glass-card rounded-3xl p-8 sm:p-10">
          <p className="text-xs uppercase tracking-[0.32em] text-white/55">Visionary Agent Protocol</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">{title}</h1>
          <p className="mt-3 max-w-3xl text-sm leading-relaxed text-white/68 sm:text-base">{subtitle}</p>
        </div>
      </section>
      {children}
      <Footer />
    </main>
  );
}
