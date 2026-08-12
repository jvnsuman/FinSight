import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Zap, BarChart3 } from 'lucide-react';

export default function HeroSection() {
  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center pt-20 pb-32 overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute inset-0 bg-ink-dark z-0" />
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full z-0" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 blur-[120px] rounded-full z-0" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full mt-10">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm animate-fade-in-up">
            <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-xs font-medium text-gray-300">Finance Analytics Platform 2.0 is now live</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight mb-8 leading-tight animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            Master Your Money with <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-accent to-purple-400">
              Intelligent Insights
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto animate-fade-in-up" style={{ animationDelay: '200ms' }}>
            The all-in-one AI-powered platform to track expenses, plan budgets, monitor investments, and achieve your financial goals with absolute clarity.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
            <Link
              to="/register"
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-semibold text-lg hover:opacity-90 transition-all transform hover:scale-105 shadow-xl shadow-primary/25 flex items-center justify-center group"
            >
              Get Started for Free
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-white/5 border border-white/10 text-white font-semibold text-lg hover:bg-white/10 transition-all backdrop-blur-sm flex items-center justify-center"
            >
              Log In
            </Link>
          </div>

          <div className="mt-12 flex flex-wrap justify-center items-center gap-8 text-gray-400 text-sm font-medium animate-fade-in-up" style={{ animationDelay: '400ms' }}>
            <div className="flex items-center">
              <ShieldCheck className="w-5 h-5 text-primary mr-2" /> Bank-grade Security
            </div>
            <div className="flex items-center">
              <Zap className="w-5 h-5 text-accent mr-2" /> AI-Powered
            </div>
            <div className="flex items-center">
              <BarChart3 className="w-5 h-5 text-purple-400 mr-2" /> Real-time Analytics
            </div>
          </div>
        </div>

        {/* Dashboard Mockup Preview */}
        <div className="mt-20 relative mx-auto max-w-5xl animate-fade-in-up" style={{ animationDelay: '500ms' }}>
          <div className="relative rounded-2xl bg-ink/80 backdrop-blur-xl border border-white/10 shadow-2xl p-2 sm:p-4 overflow-hidden">
            {/* Window controls */}
            <div className="flex items-center space-x-2 mb-4 px-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            
            {/* Mockup content */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Sidebar */}
              <div className="hidden md:block col-span-1 border-r border-white/5 pr-4 space-y-4">
                <div className="h-8 w-3/4 bg-white/5 rounded"></div>
                <div className="space-y-2">
                  <div className="h-6 w-full bg-primary/20 rounded"></div>
                  <div className="h-6 w-5/6 bg-white/5 rounded"></div>
                  <div className="h-6 w-4/6 bg-white/5 rounded"></div>
                </div>
              </div>
              
              {/* Main Content */}
              <div className="col-span-1 md:col-span-2 space-y-4">
                {/* Header cards */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-24 bg-gradient-to-br from-white/5 to-white/0 border border-white/5 rounded-xl p-4 flex flex-col justify-between">
                     <div className="h-4 w-1/2 bg-white/10 rounded"></div>
                     <div className="h-6 w-3/4 bg-white/20 rounded"></div>
                  </div>
                  <div className="h-24 bg-gradient-to-br from-white/5 to-white/0 border border-white/5 rounded-xl p-4 flex flex-col justify-between">
                     <div className="h-4 w-1/2 bg-white/10 rounded"></div>
                     <div className="h-6 w-3/4 bg-primary/40 rounded"></div>
                  </div>
                  <div className="h-24 bg-gradient-to-br from-white/5 to-white/0 border border-white/5 rounded-xl p-4 flex flex-col justify-between">
                     <div className="h-4 w-1/2 bg-white/10 rounded"></div>
                     <div className="h-6 w-3/4 bg-accent/40 rounded"></div>
                  </div>
                </div>
                {/* Chart Area */}
                <div className="h-48 bg-white/5 rounded-xl border border-white/5 relative overflow-hidden flex items-end">
                   {/* Fake chart bars */}
                   <div className="absolute bottom-0 left-0 right-0 flex items-end justify-around px-4 h-full pt-8 pb-4">
                      {[40, 70, 45, 90, 65, 100, 80].map((h, i) => (
                        <div key={i} className="w-[8%] bg-primary/40 rounded-t-sm transition-all" style={{ height: `${h}%` }}></div>
                      ))}
                   </div>
                </div>
              </div>
            </div>
            
            {/* Overlay Gradient for fade out effect at bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-ink-dark via-ink-dark/50 to-transparent z-10" />
          </div>
        </div>
      </div>
    </section>
  );
}
