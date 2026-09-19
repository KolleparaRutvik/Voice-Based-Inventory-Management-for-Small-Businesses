import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  Home,
  Package,
  ArrowLeftRight,
  Users,
  MoreHorizontal,
  Mic,
  Bell,
  LogOut,
  Settings,
  ShoppingCart,
  BarChart3,
  Truck,
  ClipboardList,
  Menu,
  X,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import LanguageSwitcher from '../components/LanguageSwitcher';

export default function AppLayout() {
  const { user, shop, logout } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const sidebarLinks = [
    { to: '/', icon: Home, label: t('navDashboard') },
    { to: '/products', icon: Package, label: t('navProducts') },
    { to: '/inventory', icon: ClipboardList, label: t('navInventory') },
    { to: '/transactions', icon: ArrowLeftRight, label: t('navTransactions') },
    { to: '/borrowings', icon: Users, label: t('navBorrowings') },
    { to: '/suppliers', icon: Truck, label: t('navSuppliers') },
    { to: '/orders', icon: ShoppingCart, label: t('navOrders') },
    { to: '/analytics', icon: BarChart3, label: t('navAnalytics') },
    { to: '/voice', icon: Mic, label: t('navVoiceAssistant') },
    { to: '/notifications', icon: Bell, label: t('navNotifications') },
    { to: '/settings', icon: Settings, label: t('navSettings') },
  ];

  const mobileNavItems = [
    { to: '/', icon: Home, label: t('navDashboard') },
    { to: '/inventory', icon: ClipboardList, label: t('navInventory') },
    { to: '/borrowings', icon: Users, label: t('navBorrowings') },
    { to: '/orders', icon: ShoppingCart, label: t('navOrders') },
    { to: '/more', icon: MoreHorizontal, label: t('navMore') },
  ];

  return (
    <div className="min-h-screen bg-surface-50">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-4 overflow-y-auto bg-white border-r border-surface-200 px-4 py-6">
          {/* Logo */}
          <div className="flex items-center gap-3 px-2">
            <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center shadow-md">
              <Mic className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-base font-bold text-surface-900 truncate">{t('appName')}</h1>
              <p className="text-xs text-surface-500 truncate">{shop?.name || 'Sri Lakshmi Kirana'}</p>
            </div>
          </div>

          {/* Language Switcher */}
          <div className="px-1 pt-1">
            <LanguageSwitcher />
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col mt-2">
            <ul className="flex flex-1 flex-col gap-1">
              {sidebarLinks.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    end={link.to === '/'}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                        isActive
                          ? 'bg-primary-50 text-primary-700 font-semibold'
                          : 'text-surface-600 hover:bg-surface-50 hover:text-surface-900'
                      }`
                    }
                  >
                    <link.icon className="w-5 h-5 flex-shrink-0" />
                    <span className="truncate">{link.label}</span>
                    <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>

          {/* User section */}
          <div className="border-t border-surface-200 pt-3">
            <div className="flex items-center gap-3 px-2">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white text-sm font-semibold">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-surface-900 truncate">{user?.full_name || 'User'}</p>
                <p className="text-xs text-surface-500 truncate">{user?.email || ''}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-surface-100 text-surface-400 hover:text-surface-600 transition-colors"
                title={t('logout')}
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Header */}
      <header className="lg:hidden sticky top-0 z-40 bg-white/90 backdrop-blur-xl border-b border-surface-200">
        <div className="flex items-center justify-between px-3 py-2.5">
          <div className="flex items-center gap-2 min-w-0">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 rounded-xl hover:bg-surface-100 transition-colors"
            >
              <Menu className="w-5 h-5 text-surface-600" />
            </button>
            <div className="min-w-0">
              <h1 className="text-sm font-bold text-surface-900 truncate">{shop?.name || t('appName')}</h1>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <LanguageSwitcher compact />
            <button
              onClick={() => navigate('/notifications')}
              className="p-1.5 rounded-xl hover:bg-surface-100 transition-colors relative"
            >
              <Bell className="w-4 h-4 text-surface-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-72 bg-white shadow-2xl animate-slide-up">
            <div className="flex items-center justify-between p-4 border-b border-surface-200">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
                  <Mic className="w-4 h-4 text-white" />
                </div>
                <span className="font-bold text-surface-900">{t('appName')}</span>
              </div>
              <button onClick={() => setSidebarOpen(false)} className="p-2 rounded-xl hover:bg-surface-100">
                <X className="w-5 h-5" />
              </button>
            </div>
            <nav className="p-3">
              {sidebarLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all mb-1 ${
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-surface-600 hover:bg-surface-50'
                    }`
                  }
                >
                  <link.icon className="w-5 h-5" />
                  <span>{link.label}</span>
                </NavLink>
              ))}
            </nav>
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-surface-200">
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 w-full px-3 py-3 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-5 h-5" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="lg:pl-64">
        <div className="min-h-screen">
          <Outlet />
        </div>
      </main>

      {/* Floating Mic Button */}
      <button
        onClick={() => navigate('/voice')}
        className="fixed bottom-20 right-4 lg:bottom-6 lg:right-6 z-30 mic-button-ready shadow-glow"
        title="Tap and Speak"
      >
        <Mic className="w-7 h-7" />
      </button>

      {/* Mobile Bottom Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-xl border-t border-surface-200 safe-bottom">
        <div className="flex items-center justify-around px-2 py-1">
          {mobileNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `${isActive ? 'nav-item-active' : 'nav-item'} min-w-[56px]`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
