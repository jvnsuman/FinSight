import React from 'react';
import { Target, Lightbulb, HeartHandshake } from 'lucide-react';

export default function AboutSection() {
  const pillars = [
    {
      icon: <Target className="w-8 h-8 text-primary" />,
      title: "Goal-Oriented",
      description: "We believe financial success starts with clear goals. FinSight helps you define, track, and reach your targets faster."
    },
    {
      icon: <Lightbulb className="w-8 h-8 text-accent" />,
      title: "Intelligent Insights",
      description: "Stop guessing. Our AI analyzes your spending patterns to provide personalized, actionable advice tailored to your life."
    },
    {
      icon: <HeartHandshake className="w-8 h-8 text-purple-400" />,
      title: "Your Financial Partner",
      description: "Managing money shouldn't be stressful. We simplify the complexity so you can focus on enjoying your wealth."
    }
  ];

  return (
    <section id="about" className="py-24 bg-ink border-y border-white/5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-primary/5 to-transparent z-0"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          
          {/* Text Content */}
          <div className="space-y-8">
            <h2 className="text-sm font-bold tracking-widest text-primary uppercase">About FinSight</h2>
            <h3 className="text-3xl md:text-4xl font-bold text-white leading-tight">
              Empowering you to make smarter financial decisions.
            </h3>
            <p className="text-gray-400 text-lg leading-relaxed">
              In today's fast-paced world, managing personal finances can feel overwhelming. Spreadsheets are tedious, and generic budgeting apps lack the intelligence to adapt to your unique situation. 
            </p>
            <p className="text-gray-400 text-lg leading-relaxed">
              That's why we built FinSight. We combine powerful analytics, intuitive design, and artificial intelligence to give you a complete, crystal-clear picture of your financial health.
            </p>
            
            <div className="pt-4 flex items-center space-x-4">
               <div className="flex -space-x-4">
                 <div className="w-12 h-12 rounded-full border-2 border-ink bg-gray-600"></div>
                 <div className="w-12 h-12 rounded-full border-2 border-ink bg-gray-500"></div>
                 <div className="w-12 h-12 rounded-full border-2 border-ink bg-gray-400 flex items-center justify-center text-xs font-bold text-white bg-gradient-to-r from-primary to-accent">10k+</div>
               </div>
               <p className="text-sm text-gray-400 font-medium">Trusted by thousands<br/>of users worldwide</p>
            </div>
          </div>

          {/* Pillars */}
          <div className="grid gap-6">
            {pillars.map((pillar, index) => (
              <div 
                key={index}
                className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors flex items-start space-x-4 group"
              >
                <div className="flex-shrink-0 p-3 rounded-xl bg-ink-dark group-hover:scale-110 transition-transform duration-300">
                  {pillar.icon}
                </div>
                <div>
                  <h4 className="text-xl font-semibold text-white mb-2">{pillar.title}</h4>
                  <p className="text-gray-400 leading-relaxed">{pillar.description}</p>
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>
    </section>
  );
}
