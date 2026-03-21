import { Navigation } from "@/components/landing/navigation"
import { HeroSection } from "@/components/landing/hero-section"
import { ProblemOutcomeSection } from "@/components/landing/problem-outcome-section"
import { HowItWorksSection } from "@/components/landing/how-it-works-section"
import { FeatureGridSection } from "@/components/landing/feature-grid-section"
import { TrustSection } from "@/components/landing/trust-section"
import { PricingSection } from "@/components/landing/pricing-section"
import { IntegrationsSection } from "@/components/landing/integrations-section"
import { FaqSection } from "@/components/landing/faq-section"
import { FinalCtaSection } from "@/components/landing/final-cta-section"
import { Footer } from "@/components/landing/footer"

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navigation />
      <main className="flex-1">
        <HeroSection />
        <ProblemOutcomeSection />
        <HowItWorksSection />
        <FeatureGridSection />
        <TrustSection />
        <PricingSection />
        <IntegrationsSection />
        <FaqSection />
        <FinalCtaSection />
      </main>
      <Footer />
    </div>
  )
}
