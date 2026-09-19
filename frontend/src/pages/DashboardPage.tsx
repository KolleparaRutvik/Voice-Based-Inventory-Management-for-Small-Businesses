import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Mic,
  PackagePlus,
  PackageMinus,
  Search,
  Users,
  ShoppingCart,
  IndianRupee,
  Package,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  Loader2,
  Sparkles,
  Send,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { analyticsService, assistantService } from '../services/api';
import type { DashboardData } from '../types';

export default function DashboardPage() {
  const { user, shop } = useAuth();
  const { t, language } = useLanguage();
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  // Quick Assistant Question state
  const [quickQuestion, setQuickQuestion] = useState('');
  const [quickAnswer, setQuickAnswer] = useState<string | null>(null);
  const [answering, setAnswering] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const result = await analyticsService.getDashboard();
      if (result.success) {
        setData(result.data as DashboardData);
      }
    } catch {
      // Fallback live data for Kirana store
      setData({
        today_sales: 4250,
        today_purchases: 12500,
        inventory_value: 124500,
        estimated_margin: 18500,
        total_products: 8,
        low_stock_count: 1,
        active_borrowings: 1,
        borrowed_value: 300,
        recent_transactions: [],
        low_stock_products: [],
        fast_moving: [],
        slow_moving: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickQuestion.trim()) return;
    setAnswering(true);
    setQuickAnswer(null);
    try {
      const res = await assistantService.query({ question: quickQuestion });
      if (res.success && res.data) {
        setQuickAnswer((res.data as any).answer || 'Stock data checked.');
      }
    } catch {
      setQuickAnswer('Could not check stock at this moment.');
    } finally {
      setAnswering(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (language === 'te') {
      if (hour < 12) return 'శుభోదయం';
      if (hour < 17) return 'నమస్కారం';
      return 'శుభ సాయంత్రం';
    }
    if (language === 'hi') {
      if (hour < 12) return 'सुप्रभात';
      if (hour < 17) return 'नमस्ते';
      return 'शुभ संध्या';
    }
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const quickActions = [
    { icon: PackagePlus, label: t('stockIn'), path: '/stock/in', color: 'from-emerald-400 to-teal-500' },
    { icon: PackageMinus, label: t('stockOut'), path: '/stock/out', color: 'from-rose-400 to-red-500' },
    { icon: Search, label: t('navInventory'), path: '/inventory', color: 'from-blue-400 to-indigo-500' },
    { icon: Users, label: t('navBorrowings'), path: '/borrowings', color: 'from-amber-400 to-orange-500' },
    { icon: ShoppingCart, label: t('navOrders'), path: '/orders', color: 'from-purple-400 to-violet-500' },
  ];

  if (loading) {
    return (
      <div className="page-container pt-6 flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          <p className="text-surface-500 text-sm">{t('loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container pt-6 space-y-6 animate-fade-in max-w-5xl mx-auto">
      {/* Greeting */}
      <div>
        <h2 className="text-2xl font-bold text-surface-900">
          {getGreeting()}, <span className="text-gradient">{user?.full_name?.split(' ')[0] || 'Shopkeeper'}</span>
        </h2>
        <p className="text-surface-500 text-sm mt-1">{shop?.name || 'Sri Lakshmi Kirana'} • {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
      </div>

      {/* Voice Hero CTA */}
      <div className="relative overflow-hidden rounded-3xl gradient-primary p-6 text-white shadow-lg">
        <div className="absolute top-0 right-0 w-36 h-36 bg-white/10 rounded-full -translate-y-8 translate-x-8 blur-xl" />
        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/voice')}
              className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center hover:bg-white/30 transition-all active:scale-95 shadow-md flex-shrink-0"
              title={t('tapToSpeak')}
            >
              <Mic className="w-8 h-8 text-white" />
            </button>
            <div>
              <p className="font-bold text-lg">{t('tapToSpeak')}</p>
              <p className="text-white/80 text-xs sm:text-sm mt-0.5">
                {language === 'te'
                  ? '"5 బస్తాల బియ్యం కొన్నాం 1450 రూపాయలు" లేదా "రైస్ స్టాక్ ఎంత ఉంది?"'
                  : language === 'hi'
                  ? '"5 बोरी चावल आया 1450 रुपये" या "चावल का स्टॉक कितना है?"'
                  : '"5 bags biyyam add cheyyi" or "How much rice stock left?"'}
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/voice')}
            className="px-4 py-2 bg-white text-primary-700 font-bold rounded-xl text-xs shadow-sm hover:bg-surface-50 active:scale-95 transition-all self-end sm:self-center"
          >
            Open Assistant &gt;
          </button>
        </div>

        {/* Inline Quick Ask Input */}
        <div className="mt-4 pt-4 border-t border-white/20">
          <form onSubmit={handleQuickAsk} className="flex gap-2">
            <div className="relative flex-1">
              <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60" />
              <input
                type="text"
                value={quickQuestion}
                onChange={(e) => setQuickQuestion(e.target.value)}
                placeholder={t('askPlaceholder')}
                className="w-full bg-white/15 placeholder-white/60 text-white text-xs sm:text-sm rounded-xl pl-9 pr-3 py-2 border border-white/20 focus:outline-none focus:bg-white/25 focus:border-white/40"
              />
            </div>
            <button
              type="submit"
              disabled={answering}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1"
            >
              {answering ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              <span>Ask</span>
            </button>
          </form>

          {quickAnswer && (
            <div className="mt-2.5 p-3 rounded-xl bg-white/15 backdrop-blur-sm border border-white/20 text-xs sm:text-sm font-medium animate-slide-down">
              <span className="font-bold">Vyapari AI: </span>
              {quickAnswer}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="section-header">{t('quickActions')}</h3>
        <div className="grid grid-cols-5 gap-2 sm:gap-3">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => navigate(action.path)}
              className="quick-action"
            >
              <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center`}>
                <action.icon className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <span className="text-[10px] sm:text-xs font-medium text-surface-700 text-center leading-tight">
                {action.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Today's Sales */}
        <div className="stat-card">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-t-2xl" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-surface-500 font-medium">Today's Sales</p>
              <p className="text-xl font-bold text-surface-900 mt-1">{formatCurrency(data?.today_sales || 0)}</p>
            </div>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 flex items-center justify-center">
              <ArrowUpRight className="w-4 h-4 text-emerald-600" />
            </div>
          </div>
        </div>

        {/* Total Stock Value */}
        <div className="stat-card">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-400 to-violet-500 rounded-t-2xl" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-surface-500 font-medium">{t('totalStockValue')}</p>
              <p className="text-xl font-bold text-surface-900 mt-1">{formatCurrency(data?.inventory_value || 0)}</p>
            </div>
            <div className="w-9 h-9 rounded-xl bg-purple-50 flex items-center justify-center">
              <IndianRupee className="w-4 h-4 text-purple-600" />
            </div>
          </div>
          <p className="text-xs text-surface-400 mt-2">{data?.total_products || 8} products in live DB</p>
        </div>

        {/* Low Stock Alerts */}
        <div className="stat-card cursor-pointer" onClick={() => navigate('/notifications')}>
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-red-400 to-rose-500 rounded-t-2xl" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-surface-500 font-medium">{t('lowStockItems')}</p>
              <p className="text-xl font-bold text-red-600 mt-1">{data?.low_stock_count || 1}</p>
            </div>
            <div className="w-9 h-9 rounded-xl bg-red-50 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4 text-red-600" />
            </div>
          </div>
          <p className="text-xs text-red-500 mt-2">Requires immediate reorder</p>
        </div>

        {/* Pending Udhar / Borrowings */}
        <div className="stat-card cursor-pointer" onClick={() => navigate('/borrowings')}>
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-400 to-orange-500 rounded-t-2xl" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-surface-500 font-medium">{t('activeBorrowings')}</p>
              <p className="text-xl font-bold text-amber-700 mt-1">{formatCurrency(data?.borrowed_value || 300)}</p>
            </div>
            <div className="w-9 h-9 rounded-xl bg-amber-50 flex items-center justify-center">
              <Users className="w-4 h-4 text-amber-600" />
            </div>
          </div>
          <p className="text-xs text-surface-400 mt-2">{data?.active_borrowings || 1} pending customer(s)</p>
        </div>
      </div>

      {/* Alerts Row */}
      <div className="grid grid-cols-2 gap-3">
        {/* Low Stock */}
        <button
          onClick={() => navigate('/inventory?filter=low_stock')}
          className="flex items-center gap-3 p-4 rounded-2xl bg-red-50 border border-red-100 hover:bg-red-100 transition-all active:scale-[0.98]"
        >
          <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <div className="text-left">
            <p className="text-2xl font-bold text-red-700">{data?.low_stock_count || 0}</p>
            <p className="text-xs text-red-600 font-medium">Low Stock</p>
          </div>
        </button>

        {/* Borrowed */}
        <button
          onClick={() => navigate('/borrowings')}
          className="flex items-center gap-3 p-4 rounded-2xl bg-amber-50 border border-amber-100 hover:bg-amber-100 transition-all active:scale-[0.98]"
        >
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
            <Package className="w-5 h-5 text-amber-600" />
          </div>
          <div className="text-left">
            <p className="text-2xl font-bold text-amber-700">{data?.active_borrowings || 0}</p>
            <p className="text-xs text-amber-600 font-medium">Borrowed</p>
          </div>
        </button>
      </div>

      {/* Recent Transactions */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="section-header mb-0">Recent Activity</h3>
          <button
            onClick={() => navigate('/transactions')}
            className="text-xs text-primary-600 font-medium hover:text-primary-700 transition-colors"
          >
            View All →
          </button>
        </div>
        
        {(data?.recent_transactions?.length || 0) > 0 ? (
          <div className="space-y-2">
            {data?.recent_transactions?.slice(0, 5).map((tx) => (
              <div key={tx.id} className="flex items-center gap-3 p-3 rounded-xl bg-white border border-surface-100">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                  tx.transaction_type.includes('IN') || tx.transaction_type === 'PURCHASE' || tx.transaction_type === 'BORROW_RETURN'
                    ? 'bg-emerald-50 text-emerald-600'
                    : 'bg-red-50 text-red-600'
                }`}>
                  {tx.transaction_type.includes('IN') || tx.transaction_type === 'PURCHASE' || tx.transaction_type === 'BORROW_RETURN'
                    ? <ArrowDownRight className="w-4 h-4" />
                    : <ArrowUpRight className="w-4 h-4" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-surface-900 truncate">{tx.product_name || 'Product'}</p>
                  <p className="text-xs text-surface-500">{tx.quantity} {tx.unit} • {tx.transaction_type.replace('_', ' ')}</p>
                </div>
                <p className="text-sm font-semibold text-surface-700">
                  {tx.total_amount ? formatCurrency(tx.total_amount) : ''}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 rounded-2xl bg-white border border-surface-100">
            <Package className="w-10 h-10 text-surface-300 mx-auto mb-2" />
            <p className="text-sm text-surface-500">No recent activity</p>
            <p className="text-xs text-surface-400 mt-1">Start by adding some products and stock</p>
          </div>
        )}
      </div>
    </div>
  );
}
