import { useNavigate } from 'react-router-dom';
import {
  Settings,
  BarChart3,
  Bell,
  Mic,
  Truck,
  Package,
  ChevronRight,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function MorePage() {
  const navigate = useNavigate();
  const { user, shop, logout } = useAuth();

  const menuItems = [
    { icon: Package, label: 'Products', path: '/products', color: 'text-blue-600 bg-blue-50' },
    { icon: Truck, label: 'Suppliers', path: '/suppliers', color: 'text-emerald-600 bg-emerald-50' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics', color: 'text-purple-600 bg-purple-50' },
    { icon: Mic, label: 'Voice History', path: '/voice-history', color: 'text-rose-600 bg-rose-50' },
    { icon: Bell, label: 'Notifications', path: '/notifications', color: 'text-amber-600 bg-amber-50' },
    { icon: Settings, label: 'Settings', path: '/settings', color: 'text-surface-600 bg-surface-100' },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in">
      {/* User Profile Card */}
      <div className="bg-white rounded-2xl border border-surface-100 p-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white text-xl font-bold">
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div>
            <p className="text-lg font-bold text-surface-900">{user?.full_name || 'User'}</p>
            <p className="text-sm text-surface-500">{shop?.name || 'Your Shop'}</p>
            <p className="text-xs text-surface-400">{user?.email || ''}</p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <div className="bg-white rounded-2xl border border-surface-100 overflow-hidden">
        {menuItems.map((item, i) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`w-full flex items-center gap-4 px-5 py-4 hover:bg-surface-50 transition-colors text-left ${
              i < menuItems.length - 1 ? 'border-b border-surface-100' : ''
            }`}
          >
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${item.color}`}>
              <item.icon className="w-5 h-5" />
            </div>
            <span className="flex-1 text-sm font-medium text-surface-800">{item.label}</span>
            <ChevronRight className="w-4 h-4 text-surface-300" />
          </button>
        ))}
      </div>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="w-full flex items-center gap-4 px-5 py-4 bg-white rounded-2xl border border-surface-100 hover:bg-red-50 transition-colors"
      >
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-red-600 bg-red-50">
          <LogOut className="w-5 h-5" />
        </div>
        <span className="flex-1 text-sm font-medium text-red-600 text-left">Logout</span>
      </button>
    </div>
  );
}
