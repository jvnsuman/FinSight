import React from 'react';
import { Star } from 'lucide-react';

export default function Testimonials() {
  const testimonials = [
    {
      name: "Sarah Jenkins",
      role: "Small Business Owner",
      text: "Finance Analytics Platform completely changed how I look at my money. The AI insights caught a massive leak in my software subscriptions that saved me $400 a month!",
      avatar: "SJ"
    },
    {
      name: "David Chen",
      role: "Software Engineer",
      text: "As someone who loves data, the analytics are phenomenal. It's the first finance app that feels like a premium SaaS product rather than a clunky spreadsheet.",
      avatar: "DC"
    },
    {
      name: "Elena Rodriguez",
      role: "Freelance Designer",
      text: "The budget tracking is effortless. I finally have peace of mind knowing exactly how much I need to save for taxes and how much I can invest.",
      avatar: "ER"
    }
  ];

  return (
    <section className="py-24 bg-ink-dark border-y border-white/5 relative">
      <div className="absolute left-0 bottom-0 w-1/4 h-1/2 bg-purple-500/10 blur-[100px] rounded-full"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-primary font-bold tracking-wide uppercase text-sm mb-3">Customer Stories</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white mb-6">Loved by thousands</h3>
          <p className="text-gray-400 text-lg">
            Don't just take our word for it. Here's what our users have to say about their journey to financial freedom.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, i) => (
            <div key={i} className="bg-white/5 border border-white/10 p-8 rounded-3xl relative">
               <div className="flex space-x-1 mb-6">
                 {[...Array(5)].map((_, j) => (
                   <Star key={j} className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                 ))}
               </div>
               <p className="text-gray-300 text-lg leading-relaxed mb-8 italic">"{t.text}"</p>
               <div className="flex items-center space-x-4">
                 <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg">
                   {t.avatar}
                 </div>
                 <div>
                   <h5 className="text-white font-semibold">{t.name}</h5>
                   <p className="text-gray-500 text-sm">{t.role}</p>
                 </div>
               </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
