import { useEffect, useState } from 'react'
import { Activity, RefreshCcw, TrendingUp, AlertCircle, CheckCircle2, ChevronRight, Zap } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { financialHealthApi } from '../api/financialHealthApi'

function getScoreColor(score) {
    if (score >= 90) return 'text-mint border-mint bg-mint/10'
    if (score >= 75) return 'text-teal border-teal bg-teal/10'
    if (score >= 60) return 'text-amber-500 border-amber-500 bg-amber-500/10'
    if (score >= 40) return 'text-orange-500 border-orange-500 bg-orange-500/10'
    return 'text-red-500 border-red-500 bg-red-500/10'
}

function MetricCard({ title, value, max = 100, suffix = "%" }) {
    const isNA = value < 0;
    const displayValue = isNA ? "N/A" : Math.round(value) + suffix;
    const progress = isNA ? 0 : Math.min(100, (value / max) * 100);

    return (
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-5">
            <h3 className="text-sm font-medium text-slate-500 mb-2">{title}</h3>
            <div className="text-2xl font-bold text-navy mb-3">{displayValue}</div>
            <div className="w-full bg-slate-100 rounded-full h-2">
                <div 
                    className="bg-teal h-2 rounded-full transition-all duration-1000" 
                    style={{ width: `${progress}%` }} 
                />
            </div>
        </div>
    )
}

