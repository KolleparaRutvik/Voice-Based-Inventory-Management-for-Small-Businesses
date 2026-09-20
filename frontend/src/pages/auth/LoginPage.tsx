import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import type { StoreTypeSlug } from '../../context/AuthContext';

interface DemoStoreInfo {
  type: StoreTypeSlug;
  name: string;
  badge: string;
  emoji: string;
  desc: string;
  email: string;
  borderAccent: string;
  bgAccent: string;
  textAccent: string;
}

const ALL_DEMO_STORES: DemoStoreInfo[] = [
  {
    type: 'kirana',
    name: 'Sri Lakshmi Kirana Store',
    badge: 'Kirana',
    emoji: '🛒',
    desc: 'Rice, Dal, Oil, FMCG & Customer Udhar',
    email: 'srinivas@dukaansetu.com',
    borderAccent: 'border-emerald-500/30',
    bgAccent: 'bg-emerald-500/10 hover:bg-emerald-500/20',
    textAccent: 'text-emerald-300',
  },
  {
    type: 'jewellery',
    name: 'Sri Swarna Mahal Jewellers',
    badge: 'Jewellery',
    emoji: '💎',
    desc: '22K Gold 916, Silver, Diamonds, Grams & Gold Loans',
    email: 'jewellery@dukaansetu.com',
    borderAccent: 'border-amber-500/30',
    bgAccent: 'bg-amber-500/10 hover:bg-amber-500/20',
    textAccent: 'text-amber-300',
  },
  {
    type: 'flowers',
    name: 'Sri Venkateswara Flower Mart',
    badge: 'Flowers',
    emoji: '🌸',
    desc: 'Jasmine, Marigold, Garlands, Mora & Temple Decor',
    email: 'flowers@dukaansetu.com',
    borderAccent: 'border-rose-500/30',
    bgAccent: 'bg-rose-500/10 hover:bg-rose-500/20',
    textAccent: 'text-rose-300',
  },
  {
    type: 'clothing',
    name: 'Sri Raghavendra Cloth Emporium',
    badge: 'Clothing',
    emoji: '👕',
    desc: 'Kanchi Sarees, Kurtas, Denim, Fabrics & Alterations',
    email: 'clothing@dukaansetu.com',
    borderAccent: 'border-indigo-500/30',
    bgAccent: 'bg-indigo-500/10 hover:bg-indigo-500/20',
    textAccent: 'text-indigo-300',
  },
  {
    type: 'pharmacy',
    name: 'Sri Durga Medical & General Stores',
    badge: 'Pharmacy',
    emoji: '💊',
    desc: 'Dolo 650, Insulins, Syrups, Expiry Alerts & Batch Numbers',
    email: 'pharmacy@dukaansetu.com',
    borderAccent: 'border-cyan-500/30',
    bgAccent: 'bg-cyan-500/10 hover:bg-cyan-500/20',
    textAccent: 'text-cyan-300',
  },
  {
    type: 'bakery',
    name: 'Sri Sai Sweet Home & Bakery',
    badge: 'Bakery',
    emoji: '🍞',
    desc: 'Fresh Cakes, Milk Bread, Mysore Pak, Puffs & Biscuits',
    email: 'bakery@dukaansetu.com',
    borderAccent: 'border-orange-500/30',
    bgAccent: 'bg-orange-500/10 hover:bg-orange-500/20',
    textAccent: 'text-orange-300',
  },
  {
    type: 'restaurant',
    name: 'Sri Annapurna Tiffin & Meals',
    badge: 'Restaurant',
    emoji: '🍽️',
    desc: 'Dum Biryani, Dosa, Idli Sambar, Raw Spices & Thali',
    email: 'restaurant@dukaansetu.com',
    borderAccent: 'border-red-500/30',
    bgAccent: 'bg-red-500/10 hover:bg-red-500/20',
    textAccent: 'text-red-300',
  },
  {
    type: 'teacoffee',
    name: 'Sri Balaji Irani Tea & Coffee Point',
    badge: 'Tea & Coffee',
    emoji: '☕',
    desc: 'Irani Dum Chai, Filter Coffee, Samosa & Daily Milk',
    email: 'teacoffee@dukaansetu.com',
    borderAccent: 'border-yellow-500/30',
    bgAccent: 'bg-yellow-500/10 hover:bg-yellow-500/20',
    textAccent: 'text-yellow-300',
  },
  {
    type: 'hardware',
    name: 'Sri Hanuman Hardware & Electricals',
    badge: 'Hardware',
    emoji: '🔧',
    desc: 'PVC Pipes, Copper Wire, Switches, Cement & Asian Paints',
    email: 'hardware@dukaansetu.com',
    borderAccent: 'border-slate-400/30',
    bgAccent: 'bg-slate-500/10 hover:bg-slate-500/20',
    textAccent: 'text-slate-300',
  },
  {
    type: 'autoparts',
    name: 'Sri Ganesh Auto Spares & Accessories',
    badge: 'Auto Parts',
    emoji: '🛠️',
    desc: 'Castrol Engine Oil, Brake Shoes, Batteries & Tyres',
    email: 'autoparts@dukaansetu.com',
    borderAccent: 'border-blue-500/30',
    bgAccent: 'bg-blue-500/10 hover:bg-blue-500/20',
    textAccent: 'text-blue-300',
  },
  {
    type: 'vegetables',
    name: 'Sri Lakshmi Fresh Veg & Fruits',
    badge: 'Vegetables',
    emoji: '🥬',
    desc: 'Tomatoes, Onions, Potatoes, Chillies, Palak & Fruits',
    email: 'vegetables@dukaansetu.com',
    borderAccent: 'border-lime-500/30',
    bgAccent: 'bg-lime-500/10 hover:bg-lime-500/20',
    textAccent: 'text-lime-300',
  },
  {
    type: 'electronics',
    name: 'Sri Tech Zone Mobiles & Electronics',
    badge: 'Electronics',
    emoji: '📱',
    desc: '5G Smartphones, Chargers, Earbuds, Cables & Screen Guards',
    email: 'electronics@dukaansetu.com',
    borderAccent: 'border-purple-500/30',
    bgAccent: 'bg-purple-500/10 hover:bg-purple-500/20',
    textAccent: 'text-purple-300',
  },
];

