"use client";

import { CaretDown } from "@phosphor-icons/react";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

import { Section } from "@/components/ui/section";

const faqs = [
  {
    question: "What input types does Visionary Agent Protocol support?",
    answer: "You can analyze static images, uploaded video files, and live webcam streams in the same interface.",
  },
  {
    question: "Does the platform support real-time streaming responses?",
    answer: "Yes. Vision analysis streams over WebSockets for low-latency incremental agent output.",
  },
  {
    question: "Can enterprise teams deploy this in isolated environments?",
    answer: "Yes. The architecture is container-first and supports dedicated infrastructure patterns.",
  },
  {
    question: "How does the Pro plan differ from Free?",
    answer: "Pro includes live stream analysis, priority processing, and advanced agent response controls.",
  },
] as const;

export function FAQSection() {
  const [activeIndex, setActiveIndex] = useState<number | null>(0);

  return (
    <Section id="faq">
      <div className="mb-8 text-center">
        <p className="text-xs uppercase tracking-[0.32em] text-white/55">FAQ</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Answers for Implementation Teams</h2>
      </div>

      <div className="space-y-3">
        {faqs.map((faq, idx) => {
          const isOpen = activeIndex === idx;
          return (
            <div key={faq.question} className="glass-card overflow-hidden rounded-2xl border border-white/12">
              <button
                type="button"
                onClick={() => setActiveIndex((prev) => (prev === idx ? null : idx))}
                className="flex w-full items-center justify-between px-5 py-4 text-left"
              >
                <span className="text-sm font-medium text-white/90 sm:text-base">{faq.question}</span>
                <motion.span animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
                  <CaretDown size={16} className="text-white/70" />
                </motion.span>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.24, ease: "easeOut" }}
                    className="overflow-hidden"
                  >
                    <p className="px-5 pb-5 text-sm leading-relaxed text-white/70">{faq.answer}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </Section>
  );
}
