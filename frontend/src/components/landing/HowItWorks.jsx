import React from 'react';

export default function HowItWorks() {
  const steps = [
    { num: "01", title: "Create an Account", desc: "Sign up securely in less than 2 minutes." },
    { num: "02", title: "Complete Profile", desc: "Tell us your goals, income, and preferred currency." },
    { num: "03", title: "Track Finances", desc: "Log your income and expenses seamlessly." },
    { num: "04", title: "Set Budgets", desc: "Define limits for categories to control spending." },
    { num: "05", title: "Monitor Investments", desc: "Watch your portfolio grow with real-time tracking." },
    { num: "06", title: "Get AI Insights", desc: "Receive personalized, actionable recommendations." },
    { num: "07", title: "Achieve Goals", desc: "Hit your milestones faster and secure your future." }
  ];

  return (
    <section className="py-24 bg-ink relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-primary font-bold tracking-wide uppercase text-sm mb-3">User Journey</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white mb-6">How FinSight works</h3>
          <p className="text-gray-400 text-lg">
            A simple, streamlined path from financial confusion to absolute clarity.
          </p>
        </div>

        <div className="relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-white/10 -translate-y-1/2"></div>
          
          <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-8 relative z-10 overflow-x-auto pb-8 hide-scrollbar">
            {steps.map((step, index) => (
              <div key={index} className="flex flex-col items-center text-center w-full md:w-48 flex-shrink-0 group">
                <div className="w-16 h-16 rounded-full bg-ink-dark border-2 border-white/20 flex items-center justify-center text-xl font-bold text-white mb-6 group-hover:border-primary group-hover:text-primary transition-colors relative z-10">
                  {step.num}
                  <div className="absolute inset-0 bg-primary/20 rounded-full blur-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                <h4 className="text-white font-semibold mb-2">{step.title}</h4>
                <p className="text-gray-400 text-sm">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
