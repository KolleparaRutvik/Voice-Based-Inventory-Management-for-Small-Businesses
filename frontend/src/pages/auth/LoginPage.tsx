import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

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
          <span className="bg-[#0f172a] px-3 text-surface-400 font-medium">Or explore personalized demo stores</span>
        </div>
      </div>

      <div className="space-y-2.5 mb-6">
        {/* Kirana Store Demo */}
        <button
          type="button"
          disabled={loading}
          onClick={async () => {
            setLoading(true);
            try {
              await loginAsDemo('kirana');
              navigate('/');
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Demo login failed');
            } finally {
              setLoading(false);
            }
          }}
          className="w-full p-3 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-left transition-all group flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl p-2 rounded-lg bg-emerald-500/20 border border-emerald-500/30">🌾</span>
            <div>
              <div className="text-sm font-semibold text-emerald-300 group-hover:text-white flex items-center gap-2">
                Sri Lakshmi Kirana Store
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-normal">Kirana</span>
              </div>
              <div className="text-xs text-surface-400">Rice, Dal, Oil, FMCG & Customer Udhar</div>
            </div>
          </div>
          <span className="text-xs font-semibold text-emerald-400 group-hover:translate-x-0.5 transition-transform">Enter →</span>
        </button>

        {/* Jewellery Shop Demo */}
        <button
          type="button"
          disabled={loading}
          onClick={async () => {
            setLoading(true);
            try {
              await loginAsDemo('jewellery');
              navigate('/');
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Jewellery demo login failed');
            } finally {
              setLoading(false);
            }
          }}
          className="w-full p-3 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-left transition-all group flex items-center justify-between shadow-lg shadow-amber-950/20"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl p-2 rounded-lg bg-amber-500/20 border border-amber-500/30">💎</span>
            <div>
              <div className="text-sm font-semibold text-amber-300 group-hover:text-white flex items-center gap-2">
                Sri Swarna Mahal Jewellers
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-normal">Jewellery</span>
              </div>
              <div className="text-xs text-surface-400">22K Gold 916, Silver, Diamonds, Grams & Loans</div>
            </div>
          </div>
          <span className="text-xs font-semibold text-amber-400 group-hover:translate-x-0.5 transition-transform">Enter →</span>
        </button>

        {/* Flower Shop Demo */}
        <button
          type="button"
          disabled={loading}
          onClick={async () => {
            setLoading(true);
            try {
              await loginAsDemo('flowers');
              navigate('/');
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Flower demo login failed');
            } finally {
              setLoading(false);
            }
          }}
          className="w-full p-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-left transition-all group flex items-center justify-between shadow-lg shadow-rose-950/20"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl p-2 rounded-lg bg-rose-500/20 border border-rose-500/30">🌸</span>
            <div>
              <div className="text-sm font-semibold text-rose-300 group-hover:text-white flex items-center gap-2">
                Sri Venkateswara Flower Mart
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-normal">Flowers</span>
              </div>
              <div className="text-xs text-surface-400">Jasmine, Marigold, Garlands, Mora & Temple Decor</div>
            </div>
          </div>
          <span className="text-xs font-semibold text-rose-400 group-hover:translate-x-0.5 transition-transform">Enter →</span>
        </button>
      </div>

      <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-xs text-surface-400">
        <div className="font-medium text-surface-300 mb-1.5">Quick Auto-Fill Credentials:</div>
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => { setEmail('srinivas@dukaansetu.com'); setPassword('password123'); }}
            className="px-2 py-1 rounded bg-white/10 hover:bg-white/20 text-surface-300 hover:text-white transition-colors"
          >
            🌾 Kirana Login
          </button>
          <button
            type="button"
            onClick={() => { setEmail('jewellery@dukaansetu.com'); setPassword('password123'); }}
            className="px-2 py-1 rounded bg-white/10 hover:bg-white/20 text-amber-300 hover:text-white transition-colors"
          >
            💎 Jewellery Login
          </button>
          <button
            type="button"
            onClick={() => { setEmail('flowers@dukaansetu.com'); setPassword('password123'); }}
            className="px-2 py-1 rounded bg-white/10 hover:bg-white/20 text-rose-300 hover:text-white transition-colors"
          >
            🌸 Flower Login
          </button>
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
