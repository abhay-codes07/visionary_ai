import Link from "next/link";

import { siteConfig } from "@/lib/site";

const footerLinks = [
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
  { label: "Blog", href: "/blog" },
] as const;

export function Footer() {
  return (
    <footer className="mx-auto mt-10 w-full max-w-6xl px-6 pb-10">
      <div className="glass-card rounded-2xl border border-white/12 px-6 py-7 sm:px-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-white/55">Visionary Agent Protocol</p>
            <p className="mt-3 max-w-md text-sm text-white/65">{siteConfig.description}</p>
          </div>
          <div className="flex flex-wrap gap-5 text-sm text-white/75">
            {footerLinks.map((link) => (
              <Link key={link.label} href={link.href} className="transition hover:text-white">
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="mt-6 border-t border-white/10 pt-4 text-xs text-white/45">
          © {new Date().getFullYear()} Visionary Agent Protocol. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
