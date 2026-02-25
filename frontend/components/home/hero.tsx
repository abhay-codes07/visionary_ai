"use client";

import { ArrowRight } from "@phosphor-icons/react";
import { motion } from "framer-motion";

import { siteConfig } from "@/lib/site";

export function HeroSection() {
  return (
    <section className="mx-auto grid w-full max-w-6xl gap-10 px-6 pb-14 pt-10 md:grid-cols-2 md:items-center md:pt-16">
      <div className="space-y-6">
        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="text-xs uppercase tracking-[0.35em] text-white/60"
        >
          Visionary Agent Protocol
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.05 }}
          className="text-4xl font-semibold leading-tight tracking-tight sm:text-6xl"
        >
          {siteConfig.tagline}
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.1 }}
          className="max-w-xl text-base text-white/70 sm:text-lg"
        >
          {siteConfig.description}
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, delay: 0.15 }}
          className="flex flex-wrap gap-4"
        >
          <button className="neon-ring rounded-xl bg-white/10 px-6 py-3 text-sm font-medium text-white transition hover:bg-white/20">
            Launch Agent
          </button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-transparent px-6 py-3 text-sm font-medium text-white/85 transition hover:border-white/40 hover:text-white">
            Watch Demo <ArrowRight size={16} />
          </button>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 22 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.1 }}
        className="glass-card rounded-3xl p-3"
      >
        <div className="relative h-[340px] overflow-hidden rounded-2xl border border-white/10 bg-black/30">
          <spline-viewer
            url="https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode"
            class="h-full w-full"
          />
        </div>
      </motion.div>
    </section>
  );
}
