import { useState } from 'react';
import { Search, Download, RefreshCw, Eye, CheckCircle2, XCircle } from 'lucide-react';

interface HistoryRecord {
  id: number;
  filename: string;
  timestamp: string;
  decision: string;
  angle: number;
  detections: number;
  ocr_text: string;
  status: 'PASS' | 'FAIL';
  confidence: number;
}

function HistoryPage() {
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'PASS' | 'FAIL'>('ALL');
  
  // Mock History Records
  const records: HistoryRecord[] = [
    { id: 8412, filename: 'inspection_08342.jpg', timestamp: '2026-08-06 14:28:44', decision: 'HDR + Straighten', angle: -3.20, detections: 2, ocr_text: 'VP-2026-A9', status: 'PASS', confidence: 0.97 },
    { id: 8411, filename: 'inspection_08341.jpg', timestamp: '2026-08-06 14:25:12', decision: 'Straighten Only', angle: 1.15, detections: 1, ocr_text: 'VP-2026-A8', status: 'PASS', confidence: 0.94 },
    { id: 8410, filename: 'inspection_08340.jpg', timestamp: '2026-08-06 14:23:10', decision: 'Skip Optimization', angle: 0.00, detections: 2, ocr_text: 'UNREADABLE', status: 'FAIL', confidence: 0.74 },
    { id: 8409, filename: 'inspection_08339.jpg', timestamp: '2026-08-06 14:18:23', decision: 'HDR Fusion Only', angle: 0.00, detections: 1, ocr_text: 'VP-2026-A7', status: 'PASS', confidence: 0.96 },
    { id: 8408, filename: 'inspection_08338.jpg', timestamp: '2026-08-06 14:12:01', decision: 'HDR + Straighten', angle: -2.45, detections: 2, ocr_text: 'VP-2026-A6', status: 'PASS', confidence: 0.98 },
    { id: 8407, filename: 'inspection_08337.jpg', timestamp: '2026-08-06 14:05:44', decision: 'Straighten Only', angle: 0.85, detections: 1, ocr_text: 'VP-2026-A5', status: 'PASS', confidence: 0.95 },
    { id: 8406, filename: 'inspection_08336.jpg', timestamp: '2026-08-06 13:58:12', decision: 'Skip Optimization', angle: 0.00, detections: 0, ocr_text: 'EMPTY CARD', status: 'FAIL', confidence: 0.62 }
  ];

  // Filtering logic
  const filteredRecords = records.filter(rec => {
    const matchesSearch = rec.filename.toLowerCase().includes(search.toLowerCase()) || 
                          rec.ocr_text.toLowerCase().includes(search.toLowerCase()) ||
                          rec.id.toString().includes(search);
    
    const matchesStatus = filterStatus === 'ALL' || rec.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <p className="text-xs font-semibold text-industrial-400 uppercase tracking-widest">Inspection Logs</p>
        <h2 className="text-xl font-bold text-white uppercase tracking-wider mt-1">Inspection Transaction History</h2>
      </div>

      {/* Filters and Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative max-w-md w-full">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500 pointer-events-none">
            <Search size={16} />
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID, filename, or OCR text..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-800 text-xs font-semibold text-white rounded-xl focus:outline-none focus:border-industrial-500"
          />
        </div>

        {/* Status filter tabs */}
        <div className="flex bg-slate-900 border border-slate-800 p-1 rounded-xl self-start">
          {['ALL', 'PASS', 'FAIL'].map((statusOption) => (
            <button
              key={statusOption}
              onClick={() => setFilterStatus(statusOption as any)}
              className={`py-1.5 px-4 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-colors ${
                filterStatus === statusOption 
                  ? statusOption === 'FAIL' 
                    ? 'bg-rose-600 text-white' 
                    : statusOption === 'PASS' 
                      ? 'bg-emerald-600 text-white' 
                      : 'bg-industrial-600 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {statusOption}
            </button>
          ))}
        </div>
      </div>

      {/* Transaction Table */}
      <div className="glass-panel rounded-3xl overflow-hidden border border-[#1e293b]/50">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-[#1e293b]/50 bg-slate-900/35 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                <th className="px-6 py-4">Image ID</th>
                <th className="px-6 py-4">Filename</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">Decision Policy</th>
                <th className="px-6 py-4">Skew Angle</th>
                <th className="px-6 py-4">Detections</th>
                <th className="px-6 py-4">OCR Output</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Confidence</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b]/30 text-xs font-semibold text-slate-300">
              {filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-6 py-12 text-center text-slate-500 font-normal">
                    No transactions match the specified filter query.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((rec) => (
                  <tr key={rec.id} className="hover:bg-slate-900/10 transition-colors">
                    <td className="px-6 py-4 text-industrial-400 font-mono">#{rec.id}</td>
                    <td className="px-6 py-4 text-white truncate max-w-[150px]">{rec.filename}</td>
                    <td className="px-6 py-4 font-normal text-slate-400">{rec.timestamp}</td>
                    <td className="px-6 py-4">
                      <span className="inline-block px-2.5 py-0.5 text-[9px] font-bold bg-slate-950 border border-slate-800 rounded-full uppercase tracking-wider text-slate-300">
                        {rec.decision}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono">{rec.angle > 0 ? `+${rec.angle}` : rec.angle}°</td>
                    <td className="px-6 py-4">{rec.detections} items</td>
                    <td className="px-6 py-4 font-mono text-[10px] text-industrial-300">{rec.ocr_text}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5">
                        {rec.status === 'FAIL' 
                          ? <XCircle size={14} className="text-rose-500" />
                          : <CheckCircle2 size={14} className="text-emerald-500" />
                        }
                        <span className={rec.status === 'FAIL' ? 'text-rose-400' : 'text-emerald-400'}>{rec.status}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono">{(rec.confidence * 100).toFixed(0)}%</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button className="p-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <Eye size={12} />
                        </button>
                        <button className="p-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <Download size={12} />
                        </button>
                        <button className="p-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <RefreshCw size={12} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default HistoryPage;