export default function LoginPage() {
  const { login, loginAsDemo } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoClick = async (storeType: StoreTypeSlug) => {
    setLoading(true);
    setError('');
    try {
      await loginAsDemo(storeType);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Demo store login failed');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-1">Welcome back</h2>
      <p className="text-surface-400 text-sm mb-6">Sign in to manage your shop</p>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-200 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="login-email">
            Email
          </label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            placeholder="you@example.com"
            required
            autoComplete="email"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="login-password">
            Password
          </label>
          <div className="relative">
            <input
              id="login-password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all pr-12"
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white transition-colors"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl gradient-primary text-white font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 min-h-[48px]"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Signing in...
            </>
          ) : (
            'Sign In'
          )}
        </button>
      </form>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-white/10"></div>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-[#0f172a] px-3 text-surface-300 font-bold flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-amber-400" />
            1-Click Demo Login (All 12 Retail Stores)
          </span>
        </div>
      </div>

      {/* Direct 1-Click Login for ALL 12 Stores */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-6">
        {ALL_DEMO_STORES.map((store) => (
          <button
            key={store.type}
            type="button"
            disabled={loading}
            onClick={() => handleDemoClick(store.type)}
            className={`p-3 rounded-xl ${store.bgAccent} border ${store.borderAccent} text-left transition-all group flex items-center justify-between shadow-xs hover:scale-[1.01] active:scale-[0.99]`}
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <span className="text-xl p-1.5 rounded-lg bg-black/30 border border-white/10 flex-shrink-0">
                {store.emoji}
              </span>
              <div className="min-w-0">
                <div className={`text-xs font-bold ${store.textAccent} group-hover:text-white flex items-center gap-1.5 truncate`}>
                  <span className="truncate">{store.name}</span>
                </div>
                <div className="text-[10px] text-surface-400 flex items-center gap-1 mt-0.5">
                  <span className={`px-1.5 py-0.2 rounded-full bg-white/10 ${store.textAccent} font-medium border border-white/10 text-[9px]`}>
                    {store.badge}
                  </span>
                  <span className="truncate text-surface-400 text-[10px]">{store.desc.split(',')[0]}</span>
                </div>
              </div>
            </div>
            <span className={`text-xs font-bold ${store.textAccent} group-hover:translate-x-0.5 transition-transform flex-shrink-0 ml-1`}>
              Login →
            </span>
          </button>
        ))}
      </div>

      {/* Quick Auto-Fill Credentials */}
      <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-xs text-surface-400">
        <div className="font-medium text-surface-300 mb-1.5">Quick Auto-Fill Credentials (All 12):</div>
        <div className="flex flex-wrap gap-1.5">
          {ALL_DEMO_STORES.map((store) => (
            <button
              key={store.type}
              type="button"
              onClick={() => {
                setEmail(store.email);
                setPassword('password123');
              }}
              className="px-2 py-1 rounded bg-white/10 hover:bg-white/20 text-surface-300 hover:text-white transition-colors text-[11px] flex items-center gap-1"
            >
              <span>{store.emoji}</span>
              <span>{store.badge}</span>
            </button>
          ))}
        </div>
      </div>

      <p className="text-center text-surface-400 text-sm mt-6">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
          Register
        </Link>
      </p>
    </div>
  );
}
