export const siteConfig = {
  name: "Visionary Agent Protocol",
  tagline: "Real-Time Vision Intelligence for Autonomous Teams",
  description:
    "Luxury-grade multimodal control center for live image and video reasoning with streaming AI agents.",
  navigation: [
    { label: "Product", href: "#features" },
    { label: "How it Works", href: "#how-it-works" },
    { label: "Pricing", href: "#pricing" },
    { label: "FAQ", href: "#faq" },
  ],
} as const;

export type SiteConfig = typeof siteConfig;
