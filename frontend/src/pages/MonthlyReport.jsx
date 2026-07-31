import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Download, TrendingUp, TrendingDown, Sparkles, Search, FileText } from 'lucide-react';
import AppShell from '../components/layout/AppShell';
import { getAllTransactions } from '../api/transactionsApi';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#EF4444', '#8884d8'];

export default function MonthlyReport() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState('2026-07');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); 

  useEffect(() => {
    async function fetchRealData() {
      try {
        setLoading(true);
        const data = await getAllTransactions();
        setTransactions(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to fetch transactions", err);
      } finally {
        setLoading(false);
      }
    }
    fetchRealData();
  }, []);

  const parseAmount = (amt) => {
    if (amt === undefined || amt === null) return 0;
    if (typeof amt === 'number') return amt;
    const cleaned = String(amt).replace(/[^\d.-]/g, '');
    return Number(cleaned) || 0;
  };
  
  const getRawDate = (t) => String(t?.date || t?.transaction_date || t?.createdAt || '');
  const getRawType = (t) => String(t?.type || t?.transaction_type || '').toLowerCase();
  
  const getTdsAmount = (t) => parseAmount(t?.tds || t?.tax) || 0;

  const getCategory = (t) => {
    if (!t) return 'Uncategorized';
    if (typeof t.category === 'string') return t.category;
    if (typeof t.Category === 'string') return t.Category;
    if (typeof t.category_name === 'string') return t.category_name;
    if (typeof t.categoryName === 'string') return t.categoryName;
    if (t.category && typeof t.category === 'object') {
      const explicitName = t.category.name || t.category.title || t.category.type || t.category.category_name;
      if (explicitName) return String(explicitName);
      const firstStringVal = Object.values(t.category).find(v => typeof v === 'string');
      if (firstStringVal) return firstStringVal;
    }
    return 'Uncategorized';
  };

  const [selYear, selMonth] = selectedMonth.split('-').map(Number);
  const lastMonthDate = new Date(selYear, selMonth - 2, 1);
  const lastYear = lastMonthDate.getFullYear();
  const lastMonthNum = lastMonthDate.getMonth() + 1;

  const isCurrentMonth = (rawDate) => {
    try {
      const d = new Date(rawDate);
      if (!isNaN(d.getTime())) {
        return d.getFullYear() === selYear && (d.getMonth() + 1) === selMonth;
      }
      return rawDate.startsWith(selectedMonth);
    } catch { return rawDate.startsWith(selectedMonth); }
  };

  const isLastMonth = (rawDate) => {
    try {
      const d = new Date(rawDate);
      if (!isNaN(d.getTime())) return d.getFullYear() === lastYear && (d.getMonth() + 1) === lastMonthNum;
      const lmStr = `${lastYear}-${String(lastMonthNum).padStart(2, '0')}`;
      return rawDate.startsWith(lmStr);
    } catch { return false; }
  };

  const isPastMonth = (rawDate) => {
    try {
      const d = new Date(rawDate);
      if (isNaN(d.getTime())) return false;
      if (d.getFullYear() < selYear) return true;
      if (d.getFullYear() === selYear && (d.getMonth() + 1) < selMonth) return true;
      return false;
    } catch { return false; }
  };

  const filteredData = transactions.filter((t) => t && getRawDate(t) && isCurrentMonth(getRawDate(t)));
  const pastData = transactions.filter((t) => t && getRawDate(t) && isPastMonth(getRawDate(t)));
  const lastMonthData = transactions.filter((t) => t && getRawDate(t) && isLastMonth(getRawDate(t)));

  const searchedTransactions = filteredData.filter((t) => {
    if (!t) return false;
    const typeMatch = filterType === 'all' || getRawType(t) === filterType;
    if (!typeMatch) return false;

    const safeSearch = String(searchTerm || '').toLowerCase();
    const cat = String(getCategory(t)).toLowerCase();
    const dateStr = String(getRawDate(t)).toLowerCase();
    return cat.includes(safeSearch) || dateStr.includes(safeSearch);
  });

  const openingIncome = pastData.filter((t) => getRawType(t) === 'income').reduce((acc, curr) => acc + parseAmount(curr?.amount), 0);
  const openingExpense = pastData.filter((t) => getRawType(t) === 'expense').reduce((acc, curr) => acc + parseAmount(curr?.amount), 0);
  const openingBalance = openingIncome - openingExpense;

  const totalIncome = filteredData.filter((t) => getRawType(t) === 'income').reduce((acc, curr) => acc + parseAmount(curr?.amount), 0);
  const totalExpense = filteredData.filter((t) => getRawType(t) === 'expense').reduce((acc, curr) => acc + parseAmount(curr?.amount), 0);
  const totalTDS = filteredData.reduce((acc, curr) => acc + getTdsAmount(curr), 0);
  
  const netBalance = totalIncome - totalExpense;
  const closingBalance = openingBalance + netBalance;

  const lastMonthIncome = lastMonthData.filter(t => getRawType(t) === 'income').reduce((acc, curr) => acc + parseAmount(curr?.amount), 0);
  const lastMonthExpense = lastMonthData.filter(t => getRawType(t) === 'expense').reduce((acc, curr) => acc + parseAmount(curr?.amount), 0);
  
  const calcMoM = (current, previous) => previous === 0 ? (current > 0 ? 100 : 0) : (((current - previous) / previous) * 100).toFixed(1);
  const incomeMoM = calcMoM(totalIncome, lastMonthIncome);
  const expenseMoM = calcMoM(totalExpense, lastMonthExpense);

  const expenseByCategory = filteredData
    .filter((t) => getRawType(t) === 'expense')
    .reduce((acc, curr) => {
      const catName = getCategory(curr);
      const existing = acc.find((item) => item.name === catName);
      if (existing) {
        existing.value += parseAmount(curr?.amount);
      } else {
        acc.push({ name: catName, value: parseAmount(curr?.amount) });
      }
      return acc;
    }, []).sort((a, b) => b.value - a.value);

  const topCategory = expenseByCategory.length > 0 ? expenseByCategory[0] : null;

  const comparisonData = [
    { name: 'Financial Overview', Income: totalIncome, Expense: totalExpense }
  ];

  const savingsRate = totalIncome > 0 ? (((totalIncome - totalExpense) / totalIncome) * 100).toFixed(1) : 0;
  const insightPrimary = topCategory ? `Your highest expense this month was on ${topCategory.name} (₹${topCategory.value.toLocaleString('en-IN')}).` : "No major expenses recorded yet.";
  const insightSecondary = totalIncome > 0 ? (totalIncome > totalExpense ? `Excellent! You saved ${savingsRate}% of your total income.` : `Warning: Your expenses exceeded your income by ₹${Math.abs(netBalance).toLocaleString('en-IN')}.`) : "";

  const handleDownloadPDF = () => {
    window.print();
  };

  const handleDownloadCSV = () => {
    const headers = ['Date', 'Category', 'Transaction Type', 'Amount (INR)'];
    const csvRows = [headers.join(',')];
    filteredData.forEach(t => {
      csvRows.push([getRawDate(t), `"${getCategory(t)}"`, getRawType(t), parseAmount(t?.amount)].join(','));
    });
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `FinSight_Ledger_${selectedMonth}.csv`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <AppShell>
      <style>
        {`
          #ca-print-report { display: none; }
          
          @media print {
            body * { visibility: hidden; }
            body { background-color: #ffffff !important; margin: 0; }
            
            #ca-print-report {
              display: block; position: absolute; left: 0; top: 0; width: 100%;
              color: #1e293b; font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px;
            }
            #ca-print-report * { visibility: visible; }
            
            .corp-header { border-bottom: 3px solid #0f172a; padding-bottom: 15px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }
            .corp-logo { font-size: 32px; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -1px; }
            .corp-logo span { color: #14b8a6; }
            .corp-tagline { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }
            .corp-meta { text-align: right; font-size: 12px; color: #475569; line-height: 1.6; }
            .corp-meta strong { color: #0f172a; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; }

            .section-title { font-size: 14px; font-weight: 700; color: #0f172a; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin: 35px 0 15px 0; letter-spacing: 0.5px; }
            
            .corp-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 11px; }
            .corp-table th { background-color: #0f172a !important; color: #ffffff !important; padding: 10px; text-align: left; text-transform: uppercase; letter-spacing: 0.5px; -webkit-print-color-adjust: exact; print-color-adjust: exact; border: none; }
            .corp-table td { padding: 10px; border-bottom: 1px solid #e2e8f0; color: #334155; }
            .corp-table tr:nth-child(even) td { background-color: #f8fafc !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            
            .val-pos { color: #16a34a; font-weight: 600; }
            .val-neg { color: #dc2626; font-weight: 600; }
            .val-net { font-size: 14px; font-weight: 800; color: #0f172a; }
            
            .watermark { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 90px; font-weight: 900; color: rgba(15, 23, 42, 0.03); z-index: -1; white-space: nowrap; pointer-events: none; }
            
            .sign-block { display: flex; justify-content: space-between; margin-top: 80px; padding-top: 20px; break-inside: avoid; }
            .sign-box { text-align: center; width: 200px; border-top: 1px solid #000; padding-top: 10px; font-size: 12px; font-weight: 600; color: #0f172a; }

            .footer-legal { margin-top: 50px; font-size: 9px; color: #94a3b8; text-align: justify; border-top: 1px solid #e2e8f0; padding-top: 15px; line-height: 1.5; break-inside: avoid; }
            
            .insight-box { background-color: #f8fafc !important; border-left: 4px solid #14b8a6 !important; padding: 12px; margin-bottom: 20px; font-size: 12px; color: #334155; }
          }
        `}
      </style>

      {/* 1. VISIBLE DASHBOARD */}
      <div className="max-w-6xl mx-auto print:hidden">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-7">
          <div>
            <h1 className="font-display text-2xl font-semibold text-ink">Monthly Report</h1>
            <p className="text-sm text-ink-light mt-0.5">Advanced financial analytics & insights.</p>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} className="p-2 border border-slate-200 rounded-lg shadow-card text-sm font-medium text-ink focus:outline-none focus:ring-2 focus:ring-teal" />
            
            <button onClick={handleDownloadCSV} className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg text-sm font-medium transition-colors shadow-card">
              <FileText size={16} /> Export CSV
            </button>
            
            <button onClick={handleDownloadPDF} className="flex items-center gap-2 px-4 py-2 bg-teal text-white rounded-lg text-sm font-medium hover:bg-teal-dark transition-colors shadow-card">
              <Download size={16} /> Export PDF
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-20 text-ink-light">Loading report from database...</div>
        ) : (
          <>
            <div className="bg-gradient-to-r from-teal-50/50 to-blue-50/50 p-4 rounded-xl border border-teal-100 mb-6 flex items-start gap-3">
              <Sparkles className="text-teal shrink-0 mt-0.5" size={20} />
              <div>
                <h3 className="font-semibold text-ink text-sm">Smart Insights</h3>
                <p className="text-sm text-ink-light mt-1">{insightPrimary} {insightSecondary}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white p-6 rounded-xl shadow-card border border-slate-100 border-l-4 border-l-green-500">
                <p className="text-xs text-ink-light font-medium uppercase tracking-wider">Total Income</p>
                <p className="font-display text-3xl font-semibold text-ink mt-2">₹{totalIncome.toLocaleString('en-IN')}</p>
                <div className="mt-2 text-xs font-medium">
                  {incomeMoM >= 0 ? <span className="text-green-600 flex items-center gap-1"><TrendingUp size={14}/> +{incomeMoM}% from last month</span> : <span className="text-red-500 flex items-center gap-1"><TrendingDown size={14}/> {incomeMoM}% from last month</span>}
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-card border border-slate-100 border-l-4 border-l-red-500 relative">
                <p className="text-xs text-ink-light font-medium uppercase tracking-wider">Total Expenses</p>
                <p className="font-display text-3xl font-semibold text-ink mt-2">₹{totalExpense.toLocaleString('en-IN')}</p>
                <div className="mt-2 text-xs font-medium">
                  {expenseMoM > 0 ? <span className="text-red-500 flex items-center gap-1"><TrendingUp size={14}/> +{expenseMoM}% from last month</span> : <span className="text-green-600 flex items-center gap-1"><TrendingDown size={14}/> {expenseMoM}% from last month</span>}
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-xl shadow-card border border-slate-100 border-l-4 border-l-blue-500">
                <p className="text-xs text-ink-light font-medium uppercase tracking-wider">Closing Balance</p>
                <p className="font-display text-3xl font-semibold text-ink mt-2">₹{closingBalance.toLocaleString('en-IN')}</p>
                <div className="mt-2 text-xs text-slate-400 font-medium">Available liquid funds</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="bg-white p-6 rounded-xl shadow-card border border-slate-100">
                <h2 className="text-lg font-semibold text-ink mb-4">Expense Distribution</h2>
                {expenseByCategory.length > 0 ? (
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                        <Pie data={expenseByCategory} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                          {expenseByCategory.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                        </Pie>
                        <Tooltip formatter={(value) => `₹${value.toLocaleString('en-IN')}`} />
                        <Legend verticalAlign="bottom" height={36} wrapperStyle={{ paddingTop: '15px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : <p className="text-ink-light text-center py-20">No expense records found.</p>}
              </div>

              <div className="bg-white p-6 rounded-xl shadow-card border border-slate-100">
                <h2 className="text-lg font-semibold text-ink mb-4"> Comparison</h2>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonData} margin={{ top: 10, right: 15, left: 10, bottom: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="name" hide />
                      <YAxis width={110} tick={{ fontSize: 11 }} tickFormatter={(value) => `₹${Number(value).toLocaleString('en-IN')}`} />
                      <Tooltip formatter={(value) => `₹${value.toLocaleString('en-IN')}`} />
                      <Legend verticalAlign="bottom" height={36} wrapperStyle={{ paddingTop: '15px' }} />
                      <Bar dataKey="Income" fill="#22c55e" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Expense" fill="#ef4444" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-card border border-slate-100">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                <h2 className="text-lg font-semibold text-ink">Statement Log (Ledger)</h2>
                
                <div className="flex gap-3 w-full sm:w-auto">
                  <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-teal">
                    <option value="all">All Entries</option>
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                  
                  <div className="relative flex-1 sm:w-64">
                    <Search className="absolute left-3 top-2.5 text-slate-400" size={18} />
                    <input type="text" placeholder="Search Category..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal" />
                  </div>
                </div>
              </div>
              
              <div className="overflow-x-auto max-h-72">
                <table className="w-full min-w-[500px] text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 text-ink-light text-sm">
                      <th className="pb-3 font-medium">Date</th>
                      <th className="pb-3 font-medium">Category</th>
                      <th className="pb-3 font-medium text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchedTransactions.length > 0 ? searchedTransactions.map((t, idx) => (
                      <tr key={t?.id || idx} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                        <td className="py-3 text-sm text-ink-light">{getRawDate(t)}</td>
                        <td className="py-3 text-sm font-medium text-ink">{getCategory(t)}</td>
                        <td className={`py-3 text-sm font-bold text-right ${getRawType(t) === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                          {getRawType(t) === 'income' ? '+' : '-'}₹{parseAmount(t?.amount).toLocaleString('en-IN')}
                        </td>
                      </tr>
                    )) : <tr><td colSpan="3" className="py-6 text-center text-ink-light">No transactions found.</td></tr>}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>

      {/* 2. ENTERPRISE HIDDEN REPORT (PRINT VIEW) */}
      <div id="ca-print-report">
        <div className="watermark">FINSIGHT ANALYTICS</div>
        <div className="corp-header">
          <div>
            <h1 className="corp-logo">FinSight<span>.</span></h1>
            <p className="corp-tagline">Advanced Financial Intelligence & Audit</p>
          </div>
          <div className="corp-meta">
            <p style={{ margin: '0 0 5px 0' }}><strong>Statement of Accounts</strong></p>
            <p style={{ margin: '0' }}>Billing Period: {selectedMonth}</p>
            <p style={{ margin: '0' }}>Generated On: {new Date().toLocaleDateString('en-IN')}</p>
          </div>
        </div>

        <div className="insight-box">
          <strong>Key Insight:</strong> {insightPrimary} {insightSecondary}
        </div>

        <div className="section-title">1. Executive Summary & Reconciliation</div>
        <table className="corp-table">
          <thead>
            <tr>
              <th style={{ width: '70%' }}>Particulars</th>
              <th style={{ textAlign: 'right' }}>Amount (INR)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ fontWeight: '600' }}>Opening Balance (As on 1st {selectedMonth})</td>
              <td style={{ textAlign: 'right', fontWeight: '600' }}>₹{openingBalance.toLocaleString('en-IN')}</td>
            </tr>
            <tr>
              <td>Total Receipts / Income Credited</td>
              <td style={{ textAlign: 'right' }} className="val-pos">+ ₹{totalIncome.toLocaleString('en-IN')}</td>
            </tr>
            <tr>
              <td>Total Payments / Expenses Debited</td>
              <td style={{ textAlign: 'right' }} className="val-neg">- ₹{totalExpense.toLocaleString('en-IN')}</td>
            </tr>
            <tr>
              <td>Tax Deducted at Source (TDS) / Estimated Tax</td>
              <td style={{ textAlign: 'right', color: '#ea580c' }}>- ₹{totalTDS.toLocaleString('en-IN')}</td>
            </tr>
            <tr style={{ borderTop: '2px solid #e2e8f0' }}>
              <td style={{ fontWeight: '800', color: '#0f172a', paddingTop: '15px' }}>Closing Balance / Net Available Funds</td>
              <td style={{ textAlign: 'right', paddingTop: '15px' }} className="val-net">₹{closingBalance.toLocaleString('en-IN')}</td>
            </tr>
          </tbody>
        </table>

        {/* --- FIXED BAR CHART IN PDF VIEW --- */}
        <div className="section-title" style={{ breakBefore: 'auto' }}>2. Visual Analytics</div>
        <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', marginBottom: '25px', breakInside: 'avoid' }}>
          
          {expenseByCategory.length > 0 && (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#0f172a', marginBottom: '10px' }}>Expense Distribution</div>
              <PieChart width={300} height={230} margin={{ top: 0, right: 0, left: 0, bottom: 30 }}>
                <Pie data={expenseByCategory} cx="50%" cy="50%" innerRadius={45} outerRadius={75} paddingAngle={5} dataKey="value" isAnimationActive={false}>
                  {expenseByCategory.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Legend verticalAlign="bottom" height={30} wrapperStyle={{ fontSize: '10px', paddingTop: '15px' }} />
              </PieChart>
            </div>
          )}

          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#0f172a', marginBottom: '10px' }}></div>
            
            <BarChart width={340} height={230} data={comparisonData} isAnimationActive={false} margin={{ top: 15, right: 15, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" hide />
              <YAxis width={100} tick={{ fontSize: 10 }} tickFormatter={(value) => `₹${Number(value).toLocaleString('en-IN')}`} style={{ fontSize: '10px' }} />
              
              <Bar dataKey="Income" fill="#22c55e" radius={[6, 6, 0, 0]} isAnimationActive={false} />
              <Bar dataKey="Expense" fill="#ef4444" radius={[6, 6, 0, 0]} isAnimationActive={false} />
            </BarChart>

            {/* Custom HTML Legend  */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '25px', marginTop: '10px', fontSize: '11px', fontWeight: '600' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {/* 🟢 Income */}
                <svg width="12" height="12"><rect width="12" height="12" rx="2" fill="#22c55e" /></svg>
                <span style={{ color: '#475569' }}>Income</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {/* 🔴 Expense */}
                <svg width="12" height="12"><rect width="12" height="12" rx="2" fill="#ef4444" /></svg>
                <span style={{ color: '#475569' }}>Expense</span>
              </div>
            </div>
          </div>
        </div>

        {expenseByCategory.length > 0 && (
          <>
            <div className="section-title">3. Category-wise Expense Analysis</div>
            <table className="corp-table">
              <thead>
                <tr>
                  <th style={{ width: '50%' }}>Expense Category</th>
                  <th style={{ textAlign: 'right' }}>Amount (INR)</th>
                  <th style={{ textAlign: 'right' }}>% of Total Exp.</th>
                </tr>
              </thead>
              <tbody>
                {expenseByCategory.map((cat, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: '500' }}>{cat.name}</td>
                    <td style={{ textAlign: 'right' }}>₹{cat.value.toLocaleString('en-IN')}</td>
                    <td style={{ textAlign: 'right', color: '#64748b' }}>{totalExpense > 0 ? ((cat.value / totalExpense) * 100).toFixed(1) : 0}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        <div className="section-title">4. Detailed Transaction Ledger</div>
        <table className="corp-table">
          <thead>
            <tr>
              <th style={{ width: '20%' }}>Date</th>
              <th style={{ width: '40%' }}>Particulars</th>
              <th style={{ width: '15%', textAlign: 'center' }}>Type</th>
              <th style={{ width: '25%', textAlign: 'right' }}>Amount (INR)</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.length > 0 ? filteredData.map((t, idx) => (
              <tr key={t?.id || idx}>
                <td style={{ color: '#64748b' }}>{getRawDate(t)}</td>
                <td style={{ fontWeight: '600' }}>{getCategory(t)}</td>
                <td style={{ textAlign: 'center', textTransform: 'capitalize' }}>
                  <span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: '700', backgroundColor: getRawType(t) === 'income' ? '#dcfce7' : '#fee2e2', color: getRawType(t) === 'income' ? '#16a34a' : '#dc2626' }}>
                    {getRawType(t)}
                  </span>
                </td>
                <td style={{ textAlign: 'right', fontWeight: '700' }}>
                  {getRawType(t) === 'income' ? <span className="val-pos">+ ₹{parseAmount(t?.amount).toLocaleString('en-IN')}</span> : <span className="val-neg">- ₹{parseAmount(t?.amount).toLocaleString('en-IN')}</span>}
                </td>
              </tr>
            )) : <tr><td colSpan="4" style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>No transactions recorded for this billing cycle.</td></tr>}
          </tbody>
        </table>

        {/* --- SIGNATURE BLOCK --- */}
        <div className="sign-block">
          <div className="sign-box">System Admin / Preparer</div>
          <div className="sign-box">Authorized Signatory / CA</div>
        </div>

        <div className="footer-legal">
          <p><strong>CONFIDENTIALITY NOTICE:</strong> This document and any attachments are confidential and may also be privileged. If you are not the intended recipient, please delete all copies and notify the sender immediately.</p>
          <p style={{ marginTop: '5px' }}>This financial statement is generated automatically by FinSight Analytics systems. While every effort has been made to ensure accuracy, FinSight Analytics accepts no liability for any errors or omissions.</p>
          <p style={{ marginTop: '10px', textAlign: 'center', fontWeight: 'bold', color: '#cbd5e1' }}>*** END OF SYSTEM GENERATED REPORT ***</p>
        </div>
      </div>
    </AppShell>
  );
}