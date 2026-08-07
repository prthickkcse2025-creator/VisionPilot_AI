import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, Lock, User, AlertCircle } from 'lucide-react';

function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Mock API call validation (same logic as FastAPI main.py mockup)
    setTimeout(() => {
      if (['admin', 'operator', 'viewer'].includes(username.toLowerCase()) && password === username) {
        const mockUser = { username: username.toLowerCase(), role: username.toLowerCase() };
        localStorage.setItem('token', `mock_token_${username}`);
        localStorage.setItem('user', JSON.stringify(mockUser));
        navigate('/dashboard');
      } else {
        setError('Invalid credentials. Use admin/admin, operator/operator, or viewer/viewer.');
        setLoading(false);
      }
    }, 600);
  };

  const handleQuickLogin = (role: string) => {
    setUsername(role);
    setPassword(role);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#070b13] relative overflow-hidden px-4">
      {/* Decorative background grid and gradients */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f29370a_1px,transparent_1px),linear-gradient(to_bottom,#1f29370a_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-industrial-600/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-md z-10">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-industrial-600/20 text-industrial-500 rounded-2xl border border-industrial-500/20 mb-3 shadow-glass shadow-industrial-600/10">
            <Cpu size={32} className="animate-pulse" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-wider">VisionPilot AI</h1>
          <p className="text-sm text-slate-400 mt-2 font-medium">Adaptive Vision Optimization Middleware</p>
        </div>

        {/* Login Card */}
        <div className="glass-panel rounded-3xl p-8 border border-white/5 shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-6">Portal Sign In</h2>
          
          {error && (
            <div className="mb-6 p-4 bg-rose-950/20 border border-rose-900/30 text-rose-400 text-sm rounded-2xl flex items-center gap-3">
              <AlertCircle size={18} className="flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Username</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <User size={16} />
                </span>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username (admin, operator, viewer)"
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/50 hover:bg-slate-950/80 focus:bg-slate-950 border border-slate-800 focus:border-industrial-500 text-sm text-white rounded-2xl transition-all focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <Lock size={16} />
                </span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  className="w-full pl-10 pr-4 py-3 bg-slate-950/50 hover:bg-slate-950/80 focus:bg-slate-950 border border-slate-800 focus:border-industrial-500 text-sm text-white rounded-2xl transition-all focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-industrial-600 hover:bg-industrial-500 disabled:bg-industrial-800 text-sm font-bold text-white rounded-2xl transition-all shadow-glass shadow-industrial-600/25 active:scale-95"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          {/* Quick login roles */}
          <div className="mt-8 border-t border-slate-800/80 pt-6">
            <p className="text-center text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Quick Role Selection</p>
            <div className="grid grid-cols-3 gap-2">
              {['admin', 'operator', 'viewer'].map((role) => (
                <button
                  key={role}
                  onClick={() => handleQuickLogin(role)}
                  className="py-2 px-3 text-xs bg-slate-900 hover:bg-industrial-950 hover:text-industrial-300 border border-slate-800 hover:border-industrial-800/30 text-slate-300 font-semibold uppercase rounded-xl transition-all"
                >
                  {role}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
