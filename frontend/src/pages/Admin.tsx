import { useState } from 'react';
import { ShieldAlert, Server, ToggleLeft, ToggleRight, UserPlus, Trash, Terminal, RefreshCw } from 'lucide-react';

interface UserRole {
  id: number;
  username: string;
  role: 'admin' | 'operator' | 'viewer';
  created: string;
}

function AdminPage() {
  const [engines, setEngines] = useState({
    straightener: true,
    hdr: true,
    yolo: true,
    ocr: true,
    verifier: true
  });

  const [users, setUsers] = useState<UserRole[]>([
    { id: 1, username: 'admin', role: 'admin', created: '2026-08-01' },
    { id: 2, username: 'operator', role: 'operator', created: '2026-08-01' },
    { id: 3, username: 'viewer', role: 'viewer', created: '2026-08-02' }
  ]);

  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    "[18:42:01] VisionPilot Middleware Daemon v1.0.0 listening on 0.0.0.0:8000",
    "[18:42:05] Database Connection Successful: sqlite fallback engine loaded",
    "[18:42:06] Approved Image Straightener copied engine imported",
    "[18:42:06] Approved HDR Fusion copied engine loaded (Laplacian active)",
    "[19:02:12] Ingested inspection_08342.jpg successfully from Client 127.0.0.1",
    "[19:02:14] Pipeline transaction #8412 resolved: STATUS PASS (96.4% conf)"
  ]);

  const toggleEngine = (key: keyof typeof engines) => {
    setEngines(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleRestart = () => {
    setTerminalLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] RESTARTING CORE DAEMON SYSTEM...`, `[${new Date().toLocaleTimeString()}] Core restarted successfully.`]);
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <p className="text-xs font-semibold text-rose-400 uppercase tracking-widest">Admin Control Center</p>
        <h2 className="text-xl font-bold text-white uppercase tracking-wider mt-1">System Administration</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Toggle switches for active engines */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col h-[400px]">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-4 border-b border-slate-800 pb-4 flex items-center gap-2">
            <Server size={16} className="text-rose-500" />
            Middleware Pipeline Modules
          </h3>
          
          <div className="flex-1 space-y-4 overflow-y-auto custom-scrollbar">
            {[
              { key: 'straightener', label: 'Image Straightener Engine', desc: 'Ensemble Hough + FFT angle correction' },
              { key: 'hdr', label: 'HDR Fusion Blending', desc: 'Luminosity-mask Laplacian blends' },
              { key: 'yolo', label: 'YOLO Detector Inference', desc: 'Lightweight product boundary boxes' },
              { key: 'ocr', label: 'OCR Extraction Engine', desc: 'Text-like alphanumeric readers' },
              { key: 'verifier', label: 'Packaging Verification Rules', desc: 'Business logic pass/fail checks' }
            ].map((module) => {
              const active = engines[module.key as keyof typeof engines];
              return (
                <div key={module.key} className="flex items-center justify-between gap-4 p-3 bg-slate-900/40 rounded-xl border border-slate-800/40">
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-bold text-white leading-normal">{module.label}</p>
                    <span className="text-[9px] text-slate-500 block mt-0.5">{module.desc}</span>
                  </div>
                  <button 
                    onClick={() => toggleEngine(module.key as any)}
                    className={`transition-colors ${active ? 'text-industrial-400' : 'text-slate-600'}`}
                  >
                    {active ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* User Roles management panel */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col h-[400px]">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
            <h3 className="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert size={16} className="text-rose-500" />
              Role Permissions
            </h3>
            <button className="flex items-center gap-1 py-1 px-2.5 text-[9px] font-bold uppercase tracking-wider text-industrial-400 bg-industrial-950 hover:bg-industrial-900 border border-industrial-900/30 rounded-lg transition-all">
              <UserPlus size={10} /> Add
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2">
            {users.map((u) => (
              <div key={u.id} className="flex items-center justify-between p-3 bg-slate-900/40 border border-slate-800/40 rounded-xl">
                <div>
                  <p className="text-xs font-bold text-white">{u.username}</p>
                  <span className="text-[9px] font-mono text-slate-500">Created: {u.created}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 text-[9px] font-bold text-industrial-300 uppercase bg-industrial-950 border border-industrial-800/30 rounded-full">
                    {u.role}
                  </span>
                  <button 
                    disabled={u.username === 'admin'}
                    className="text-slate-500 hover:text-rose-400 transition-colors disabled:opacity-30 disabled:pointer-events-none"
                  >
                    <Trash size={12} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Server operational controls and console logs */}
        <div className="glass-panel rounded-3xl p-6 flex flex-col h-[400px]">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
            <h3 className="font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
              <Terminal size={16} className="text-rose-500" />
              System Console
            </h3>
            <button 
              onClick={handleRestart}
              className="flex items-center gap-1 py-1 px-2.5 text-[9px] font-bold uppercase tracking-wider text-white bg-rose-950/40 hover:bg-rose-900 border border-rose-900/30 rounded-lg transition-all"
            >
              <RefreshCw size={10} /> Restart Daemon
            </button>
          </div>

          {/* Console Output */}
          <div className="flex-1 bg-slate-950 rounded-xl p-4 font-mono text-[9px] text-[#38bdf8] space-y-1.5 overflow-y-auto custom-scrollbar select-text">
            {terminalLogs.map((log, idx) => (
              <p key={idx}>{log}</p>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

export default AdminPage;
