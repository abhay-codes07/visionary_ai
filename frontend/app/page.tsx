import { AgentStudioSection } from "@/components/home/agent-studio";
import { FeaturedSection } from "@/components/home/featured";
import { FeaturesGridSection } from "@/components/home/features-grid";
import { FAQSection } from "@/components/home/faq";
import { HeroSection } from "@/components/home/hero";
import { HowItWorksSection } from "@/components/home/how-it-works";
import { LiveAgentFeedSection } from "@/components/home/live-agent-feed";
import { LiveVisionLabSection } from "@/components/home/live-vision-lab";
import { MissionSection } from "@/components/home/mission";
import { PricingSection } from "@/components/home/pricing";
import { TestimonialsSection } from "@/components/home/testimonials";
import { Footer } from "@/components/layout/footer";
import { Navbar } from "@/components/layout/navbar";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Navbar />
      <HeroSection />
      <FeaturedSection />
      <AgentStudioSection />
      <LiveVisionLabSection />
      <LiveAgentFeedSection />
      <FeaturesGridSection />
      <HowItWorksSection />
      <MissionSection />
      <TestimonialsSection />
      <PricingSection />
      <FAQSection />
      <Footer />
    </main>
  );
}
