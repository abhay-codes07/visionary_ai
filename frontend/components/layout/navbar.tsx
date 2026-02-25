"use client";

import Link from "next/link";
import { List, X } from "@phosphor-icons/react";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

import { siteConfig } from "@/lib/site";

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-50 px-4 py-4 sm:px-6">
        <nav className="glass-card mx-auto flex max-w-6xl items-center justify-between rounded-2xl px-5 py-3">
          <Link href="/" className="text-sm font-semibold tracking-[0.2em] text-white/90">
            VISIONARY
          </Link>
          <div className="hidden items-center gap-8 md:flex">
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
