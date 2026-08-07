import { useState } from 'react';
import { 
  AreaChart, Area, BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { BarChart3, TrendingUp, ShieldCheck, AlertCircle, Percent } from 'lucide-react';

function Analytics() {
  const [timeframe, setTimeframe] = useState('daily');
  
  // Mock Analytics Summary Data
  const summary = {
    total_processed: 58240,
    total_passed: 57420,
    total_failed: 820,
    yield_rate: 98.59,
    mean_processing_time: 42.8
  };

  // Mock Throughput & Yield Over Time
  const performanceTrend = [
    { name: 'Mon', processed: 8400, passed: 8310, yield: 98.9 },
    { name: 'Tue', processed: 9200, passed: 9080, yield: 98.7 },
    { name: 'Wed', processed: 8900, passed: 8780, yield: 98.6 },
    { name: 'Thu', processed: 9500, passed: 9410, yield: 99.1 },
    { name: 'Fri', processed: 9800, passed: 9680, yield: 98.8 },
    { name: 'Sat', processed: 6400, passed: 6310, yield: 98.6 },
    { name: 'Sun', processed: 6040, passed: 5850, yield: 96.8 }
  ];

  // Mock Skew Angle Correction Scatter
  const skewAngles = [
    { item: 1, angle: -1.2, confidence: 0.94 },
    { item: 2, angle: 2.1, confidence: 0.88 },
    { item: 3, angle: -0.4, confidence: 0.98 },
    { item: 4, angle: 3.5, confidence: 0.72 },
    { item: 5, angle: -2.8, confidence: 0.89 },
    { item: 6, angle: 0.1, confidence: 0.99 },
    { item: 7, angle: -4.2, confidence: 0.65 },
    { item: 8, angle: 1.5, confidence: 0.92 },
    { item: 9, angle: -0.9, confidence: 0.96 }
  ];

  // Mock Exposure Levels Distribution
  const exposureLevels = [
    { label: 'Normal (Balanced)', count: 4890, pct: 58 },
    { label: 'Under-exposed (Shadows)', count: 2108, pct: 25 },
    { label: 'Over-exposed (Highlights)', count: 1414, pct: 17 }
  ];

  return (
    <div className="space-y-8">
      {/* Page Header and Time Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold text-industrial-400 uppercase tracking-widest">Performance Dashboard</p>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider mt-1">Inspection Analytics</h2>
        </div>
        
        <div className="flex bg-slate-900 border border-slate-800 p-1.5 rounded-xl">
          {['daily', 'weekly', 'monthly'].map((t) => (
            <button
              key={t}
              onClick={() => setTimeframe(t)}
              className={`py-1.5 px-4 text-xs font-semibold uppercase tracking-wider rounded-lg transition-colors ${
                timeframe === t ? 'bg-industrial-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { title: 'Total Ingested', value: summary.total_processed.toLocaleString(), label: 'Inspected frames', icon: BarChart3, color: 'text-industrial-400' },
          { title: 'Yield Rate', value: `${summary.yield_rate}%`, label: 'Compliance target: 99%', icon: Percent, color: 'text-emerald-400' },
          { title: 'Passed Products', value: summary.total_passed.toLocaleString(), label: 'Shipped cartons', icon: ShieldCheck, color: 'text-cyan-400' },
          { title: 'Failed Audits', value: summary.total_failed.toLocaleString(), label: 'Rejected items', icon: AlertCircle, color: 'text-rose-400' }
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="glass-panel rounded-2xl p-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{item.title}</span>
                <div className={`p-2 bg-slate-900/50 rounded-xl ${item.color}`}>
                  <Icon size={16} />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">{item.value}</h3>
              <p className="text-xs text-slate-500 font-medium">{item.label}</p>
            </div>
          );
        })}
      </div>

      {/* Throughput and Yield Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-panel rounded-3xl p-6 h-[380px] flex flex-col">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-6">Yield Compliance & Frame Volume</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceTrend}>
                <defs>
                  <linearGradient id="colorProcessed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0e8ee9" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#0e8ee9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPassed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px' }} />
                <Legend verticalAlign="top" height={36} />
                <Area type="monotone" dataKey="processed" name="Total Ingested" stroke="#0e8ee9" fillOpacity={1} fill="url(#colorProcessed)" />
                <Area type="monotone" dataKey="passed" name="Compliance Shipped" stroke="#10b981" fillOpacity={1} fill="url(#colorPassed)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Exposure Distribution Bar chart */}
        <div className="glass-panel rounded-3xl p-6 h-[380px] flex flex-col">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-6">Ingested Exposure Categories</h3>
          <div className="flex-1 min-h-0 flex flex-col justify-between">
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={exposureLevels} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis type="number" stroke="#64748b" fontSize={9} />
                  <YAxis dataKey="label" type="category" stroke="#64748b" fontSize={10} width={80} tickLine={false} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: 'none' }} />
                  <Bar dataKey="pct" name="Percentage %" fill="#38a9f8" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="space-y-3 mt-4 border-t border-slate-800/80 pt-4">
              {exposureLevels.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-xs text-slate-400 font-medium">{item.label}</span>
                  <span className="text-xs font-mono font-bold text-white">{item.count.toLocaleString()} ({item.pct}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Skew Rotation scatter chart */}
      <div className="glass-panel rounded-3xl p-6 h-[350px] flex flex-col">
        <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-6">Ensemble Correction Dispersion</h3>
        <div className="flex-1 min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" dataKey="angle" name="Skew Angle" unit="°" stroke="#64748b" fontSize={11} />
              <YAxis type="number" dataKey="confidence" name="Engine Confidence" unit="" min={0.5} max={1.0} stroke="#64748b" fontSize={11} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#0f172a', border: 'none' }} />
              <Scatter name="Image Correction Samples" data={skewAngles} fill="#818cf8" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
