import { SiteHeader } from "../components/landing/SiteHeader.jsx";
import { Hero } from "../components/landing/Hero.jsx";
import { WorkflowIndex } from "../components/landing/WorkflowIndex.jsx";
import { HowItWorks } from "../components/landing/HowItWorks.jsx";
import { TechStack } from "../components/landing/TechStack.jsx";
import { SiteFooter } from "../components/landing/SiteFooter.jsx";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-ink">
      <SiteHeader />
      <Hero />
      <WorkflowIndex />
      <HowItWorks />
      <TechStack />
      <SiteFooter />
    </div>
  );
}
