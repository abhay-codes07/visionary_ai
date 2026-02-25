import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Visionary Agent Protocol",
  description: "Real-time Vision AI Agent platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Script
          type="module"
          src="https://unpkg.com/@splinetool/viewer@1.10.43/build/spline-viewer.js"
          strategy="afterInteractive"
        />
        {children}
      </body>
    </html>
  );
}