export default function FinancialHealth() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)
    const [simulateSavings, setSimulateSavings] = useState(0)
    const [simulateBudget, setSimulateBudget] = useState(0)
    const [simulateEmergency, setSimulateEmergency] = useState(0)
    const [insightsLoading, setInsightsLoading] = useState(false)
    
    useEffect(() => {
        loadData()
    }, [])

    async function loadData() {
        setLoading(true)
        try {
            const res = await financialHealthApi.getHealthScore()
            setData(res)
        } catch (error) {
            console.error("Failed to load health score", error)
        } finally {
            setLoading(false)
        }
    }

    async function handleRefresh() {
        setRefreshing(true)
        try {
            const res = await financialHealthApi.refreshHealthScore()
            setData(res)
        } catch (error) {
            console.error("Failed to refresh", error)
        } finally {
            setRefreshing(false)
        }
    }

    async function handleSimulate(e) {
        e.preventDefault()
        if (simulateSavings === 0 && simulateBudget === 0 && simulateEmergency === 0) return;
        setRefreshing(true)
        setInsightsLoading(true)
        try {
            const overrides = {}
            if (simulateSavings > 0) overrides.savings_rate = Math.min(100, data.metrics.savings_rate + simulateSavings)
            if (simulateBudget > 0) overrides.budget_discipline = Math.min(100, data.metrics.budget_discipline + simulateBudget)
            if (simulateEmergency > 0) overrides.emergency_fund = Math.min(100, data.metrics.emergency_fund + simulateEmergency)

            // We don't need step 1 anymore because the frontend calculates it in real-time!
            // Just trigger the AI background generation
            const aiRes = await financialHealthApi.simulateHealthScore(overrides, false)
            
            setData(prev => ({
                ...prev,
                score: aiRes.score,
                metrics: aiRes.metrics,
                insights: aiRes.insights,
                isSimulation: true
            }))
            setRefreshing(false)
        } catch (error) {
            console.error("Simulation failed", error)
            setRefreshing(false)
        } finally {
            setInsightsLoading(false)
        }
    }

    if (loading || !data) {
        return (
            <AppShell>
                <div className="animate-pulse flex flex-col gap-6">
                    <div className="h-48 bg-white rounded-xl shadow-card"></div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="h-32 bg-white rounded-xl shadow-card"></div>
                        <div className="h-32 bg-white rounded-xl shadow-card"></div>
                    </div>
                </div>
            </AppShell>
        )
    }

    const { score, metrics, insights, isSimulation } = data

    // REAL-TIME PROJECTION: Calculate the projected score instantly as the user drags the sliders
    const baseWeights = {
        savings_rate: 20, budget_discipline: 20, emergency_fund: 15,
        investment_habit: 15, expense_stability: 10, goal_progress: 10, debt_management: 10
    };

    const projectedMetrics = { ...metrics };
    let displayScore = score;
    let isPreviewing = false;

    if (!isSimulation && (simulateSavings > 0 || simulateBudget > 0 || simulateEmergency > 0)) {
        isPreviewing = true;
        if (simulateSavings > 0) projectedMetrics.savings_rate = Math.min(100, Math.max(0, metrics.savings_rate) + simulateSavings);
        if (simulateBudget > 0) projectedMetrics.budget_discipline = Math.min(100, Math.max(0, metrics.budget_discipline) + simulateBudget);
        if (simulateEmergency > 0) projectedMetrics.emergency_fund = Math.min(100, Math.max(0, metrics.emergency_fund) + simulateEmergency);
        
        let activeWeights = 0;
        let totalScore = 0;
        for (const [key, val] of Object.entries(projectedMetrics)) {
            if (val >= 0) activeWeights += baseWeights[key] || 0;
        }
        if (activeWeights > 0) {
            for (const [key, val] of Object.entries(projectedMetrics)) {
                if (val >= 0) totalScore += val * ((baseWeights[key] || 0) / activeWeights);
            }
            displayScore = Math.round(totalScore);
        }
    }

    const scoreColorClass = getScoreColor(displayScore)

    return (
        <AppShell>
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="font-display text-3xl font-bold text-navy flex items-center gap-2">
                        <Activity className="text-teal" size={32} />
                        Financial Health Score
                    </h1>
                    <p className="text-slate-500 mt-1">
                        {isSimulation ? "Simulated projection based on your what-if scenario." : "A comprehensive evaluation of your financial habits based on your data."}
                    </p>
                </div>
                {!isSimulation && (
                    <button 
                        onClick={handleRefresh} 
                        disabled={refreshing}
                        className="flex items-center gap-2 bg-white border border-slate-200 shadow-sm px-4 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50"
                    >
                        <RefreshCcw size={16} className={refreshing ? "animate-spin" : ""} />
                        Refresh Score
                    </button>
                )}
                {isSimulation && (
                    <button 
                        onClick={() => {
                            setSimulateSavings(0);
                            setSimulateBudget(0);
                            setSimulateEmergency(0);
                            setData(prev => ({ ...prev, isSimulation: false }));
                            loadData();
                        }}
                        className="flex items-center gap-2 bg-teal text-white shadow-sm px-4 py-2 rounded-lg text-sm font-medium hover:bg-teal/90 transition-colors"
                    >
                        Reset to Actual
                    </button>
                )}
            </div>

            {/* Score Header */}
            <div className="bg-navy rounded-3xl p-8 shadow-xl text-white mb-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-navy via-navy to-teal/40 opacity-80" />
                <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
                    {/* Circular Score */}
                    <div className="relative w-48 h-48 flex items-center justify-center shrink-0">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
                            <circle 
                                cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="8" 
                                strokeDasharray={`${(displayScore / 100) * 283} 283`}
                                className={`transition-all duration-1500 ${getScoreColor(displayScore).split(' ')[0]}`}
                            />
                        </svg>
                        <div className="absolute flex flex-col items-center">
                            <span className="text-5xl font-display font-bold">{displayScore}</span>
                            <span className="text-sm font-medium text-slate-300 uppercase tracking-widest mt-1">/ 100</span>
                        </div>
                    </div>
                    
                    <div className="flex-1 text-center md:text-left">
                        <h2 className="text-3xl font-display font-semibold mb-2">{insights?.score_category || "Analyzing..."}</h2>
                        <p className="text-lg text-slate-300 mb-6 max-w-2xl leading-relaxed">
                            {insights?.explanation || "We evaluated your savings rate, budget discipline, emergency fund, and investment habits to determine this score."}
                        </p>
                        
                        <div className={`grid grid-cols-2 gap-4 max-w-lg transition-opacity ${insightsLoading ? 'opacity-50' : 'opacity-100'}`}>
                            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/5">
                                <div className="text-sm text-slate-300 mb-1">Savings Rate</div>
                                <div className="text-xl font-bold">{projectedMetrics.savings_rate >= 0 ? Math.round(projectedMetrics.savings_rate) + '%' : 'N/A'}</div>
                            </div>
                            <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/5">
                                <div className="text-sm text-slate-300 mb-1">Budget Discipline</div>
                                <div className="text-xl font-bold">{projectedMetrics.budget_discipline >= 0 ? Math.round(projectedMetrics.budget_discipline) + '/100' : 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Metrics Breakdown */}
                <div className="lg:col-span-2 space-y-8">
                    <h2 className="text-xl font-bold text-navy">Metrics Breakdown</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <MetricCard title="Emergency Fund" value={projectedMetrics.emergency_fund} />
                        <MetricCard title="Investment Habit" value={projectedMetrics.investment_habit} />
                        <MetricCard title="Expense Stability" value={projectedMetrics.expense_stability} />
                        <MetricCard title="Goal Progress" value={projectedMetrics.goal_progress} />
                    </div>

                    {/* AI Insights */}
                    <div className={`bg-white rounded-2xl shadow-card border border-slate-100 overflow-hidden transition-opacity ${insightsLoading ? 'opacity-50' : 'opacity-100'}`}>
                        <div className="bg-slate-50 border-b border-slate-100 p-5 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Zap className="text-amber-500" size={20} />
                                <h3 className="font-semibold text-navy">AI Coach Insights</h3>
                            </div>
                            {insightsLoading && (
                                <div className="flex items-center gap-2 text-sm text-teal font-medium">
                                    <RefreshCcw size={14} className="animate-spin" />
                                    Analyzing new scenario...
                                </div>
                            )}
                        </div>
                        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div>
                                <h4 className="flex items-center gap-2 text-sm font-bold text-mint mb-3 uppercase tracking-wider">
                                    <CheckCircle2 size={16} /> Strengths
                                </h4>
                                <ul className="space-y-3">
                                    {insights?.strengths?.map((s, i) => (
                                        <li key={i} className="text-slate-600 text-sm flex items-start gap-2">
                                            <span className="text-mint mt-0.5">•</span> {s}
                                        </li>
                                    )) || <li className="text-slate-400 text-sm">No specific strengths identified.</li>}
                                </ul>
                            </div>
                            <div>
                                <h4 className="flex items-center gap-2 text-sm font-bold text-red-500 mb-3 uppercase tracking-wider">
                                    <AlertCircle size={16} /> Areas to Improve
                                </h4>
                                <ul className="space-y-3">
                                    {insights?.weaknesses?.map((w, i) => (
                                        <li key={i} className="text-slate-600 text-sm flex items-start gap-2">
                                            <span className="text-red-500 mt-0.5">•</span> {w}
                                        </li>
                                    )) || <li className="text-slate-400 text-sm">No major weaknesses identified.</li>}
                                </ul>
                            </div>
                        </div>
                        <div className="bg-slate-50 p-6 border-t border-slate-100">
                            <h4 className="text-sm font-bold text-navy mb-3 uppercase tracking-wider">Action Plan</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {insights?.action_plan?.map((action, i) => (
                                    <div key={i} className="bg-white border border-slate-200 rounded-lg p-3 text-sm text-slate-700 shadow-sm flex items-center gap-3">
                                        <div className="w-6 h-6 rounded-full bg-teal/10 text-teal flex items-center justify-center shrink-0 font-bold text-xs">{i+1}</div>
                                        {action}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Simulator */}
                <div className="space-y-6">
                    <div className="bg-white rounded-2xl shadow-card border border-teal/20 p-6 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-teal/5 rounded-full -mr-16 -mt-16 blur-2xl"></div>
                        <h3 className="font-bold text-navy flex items-center gap-2 mb-2">
                            <TrendingUp size={20} className="text-teal" />
                            What-If Simulator
                        </h3>
                        <p className="text-sm text-slate-500 mb-6">
                            See how small changes to your habits could improve your Financial Health Score.
                        </p>

                        <form onSubmit={handleSimulate} className="space-y-5 relative z-10">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Increase Savings Rate
                                </label>
                                <div className="flex items-center gap-4">
                                    <input 
                                        type="range" 
                                        min="0" max="50" step="1"
                                        value={simulateSavings}
                                        onChange={(e) => setSimulateSavings(Number(e.target.value))}
                                        className="w-full accent-teal"
                                    />
                                    <span className="font-bold text-navy min-w-[3rem] text-right">+{simulateSavings}%</span>
                                </div>
                            </div>
                            
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Improve Budget Discipline
                                </label>
                                <div className="flex items-center gap-4">
                                    <input 
                                        type="range" 
                                        min="0" max="50" step="1"
                                        value={simulateBudget}
                                        onChange={(e) => setSimulateBudget(Number(e.target.value))}
                                        className="w-full accent-teal"
                                    />
                                    <span className="font-bold text-navy min-w-[3rem] text-right">+{simulateBudget}%</span>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Increase Emergency Fund
                                </label>
                                <div className="flex items-center gap-4">
                                    <input 
                                        type="range" 
                                        min="0" max="50" step="1"
                                        value={simulateEmergency}
                                        onChange={(e) => setSimulateEmergency(Number(e.target.value))}
                                        className="w-full accent-teal"
                                    />
                                    <span className="font-bold text-navy min-w-[3rem] text-right">+{simulateEmergency}%</span>
                                </div>
                            </div>
                            
                            <button 
                                type="submit" 
                                disabled={refreshing || (simulateSavings === 0 && simulateBudget === 0 && simulateEmergency === 0)}
                                className={`w-full py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 flex justify-center items-center gap-2 ${isPreviewing ? 'bg-teal hover:bg-teal/90 text-white shadow-md animate-pulse' : 'bg-navy hover:bg-navy/90 text-white'}`}
                            >
                                {refreshing ? "Generating AI Insights..." : (isPreviewing ? "Get AI Insights for this Scenario" : "Simulate Impact")}
                            </button>
                        </form>
                    </div>
                    
                    {/* Add Recommendations block */}
                    <div className={`bg-mint/10 border border-mint/20 rounded-2xl p-6 transition-opacity ${insightsLoading ? 'opacity-50' : 'opacity-100'}`}>
                        <h4 className="font-bold text-navy mb-4 flex items-center justify-between">
                            Key Recommendations
                            {insightsLoading && <RefreshCcw size={14} className="animate-spin text-teal" />}
                        </h4>
                        <ul className="space-y-4">
                            {insights?.recommendations?.map((rec, i) => (
                                <li key={i} className="flex items-start gap-3 text-sm text-slate-700">
                                    <ChevronRight size={16} className="text-mint shrink-0 mt-0.5" />
                                    <span>{rec}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </AppShell>
    )
}
