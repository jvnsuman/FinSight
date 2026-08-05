import React from 'react';
import { 
  Wallet, PieChart, TrendingUp, Target, 
  BrainCircuit, LineChart, Shield, Bell,
  LayoutDashboard, Lock, Download, Activity
} from 'lucide-react';

export default function FeaturesSection() {
  const features = [
    { icon: <Wallet />, title: "Expense Tracking", desc: "Log and categorize every penny effortlessly." },
    { icon: <PieChart />, title: "Budget Management", desc: "Set strict limits and monitor your spending." },
    { icon: <TrendingUp />, title: "Investment Portfolio", desc: "Track live market prices and performance." },
    { icon: <Target />, title: "Goal Planning", desc: "Save for that house, car, or vacation systematically." },
    { icon: <BrainCircuit />, title: "AI-Powered Insights", desc: "Get smart recommendations based on your habits." },
    { icon: <LineChart />, title: "Spending Analysis", desc: "Visualize where your money is actually going." },
    { icon: <Activity />, title: "Financial Health Score", desc: "A single metric to gauge your overall stability." },
    { icon: <Shield />, title: "Risk Assessment", desc: "Analyze the risk profile of your investments." },
    { icon: <Bell />, title: "Smart Notifications", desc: "Never miss a bill payment or budget breach." },
    { icon: <LayoutDashboard />, title: "Interactive Dashboards", desc: "Stunning visualizations of your data." },
    { icon: <Lock />, title: "Secure Authentication", desc: "Bank-grade encryption for your peace of mind." },
    { icon: <Download />, title: "Downloadable Reports", desc: "Export your data for tax season in one click." },
  ];

  return (
    <section id="features" className="py-24 bg-ink-dark relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-primary font-bold tracking-wide uppercase text-sm mb-3">Core Features</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white mb-6">Everything you need to succeed</h3>
          <p className="text-gray-400 text-lg">
            A comprehensive suite of tools designed to replace your spreadsheets and give you total control over your financial destiny.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {features.map((feature, i) => (
            <div 
              key={i} 
              className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-primary/50 hover:-translate-y-1 transition-all duration-300 group"
            >
              <div className="w-12 h-12 rounded-xl bg-ink-dark border border-white/10 flex items-center justify-center text-gray-400 group-hover:text-primary group-hover:border-primary/30 transition-colors mb-4">
                {React.cloneElement(feature.icon, { size: 24 })}
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">{feature.title}</h4>
              <p className="text-sm text-gray-400 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
