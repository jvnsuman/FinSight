import React, { useState } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend
} from 'recharts';

export default function AnalyticsPreview() {
  const [activeTab, setActiveTab] = useState('cashflow');

  const cashFlowData = [
    { month: 'Jan', income: 4000, expense: 2400 },
    { month: 'Feb', income: 4500, expense: 2800 },
    { month: 'Mar', income: 4200, expense: 2100 },
    { month: 'Apr', income: 5000, expense: 2900 },
    { month: 'May', income: 4800, expense: 2300 },
    { month: 'Jun', income: 5500, expense: 2600 },
    { month: 'Jul', income: 5200, expense: 2400 },
  ];

  const spendingData = [
    { name: 'Housing', value: 35 },
    { name: 'Food', value: 20 },
    { name: 'Transport', value: 15 },
    { name: 'Entertainment', value: 10 },
    { name: 'Utilities', value: 20 },
  ];
  
  const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-ink p-3 rounded-lg border border-white/10 shadow-xl">
          <p className="text-white font-medium mb-1">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: ${entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <section id="analytics" className="py-24 bg-ink-dark border-y border-white/5 relative">
      <div className="absolute left-0 top-1/4 w-1/3 h-1/2 bg-accent/10 blur-[100px] rounded-full"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-purple-400 font-bold tracking-wide uppercase text-sm mb-3">Interactive Analytics</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white mb-6">See your money in a new light</h3>
          <p className="text-gray-400 text-lg">
            Beautiful, interactive charts that turn your raw financial data into meaningful stories and actionable insights.
          </p>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-2 sm:p-6 backdrop-blur-xl shadow-2xl">
          {/* Tabs */}
          <div className="flex flex-wrap justify-center gap-2 mb-8 border-b border-white/5 pb-6">
            <button 
              onClick={() => setActiveTab('cashflow')}
              className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                activeTab === 'cashflow' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              Cash Flow Trend
            </button>
            <button 
              onClick={() => setActiveTab('spending')}
              className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                activeTab === 'spending' ? 'bg-accent text-white shadow-lg shadow-accent/20' : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              Spending Breakdown
            </button>
          </div>

          {/* Charts */}
          <div className="h-[400px] w-full mt-4">
            {activeTab === 'cashflow' && (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={cashFlowData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="month" stroke="#4B5563" tick={{fill: '#9CA3AF', fontSize: 12}} axisLine={false} tickLine={false} />
                  <YAxis stroke="#4B5563" tick={{fill: '#9CA3AF', fontSize: 12}} axisLine={false} tickLine={false} />
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '14px', color: '#fff' }} />
                  <Area type="monotone" dataKey="income" name="Income" stroke="#10B981" strokeWidth={3} fillOpacity={1} fill="url(#colorIncome)" />
                  <Area type="monotone" dataKey="expense" name="Expenses" stroke="#EF4444" strokeWidth={3} fillOpacity={1} fill="url(#colorExpense)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
            
            {activeTab === 'spending' && (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={spendingData}
                    cx="50%"
                    cy="50%"
                    innerRadius={100}
                    outerRadius={140}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {spendingData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.5rem' }}
                    itemStyle={{ color: '#fff' }}
                    formatter={(value) => [`${value}%`, 'Share']}
                  />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '14px', color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
