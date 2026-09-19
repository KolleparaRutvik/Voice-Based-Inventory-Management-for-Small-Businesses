import { Outlet } from 'react-router-dom';
import { Mic } from 'lucide-react';

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-surface-900 via-primary-950 to-surface-900 px-4 py-8">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-20 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-20 w-72 h-72 bg-accent-500/10 rounded-full blur-3xl" />
      </div>

      {/* Logo */}
      <div className="relative z-10 flex flex-col items-center mb-8">
        <div className="w-16 h-16 rounded-2xl gradient-accent flex items-center justify-center mb-4 shadow-glow-accent">
          <Mic className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white">DukaanSetu</h1>
        <p className="text-surface-400 text-sm mt-1">Voice-first inventory assistant</p>
      </div>

      {/* Auth Card */}
      <div className="relative z-10 w-full max-w-md">
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl border border-white/10 p-8 shadow-2xl">
          <Outlet />
        </div>
      </div>

      {/* Footer */}
      <p className="relative z-10 text-surface-500 text-xs mt-8">
        Shopkeeper speaks. DukaanSetu understands.
      </p>
    </div>
  );
}
