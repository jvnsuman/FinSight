import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function CTASection() {
  return (
    <section className="py-24 relative overflow-hidden bg-ink-dark">
      {/* Dynamic Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-ink-dark to-accent/20 z-0"></div>
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20 mix-blend-overlay"></div>
      
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <h2 className="text-4xl md:text-6xl font-extrabold text-white mb-6 tracking-tight">
          Take control of your finances today.
        </h2>
        <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
          Start your journey toward smarter financial decisions, automated insights, and true wealth building with FinSight.
        </p>
        
        <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6">
          <Link
            to="/register"
            className="w-full sm:w-auto px-10 py-5 rounded-2xl bg-gradient-to-r from-primary to-accent text-white font-bold text-lg hover:opacity-90 transition-all transform hover:scale-105 shadow-2xl shadow-primary/30 flex items-center justify-center group"
          >
            Create Free Account
            <ArrowRight className="ml-2 w-6 h-6 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto px-10 py-5 rounded-2xl bg-white/10 border border-white/20 text-white font-bold text-lg hover:bg-white/20 transition-all flex items-center justify-center backdrop-blur-md"
          >
            Log In to FinSight
          </Link>
        </div>
        
        <p className="mt-8 text-sm text-gray-400">
          No credit card required. Setup takes less than 2 minutes.
        </p>
      </div>
    </section>
  );
}
