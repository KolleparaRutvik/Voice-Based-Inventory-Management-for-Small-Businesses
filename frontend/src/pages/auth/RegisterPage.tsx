import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(formData);
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const shopTypes = [
    { value: 'kirana', label: 'Kirana Store' },
    { value: 'grocery', label: 'Grocery Store' },
    { value: 'wholesale', label: 'Wholesale' },
    { value: 'retail', label: 'Retail Shop' },
    { value: 'distributor', label: 'Distributor' },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-1">Create Account</h2>
      <p className="text-surface-400 text-sm mb-6">Start managing your shop with voice</p>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-200 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-name">
            Your Name
          </label>
          <input
            id="reg-name"
            name="full_name"
            type="text"
            value={formData.full_name}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder="Srinivas Kumar"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-email">
            Email
          </label>
          <input
            id="reg-email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder="you@example.com"
            required
            autoComplete="email"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-phone">
            Phone (Optional)
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
          <p className="text-xs text-surface-400 mb-3">Shop Information</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-shop">
            Shop Name
          </label>
          <input
            id="reg-shop"
            name="shop_name"
            type="text"
            value={formData.shop_name}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
            placeholder="Sri Lakshmi Kirana Store"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-surface-300 mb-1.5" htmlFor="reg-shop-type">
            Shop Type
          </label>
          <select
            id="reg-shop-type"
            name="shop_type"
            value={formData.shop_type}
            onChange={handleChange}
            className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
          >
            {shopTypes.map(type => (
              <option key={type.value} value={type.value} className="bg-surface-800">
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl gradient-accent text-white font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 min-h-[48px]"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating account...
            </>
          ) : (
            'Create Account'
          )}
        </button>
      </form>

      <p className="text-center text-surface-400 text-sm mt-6">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
          Sign In
        </Link>
      </p>
    </div>
  );
}
