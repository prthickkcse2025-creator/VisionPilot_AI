import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';
import { 
  Layers, CheckCircle, Percent, Eye, HelpCircle, ShieldCheck, Timer, Wifi, Camera, AlertTriangle, Play, Pause, RefreshCw, Cpu, Sliders, AlignLeft
} from 'lucide-react';

function Dashboard() {
  const [isPlaying, setIsPlaying] = useState(true);
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  
  // Update time for mock feed
  useEffect(() => {
    const timer = setInterval(() => {
      if (isPlaying) {
        setTime(new Date().toLocaleTimeString());
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [isPlaying]);

  // Mock Widget Stats
  const widgets = [
    { title: 'Total Products', value: '24,590', change: '+12% from yesterday', icon: Layers, color: 'text-industrial-400' },
    { title: 'Images Processed', value: '8,412', change: 'Ingested frames', icon: CheckCircle, color: 'text-emerald-400' },
    { title: 'Policy Decision', value: 'HDR_FUSION', change: 'Exposure blending', icon: Cpu, color: 'text-cyan-400' },
    { title: 'Selected Strategy', value: 'HDR_FUSION_Ensemble_v1', change: 'Weighted-median voting', icon: AlignLeft, color: 'text-indigo-400' },
    { title: 'Feature Summary', value: 'DR: 0.78 | Luma: 0.52', change: 'Blur: 0.08 | Skew: 0.02', icon: Sliders, color: 'text-purple-400' },
    { title: 'Confidence Score', value: '94.0%', change: 'Policy reliability', icon: ShieldCheck, color: 'text-teal-400' },
    { title: 'Products Detected', value: '23,410', change: 'YOLO box matches', icon: Eye, color: 'text-amber-400' },
    { title: 'OCR Accuracy', value: '98.42%', change: 'Text validated', icon: HelpCircle, color: 'text-sky-400' },
    { title: 'Packaging Status', value: '99.1% PASS', change: '12 failed inspections', icon: ShieldCheck, color: 'text-emerald-500' },
    { title: 'Processing Time', value: '45.2 ms', change: 'FastAPI local pipeline', icon: Timer, color: 'text-rose-400' }
  ];

  // Mock Chart Data
  const throughputData = [
    { hour: '08:00', processed: 420, defects: 3 },
    { hour: '09:00', processed: 580, defects: 5 },
    { hour: '10:00', processed: 610, defects: 2 },
    { hour: '11:00', processed: 490, defects: 8 },
    { hour: '12:00', processed: 520, defects: 4 },
    { hour: '13:00', processed: 640, defects: 1 },
    { hour: '14:00', processed: 590, defects: 6 }
  ];

  const defectCategories = [
    { name: 'Misaligned Label', value: 45, color: '#0ea5e9' },
    { name: 'OCR Read Failure', value: 28, color: '#6366f1' },
    { name: 'Barcode Unreadable', value: 15, color: '#f59e0b' },
    { name: 'Damaged Box', value: 12, color: '#f43f5e' }
  ];

  const timelineEvents = [
    { id: 1, type: 'fail', time: '14:28:44', label: 'Item #8412', message: 'Label misaligned (-12.4 deg)' },
    { id: 2, type: 'pass', time: '14:27:10', label: 'Item #8411', message: 'Passed. OCR VerifiedVP-2026' },
    { id: 3, type: 'pass', time: '14:26:05', label: 'Item #8410', message: 'Passed. HDR Optimized' },
    { id: 4, type: 'fail', time: '14:23:10', label: 'Item #8409', message: 'OCR confidence 74% below threshold' }
  ];

  return (
    <div className="space-y-8">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {widgets.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="glass-panel hover:glass-panel-accent transition-all duration-300 rounded-2xl p-6 group">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{stat.title}</span>
                <div className={`p-2 bg-slate-900/50 rounded-xl group-hover:scale-105 transition-transform ${stat.color}`}>
                  <Icon size={16} />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">{stat.value}</h3>
              <p className="text-xs text-slate-400 font-medium">{stat.change}</p>
            </div>
          );
        })}
      </div>

      {/* Camera Feed & Timeline Block */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Mock Live Camera Feed */}
        <div className="lg:col-span-2 glass-panel rounded-3xl overflow-hidden flex flex-col h-[400px]">
          <div className="px-6 py-4 border-b border-[#1e293b]/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Camera size={16} className="text-industrial-500" />
              <h3 className="font-bold text-sm text-white uppercase tracking-wider">Live Inspection Stream</h3>
            </div>
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-1.5 bg-slate-900 hover:bg-slate-800 rounded-lg text-slate-300 transition-colors"
              >
                {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              </button>
              <div className="h-4 w-[1px] bg-slate-800"></div>
              <span className="text-xs font-mono font-semibold text-industrial-400">{time}</span>
            </div>
          </div>
          
          <div className="flex-1 bg-slate-950/80 relative flex items-center justify-center p-6">
            {/* Overlay Grid lines for industrial inspection look */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#38bdf805_1px,transparent_1px),linear-gradient(to_bottom,#38bdf805_1px,transparent_1px)] bg-[size:2rem_2rem]"></div>
            
            {/* Target Reticle */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border border-industrial-500/20 rounded-full pointer-events-none"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-industrial-500 rounded-full"></div>
            <div className="absolute top-12 left-12 w-8 h-8 border-t-2 border-l-2 border-industrial-500/40"></div>
            <div className="absolute top-12 right-12 w-8 h-8 border-t-2 border-r-2 border-industrial-500/40"></div>
            <div className="absolute bottom-12 left-12 w-8 h-8 border-b-2 border-l-2 border-industrial-500/40"></div>
            <div className="absolute bottom-12 right-12 w-8 h-8 border-b-2 border-r-2 border-industrial-500/40"></div>

            {/* Inspection Object Mock Box */}
            <div className="border border-emerald-500/60 bg-emerald-500/5 px-8 py-10 rounded-xl max-w-sm text-center relative animate-pulse">
              <span className="absolute -top-3 left-4 px-2 py-0.5 text-[9px] font-bold text-emerald-300 bg-emerald-950 rounded border border-emerald-500/30 uppercase tracking-widest">
                Class: Carton_Package
              </span>
              <p className="text-sm font-bold text-white tracking-wide uppercase">Industrial Product Pack</p>
              <div className="mt-4 border-t border-slate-800/80 pt-4 flex flex-col items-center gap-1">
                <span className="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-950/40 px-2 py-0.5 rounded">OCR: EXP 12/28 - VP-2026</span>
                <span className="text-[10px] text-slate-400 font-semibold">Verification: PASS (98%)</span>
              </div>
            </div>

            {isPlaying && (
              <div className="absolute top-4 left-4 flex items-center gap-2 bg-rose-950/30 border border-rose-900/30 px-2 py-0.5 rounded">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-ping"></span>
                <span className="text-[9px] font-bold text-rose-400 uppercase tracking-widest">REC STREAM</span>
              </div>
            )}
          </div>
        </div>

        {/* Timeline Events / Alerts */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col h-[400px]">
          <div className="flex items-center justify-between mb-4 border-b border-[#1e293b]/50 pb-4">
            <h3 className="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle size={16} className="text-industrial-500" />
              Inspection Timeline
            </h3>
            <button className="text-xs text-slate-400 font-semibold hover:text-white flex items-center gap-1 transition-colors">
              <RefreshCw size={10} /> Clear
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-4 custom-scrollbar pr-2">
            {timelineEvents.map((evt) => (
              <div 
                key={evt.id} 
                className={`p-4 rounded-xl border flex gap-3 ${
                  evt.type === 'fail' 
                    ? 'bg-rose-950/10 border-rose-900/20 text-rose-300' 
                    : 'bg-emerald-950/10 border-emerald-900/20 text-emerald-300'
                }`}
              >
                <div className={`h-2 w-2 mt-1.5 rounded-full flex-shrink-0 ${evt.type === 'fail' ? 'bg-rose-500' : 'bg-emerald-500'}`}></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white uppercase tracking-wide">{evt.label}</span>
                    <span className="text-[10px] font-mono text-slate-500">{evt.time}</span>
                  </div>
                  <p className="text-xs text-slate-400 truncate">{evt.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Hourly Throughput Bar Chart */}
        <div className="lg:col-span-2 glass-panel rounded-3xl p-6 h-[320px] flex flex-col">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-6">Throughput & Defect Yield</h3>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={throughputData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                />
                <Bar dataKey="processed" name="Processed" fill="#0e8ee9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="defects" name="Failed Inspections" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Defect Categories Pie Chart */}
        <div className="glass-panel rounded-3xl p-6 h-[320px] flex flex-col">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-6 font-sans">Defect Breakdown</h3>
          <div className="flex-1 min-h-0 relative flex items-center justify-center">
            <div className="w-1/2 h-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={defectCategories}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {defectCategories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="w-1/2 space-y-2.5">
              {defectCategories.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }}></div>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold text-white truncate">{item.name}</p>
                    <span className="text-[10px] text-slate-500">{item.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
