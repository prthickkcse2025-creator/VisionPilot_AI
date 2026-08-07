import React, { useState } from 'react';
import { Upload, FileImage, Layers, ArrowRight, Download, Check, AlertTriangle, ShieldCheck, ZoomIn, ZoomOut, Maximize } from 'lucide-react';

function UploadPage() {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [enhancementMethod, setEnhancementMethod] = useState<string>('policy');
  const [currentStep, setCurrentStep] = useState<'upload' | 'processing' | 'results'>('upload');
  
  // API Response results
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');
  
  // Interactive UI State
  const [zoomScale, setZoomScale] = useState<number>(1);
  const [logs, setLogs] = useState<string[]>([]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      setFiles(droppedFiles);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(selectedFiles);
    }
  };

  const startEnhancement = async () => {
    if (files.length === 0) return;
    setCurrentStep('processing');
    setErrorMsg('');
    setLogs(["Preparing request...", "Reading local file headers...", "Initiating network payload..."]);

    const formData = new FormData();
    formData.append("file", files[0]);
    formData.append("enhancement", enhancementMethod);

    const token = localStorage.getItem("token") || "";

    try {
      setTimeout(() => setLogs(p => [...p, "Uploading image to VisionPilot middleware...", "Executing policy prediction network..."]), 250);
      setTimeout(() => setLogs(p => [...p, "Running selected enhancement plugin on active thread...", "Validating output constraints..."]), 600);

      // Backend endpoint configuration (falls back to localhost:8000 if running locally)
      const baseUrl = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');
      const response = await fetch(`${baseUrl}/enhance`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setTimeout(() => {
        setResult(data);
        setCurrentStep('results');
      }, 1000);

    } catch (e: any) {
      console.error(e);
      setErrorMsg(e.message || "An unexpected error occurred during image processing.");
      setCurrentStep('upload');
    }
  };

  const resetPipeline = () => {
    setFiles([]);
    setResult(null);
    setErrorMsg('');
    setZoomScale(1);
    setCurrentStep('upload');
  };

  const getMediaUrl = (path: string) => {
    if (!path) return "";
    const baseUrl = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '');
    return `${baseUrl}/${path}`;
  };

  return (
    <div className="space-y-8">
      {/* Upload Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-industrial-400 uppercase tracking-widest">Inspection Ingestion</p>
          <h2 className="text-xl font-bold text-white uppercase tracking-wider mt-1">Ingest Image stream</h2>
        </div>
        
        {files.length > 0 && currentStep === 'upload' && (
          <button
            onClick={startEnhancement}
            className="flex items-center gap-2 py-2.5 px-6 text-sm font-bold text-white bg-industrial-600 hover:bg-industrial-500 rounded-2xl transition-all shadow-glass shadow-industrial-600/25 active:scale-95 animate-fade-in"
          >
            Run Pipeline
            <ArrowRight size={16} />
          </button>
        )}
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-950/20 border border-rose-900/30 text-rose-400 text-sm rounded-2xl flex items-center gap-3">
          <AlertTriangle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      {currentStep === 'upload' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Ingest Zone */}
          <div className="lg:col-span-2 space-y-6">
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-3xl p-12 text-center transition-all flex flex-col items-center justify-center min-h-[350px] relative overflow-hidden ${
                dragActive 
                  ? 'border-industrial-500 bg-industrial-950/20' 
                  : 'border-[#1e293b]/50 hover:border-industrial-500/50 bg-[#0c1220]/45 hover:bg-[#0c1220]/80'
              }`}
            >
              <input
                type="file"
                onChange={handleFileInput}
                id="file-upload-input"
                className="hidden"
                accept="image/png, image/jpeg, image/tiff, image/bmp"
              />
              
              <div className="p-4 bg-industrial-950/40 rounded-2xl border border-industrial-900/30 text-industrial-400 mb-4">
                <Upload size={32} />
              </div>
              <h3 className="font-bold text-white mb-2">Drag & Drop inspection file here</h3>
              <p className="text-xs text-slate-400 mb-6 max-w-xs leading-relaxed">
                Supports PNG, JPEG, TIFF, BMP.
              </p>
              
              <label
                htmlFor="file-upload-input"
                className="py-2.5 px-6 bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-white border border-slate-800 hover:border-slate-700 rounded-xl cursor-pointer transition-all active:scale-95"
              >
                Browse File
              </label>
            </div>
          </div>

          {/* Configuration & Options */}
          <div className="glass-panel rounded-3xl p-6 flex flex-col justify-between h-[350px]">
            <div>
              <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-4 border-b border-[#1e293b]/50 pb-4">
                Pipeline Config
              </h3>
              
              {/* Enhancement Choice Dropdown */}
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-bold text-slate-400 block mb-2">Enhancement Method</label>
                  <select
                    value={enhancementMethod}
                    onChange={(e) => setEnhancementMethod(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-industrial-500 transition-colors"
                  >
                    <option value="policy">Policy Predictor (Auto-Select)</option>
                    <option value="HDR Fusion">HDR Fusion (MAWB-Net V13.2)</option>
                    <option value="Image Straightener">Image Straightener</option>
                  </select>
                </div>

                {files.length > 0 && (
                  <div className="p-3 bg-slate-950/50 border border-slate-900 rounded-xl flex items-center gap-3">
                    <div className="p-2 bg-industrial-950/50 text-industrial-400 rounded-lg">
                      <FileImage size={16} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-semibold text-white truncate">{files[0].name}</p>
                      <span className="text-[10px] text-slate-500 font-mono">{(files[0].size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {files.length > 0 && (
              <button
                onClick={startEnhancement}
                className="w-full py-2.5 px-4 text-xs font-bold text-white bg-industrial-600 hover:bg-industrial-500 rounded-xl transition-all shadow-glass"
              >
                Execute Integration
              </button>
            )}
          </div>
        </div>
      )}

      {currentStep === 'processing' && (
        <div className="glass-panel rounded-3xl p-8 max-w-3xl mx-auto flex flex-col min-h-[350px]">
          <h3 className="font-bold text-sm text-white uppercase tracking-wider mb-6 flex items-center gap-3">
            <Layers size={16} className="text-industrial-500 animate-spin" />
            Adaptive pipeline running
          </h3>
          
          <div className="flex-1 bg-slate-950/50 border border-slate-900 rounded-2xl p-6 font-mono text-xs text-slate-300 space-y-2 overflow-y-auto h-48 custom-scrollbar">
            {logs.map((log, idx) => (
              <div key={idx} className="flex gap-2">
                <span className="text-slate-600 font-bold select-none">&gt;</span>
                <p className="animate-fade-in">{log}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {currentStep === 'results' && result && (
        <div className="space-y-6">
          {/* Results Summary and Reset */}
          <div className="glass-panel rounded-3xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-emerald-950/50 text-emerald-400 border border-emerald-900/30 rounded-xl">
                  <ShieldCheck size={20} />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</h4>
                  <p className="text-sm font-bold text-emerald-400 uppercase mt-0.5">{result.status}</p>
                </div>
              </div>
              <div className="h-8 w-[1px] bg-slate-800 hidden md:block"></div>
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Plugin Executed</h4>
                <p className="text-sm font-bold text-white mt-0.5">{result.plugin}</p>
              </div>
              <div className="h-8 w-[1px] bg-slate-800 hidden md:block"></div>
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Latency</h4>
                <p className="text-sm font-bold text-white mt-0.5">{(result.processing_time * 1000).toFixed(1)} ms</p>
              </div>
              <div className="h-8 w-[1px] bg-slate-800 hidden md:block"></div>
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Resolution</h4>
                <p className="text-sm font-bold text-slate-300 mt-0.5">{result.metadata?.output_dimensions || 'N/A'}</p>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={resetPipeline}
                className="py-2.5 px-6 text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded-2xl transition-all"
              >
                Reset Pipeline
              </button>
            </div>
          </div>

          {/* Interactive Workspaces */}
          <div className="glass-panel rounded-3xl overflow-hidden flex flex-col h-[560px]">
            <div className="px-6 py-4 border-b border-[#1e293b]/50 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-xs font-bold text-industrial-400 uppercase tracking-wider">
                  Active Comparison View
                </span>
                
                {/* Zoom Controls */}
                <div className="flex items-center gap-1 bg-slate-950 border border-slate-900 rounded-xl px-2 py-1">
                  <button 
                    onClick={() => setZoomScale(p => Math.max(0.5, p - 0.25))}
                    className="p-1 text-slate-400 hover:text-white rounded transition-colors"
                  >
                    <ZoomOut size={14} />
                  </button>
                  <span className="text-[10px] text-slate-300 font-mono font-bold w-12 text-center select-none">
                    {(zoomScale * 100).toFixed(0)}%
                  </span>
                  <button 
                    onClick={() => setZoomScale(p => Math.min(3, p + 0.25))}
                    className="p-1 text-slate-400 hover:text-white rounded transition-colors"
                  >
                    <ZoomIn size={14} />
                  </button>
                </div>
              </div>

              <a 
                href={getMediaUrl(result.output_image)}
                download
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 py-1.5 px-4 text-xs font-semibold text-slate-300 hover:text-white bg-slate-900 border border-slate-800 rounded-lg transition-all"
              >
                <Download size={12} />
                Download Output
              </a>
            </div>

            {/* Comparer Body */}
            <div className="flex-1 bg-slate-950/80 relative overflow-hidden grid grid-cols-2 gap-6 p-6">
              {/* Original Left Pane */}
              <div className="border border-slate-800/80 bg-slate-900/10 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center">
                <span className="absolute top-4 left-4 z-10 text-[9px] font-bold text-slate-400 bg-slate-950 px-2 py-0.5 rounded uppercase tracking-wider">
                  Original Input Frame
                </span>
                
                <div 
                  style={{ transform: `scale(${zoomScale})` }} 
                  className="transition-transform duration-200 ease-out max-h-full max-w-full"
                >
                  <img 
                    src={getMediaUrl(result.input_image)} 
                    alt="Original" 
                    className="max-h-[360px] object-contain rounded-lg border border-slate-850"
                  />
                </div>
              </div>
              
              {/* Processed Right Pane */}
              <div className="border border-industrial-500/30 bg-industrial-950/5 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center">
                <span className="absolute top-4 left-4 z-10 text-[9px] font-bold text-industrial-300 bg-industrial-950 px-2 py-0.5 rounded uppercase tracking-wider border border-industrial-800/30">
                  Enhanced output ({result.plugin})
                </span>
                
                <div 
                  style={{ transform: `scale(${zoomScale})` }} 
                  className="transition-transform duration-200 ease-out max-h-full max-w-full"
                >
                  <img 
                    src={getMediaUrl(result.output_image)} 
                    alt="Processed" 
                    className="max-h-[360px] object-contain rounded-lg border border-industrial-800/30"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadPage;
