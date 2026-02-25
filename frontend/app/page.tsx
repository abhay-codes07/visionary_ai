import { FeaturedSection } from "@/components/home/featured";
import { FeaturesGridSection } from "@/components/home/features-grid";
import { FAQSection } from "@/components/home/faq";
import { HeroSection } from "@/components/home/hero";
import { HowItWorksSection } from "@/components/home/how-it-works";
import { MissionSection } from "@/components/home/mission";
import { PricingSection } from "@/components/home/pricing";
import { TestimonialsSection } from "@/components/home/testimonials";
import { Navbar } from "@/components/layout/navbar";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Navbar />
      <HeroSection />
      <FeaturedSection />
      <FeaturesGridSection />
      <HowItWorksSection />
      <MissionSection />
      <TestimonialsSection />
      <PricingSection />
      <FAQSection />
    </main>
  );
}
