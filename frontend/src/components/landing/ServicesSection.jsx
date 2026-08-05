import React from 'react';
import { Briefcase, Landmark, PiggyBank, GraduationCap, Map, BarChart } from 'lucide-react';

export default function ServicesSection() {
  const services = [
    {
      icon: <Briefcase className="w-10 h-10 text-primary" />,
      title: "Personal Finance Management",
      desc: "Holistic tools to manage your day-to-day cash flow with absolute precision."
    },
    {
      icon: <BarChart className="w-10 h-10 text-accent" />,
      title: "Investment Analysis",
      desc: "Deep-dive metrics into your portfolio to ensure maximum returns."
    },
    {
      icon: <PiggyBank className="w-10 h-10 text-purple-400" />,
      title: "Savings Planning",
      desc: "Automated routing of your surplus income into dedicated savings pools."
    },
    {
      icon: <Map className="w-10 h-10 text-primary" />,
      title: "Retirement Planning",
      desc: "Long-term forecasting to ensure you can retire comfortably and securely."
    },
    {
      icon: <Landmark className="w-10 h-10 text-accent" />,
      title: "Wealth Growth Insights",
      desc: "AI-driven recommendations on how to allocate assets for optimal growth."
    },
    {
      icon: <GraduationCap className="w-10 h-10 text-purple-400" />,
      title: "Financial Education",
      desc: "Learn the fundamentals of wealth building through our smart tips and reports."
    }
  ];

  return (
    <section id="services" className="py-24 bg-ink relative overflow-hidden">
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03]"></div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
          <div className="max-w-2xl">
            <h2 className="text-accent font-bold tracking-wide uppercase text-sm mb-3">Premium Services</h2>
            <h3 className="text-3xl md:text-5xl font-bold text-white">Expert tools for every stage of your journey</h3>
          </div>
          <button className="px-6 py-3 rounded-lg border border-white/20 text-white hover:bg-white/5 transition-colors self-start md:self-end">
            Explore All Services
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div 
              key={index}
              className="relative p-8 rounded-3xl bg-gradient-to-b from-white/5 to-transparent border border-white/10 overflow-hidden group hover:border-white/20 transition-all duration-500"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110 duration-500"></div>
              
              <div className="mb-6">
                {service.icon}
              </div>
              <h4 className="text-2xl font-semibold text-white mb-4 relative z-10">{service.title}</h4>
              <p className="text-gray-400 leading-relaxed relative z-10">{service.desc}</p>
              
              <div className="mt-8 flex items-center text-sm font-medium text-gray-300 group-hover:text-white transition-colors cursor-pointer w-max relative z-10">
                Learn more <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
