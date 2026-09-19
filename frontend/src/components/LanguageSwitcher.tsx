import { Globe } from 'lucide-react';
import { useLanguage, type Language } from '../context/LanguageContext';

export default function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { language, setLanguage } = useLanguage();

  const options: { code: Language; label: string; native: string }[] = [
    { code: 'en', label: 'English', native: 'EN' },
    { code: 'te', label: 'తెలుగు', native: 'తె' },
    { code: 'hi', label: 'हिंदी', native: 'हिं' },
  ];

  if (compact) {
    return (
      <div className="flex items-center gap-1 bg-surface-100 p-1 rounded-xl border border-surface-200">
        <Globe className="w-3.5 h-3.5 text-surface-500 ml-1" />
        {options.map((opt) => (
          <button
            key={opt.code}
            onClick={() => setLanguage(opt.code)}
            className={`px-2 py-1 rounded-lg text-xs font-semibold transition-all ${
              language === opt.code
                ? 'bg-primary-600 text-white shadow-sm'
                : 'text-surface-600 hover:text-surface-900 hover:bg-surface-200/60'
            }`}
            title={opt.label}
          >
            {opt.native}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1 bg-surface-50 p-1 rounded-xl border border-surface-200">
      <Globe className="w-4 h-4 text-surface-400 ml-1.5 mr-0.5" />
      {options.map((opt) => (
        <button
          key={opt.code}
          onClick={() => setLanguage(opt.code)}
          className={`flex-1 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all text-center ${
            language === opt.code
              ? 'bg-primary-600 text-white shadow-sm font-semibold'
              : 'text-surface-600 hover:text-surface-900 hover:bg-surface-100'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
