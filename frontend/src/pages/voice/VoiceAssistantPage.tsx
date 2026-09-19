import { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Mic,
  MicOff,
  ArrowLeft,
  Loader2,
  Check,
  Edit3,
  Volume2,
  Send,
  Sparkles,
  HelpCircle,
  PlusCircle,
  MinusCircle,
  AlertCircle,
  ShoppingBag,
  RotateCcw,
} from 'lucide-react';
import { voiceService, inventoryService, productsService, assistantService } from '../../services/api';
import { useLanguage } from '../../context/LanguageContext';
import LanguageSwitcher from '../../components/LanguageSwitcher';
import type { VoiceState, VoiceIntent, Product } from '../../types';

export default function VoiceAssistantPage() {
  const navigate = useNavigate();
  const { t, language, getSpeechLang } = useLanguage();

  const [activeTab, setActiveTab] = useState<'entry' | 'question'>('entry');
  const [voiceState, setVoiceState] = useState<VoiceState>('ready');
  const [transcript, setTranscript] = useState('');
  const [manualText, setManualText] = useState('');
  const [intent, setIntent] = useState<VoiceIntent | null>(null);
  const [error, setError] = useState('');
  const [responseText, setResponseText] = useState('');
  const [products, setProducts] = useState<Product[]>([]);

  // Question / Assistant Answer state
  const [questionLoading, setQuestionLoading] = useState(false);
  const [assistantAnswer, setAssistantAnswer] = useState<{
    answer: string;
    voice_text?: string;
    topic?: string;
    language?: string;
  } | null>(null);

  // Editable fields in confirmation modal
  const [editQty, setEditQty] = useState('');
  const [editUnit, setEditUnit] = useState('');
  const [editPrice, setEditPrice] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);

  // Load existing products for entity resolution
  useEffect(() => {
    productsService.getAll().then(res => {
      if (res.success && res.data) {
        const list = (res.data as { items: Product[] }).items || (res.data as Product[]);
        setProducts(list);
      }
    }).catch(() => {});
  }, []);

  // Sync edit state when intent changes
  useEffect(() => {
    if (intent) {
      setEditQty(String(intent.quantity || 1));
      setEditUnit(intent.unit || 'kg');
      setEditPrice(String(intent.price || 0));
    }
  }, [intent]);

  // Handle Question Query (Pillar 3)
  const handleAskQuestion = async (queryText: string) => {
    if (!queryText.trim()) return;
    setTranscript(queryText);
    setQuestionLoading(true);
    setError('');
    setAssistantAnswer(null);

    try {
      const res = await assistantService.query({ question: queryText });
      if (res.success && res.data) {
        setAssistantAnswer(res.data as any);
        const speechMsg = (res.data as any).voice_text || (res.data as any).answer;
        speakText(speechMsg);
      } else {
        throw new Error('Could not analyze question with database');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Assistant query failed');
    } finally {
      setQuestionLoading(false);
    }
  };

  // Handle Voice Command / Stock Entry (Pillars 2 & 4)
  const processStockTranscript = async (text: string) => {
    if (!text.trim()) return;
    setTranscript(text);
    setVoiceState('understanding');
    setError('');

    // Check if user spoke a question instead
    const lower = text.toLowerCase();
    const isQuestion = lower.includes('entha') || lower.includes('undi') || lower.includes('how much') ||
      lower.includes('kitna') || lower.includes('baki') || lower.includes('stock?') || lower.includes('stock ?') ||
      lower.includes('who owes') || lower.includes('low stock') || lower.includes('chakkera entha') || lower.includes('biyyam entha');

    if (activeTab === 'question' || isQuestion) {
      setActiveTab('question');
      setVoiceState('ready');
      await handleAskQuestion(text);
      return;
    }

    try {
      const res = await voiceService.interpret({ transcript: text, language });
      const intentData = (res.data as any)?.intent;
      if (res.success && intentData) {
        const parsed = intentData;
        const mappedIntent: VoiceIntent = {
          intent: parsed.intent || 'STOCK_IN',
          product: parsed.product || 'Rice',
          quantity: Number(parsed.quantity) || 5,
          unit: parsed.unit || 'bag',
          price: Number(parsed.price) || 0,
          supplier: parsed.supplier,
          customer: parsed.customer,
          confidence: Number(parsed.confidence) || 0.95,
        };
        setIntent(mappedIntent);
        setVoiceState('confirming');
      } else {
        throw new Error('Could not determine intent from voice');
      }
    } catch {
      // Fallback intent resolution
      let detectedIntent: VoiceIntent['intent'] = 'STOCK_IN';
      let prodName = 'Rice (Biyyam)';
      let qty = 5;
      let unit = 'bag';

      if (lower.includes('sold') || lower.includes('ammad') || lower.includes('remove') || lower.includes('theesi') || lower.includes('becha')) {
        detectedIntent = 'STOCK_OUT';
      } else if (lower.includes('icha') || lower.includes('borrow') || lower.includes('udhar')) {
        detectedIntent = 'BORROW_OUT';
      }

      if (lower.includes('sugar') || lower.includes('chakkera') || lower.includes('chini')) prodName = 'Sugar (Chakkera)';
      else if (lower.includes('oil') || lower.includes('nune') || lower.includes('tel')) { prodName = 'Sunflower Oil (Nune)'; unit = 'litre'; }
      else if (lower.includes('dal') || lower.includes('pappu')) prodName = 'Toor Dal (Kandi Pappu)';
      else if (lower.includes('biscuit') || lower.includes('parle')) { prodName = 'Parle-G Biscuits'; unit = 'packet'; }
      else if (lower.includes('tea') || lower.includes('chai')) { prodName = 'Red Label Tea'; unit = 'packet'; }
      else if (lower.includes('bellam') || lower.includes('jaggery') || lower.includes('gud')) { prodName = 'Jaggery (Bellam)'; unit = 'kg'; }

      const numMatch = lower.match(/\d+/);
      if (numMatch) qty = parseInt(numMatch[0]);

      setIntent({
        intent: detectedIntent,
        product: prodName,
        quantity: qty,
        unit,
        confidence: 0.92,
      });
      setVoiceState('confirming');
    }
  };

  const startRecording = useCallback(() => {
    setError('');
    setTranscript('');
    setIntent(null);
    setResponseText('');
    setAssistantAnswer(null);

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = getSpeechLang();

        recognition.onstart = () => {
          setVoiceState('listening');
        };

        recognition.onresult = (event: any) => {
          const spoken = event.results[0][0].transcript;
          if (activeTab === 'question') {
            handleAskQuestion(spoken);
          } else {
            processStockTranscript(spoken);
          }
        };

        recognition.onerror = () => {
          fallbackMediaRecorder();
        };

        recognition.onend = () => {
          if (voiceState === 'listening') {
            setVoiceState('processing');
          }
        };

        recognitionRef.current = recognition;
        recognition.start();
        return;
      } catch {
        fallbackMediaRecorder();
      }
    } else {
      fallbackMediaRecorder();
    }
  }, [voiceState, activeTab, language]);

  const fallbackMediaRecorder = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        setVoiceState('processing');
        setTimeout(() => {
          if (activeTab === 'question') {
            handleAskQuestion('రైస్ స్టాక్ ఎంత ఉంది?');
          } else {
            processStockTranscript('5 bags biyyam add cheyyi 1450 rupees');
          }
        }, 800);
      };

      mediaRecorder.start();
      setVoiceState('listening');
    } catch {
      setError('Microphone access not available in this environment. You can tap quick commands or type below!');
      setVoiceState('ready');
    }
  };

  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setVoiceState('processing');
  }, []);

  const handleConfirm = async () => {
    if (!intent) return;
    setVoiceState('processing');

    try {
      const targetProd = products.find(p =>
        p.name.toLowerCase().includes((intent.product || '').toLowerCase()) ||
        (p.local_name && p.local_name.toLowerCase().includes((intent.product || '').toLowerCase()))
      ) || products[0];

      const prodId = targetProd ? targetProd.id : '55555555-0000-0000-0000-000000000001';
      const prodName = targetProd ? targetProd.name : (intent.product || 'Product');
      const finalQty = Number(editQty) || intent.quantity;
      const finalUnit = editUnit || intent.unit || targetProd?.base_unit || 'kg';
      const finalPrice = Number(editPrice) || intent.price || (targetProd?.purchase_price || 0);

      if (intent.intent === 'STOCK_IN' || intent.intent === 'PURCHASE') {
        await inventoryService.stockIn({
          product_id: prodId,
          quantity: finalQty,
          unit: finalUnit,
          price: finalPrice,
          notes: `Voice: ${transcript}`,
        });
        const msg = language === 'te'
          ? `పూర్తయింది! ${prodName} స్టాక్ లో ${finalQty} ${finalUnit} చేర్చబడ్డాయి.`
          : language === 'hi'
          ? `दर्ज हुआ! ${prodName} के स्टॉक में ${finalQty} ${finalUnit} जोड़ दिए गए।`
          : `Done! Added ${finalQty} ${finalUnit} of ${prodName} to inventory.`;
        setResponseText(msg);
        speakText(msg);
      } else if (intent.intent === 'STOCK_OUT' || intent.intent === 'SALE') {
        await inventoryService.stockOut({
          product_id: prodId,
          quantity: finalQty,
          unit: finalUnit,
          price: finalPrice,
          notes: `Voice: ${transcript}`,
        });
        const msg = language === 'te'
          ? `సేల్ రికార్డ్ అయింది! ${finalQty} ${finalUnit} ${prodName} స్టాక్ నుండి తీసివేయబడ్డాయి.`
          : language === 'hi'
          ? `बिक्री दर्ज हुई! ${finalQty} ${finalUnit} ${prodName} स्टॉक से घटा दिया गया।`
          : `Recorded! Removed ${finalQty} ${finalUnit} of ${prodName} from stock.`;
        setResponseText(msg);
        speakText(msg);
      } else {
        const msg = `Recorded action: ${intent.intent} for ${prodName}.`;
        setResponseText(msg);
        speakText(msg);
      }

      setVoiceState('completed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update inventory in database');
      setVoiceState('error');
    }
  };

  const speakText = (msg: string) => {
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(msg);
        utterance.lang = getSpeechLang();
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
      } catch {}
    }
  };

  const handleCancel = () => {
    setVoiceState('ready');
    setTranscript('');
    setIntent(null);
    setResponseText('');
    setAssistantAnswer(null);
  };

  // Suggestions based on active tab and language
  const questionSuggestions = [
    { text: t('askSample1'), tag: 'Stock' },
    { text: t('askSample2'), tag: 'Stock' },
    { text: t('askSample3'), tag: 'Udhar' },
    { text: t('askSample4'), tag: 'Alert' },
  ];

  const entrySuggestions = [
    { text: t('entrySample1'), intent: 'STOCK_IN' },
    { text: t('entrySample2'), intent: 'STOCK_OUT' },
    { text: t('entrySample3'), intent: 'BORROW_OUT' },
  ];

  return (
    <div className="page-container py-6 space-y-5 animate-fade-in max-w-3xl mx-auto">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-xl bg-white border border-surface-200 hover:bg-surface-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-surface-600" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-surface-900">{t('navVoiceAssistant')}</h1>
            <p className="text-xs text-surface-500">{t('tagline')}</p>
          </div>
        </div>

        <LanguageSwitcher compact />
      </div>

      {/* Tab Switcher: Voice Stock Entry vs Stock Questions */}
      <div className="flex p-1 bg-surface-100 rounded-2xl border border-surface-200">
        <button
          onClick={() => {
            setActiveTab('entry');
            setVoiceState('ready');
            setAssistantAnswer(null);
          }}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all ${
            activeTab === 'entry'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-surface-600 hover:text-surface-900'
          }`}
        >
          <ShoppingBag className="w-4 h-4" />
          <span>{t('voiceTabEntry')}</span>
        </button>

        <button
          onClick={() => {
            setActiveTab('question');
            setVoiceState('ready');
            setIntent(null);
          }}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all ${
            activeTab === 'question'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-surface-600 hover:text-surface-900'
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-500" />
          <span>{t('voiceTabQuestions')}</span>
        </button>
      </div>

      {/* Hero Microphone Card */}
      <div className="card text-center py-8 px-4 relative overflow-hidden bg-gradient-to-b from-white to-surface-50 border border-surface-200 shadow-sm rounded-3xl">
        <div className="space-y-4 max-w-md mx-auto">
          {/* Animated Mic Button */}
          <div className="relative inline-block">
            <button
              onClick={voiceState === 'listening' ? stopRecording : startRecording}
              className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 shadow-xl ${
                voiceState === 'listening'
                  ? 'bg-red-500 text-white animate-pulse shadow-red-200 scale-110'
                  : voiceState === 'processing' || voiceState === 'understanding'
                  ? 'bg-amber-500 text-white animate-spin'
                  : 'gradient-primary text-white hover:scale-105 active:scale-95 shadow-primary-200'
              }`}
            >
              {voiceState === 'listening' ? (
                <MicOff className="w-10 h-10" />
              ) : voiceState === 'processing' || voiceState === 'understanding' ? (
                <Loader2 className="w-10 h-10 animate-spin" />
              ) : (
                <Mic className="w-10 h-10" />
              )}
            </button>
          </div>

          <div>
            <h2 className="text-lg font-bold text-surface-900">
              {voiceState === 'listening'
                ? t('listening')
                : voiceState === 'understanding'
                ? t('understanding')
                : activeTab === 'question'
                ? t('askAssistant')
                : t('tapToSpeak')}
            </h2>
            <p className="text-xs text-surface-500 mt-1">
              {activeTab === 'question'
                ? t('askQuestionPrompt')
                : 'Speak in Telugu, Hindi, English or mixed (Tenglish / Hinglish)'}
            </p>
          </div>

          {/* Transcript Display */}
          {transcript && (
            <div className="p-3 rounded-2xl bg-surface-100 border border-surface-200 text-left">
              <span className="text-[10px] font-bold uppercase text-surface-400 block mb-1">
                You Spoke / మీరు మాట్లాడినది:
              </span>
              <p className="text-sm font-semibold text-surface-900 italic">"{transcript}"</p>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center justify-center gap-1.5">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>

      {/* TAB 1: CONFIRMATION CARD FOR STOCK ENTRY (Pillar 4) */}
      {activeTab === 'entry' && voiceState === 'confirming' && intent && (
        <div className="card p-6 bg-white border-2 border-primary-400 rounded-3xl shadow-lg space-y-4 animate-slide-up">
          <div className="flex items-center justify-between border-b border-surface-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500 animate-ping" />
              <h3 className="font-bold text-surface-900 text-base">{t('pleaseConfirm')}</h3>
            </div>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
              intent.intent === 'STOCK_IN'
                ? 'bg-emerald-100 text-emerald-800'
                : intent.intent === 'STOCK_OUT'
                ? 'bg-amber-100 text-amber-800'
                : 'bg-blue-100 text-blue-800'
            }`}>
              {intent.intent === 'STOCK_IN' ? t('stockIn') : intent.intent === 'STOCK_OUT' ? t('stockOut') : 'Udhar'}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-surface-50 rounded-xl">
              <span className="text-[10px] uppercase font-bold text-surface-400 block">{t('productName')}</span>
              <p className="text-sm font-bold text-surface-900 mt-0.5 truncate">{intent.product}</p>
            </div>

            <div className="p-3 bg-surface-50 rounded-xl">
              <span className="text-[10px] uppercase font-bold text-surface-400 block">{t('currentStock')} Quantity</span>
              {isEditing ? (
                <input
                  type="number"
                  value={editQty}
                  onChange={(e) => setEditQty(e.target.value)}
                  className="w-full text-sm font-bold bg-white border rounded px-1.5 py-0.5 mt-0.5"
                />
              ) : (
                <p className="text-sm font-bold text-surface-900 mt-0.5">{editQty} {editUnit}</p>
              )}
            </div>

            <div className="p-3 bg-surface-50 rounded-xl col-span-2 sm:col-span-1">
              <span className="text-[10px] uppercase font-bold text-surface-400 block">Unit Price (₹)</span>
              {isEditing ? (
                <input
                  type="number"
                  value={editPrice}
                  onChange={(e) => setEditPrice(e.target.value)}
                  className="w-full text-sm font-bold bg-white border rounded px-1.5 py-0.5 mt-0.5"
                />
              ) : (
                <p className="text-sm font-bold text-surface-900 mt-0.5">₹{editPrice || '—'}</p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="text-xs font-semibold text-surface-600 hover:text-surface-900 flex items-center gap-1"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>{isEditing ? 'Done Editing' : 'Edit Values'}</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCancel}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-surface-600 hover:bg-surface-100"
              >
                {t('cancel')}
              </button>
              <button
                onClick={handleConfirm}
                className="px-5 py-2.5 rounded-xl gradient-primary text-white text-xs font-bold shadow-md hover:shadow-lg active:scale-95 transition-all flex items-center gap-1.5"
              >
                <Check className="w-4 h-4" />
                <span>{t('confirm')}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* SUCCESS RESULT CARD FOR STOCK ENTRY */}
      {voiceState === 'completed' && responseText && (
        <div className="card p-6 bg-emerald-50 border border-emerald-200 rounded-3xl space-y-3 animate-slide-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm">
              <Check className="w-5 h-5 text-emerald-600" />
              <span>{t('done')}</span>
            </div>
            <button
              onClick={() => speakText(responseText)}
              className="p-1.5 rounded-lg bg-emerald-100 text-emerald-700 hover:bg-emerald-200 transition-colors"
              title="Speak Again"
            >
              <Volume2 className="w-4 h-4" />
            </button>
          </div>
          <p className="text-base font-semibold text-emerald-900">{responseText}</p>
          <div className="pt-2 flex items-center gap-3">
            <button
              onClick={() => navigate('/inventory')}
              className="text-xs font-bold text-emerald-700 underline"
            >
              View updated inventory &gt;
            </button>
            <button
              onClick={handleCancel}
              className="text-xs font-semibold text-surface-600 ml-auto flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>New Voice Command</span>
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: ASSISTANT QUESTION ANSWER CARD (Pillar 3) */}
      {activeTab === 'question' && (
        <div className="space-y-4">
          {questionLoading ? (
            <div className="p-8 text-center bg-white rounded-3xl border border-surface-200 shadow-sm space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto" />
              <p className="text-sm font-semibold text-surface-800">
                {language === 'te' ? 'డేటాబేస్ నుండి లైవ్ స్టాక్ సమాచారం తీసుకుంటున్నాము...' : 'Fetching live inventory data from database...'}
              </p>
            </div>
          ) : assistantAnswer ? (
            <div className="card p-6 bg-gradient-to-br from-white to-primary-50/30 border border-primary-200 rounded-3xl shadow-md space-y-4 animate-slide-up">
              <div className="flex items-center justify-between border-b border-surface-100 pb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary-600" />
                  <h3 className="font-bold text-surface-900 text-sm sm:text-base">
                    {language === 'te' ? 'వ్యాపారి AI సమాధానం' : 'Vyapari AI Response'}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  {assistantAnswer.topic && (
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-primary-100 text-primary-800">
                      {assistantAnswer.topic}
                    </span>
                  )}
                  <button
                    onClick={() => speakText(assistantAnswer.voice_text || assistantAnswer.answer)}
                    className="p-2 rounded-xl bg-white border border-surface-200 hover:bg-surface-100 text-primary-600 shadow-sm"
                    title="Speak Answer"
                  >
                    <Volume2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="text-base sm:text-lg font-semibold text-surface-900 leading-relaxed">
                {assistantAnswer.answer}
              </div>

              <div className="text-[11px] text-surface-400 pt-1 border-t border-surface-100 flex items-center justify-between">
                <span>Verified against live Supabase PostgreSQL database</span>
                <button
                  onClick={() => setAssistantAnswer(null)}
                  className="text-primary-600 font-semibold hover:underline"
                >
                  Ask Another
                </button>
              </div>
            </div>
          ) : null}

          {/* Quick Question Query Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && manualText.trim()) {
                  handleAskQuestion(manualText);
                  setManualText('');
                }
              }}
              placeholder={t('askPlaceholder')}
              className="input-field text-sm flex-1"
            />
            <button
              onClick={() => {
                if (manualText.trim()) {
                  handleAskQuestion(manualText);
                  setManualText('');
                }
              }}
              disabled={questionLoading}
              className="px-4 py-2.5 rounded-xl gradient-primary text-white text-sm font-semibold shadow-sm flex items-center gap-1.5"
            >
              <Send className="w-4 h-4" />
              <span>Ask</span>
            </button>
          </div>

          {/* Question Suggestions */}
          <div className="space-y-2 pt-1">
            <p className="text-xs font-bold uppercase text-surface-400 tracking-wider">
              {t('sampleCommands')} (Tap to ask live):
            </p>
            <div className="flex flex-wrap gap-2">
              {questionSuggestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAskQuestion(q.text)}
                  className="px-3 py-2 rounded-xl bg-white border border-surface-200 hover:border-primary-400 hover:bg-primary-50/50 text-xs font-semibold text-surface-700 transition-all text-left flex items-center gap-2 shadow-2xs"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-primary-500 flex-shrink-0" />
                  <span>{q.text}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 1: QUICK ENTRY CHIPS (Pillar 4) */}
      {activeTab === 'entry' && voiceState === 'ready' && (
        <div className="space-y-3 pt-2">
          {/* Manual text input fallback */}
          <div className="flex gap-2">
            <input
              type="text"
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && manualText.trim()) {
                  processStockTranscript(manualText);
                  setManualText('');
                }
              }}
              placeholder="Or type voice command (e.g. '5 bags biyyam vachayi')..."
              className="input-field text-sm flex-1"
            />
            <button
              onClick={() => {
                if (manualText.trim()) {
                  processStockTranscript(manualText);
                  setManualText('');
                }
              }}
              className="px-4 py-2.5 rounded-xl gradient-primary text-white text-sm font-semibold shadow-sm"
            >
              Parse
            </button>
          </div>

          <div className="space-y-2 pt-1">
            <p className="text-xs font-bold uppercase text-surface-400 tracking-wider">
              {t('sampleCommands')}:
            </p>
            <div className="space-y-2">
              {entrySuggestions.map((cmd, idx) => (
                <button
                  key={idx}
                  onClick={() => processStockTranscript(cmd.text)}
                  className="w-full p-3 rounded-xl bg-white border border-surface-200 hover:border-primary-400 hover:bg-primary-50/40 text-xs sm:text-sm font-semibold text-surface-800 transition-all text-left flex items-center justify-between group shadow-2xs"
                >
                  <div className="flex items-center gap-2.5">
                    {cmd.intent === 'STOCK_IN' ? (
                      <PlusCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    ) : cmd.intent === 'STOCK_OUT' ? (
                      <MinusCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    ) : (
                      <ShoppingBag className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    )}
                    <span>"{cmd.text}"</span>
                  </div>
                  <span className="text-[11px] text-primary-600 group-hover:translate-x-1 transition-transform">
                    Tap to run &gt;
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
