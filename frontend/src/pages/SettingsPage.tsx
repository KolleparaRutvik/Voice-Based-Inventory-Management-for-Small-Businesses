import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Mic, Globe, Bell, Shield, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user, shop } = useAuth();
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    save_voice_recordings: false,
    language: 'en',
    tts_enabled: true,
    notifications_enabled: true,
    low_stock_alerts: true,
    borrow_reminders: true,
  });

  const handleSave = async () => {
    setSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setSaving(false);
  };

  return (
    <div className="page-container pt-6 space-y-4 animate-fade-in">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10 lg:hidden">
          <ArrowLeft className="w-5 h-5 text-surface-600" />
        </button>
        <h2 className="text-xl font-bold text-surface-900">Settings</h2>
      </div>

      {/* Shop Info */}
      <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-3">
        <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2">
          <Shield className="w-4 h-4" /> Shop Information
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between py-2 border-b border-surface-50">
            <span className="text-surface-500">Shop Name</span>
            <span className="font-medium text-surface-800">{shop?.name || 'Your Shop'}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-surface-50">
            <span className="text-surface-500">Owner</span>
            <span className="font-medium text-surface-800">{user?.full_name || 'User'}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-surface-50">
            <span className="text-surface-500">Email</span>
            <span className="font-medium text-surface-800">{user?.email || '-'}</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-surface-500">Shop Type</span>
            <span className="font-medium text-surface-800 capitalize">{shop?.type || 'kirana'}</span>
          </div>
        </div>
      </div>

      {/* Voice Settings */}
      <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
        <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2">
          <Mic className="w-4 h-4" /> Voice Settings
        </h3>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-surface-800">Save Voice Recordings</p>
            <p className="text-xs text-surface-500">Store audio files for history</p>
          </div>
          <button
            onClick={() => setSettings(prev => ({ ...prev, save_voice_recordings: !prev.save_voice_recordings }))}
            className={`relative w-12 h-7 rounded-full transition-colors ${
              settings.save_voice_recordings ? 'bg-primary-500' : 'bg-surface-300'
            }`}
          >
            <span className={`absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-transform ${
              settings.save_voice_recordings ? 'translate-x-5' : 'translate-x-0.5'
            }`} />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-surface-800">Voice Response (TTS)</p>
            <p className="text-xs text-surface-500">Speak responses aloud</p>
          </div>
          <button
            onClick={() => setSettings(prev => ({ ...prev, tts_enabled: !prev.tts_enabled }))}
            className={`relative w-12 h-7 rounded-full transition-colors ${
              settings.tts_enabled ? 'bg-primary-500' : 'bg-surface-300'
            }`}
          >
            <span className={`absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-transform ${
              settings.tts_enabled ? 'translate-x-5' : 'translate-x-0.5'
            }`} />
          </button>
        </div>
      </div>

      {/* Language */}
      <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-3">
        <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2">
          <Globe className="w-4 h-4" /> Language
        </h3>
        <select
          value={settings.language}
          onChange={(e) => setSettings(prev => ({ ...prev, language: e.target.value }))}
          className="input-field"
        >
          <option value="en">English</option>
          <option value="te">Telugu (తెలుగు)</option>
          <option value="hi">Hindi (हिन्दी)</option>
        </select>
      </div>

      {/* Notifications */}
      <div className="bg-white rounded-2xl border border-surface-100 p-4 space-y-4">
        <h3 className="text-sm font-semibold text-surface-700 flex items-center gap-2">
          <Bell className="w-4 h-4" /> Notifications
        </h3>

        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-surface-800">Low Stock Alerts</p>
          <button
            onClick={() => setSettings(prev => ({ ...prev, low_stock_alerts: !prev.low_stock_alerts }))}
            className={`relative w-12 h-7 rounded-full transition-colors ${
              settings.low_stock_alerts ? 'bg-primary-500' : 'bg-surface-300'
            }`}
          >
            <span className={`absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-transform ${
              settings.low_stock_alerts ? 'translate-x-5' : 'translate-x-0.5'
            }`} />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-surface-800">Borrow Reminders</p>
          <button
            onClick={() => setSettings(prev => ({ ...prev, borrow_reminders: !prev.borrow_reminders }))}
            className={`relative w-12 h-7 rounded-full transition-colors ${
              settings.borrow_reminders ? 'bg-primary-500' : 'bg-surface-300'
            }`}
          >
            <span className={`absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-sm transition-transform ${
              settings.borrow_reminders ? 'translate-x-5' : 'translate-x-0.5'
            }`} />
          </button>
        </div>
      </div>

      <button onClick={handleSave} disabled={saving} className="w-full touch-btn gradient-primary text-white font-semibold text-sm py-3.5 disabled:opacity-50">
        {saving ? <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</> : <><Save className="w-4 h-4" /> Save Settings</>}
      </button>
    </div>
  );
}
