import { useState } from 'react';
import { Settings, Save, RefreshCw, Sliders, Database, Eye, ShieldCheck } from 'lucide-react';

function SettingsPage() {
  const [activeSection, setActiveSection] = useState<'pipeline' | 'database' | 'storage'>('pipeline');
  const [config, setConfig] = useState({
    straightener_confidence: '0.08',
    straightener_gap: '4.0',
    hdr_mode: 'pytorch_weight',
    hdr_epochs: '10',
    yolo_confidence: '0.25',
    yolo_model: 'yolov8n',
    ocr_lang: 'en',
    ocr_gpu: false,
    postgresql_url: 'postgresql+asyncpg://visionpilot:visionpilot@localhost/visionpilot_db',
    sqlite_fallback: true,
    uploads_dir: 'E:/VisionPilot_AI/uploads',
    outputs_dir: 'E:/VisionPilot_AI/outputs',
    logs_dir: 'E:/VisionPilot_AI/logs'
  });

  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <p className="text-xs font-semibold text-industrial-400 uppercase tracking-widest">Configuration Console</p>
        <h2 className="text-xl font-bold text-white uppercase tracking-wider mt-1">Middleware Settings</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Navigation Sidebar */}
        <div className="glass-panel rounded-3xl p-4 flex flex-col gap-1 h-fit">
          {[
            { id: 'pipeline', label: 'Inference Pipeline', icon: Sliders },
            { id: 'database', label: 'Database & Fallback', icon: Database },
            { id: 'storage', label: 'File System Storage', icon: Settings }
          ].map((sec) => {
            const Icon = sec.icon;
            return (
              <button
                key={sec.id}
                onClick={() => setActiveSection(sec.id as any)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold uppercase tracking-wider text-left transition-all ${
                  activeSection === sec.id 
                    ? 'bg-industrial-600 text-white shadow-glass shadow-industrial-600/10' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                }`}
              >
                <Icon size={14} />
                {sec.label}
              </button>
            );
          })}
        </div>

        {/* Configurations Form */}
        <div className="lg:col-span-3 glass-panel rounded-3xl p-8">
          <form onSubmit={handleSave} className="space-y-6">
            
            {activeSection === 'pipeline' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="font-bold text-sm text-white uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-2">
                  <Eye size={16} className="text-industrial-500" />
                  Inference Stage Thresholds
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Straightener Confidence Gate</label>
                    <input
                      type="text"
                      value={config.straightener_confidence}
                      onChange={(e) => setConfig(prev => ({ ...prev, straightener_confidence: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-semibold text-white rounded-xl focus:outline-none"
                    />
                    <p className="text-[10px] text-slate-500 mt-1 leading-normal">Minimum confidence score to rotate image. Below this, angle is locked at 0.0°.</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Ensemble Gap Cluster Radius (°)</label>
                    <input
                      type="text"
                      value={config.straightener_gap}
                      onChange={(e) => setConfig(prev => ({ ...prev, straightener_gap: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-semibold text-white rounded-xl focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">HDR Blending Mode</label>
                    <select
                      value={config.hdr_mode}
                      onChange={(e) => setConfig(prev => ({ ...prev, hdr_mode: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-semibold text-white rounded-xl focus:outline-none"
                    >
                      <option value="pytorch_weight">Approved Laplacian Blend (Luminosity weights)</option>
                      <option value="mertens">OpenCV Mertens Baseline</option>
                      <option value="deep_fuse">Deep Learning Residual CNN</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Deep CNN Training Epochs</label>
                    <input
                      type="number"
                      value={config.hdr_epochs}
                      onChange={(e) => setConfig(prev => ({ ...prev, hdr_epochs: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-semibold text-white rounded-xl focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">YOLO Box Confidence Cutoff</label>
                    <input
                      type="text"
                      value={config.yolo_confidence}
                      onChange={(e) => setConfig(prev => ({ ...prev, yolo_confidence: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-semibold text-white rounded-xl focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">OCR Language Set</label>
                    <input
                      type="text"
                      value={config.ocr_lang}
                      onChange={(e) => setConfig(prev => ({ ...prev, ocr_lang: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-semibold text-white rounded-xl focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'database' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="font-bold text-sm text-white uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-2">
                  <Database size={16} className="text-industrial-500" />
                  Database Credentials
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">PostgreSQL Async URL</label>
                    <input
                      type="text"
                      value={config.postgresql_url}
                      onChange={(e) => setConfig(prev => ({ ...prev, postgresql_url: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-mono text-white rounded-xl focus:outline-none"
                    />
                  </div>

                  <div className="flex items-center gap-3 bg-slate-950/40 p-4 border border-slate-800/60 rounded-xl">
                    <input
                      type="checkbox"
                      id="db-sqlite-chk"
                      checked={config.sqlite_fallback}
                      onChange={(e) => setConfig(prev => ({ ...prev, sqlite_fallback: e.target.checked }))}
                      className="h-4 w-4 rounded bg-slate-900 border-slate-800 text-industrial-600 focus:ring-0 focus:ring-offset-0 focus:outline-none"
                    />
                    <div>
                      <label htmlFor="db-sqlite-chk" className="block text-xs font-bold text-white uppercase tracking-wide cursor-pointer">
                        SQLite local fallback database
                      </label>
                      <p className="text-[10px] text-slate-500 mt-0.5 leading-normal">
                        Fall back to local SQLite engine (`E:\VisionPilot_AI\database\visionpilot.db`) if PostgreSQL is unready.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'storage' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="font-bold text-sm text-white uppercase tracking-wider border-b border-slate-800 pb-3 flex items-center gap-2">
                  <Settings size={16} className="text-industrial-500" />
                  Local File Directories
                </h3>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Ingestion Upload Folder</label>
                    <input
                      type="text"
                      value={config.uploads_dir}
                      onChange={(e) => setConfig(prev => ({ ...prev, uploads_dir: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-mono text-white rounded-xl focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Optimized Outputs Folder</label>
                    <input
                      type="text"
                      value={config.outputs_dir}
                      onChange={(e) => setConfig(prev => ({ ...prev, outputs_dir: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-mono text-white rounded-xl focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Execution Logs Folder</label>
                    <input
                      type="text"
                      value={config.logs_dir}
                      onChange={(e) => setConfig(prev => ({ ...prev, logs_dir: e.target.value }))}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 focus:border-industrial-500 text-xs font-mono text-white rounded-xl focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Bottom Actions */}
            <div className="mt-8 border-t border-slate-800 pt-6 flex items-center justify-between gap-4">
              <button
                type="button"
                className="flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white"
              >
                <RefreshCw size={12} />
                Restore Factory Defaults
              </button>
              
              <button
                type="submit"
                className="flex items-center gap-2 py-2.5 px-6 bg-industrial-600 hover:bg-industrial-500 text-xs font-bold text-white rounded-xl shadow-glass shadow-industrial-600/10 transition-all active:scale-95"
              >
                {saved ? <ShieldCheck size={14} /> : <Save size={14} />}
                {saved ? 'Config Saved!' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
