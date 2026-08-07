import { useState, useEffect } from 'react';
import { Video, ShieldCheck, ShieldAlert, Cpu, Play, Pause, RefreshCcw, Settings, Layers, AlignLeft } from 'lucide-react';

interface InspectionLog {
  id: number;
  time: string;
  item: string;
  status: 'PASS' | 'FAIL';
  detail: string;
}

function LiveInspection() {
  const [activeFeed, setActiveFeed] = useState('cam1');
  const [isLive, setIsLive] = useState(true);
  const [logs, setLogs] = useState<InspectionLog[]>([
    { id: 1, time: '14:32:01', item: 'VP-ITEM-08422', status: 'PASS', detail: 'OCR text read matches barcode' },
    { id: 2, time: '14:31:45', item: 'VP-ITEM-08421', status: 'PASS', detail: 'Label straightness variance: 0.12°' },
    { id: 3, time: '14:31:28', item: 'VP-ITEM-08420', status: 'FAIL', detail: 'Expiry date missing / OCR failed' },
    { id: 4, time: '14:31:12', item: 'VP-ITEM-08419', status: 'PASS', detail: 'HDR Exposure optimized: blenders active' }
  ]);

  // Simulate incoming live camera stream inspections
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLive) {
      interval = setInterval(() => {
        const itemNum = Math.floor(Math.random() * 1000) + 8423;
        const pass = Math.random() > 0.15;
        const timeStr = new Date().toLocaleTimeString();
        
        const newLog: InspectionLog = {
          id: Date.now(),
          time: timeStr,
          item: `VP-ITEM-0${itemNum}`,
          status: pass ? 'PASS' : 'FAIL',
          detail: pass 
            ? `Passed. Alignment straight. OCR Verified.`
            : `Failed. Label misaligned (${(Math.random() * 15 + 4).toFixed(2)} deg skew).`
        };

        setLogs(prev => [newLog, ...prev.slice(0, 15)]);
      }, 3500);
    }
    return () => clearInterval(interval);
  }, [isLive]);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold text-industrial-400 uppercase tracking-widest">Real-time Stream Inspection</p>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider mt-1">Live Camera Feeds</h2>
        </div>
        
        <div className="flex items-center gap-3">
          <select 
            value={activeFeed}
            onChange={(e) => setActiveFeed(e.target.value)}
            className="py-2.5 px-4 bg-slate-900 border border-slate-800 text-xs font-semibold text-white rounded-xl focus:outline-none focus:border-industrial-500"
          >
            <option value="cam1">Line 1 - Main Conveyeor (Cam 1)</option>
            <option value="cam2">Line 2 - Packaging Bin (Cam 2)</option>
            <option value="simulation">Simulation Directory Stream</option>
          </select>

          <button
            onClick={() => setIsLive(!isLive)}
            className={`flex items-center gap-2 py-2.5 px-5 text-xs font-bold text-white border rounded-xl transition-all active:scale-95 ${
              isLive 
                ? 'bg-rose-950/20 border-rose-900/30 text-rose-400' 
                : 'bg-emerald-950/20 border-emerald-900/30 text-emerald-400'
            }`}
          >
            {isLive ? <Pause size={14} /> : <Play size={14} />}
            {isLive ? 'Pause Stream' : 'Resume Live'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Live Camera Stream monitor */}
        <div className="lg:col-span-2 glass-panel rounded-3xl overflow-hidden flex flex-col h-[460px]">
          <div className="px-6 py-4 border-b border-[#1e293b]/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Video size={16} className="text-industrial-500" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">Live camera stream - active</span>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-widest">
                FPS: {isLive ? '29.4' : '0.0'}
              </span>
            </div>
          </div>

          <div className="flex-1 bg-slate-950/95 relative flex items-center justify-center p-6">
            {/* Grid background */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#38bdf803_1px,transparent_1px),linear-gradient(to_bottom,#38bdf803_1px,transparent_1px)] bg-[size:1.5rem_1.5rem]"></div>
            
            {/* Scanning Laser Line */}
            {isLive && (
              <div className="absolute inset-x-0 h-[2px] bg-industrial-500/50 shadow-glass shadow-industrial-400 top-1/4 animate-bounce pointer-events-none"></div>
            )}

            {/* Target Reticle */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 border border-dashed border-industrial-500/20 rounded-full pointer-events-none"></div>
            
            {/* Active inspection object frame */}
            <div className="border border-industrial-500/40 bg-industrial-950/10 p-8 rounded-2xl w-full max-w-md flex items-center gap-6 relative">
              {/* Corner brackets */}
              <div className="absolute top-0 left-0 h-4 w-4 border-t border-l border-industrial-400"></div>
              <div className="absolute top-0 right-0 h-4 w-4 border-t border-r border-industrial-400"></div>
              <div className="absolute bottom-0 left-0 h-4 w-4 border-b border-l border-industrial-400"></div>
              <div className="absolute bottom-0 right-0 h-4 w-4 border-b border-r border-industrial-400"></div>

              {/* Product Shape graphic mockup */}
              <div className="h-24 w-24 bg-slate-900 border border-slate-800 rounded-xl flex flex-col items-center justify-center relative flex-shrink-0">
                <Cpu size={24} className="text-slate-500 animate-pulse" />
                <span className="text-[8px] font-mono text-slate-500 mt-2">PRODUCT BOX</span>
              </div>
              
              <div className="flex-1 space-y-2">
                <div className="flex justify-between items-start">
                  <h4 className="text-xs font-bold text-white uppercase">Inspection Object</h4>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 bg-emerald-950 text-emerald-400 rounded border border-emerald-500/30">PASS</span>
                </div>
                <div className="text-[10px] text-slate-400 font-medium space-y-1">
                  <p>Model Class: <span className="text-white">Industrial Carton</span></p>
                  <p>OCR Decoded: <span className="text-industrial-400 font-semibold font-mono">VP-2026-A9</span></p>
                  <p>Orientation: <span className="text-emerald-400">0.00° Corrected</span></p>
                  <p>Barcode check: <span className="text-emerald-400">Verified</span></p>
                </div>
              </div>
            </div>

            {/* Corner status logs */}
            <div className="absolute bottom-4 left-4 bg-slate-950/80 border border-slate-900 px-3 py-1.5 rounded-lg text-[9px] font-mono text-slate-400">
              <span className="text-industrial-400 font-bold">MIDDLEWARE DECISION:</span> HDR FUSION (Mertens)
            </div>
            <div className="absolute bottom-4 right-4 bg-slate-950/80 border border-slate-900 px-3 py-1.5 rounded-lg text-[9px] font-mono text-slate-400">
              <span className="text-emerald-400 font-bold">STRAIGHTENER:</span> DBSCAN Ensemble Fused
            </div>
          </div>
        </div>

        {/* Live Logs & Packaging check panel */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col h-[460px]">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-4 border-b border-[#1e293b]/50 pb-4">
            Packaging Inspections
          </h3>
          
          <div className="flex-1 overflow-y-auto space-y-3.5 custom-scrollbar pr-2">
            {logs.map((log) => (
              <div 
                key={log.id} 
                className={`p-3.5 rounded-xl border transition-all flex items-start gap-3 ${
                  log.status === 'FAIL' 
                    ? 'bg-rose-950/15 border-rose-950/50 text-rose-300' 
                    : 'bg-emerald-950/15 border-emerald-950/50 text-emerald-300'
                }`}
              >
                {log.status === 'FAIL' 
                  ? <ShieldAlert size={16} className="text-rose-500 mt-0.5 flex-shrink-0" />
                  : <ShieldCheck size={16} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                }
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-xs font-bold text-white">{log.item}</span>
                    <span className="text-[9px] font-mono text-slate-500">{log.time}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-normal">{log.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LiveInspection;
