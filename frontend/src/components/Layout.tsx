import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Video, 
  BarChart3, 
  History as HistoryIcon, 
  Settings as SettingsIcon, 
  ShieldAlert, 
  LogOut, 
  Cpu,
  User
} from 'lucide-react';

function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get active user from localStorage or mock
  const userString = localStorage.getItem('user');
  const user = userString ? JSON.parse(userString) : { username: 'operator', role: 'operator' };
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload Image', icon: UploadCloud },
    { path: '/live', label: 'Live Inspection', icon: Video },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/history', label: 'History', icon: HistoryIcon },
    { path: '/settings', label: 'Settings', icon: SettingsIcon },
  ];

  // Render Admin tab only if admin
  if (user.role === 'admin') {
    navItems.push({ path: '/admin', label: 'Admin Control', icon: ShieldAlert });
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070b13]">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-[#1e293b]/50 bg-[#0c1220] flex flex-col">
        {/* Brand */}
        <div className="h-16 flex items-center px-6 gap-3 border-b border-[#1e293b]/50">
          <div className="p-2 bg-industrial-600 rounded-lg text-white">
            <Cpu size={20} className="animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-wider">VisionPilot AI</h1>
            <p className="text-[10px] text-industrial-400 font-semibold uppercase tracking-widest">Optimization Middleware</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto custom-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group
                  ${isActive 
                    ? 'bg-industrial-600 text-white font-medium shadow-glass shadow-industrial-600/20' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}
                `}
              >
                <Icon size={18} className="group-hover:scale-105 transition-transform" />
                <span className="text-sm">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Sidebar Footer User info */}
        <div className="p-4 border-t border-[#1e293b]/50 bg-[#0a0f1b]">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-slate-800 rounded-full text-slate-300">
              <User size={16} />
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-semibold text-white truncate">{user.username}</p>
              <span className="inline-block px-2 py-0.5 text-[10px] font-bold text-industrial-300 uppercase bg-industrial-950 rounded-full border border-industrial-800/30">
                {user.role}
              </span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 text-xs font-semibold text-rose-400 hover:text-white bg-rose-950/20 hover:bg-rose-600 border border-rose-900/30 hover:border-rose-500 rounded-xl transition-all"
          >
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Container */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 flex-shrink-0 bg-[#0c1220]/80 backdrop-blur border-b border-[#1e293b]/50 px-8 flex items-center justify-between z-10">
          <div>
            <h2 className="text-lg font-bold text-white uppercase tracking-wider">
              {location.pathname.substring(1).replace('-', ' ')}
            </h2>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Status indicators */}
            <div className="flex items-center gap-2 bg-[#0d2218] border border-emerald-900/30 px-3 py-1 rounded-full">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Engine: connected</span>
            </div>
            
            <div className="flex items-center gap-2 bg-industrial-950 border border-industrial-900/30 px-3 py-1 rounded-full">
              <span className="text-[11px] font-semibold text-industrial-300 uppercase tracking-wider">SaaS Active</span>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto bg-[#070b13] p-8 custom-scrollbar">
          <div className="max-w-7xl mx-auto animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export default Layout;
