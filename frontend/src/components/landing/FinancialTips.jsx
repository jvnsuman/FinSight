import React from 'react';
import { Lightbulb } from 'lucide-react';

export default function FinancialTips() {
  const tips = [
    { title: "Build an Emergency Fund", text: "Aim for 3-6 months of living expenses in a highly liquid account." },
    { title: "The 50/30/20 Rule", text: "Allocate 50% to needs, 30% to wants, and 20% to savings and investments." },
    { title: "Invest Consistently", text: "Dollar-cost averaging helps mitigate market volatility over the long term." },
    { title: "Track Every Expense", text: "Small, recurring expenses often drain budgets faster than large purchases." },
    { title: "Diversify Investments", text: "Don't put all your eggs in one basket. Spread risk across multiple asset classes." },
    { title: "Review Monthly", text: "Sit down at the end of each month to review your progress and adjust budgets." }
  ];

  return (
    <section className="py-24 bg-ink-dark border-y border-white/5 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-accent font-bold tracking-wide uppercase text-sm mb-3">Expert Advice</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white mb-6">Master your money</h3>
          <p className="text-gray-400 text-lg">
            Time-tested financial principles to guide your wealth-building journey.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tips.map((tip, index) => (
            <div key={index} className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-colors group">
               <div className="flex items-center space-x-3 mb-4">
                 <div className="p-2 bg-accent/20 text-accent rounded-lg group-hover:scale-110 transition-transform">
                   <Lightbulb size={20} />
                 </div>
                 <h4 className="text-white font-semibold text-lg">{tip.title}</h4>
               </div>
               <p className="text-gray-400 text-sm leading-relaxed">{tip.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
