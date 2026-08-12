import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(0);

  const faqs = [
    {
      q: "How secure is my financial data?",
      a: "Finance Analytics Platform uses bank-grade AES-256 encryption. We never sell your data to third parties, and our platform undergoes regular security audits to ensure your information remains strictly private."
    },
    {
      q: "Can I track both investments and daily expenses?",
      a: "Yes! Finance Analytics Platform is an all-in-one platform. You can log daily cash flows, set strict budgets, and track live market prices for your stock and mutual fund portfolios simultaneously."
    },
    {
      q: "How do the AI recommendations work?",
      a: "Our proprietary AI analyzes your spending habits over time. It identifies unused subscriptions, warns you if you're trending over budget, and suggests optimized asset allocations for your investments."
    },
    {
      q: "Can I generate reports for tax season?",
      a: "Absolutely. You can download comprehensive PDF or CSV reports detailing your income, expenses, and capital gains with a single click."
    },
    {
      q: "Is there a mobile app available?",
      a: "Finance Analytics Platform is built as a fully responsive progressive web app (PWA). It works flawlessly on desktop, tablet, and mobile browsers, feeling just like a native app."
    }
  ];

  return (
    <section className="py-24 bg-ink relative">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-accent font-bold tracking-wide uppercase text-sm mb-3">FAQ</h2>
          <h3 className="text-3xl md:text-4xl font-bold text-white">Frequently Asked Questions</h3>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div 
              key={index} 
              className={`border rounded-2xl overflow-hidden transition-colors ${
                openIndex === index ? 'border-primary/50 bg-white/5' : 'border-white/10 bg-transparent hover:bg-white/5'
              }`}
            >
              <button 
                className="w-full px-6 py-5 text-left flex justify-between items-center"
                onClick={() => setOpenIndex(openIndex === index ? -1 : index)}
              >
                <span className="text-white font-semibold text-lg">{faq.q}</span>
                <ChevronDown 
                  className={`w-5 h-5 text-gray-400 transition-transform duration-300 ${openIndex === index ? 'rotate-180 text-primary' : ''}`} 
                />
              </button>
              <div 
                className={`px-6 overflow-hidden transition-all duration-300 ease-in-out ${
                  openIndex === index ? 'max-h-48 pb-5 opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <p className="text-gray-400 leading-relaxed">{faq.a}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
