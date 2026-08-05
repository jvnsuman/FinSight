import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export default function WhyChooseUs() {
  const points = [
    "AI-powered personalized recommendations",
    "Real-time intelligent budgeting limits",
    "Seamless investment portfolio tracking",
    "Bank-grade security and encryption",
    "Comprehensive long-term financial planning",
    "Stunning, interactive visual analytics",
    "Simple, intuitive, and modern interface",
    "Smart alerts and customized reminders"
  ];

  return (
    <section className="py-24 bg-ink relative overflow-hidden">
      <div className="absolute right-0 bottom-0 w-1/3 h-2/3 bg-primary/10 blur-[120px] rounded-full"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          <div className="order-2 lg:order-1 relative">
             <div className="absolute inset-0 bg-gradient-to-tr from-primary to-accent rounded-3xl transform rotate-3 opacity-20 blur-lg"></div>
             <div className="relative bg-ink-dark border border-white/10 rounded-3xl p-8 shadow-2xl">
                <div className="space-y-6">
                  {/* Fake score card */}
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                    <div>
                      <p className="text-gray-400 text-sm mb-1">Financial Health Score</p>
                      <h4 className="text-3xl font-bold text-white">85<span className="text-lg text-gray-500 font-normal">/100</span></h4>
                    </div>
                    <div className="w-16 h-16 rounded-full border-4 border-primary border-r-white/10 flex items-center justify-center">
                      <span className="text-primary font-bold">Excellent</span>
                    </div>
                  </div>
                  
                  {/* Fake AI Insight */}
                  <div className="p-4 bg-gradient-to-r from-primary/10 to-transparent border-l-2 border-primary rounded-r-xl">
                     <p className="text-sm text-gray-300">
                       <strong className="text-white block mb-1">💡 AI Insight</strong>
                       You're spending 15% less on dining this month. Keep it up and you'll reach your vacation goal 2 weeks early!
                     </p>
                  </div>
                </div>
             </div>
          </div>

          <div className="order-1 lg:order-2 space-y-8">
            <h2 className="text-primary font-bold tracking-wide uppercase text-sm">Why Choose FinSight</h2>
            <h3 className="text-3xl md:text-5xl font-bold text-white leading-tight">
              A smarter way to build wealth
            </h3>
            <p className="text-gray-400 text-lg leading-relaxed">
              We go beyond simple expense tracking. FinSight acts as your personal CFO, analyzing your data to find opportunities for growth and savings that you might have missed.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
              {points.map((point, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0" />
                  <span className="text-gray-300">{point}</span>
                </div>
              ))}
            </div>
          </div>
          
        </div>
      </div>
    </section>
  );
}
