import { FeaturedSection } from "@/components/home/featured";
import { HeroSection } from "@/components/home/hero";
import { HowItWorksSection } from "@/components/home/how-it-works";
import { TestimonialsSection } from "@/components/home/testimonials";
import { Navbar } from "@/components/layout/navbar";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <Navbar />
      <HeroSection />
      <FeaturedSection />
      <HowItWorksSection />
      <TestimonialsSection />
    </main>
  );
}
