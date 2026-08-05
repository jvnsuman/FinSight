import React, { useEffect } from 'react';
import LandingNavbar from '../components/landing/LandingNavbar';
import HeroSection from '../components/landing/HeroSection';
import AboutSection from '../components/landing/AboutSection';
import FeaturesSection from '../components/landing/FeaturesSection';
import ServicesSection from '../components/landing/ServicesSection';
import AnalyticsPreview from '../components/landing/AnalyticsPreview';
import WhyChooseUs from '../components/landing/WhyChooseUs';
import FinancialTips from '../components/landing/FinancialTips';
import HowItWorks from '../components/landing/HowItWorks';
import Testimonials from '../components/landing/Testimonials';
import FAQ from '../components/landing/FAQ';
import CTASection from '../components/landing/CTASection';
import Footer from '../components/landing/Footer';

export default function LandingPage() {
  useEffect(() => {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth'
          });
        }
      });
    });
  }, []);

  return (
    <div className="bg-ink min-h-screen text-white font-sans selection:bg-primary selection:text-white">
      <LandingNavbar />
      
      <main>
        <HeroSection />
        <AboutSection />
        <FeaturesSection />
        <ServicesSection />
        <AnalyticsPreview />
        <WhyChooseUs />
        <HowItWorks />
        <FinancialTips />
        <Testimonials />
        <FAQ />
        <CTASection />
      </main>

      <Footer />
    </div>
  );
}
