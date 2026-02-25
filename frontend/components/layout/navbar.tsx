"use client";

import Link from "next/link";
import { List, X } from "@phosphor-icons/react";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

import { getSystemStatus } from "@/lib/ai-client";
import { siteConfig } from "@/lib/site";

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);
  const [aiEnabled, setAiEnabled] = useState<boolean | null>(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const status = await getSystemStatus();
        if (!alive) return;
        setApiHealthy(status.status === "ok");
        setAiEnabled(status.openai_enabled);
      } catch {
        if (!alive) return;
        setApiHealthy(false);
      }
    };

    void load();
    const interval = setInterval(() => {
      void load();
    }, 30000);

    return () => {
      alive = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <>
      <header className="sticky top-0 z-50 px-4 py-4 sm:px-6">
        <nav className="glass-card mx-auto flex max-w-6xl items-center justify-between rounded-2xl px-5 py-3">
          <Link href="/" className="text-sm font-semibold tracking-[0.2em] text-white/90">
            VISIONARY
          </Link>
          <div className="hidden items-center gap-8 md:flex">
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.16em]">
              <span
                className={`rounded-full border px-2 py-1 ${
                  apiHealthy === true
                    ? "border-emerald-300/40 bg-emerald-300/10 text-emerald-200"
                    : "border-rose-300/40 bg-rose-300/10 text-rose-200"
                }`}
              >
                API {apiHealthy === true ? "Online" : "Offline"}
              </span>
              <span
                className={`rounded-full border px-2 py-1 ${
                  aiEnabled ? "border-cyan-300/40 bg-cyan-300/10 text-cyan-100" : "border-white/20 text-white/65"
                }`}
              >
                AI {aiEnabled ? "Enabled" : "Stub"}
              </span>
            </div>
            {siteConfig.navigation.map((item) => (
              <a key={item.label} href={item.href} className="text-sm text-white/70 transition hover:text-white">
                {item.label}
              </a>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setIsOpen((prev) => !prev)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/20 text-white/90 md:hidden"
            aria-label="Toggle menu"
          >
            {isOpen ? <X size={18} weight="bold" /> : <List size={18} weight="bold" />}
          </button>
        </nav>
      </header>

      <AnimatePresence>
        {isOpen && (
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.26, ease: "easeOut" }}
            className="glass-card fixed inset-y-0 right-0 z-[60] w-72 border-l border-white/15 p-6 md:hidden"
          >
            <div className="mb-6 flex items-center justify-between">
              <p className="text-xs uppercase tracking-[0.28em] text-white/60">Navigation</p>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-white/20 text-white/90"
                aria-label="Close menu"
              >
                <X size={16} />
              </button>
            </div>
            <div className="flex flex-col gap-4">
              {siteConfig.navigation.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="rounded-xl border border-white/10 px-4 py-3 text-sm text-white/80 transition hover:border-white/25 hover:text-white"
                >
                  {item.label}
                </a>
              ))}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
