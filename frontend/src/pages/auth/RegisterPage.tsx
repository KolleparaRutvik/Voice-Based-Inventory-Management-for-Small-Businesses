import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2, Check, X, Sparkles, Store } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export interface ShopTypeOption {
  id: string;
  name: string;
  emoji: string;
  examples: string;
  need: string;
  placeholder: string;
  borderAccent: string;
  bgAccent: string;
  textAccent: string;
}

export const SHOP_TYPE_OPTIONS: ShopTypeOption[] = [
  {
    id: 'kirana',
    name: 'Kirana / Grocery',
    emoji: '🛒',
    examples: 'Rice, sugar, oil, dal, flour, spices',
    need: '⭐⭐⭐⭐⭐',
    placeholder: 'Sri Lakshmi Kirana Store',
    borderAccent: 'border-emerald-500/40',
    bgAccent: 'bg-emerald-500/10 hover:bg-emerald-500/20',
    textAccent: 'text-emerald-400',
  },
  {
    id: 'flowers',
    name: 'Flower & Pooja Shop',
    emoji: '🌸',
    examples: 'Flowers, garlands, camphor, agarbatti, pooja items',
    need: '⭐⭐⭐⭐⭐',
    placeholder: 'Sri Venkateswara Flower Mart',
    borderAccent: 'border-rose-500/40',
    bgAccent: 'bg-rose-500/10 hover:bg-rose-500/20',
    textAccent: 'text-rose-400',
  },
  {
    id: 'jewellery',
    name: 'Jewellery Shop',
    emoji: '💎',
    examples: 'Gold, silver, diamonds, 916 coins, girvi/loans',
    need: '⭐⭐⭐⭐',
    placeholder: 'Sri Swarna Mahal Jewellers',
    borderAccent: 'border-amber-500/40',
    bgAccent: 'bg-amber-500/10 hover:bg-amber-500/20',
    textAccent: 'text-amber-400',
  },
  {
    id: 'clothing',
    name: 'Clothing & Textiles',
    emoji: '👕',
    examples: 'Shirts, pattu sarees, pants, kurtis, fabrics',
    need: '⭐⭐⭐⭐',
    placeholder: 'Sri Raghavendra Cloth Emporium',
    borderAccent: 'border-indigo-500/40',
    bgAccent: 'bg-indigo-500/10 hover:bg-indigo-500/20',
    textAccent: 'text-indigo-400',
  },
  {
    id: 'pharmacy',
    name: 'Pharmacy / Medical',
    emoji: '💊',
    examples: 'Medicines, tablets, syrups, insulin, BP monitors',
    need: '⭐⭐⭐⭐⭐',
    placeholder: 'Sri Durga Medical & General Stores',
    borderAccent: 'border-cyan-500/40',
    bgAccent: 'bg-cyan-500/10 hover:bg-cyan-500/20',
    textAccent: 'text-cyan-400',
  },
  {
    id: 'bakery',
    name: 'Bakery & Sweet Shop',
    emoji: '🍞',
    examples: 'Cakes, milk bread, sweets, puffs, biscuits',
    need: '⭐⭐⭐⭐',
    placeholder: 'Sri Sai Sweet Home & Bakery',
    borderAccent: 'border-orange-500/40',
    bgAccent: 'bg-orange-500/10 hover:bg-orange-500/20',
    textAccent: 'text-orange-400',
  },
  {
    id: 'restaurant',
    name: 'Restaurant / Tiffin',
    emoji: '🍽️',
    examples: 'Biryani, dosa, idli, thali meals, bulk ingredients',
    need: '⭐⭐⭐⭐⭐',
    placeholder: 'Sri Annapurna Tiffin & Meals',
    borderAccent: 'border-red-500/40',
    bgAccent: 'bg-red-500/10 hover:bg-red-500/20',
    textAccent: 'text-red-400',
  },
  {
    id: 'teacoffee',
    name: 'Tea & Coffee Stall',
    emoji: '☕',
    examples: 'Irani chai, filter coffee, samosa, milk, snacks',
    need: '⭐⭐⭐',
    placeholder: 'Sri Balaji Irani Tea Point',
    borderAccent: 'border-yellow-500/40',
    bgAccent: 'bg-yellow-500/10 hover:bg-yellow-500/20',
    textAccent: 'text-yellow-400',
  },
  {
    id: 'hardware',
    name: 'Hardware & Electrical',
    emoji: '🔧',
    examples: 'PVC pipes, copper wire, switches, cement, paints',
    need: '⭐⭐⭐⭐',
    placeholder: 'Sri Hanuman Hardware & Electricals',
    borderAccent: 'border-slate-400/40',
    bgAccent: 'bg-slate-500/10 hover:bg-slate-500/20',
    textAccent: 'text-slate-300',
  },
  {
    id: 'autoparts',
    name: 'Auto Parts & Spares',
    emoji: '🛠️',
    examples: 'Brake pads, engine oil, tyres, batteries, cables',
    need: '⭐⭐⭐⭐',
    placeholder: 'Sri Ganesh Auto Spares & Accessories',
    borderAccent: 'border-blue-500/40',
    bgAccent: 'bg-blue-500/10 hover:bg-blue-500/20',
    textAccent: 'text-blue-400',
  },
  {
    id: 'vegetables',
    name: 'Vegetable & Fruit Market',
    emoji: '🥬',
    examples: 'Tomatoes, onions, potatoes, green chillies, fruits',
    need: '⭐⭐⭐⭐⭐',
    placeholder: 'Sri Lakshmi Fresh Veg & Fruits',
    borderAccent: 'border-lime-500/40',
    bgAccent: 'bg-lime-500/10 hover:bg-lime-500/20',
    textAccent: 'text-lime-400',
  },
  {
    id: 'electronics',
    name: 'Electronics & Mobiles',
    emoji: '📱',
    examples: 'Phones, chargers, earbuds, cables, screen guards',
    need: '⭐⭐⭐⭐',
    placeholder: 'Sri Tech Zone Mobiles & Electronics',
    borderAccent: 'border-purple-500/40',
    bgAccent: 'bg-purple-500/10 hover:bg-purple-500/20',
    textAccent: 'text-purple-400',
  },
];

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    shop_name: '',
    shop_type: 'kirana',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const selectedShopType = SHOP_TYPE_OPTIONS.find(t => t.id === formData.shop_type) || SHOP_TYPE_OPTIONS[0];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSelectShopType = (type: ShopTypeOption) => {
    setFormData(prev => ({
      ...prev,
      shop_type: type.id,
      shop_name: prev.shop_name === '' || SHOP_TYPE_OPTIONS.some(o => o.placeholder === prev.shop_name)
        ? type.placeholder
        : prev.shop_name,
    }));
    setIsModalOpen(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({
        ...formData,
        shop_name: formData.shop_name.trim() || selectedShopType.placeholder,
      });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
        <span>Create Account</span>
        <span className="text-xs font-normal px-2 py-0.5 rounded-full bg-primary-500/20 text-primary-300 border border-primary-500/30">
          12 Retail Verticals
        </span>
      </h2>
      <p className="text-surface-400 text-sm mb-6">Start managing your business with DukaanSetu Voice AI</p>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-200 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-name">
            Your Name / Merchant Name
          </label>
          <input
            id="reg-name"
            name="full_name"
            type="text"
            value={formData.full_name}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder="e.g. Srinivas Kumar"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-email">
            Email Address
          </label>
          <input
            id="reg-email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder="merchant@example.com"
            required
            autoComplete="email"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-phone">
            Phone Number (Optional)
          </label>
          <input
            id="reg-phone"
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder="+91 9876543210"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-password">
            Password
          </label>
          <div className="relative">
            <input
              id="reg-password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all pr-12"
              placeholder="Minimum 6 characters"
              required
              minLength={6}
              autoComplete="new-password"
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

        <div className="border-t border-white/10 pt-4 mt-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-surface-400 mb-3 flex items-center gap-1.5">
            <Store className="w-3.5 h-3.5 text-primary-400" />
            Shop Information & Business Vertical
          </p>
        </div>

        {/* Business Type Selection Card with Modal Trigger */}
        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5 flex items-center justify-between">
            <span>Business / Shop Vertical</span>
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="text-xs text-primary-400 hover:text-primary-300 font-semibold underline underline-offset-2 flex items-center gap-1 transition-colors"
            >
              <Sparkles className="w-3 h-3" />
              Choose from 12 Shop Types
            </button>
          </label>

          <div
            onClick={() => setIsModalOpen(true)}
            className={`cursor-pointer w-full p-3 rounded-xl border ${selectedShopType.borderAccent} bg-white/5 hover:bg-white/10 transition-all flex items-center justify-between group shadow-sm`}
          >
            <div className="flex items-center gap-3">
              <span className="text-3xl p-2 rounded-lg bg-white/10 border border-white/10">
                {selectedShopType.emoji}
              </span>
              <div>
                <div className="font-semibold text-white group-hover:text-primary-300 transition-colors flex items-center gap-2">
                  {selectedShopType.name}
                  <span className={`text-[11px] px-2 py-0.5 rounded-full border ${selectedShopType.borderAccent} ${selectedShopType.textAccent} font-normal`}>
                    {selectedShopType.need}
                  </span>
                </div>
                <div className="text-xs text-surface-400 line-clamp-1">
                  Examples: {selectedShopType.examples}
                </div>
              </div>
            </div>
            <button
              type="button"
              className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 border border-primary-500/40 transition-colors"
            >
              Change →
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-shop">
            Shop / Business Name
          </label>
          <input
            id="reg-shop"
            name="shop_name"
            type="text"
            value={formData.shop_name}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder={selectedShopType.placeholder}
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 rounded-xl gradient-accent text-white font-semibold text-sm hover:opacity-95 shadow-lg shadow-accent-950/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2 min-h-[48px]"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Setting up {selectedShopType.name}...
            </>
          ) : (
            `Register ${selectedShopType.name}`
          )}
        </button>
      </form>

      <p className="text-center text-surface-400 text-sm mt-6">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
          Sign In
        </Link>
      </p>

      {/* POPUP MODAL: Choose From 12 Shop Types */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-4xl max-h-[90vh] bg-surface-900 border border-white/20 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-white">
            {/* Modal Header */}
            <div className="p-4 sm:p-5 border-b border-white/10 flex items-center justify-between bg-surface-800/80">
              <div>
                <h3 className="text-lg sm:text-xl font-bold text-white flex items-center gap-2">
                  <span>Select Your Business Type</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary-500/20 text-primary-300 border border-primary-500/40">
                    12 Verticals
                  </span>
                </h3>
                <p className="text-xs text-surface-400 mt-0.5">
                  DukaanSetu customizes your voice assistant, catalog units, and alert system to your vertical
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-surface-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Grid of 12 Shops */}
            <div className="p-4 sm:p-6 overflow-y-auto max-h-[calc(90vh-140px)] grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {SHOP_TYPE_OPTIONS.map((type) => {
                const isSelected = formData.shop_type === type.id;
                return (
                  <div
                    key={type.id}
                    onClick={() => handleSelectShopType(type)}
                    className={`cursor-pointer relative p-3.5 rounded-xl border transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'border-primary-500 bg-primary-500/20 shadow-lg shadow-primary-500/20 ring-2 ring-primary-500/40'
                        : `${type.borderAccent} ${type.bgAccent}`
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="text-2xl p-1.5 rounded-lg bg-black/30 border border-white/10">
                          {type.emoji}
                        </span>
                        <div>
                          <div className="text-sm font-semibold text-white">
                            {type.name}
                          </div>
                          <div className="text-[11px] text-amber-300/90 font-mono">
                            Need: {type.need}
                          </div>
                        </div>
                      </div>
                      {isSelected && (
                        <span className="w-5 h-5 rounded-full bg-primary-500 text-white flex items-center justify-center text-xs shadow">
                          <Check className="w-3.5 h-3.5 stroke-[3]" />
                        </span>
                      )}
                    </div>

                    <div className="mt-3 text-xs text-surface-300/90 bg-black/20 p-2 rounded-lg border border-white/5">
                      <span className="font-medium text-surface-200">Examples:</span> {type.examples}
                    </div>

                    <div className="mt-2 text-[11px] text-surface-400 flex items-center justify-between">
                      <span className="truncate italic">"{type.placeholder}"</span>
                      <span className="text-primary-400 font-semibold group-hover:underline">Select →</span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Modal Footer */}
            <div className="p-3 sm:p-4 border-t border-white/10 bg-surface-800/80 flex items-center justify-between text-xs text-surface-400">
              <span>Click any business type to select it and apply its persona.</span>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
