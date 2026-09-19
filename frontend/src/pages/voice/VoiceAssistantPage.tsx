import { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Mic,
  MicOff,
  ArrowLeft,
  Loader2,
  Check,
  Edit3,
  Send,
  Sparkles,
  HelpCircle,
  AlertCircle,
  ShoppingBag,
  CheckCircle2,
  XCircle,
  ArrowRight,
  User,
  Package,
  CreditCard,
  Layers,
  Volume2
} from 'lucide-react';
import { voiceService, productsService, customersService } from '../../services/api';
import { useLanguage } from '../../context/LanguageContext';
import LanguageSwitcher from '../../components/LanguageSwitcher';
import type { VoiceState, VoiceIntent, Product, Customer } from '../../types';

interface ChatTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: VoiceIntent | null;
  actionExecuted?: boolean;
  actionResult?: string;
  clarificationCandidates?: string[];
}

export default function VoiceAssistantPage() {
  const navigate = useNavigate();
  const { t, language } = useLanguage();

  const [conversationId] = useState<string>(() => `conv-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`);
  const [voiceState, setVoiceState] = useState<VoiceState>('ready');
  const [transcript, setTranscript] = useState('');
  const [manualText, setManualText] = useState('');
  const [activeIntent, setActiveIntent] = useState<VoiceIntent | null>(null);
  const [error, setError] = useState('');
  const [executingAction, setExecutingAction] = useState(false);

  // Edit fields for in-stream confirmation
  const [editQty, setEditQty] = useState('');
  const [editUnit, setEditUnit] = useState('');
  const [editPrice, setEditPrice] = useState('');
  const [editCustomer, setEditCustomer] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // Cached shop catalog for reference
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);

  // Conversational Stream
  const [chatMessages, setChatMessages] = useState<ChatTurn[]>([
    {
      id: 'welcome-msg',
      role: 'assistant',
      content: language === 'te'
        ? 'నమస్కారం! నేను మీ వ్యాపారి వాయిస్ అసిస్టెంట్. బియ్యం స్టాక్, అమ్మకాలు, వచ్చే వారానికి సరిపోతుందా లేదా అప్పుల వివరాలు ఏదైనా అడగవచ్చు లేదా వాయిస్ తో స్టాక్, ఉధార్ రికార్డ్ చేయవచ్చు.'
        : language === 'hi'
        ? 'नमस्ते! मैं आपका व्यापारी वॉयस सहायक हूँ। आप स्टॉक, उधारी, बिक्री या किसी भी Kirana कार्य के लिए बोल सकते हैं।'
        : 'Welcome to Vyapari Voice! Speak naturally in Telugu, Hindi, or English to check stock, projection, customer udhar, or record sales and inventory.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const chatBottomRef = useRef<HTMLDivElement | null>(null);

  // Load shop products and customers on mount
  useEffect(() => {
    productsService.getAll().then(res => {
      if (res.success && res.data) {
        const list = (res.data as { items: Product[] }).items || (res.data as Product[]);
        setProducts(list);
      }
    }).catch(() => {});

    customersService.getAll().then(res => {
      if (res.success && res.data) {
        const list = (res.data as { items: Customer[] }).items || (res.data as Customer[]);
        setCustomers(list);
      }
    }).catch(() => {});
  }, []);

  // Scroll chat into view on updates
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, voiceState]);

  // Language-aware Text-to-Speech
  const speakText = useCallback((text: string, langCode?: string) => {
    if ('speechSynthesis' in window && text) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      // Map detected language
      if (langCode === 'te' || (!langCode && language === 'te')) {
        utterance.lang = 'te-IN';
      } else if (langCode === 'hi' || (!langCode && language === 'hi')) {
        utterance.lang = 'hi-IN';
      } else {
        utterance.lang = 'en-IN';
      }
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  }, [language]);

  // ---- UNIFIED VOICE PIPELINE ----
  // Step 1: Process text transcript (either from audio STT or typed input)
  const processTranscript = async (queryText: string) => {
    if (!queryText.trim()) return;
    setVoiceState('understanding');
    setError('');

    const userTurn: ChatTurn = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const updatedHistory = [...chatMessages, userTurn];
    setChatMessages(updatedHistory);

    try {
      // Format history for context preservation (send last 6 turns)
      const apiHistory = updatedHistory.slice(-6).map(m => ({
        role: m.role,
        content: m.content
      }));

      const res = await voiceService.interpret({
        transcript: queryText,
        conversation_history: apiHistory,
        language,
        conversation_id: conversationId
      });

      if (!res.success || !res.data) {
        throw new Error(res.error?.message || 'Failed to interpret speech');
      }

      const intentData = res.data as VoiceIntent;
      setActiveIntent(intentData);

      // Pre-fill editable confirmation fields
      setEditQty(intentData.quantity ? String(intentData.quantity) : '1');
      setEditUnit(intentData.unit || 'unit');
      setEditPrice(intentData.price ? String(intentData.price) : '0');
      setEditCustomer(intentData.customer_name || '');
      setIsEditing(false);

      if (intentData.clarification_needed) {
        // Ambiguity: Ask clarification without mutating
        setVoiceState('ready');
        const clarifyTurn: ChatTurn = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: intentData.confirmation_prompt || "I found multiple matching items. Please choose one:",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          clarificationCandidates: intentData.ambiguous_candidates
        };
        setChatMessages(prev => [...prev, clarifyTurn]);
        speakText(clarifyTurn.content, intentData.language);

      } else if (intentData.confirmation_required) {
        // Mutating action requiring confirmation
        setVoiceState('confirming');
        const confirmTurn: ChatTurn = {
          id: `asst-confirm-${Date.now()}`,
          role: 'assistant',
          content: intentData.confirmation_prompt || `Should I record this ${intentData.intent}?`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          intent: intentData
        };
        setChatMessages(prev => [...prev, confirmTurn]);
        speakText(confirmTurn.content, intentData.language);

      } else {
        // Direct answer for informational inquiries (STOCK_CHECK, CREDIT_CHECK, etc.)
        setVoiceState('completed');
        const answerText = intentData.answer || intentData.voice_text || 'Completed.';
        const answerTurn: ChatTurn = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: answerText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, answerTurn]);
        speakText(intentData.voice_text || answerText, intentData.language);

        // Save conversation log
        voiceService.saveConversation({
          conversation_id: conversationId,
          speaker: 'assistant',
          transcript: queryText,
          response_text: answerText,
          language: intentData.language || language,
          intent: intentData.intent,
          confidence: intentData.confidence || 0.95,
          confirmation_status: 'CONFIRMED'
        }).catch(() => {});
      }

    } catch (err: any) {
      setError(err?.message || 'Failed to understand voice command');
      setVoiceState('error');
    }
  };

  // Step 2: Execute Confirmed Action
  const handleConfirmAction = async (targetIntent: VoiceIntent) => {
    setExecutingAction(true);
    setVoiceState('executing');
    setError('');

    try {
      const finalQty = Number(editQty) || targetIntent.quantity || 1;
      const finalUnit = editUnit || targetIntent.unit || 'unit';
      const finalPrice = Number(editPrice) || targetIntent.price || 0;
      const finalCustomer = editCustomer || targetIntent.customer_name;
      const finalAmount = targetIntent.amount || (finalQty * finalPrice);

      const payload = {
        intent: targetIntent.intent,
        product_id: targetIntent.product_id,
        customer_id: targetIntent.customer_id,
        customer_name: finalCustomer,
        phone: targetIntent.phone,
        supplier_id: targetIntent.supplier_id,
        quantity: finalQty,
        unit: finalUnit,
        price: finalPrice,
        amount: finalAmount,
        notes: `Voice verified: ${targetIntent.transcript || transcript}`,
        conversation_id: conversationId,
        transcript: targetIntent.transcript || transcript
      };

      const res = await voiceService.execute(payload);
      if (!res.success || !res.data) {
        throw new Error(res.error?.message || 'Failed to execute database action');
      }

      const resData = res.data as { message: string; transaction_id?: string };
      setVoiceState('completed');

      // Update message stream with execution success
      const successTurn: ChatTurn = {
        id: `asst-success-${Date.now()}`,
        role: 'assistant',
        content: resData.message || 'Action executed successfully in database!',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actionExecuted: true,
        actionResult: resData.message
      };

      setChatMessages(prev => [...prev, successTurn]);
      speakText(resData.message, targetIntent.language);
      setActiveIntent(null);

    } catch (err: any) {
      setError(err?.message || 'Database execution failed');
      setVoiceState('error');
    } finally {
      setExecutingAction(false);
    }
  };

  // Step 3: Cancel Action
  const handleCancelAction = () => {
    setActiveIntent(null);
    setVoiceState('ready');
    const cancelMsg: ChatTurn = {
      id: `asst-cancel-${Date.now()}`,
      role: 'assistant',
      content: language === 'te' ? 'సరే, ఏ చర్య చేపట్టబడలేదు.' : 'Action cancelled. Nothing was modified in database.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatMessages(prev => [...prev, cancelMsg]);
    speakText(cancelMsg.content);
  };

  // Step 4: Microphone Recording via MediaRecorder (Primary Multilingual STT Pipeline)
  const startRecording = useCallback(async () => {
    setError('');
    setTranscript('');
    setActiveIntent(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        if (audioBlob.size < 500) {
          setVoiceState('ready');
          setError("Audio was too short. Please hold or click mic, speak clearly, then finish.");
          return;
        }

        setVoiceState('processing');
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
          const res = await voiceService.transcribeAudio(formData);
          if (res.success && res.data) {
            const spokenText = (res.data as { transcript: string }).transcript;
            setTranscript(spokenText);
            await processTranscript(spokenText);
          } else {
            throw new Error(res.error?.message || "I couldn't understand the audio. Please try speaking again.");
          }
        } catch (sttErr: any) {
          setError(sttErr?.message || "Voice recognition error. Please try again.");
          setVoiceState('error');
        }
      };

      mediaRecorder.start();
      setVoiceState('listening');
    } catch {
      setError("Microphone access blocked or not supported in browser. Please check microphone permissions.");
      setVoiceState('error');
    }
  }, [language, chatMessages]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setVoiceState('processing');
    }
  }, []);

  // Helper for user-friendly action labels
  const getIntentLabel = (intent: string) => {
    switch (intent) {
      case 'BORROW_OUT': return 'Record Loan / Udhar Given';
      case 'BORROW_RETURN': return 'Record Udhar Repayment';
      case 'BORROW_CLEAR': return 'Clear / Settle Full Loan';
      case 'STOCK_IN': return 'Add Stock (Stock In)';
      case 'STOCK_OUT': return 'Deduct Stock (Sale)';
      case 'STOCK_ADJUST': return 'Adjust Stock Count';
      case 'CUSTOMER_ADD': return 'Add New Customer Profile';
      case 'PRODUCT_ADD': return 'Add New Product to Inventory';
      default: return `Confirm ${intent.replace(/_/g, ' ')}`;
    }
  };

  // Quick Kirana query suggestions
  const quickSuggestions = [
    { label: 'one person Kiran has taken a loan of 500', query: 'one person Kiran has taken a loan of 500' },
    { label: 'How much loan does Kiran have?', query: 'How much loan does Kiran have?' },
    { label: 'Clear loan of Kiran', query: 'Clear loan of Kiran' },
    { label: 'రైస్ స్టాక్ ఎంత ఉంది?', query: 'రైస్ స్టాక్ ఎంత ఉంది?' },
    { label: 'Ramesh ki 500 udhar rasi pettu', query: 'Ramesh ki 500 udhar rasi pettu' },
    { label: '5 bags biyyam add cheyyi', query: '5 bags biyyam add cheyyi 1450 rupees' },
    { label: 'Ramesh 200 paid chesadu', query: 'Ramesh 200 paid chesadu' },
    { label: 'Next week ki saripothunda?', query: 'Next week ki saripothunda?' },
  ];

  return (
    <div className="page-container pt-3 space-y-4 animate-fade-in max-w-4xl mx-auto pb-16">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-surface-200">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
            <ArrowLeft className="w-5 h-5 text-surface-600" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-600 animate-pulse" />
              <span>{t('appName')} Assistant</span>
            </h2>
            <p className="text-xs text-surface-500">
              {products.length > 0 ? `${products.length} products • ${customers.length} customers • Live DB` : 'Unified Voice AI • Telugu, Hindi & English'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
        </div>
      </div>

      {/* Primary Unified Microphone Controller */}
      <div className="card p-5 text-center flex flex-col items-center justify-center space-y-3 bg-gradient-to-b from-white to-surface-50/50 shadow-xs border border-surface-200">
        <div className="relative">
          {voiceState === 'listening' && (
            <div className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-60 pointer-events-none scale-125" />
          )}

          <button
            onClick={voiceState === 'listening' ? stopRecording : startRecording}
            disabled={voiceState === 'processing' || voiceState === 'understanding' || voiceState === 'executing'}
            className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition-all active:scale-95 disabled:opacity-60 ${
              voiceState === 'listening'
                ? 'bg-red-500 text-white ring-4 ring-red-300 animate-pulse'
                : voiceState === 'processing' || voiceState === 'understanding' || voiceState === 'executing'
                ? 'bg-amber-500 text-white'
                : voiceState === 'confirming'
                ? 'bg-primary-600 text-white'
                : voiceState === 'completed'
                ? 'bg-emerald-500 text-white'
                : 'gradient-primary text-white hover:opacity-95 ring-4 ring-primary-100'
            }`}
            title="Tap to speak in Telugu, Hindi or English"
          >
            {voiceState === 'listening' ? (
              <MicOff className="w-9 h-9" />
            ) : voiceState === 'processing' || voiceState === 'understanding' || voiceState === 'executing' ? (
              <Loader2 className="w-9 h-9 animate-spin" />
            ) : voiceState === 'completed' ? (
              <Check className="w-9 h-9" />
            ) : (
              <Mic className="w-9 h-9" />
            )}
          </button>
        </div>

        {/* State Label */}
        <div className="space-y-0.5">
          <p className="text-sm font-bold text-surface-800">
            {voiceState === 'listening' && 'Listening... Speak in Telugu, Hindi, or English'}
            {voiceState === 'processing' && 'Transcribing spoken audio with Gemini AI...'}
            {voiceState === 'understanding' && 'Analyzing Kirana intent & database facts...'}
            {voiceState === 'confirming' && 'Review & Confirm Action below'}
            {voiceState === 'executing' && 'Executing update in Supabase PostgreSQL...'}
            {voiceState === 'completed' && 'Action completed successfully!'}
            {voiceState === 'ready' && 'Tap mic to speak (Telugu / Hindi / English)'}
            {voiceState === 'error' && 'Voice processing error. Tap mic to retry'}
          </p>
          <p className="text-xs text-surface-400">
            {voiceState === 'listening'
              ? 'Click again when done speaking'
              : 'Works with Kirana terms: biyyam, chakkera, nune, udhar, saripothunda'}
          </p>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 animate-shake">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Interactive Unified Conversation Stream */}
      <div className="card p-4 min-h-[380px] max-h-[500px] overflow-y-auto space-y-4 bg-surface-50/40 border-surface-200 shadow-xs">
        {chatMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-1 animate-fade-in`}
          >
            <div
              className={`max-w-[90%] sm:max-w-[80%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white rounded-br-xs'
                  : 'bg-white text-surface-900 border border-surface-200 rounded-bl-xs'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => speakText(msg.content)}
                    className="text-surface-400 hover:text-primary-600 p-1 flex-shrink-0"
                    title="Read aloud"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Clarification / Disambiguation Options (Pillar 5) */}
              {msg.clarificationCandidates && msg.clarificationCandidates.length > 0 && (
                <div className="mt-3 pt-3 border-t border-surface-100 space-y-2">
                  <p className="text-xs font-semibold text-amber-800">Select the intended option:</p>
                  <div className="flex flex-wrap gap-2">
                    {msg.clarificationCandidates.map((cand, idx) => (
                      <button
                        key={idx}
                        onClick={() => processTranscript(cand)}
                        className="px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 hover:bg-amber-100 text-xs font-semibold text-amber-900 transition-all flex items-center gap-1.5"
                      >
                        <span>{cand}</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* In-Stream Confirmation Card (Pillar 2 & 11) */}
              {msg.intent && !msg.actionExecuted && activeIntent && (
                <div className="mt-3.5 p-4 rounded-xl bg-amber-50/90 border-2 border-amber-300 text-surface-900 space-y-3 animate-scale-up">
                  <div className="flex items-center justify-between pb-2 border-b border-amber-200/80 gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <ShoppingBag className="w-4 h-4 text-amber-700 flex-shrink-0" />
                      <span className="font-bold text-xs uppercase tracking-wide text-amber-900">
                        {getIntentLabel(activeIntent.intent)}
                      </span>
                      {activeIntent.is_new_customer && (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-100 border border-emerald-300 text-emerald-800 text-[10px] font-bold flex items-center gap-1 shadow-2xs">
                          <Sparkles className="w-3 h-3 text-emerald-600" />
                          <span>✨ New Udhar Account (Auto-Create)</span>
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => setIsEditing(!isEditing)}
                      className="text-xs font-semibold text-primary-700 hover:underline flex items-center gap-1"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>{isEditing ? 'Done Editing' : 'Edit Values'}</span>
                    </button>
                  </div>

                  {/* Editable Details Form */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {activeIntent.product_name && (
                      <div className="p-2.5 rounded-lg bg-white border border-amber-200">
                        <span className="text-[10px] text-surface-500 uppercase font-bold flex items-center gap-1">
                          <Package className="w-3 h-3" /> Product
                        </span>
                        <p className="font-bold text-surface-900 mt-0.5 truncate">{activeIntent.product_name}</p>
                      </div>
                    )}

                    {(activeIntent.customer_name || activeIntent.intent.includes('BORROW') || activeIntent.intent === 'CUSTOMER_ADD') && (
                      <div className="p-2.5 rounded-lg bg-white border border-amber-200">
                        <span className="text-[10px] text-surface-500 uppercase font-bold flex items-center gap-1">
                          <User className="w-3 h-3" /> Customer {activeIntent.is_new_customer ? '(New)' : ''}
                        </span>
                        {isEditing ? (
                          <input
                            type="text"
                            value={editCustomer}
                            onChange={(e) => setEditCustomer(e.target.value)}
                            className="w-full mt-1 px-2 py-1 text-xs border rounded bg-white"
                          />
                        ) : (
                          <div>
                            <p className="font-bold text-surface-900 mt-0.5">{editCustomer || activeIntent.customer_name || 'Customer'}</p>
                            {activeIntent.phone && (
                              <p className="text-[10px] text-surface-500 mt-0.5">Phone: {activeIntent.phone}</p>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {activeIntent.intent === 'BORROW_CLEAR' ? (
                      <div className="col-span-2 p-2.5 rounded-lg bg-white border border-emerald-200">
                        <span className="text-[10px] text-emerald-700 uppercase font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Action Summary
                        </span>
                        <p className="font-bold text-emerald-800 mt-0.5">Settle all active borrowings & reset loan balance to ₹0</p>
                      </div>
                    ) : (
                      <>
                        {(activeIntent.quantity || activeIntent.intent === 'STOCK_ADJUST') && (
                          <div className="p-2.5 rounded-lg bg-white border border-amber-200">
                            <span className="text-[10px] text-surface-500 uppercase font-bold flex items-center gap-1">
                              <Layers className="w-3 h-3" /> {activeIntent.intent === 'STOCK_ADJUST' ? 'Set Stock To' : 'Quantity'}
                            </span>
                            {isEditing ? (
                              <div className="flex gap-1 mt-1">
                                <input
                                  type="number"
                                  value={editQty}
                                  onChange={(e) => setEditQty(e.target.value)}
                                  className="w-16 px-2 py-1 text-xs border rounded bg-white"
                                />
                                <input
                                  type="text"
                                  value={editUnit}
                                  onChange={(e) => setEditUnit(e.target.value)}
                                  className="w-16 px-2 py-1 text-xs border rounded bg-white"
                                />
                              </div>
                            ) : (
                              <p className="font-bold text-surface-900 mt-0.5">{editQty} {editUnit}</p>
                            )}
                          </div>
                        )}

                        {(activeIntent.amount || activeIntent.price || activeIntent.intent.includes('BORROW')) && (
                          <div className="p-2.5 rounded-lg bg-white border border-amber-200">
                            <span className="text-[10px] text-surface-500 uppercase font-bold flex items-center gap-1">
                              <CreditCard className="w-3 h-3" /> Amount / Loan
                            </span>
                            {isEditing ? (
                              <input
                                type="number"
                                value={editPrice}
                                onChange={(e) => setEditPrice(e.target.value)}
                                className="w-full mt-1 px-2 py-1 text-xs border rounded bg-white"
                              />
                            ) : (
                              <p className="font-bold text-surface-900 mt-0.5">₹{editPrice || activeIntent.amount || activeIntent.price || 0}</p>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {/* Confirmation Action Buttons */}
                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={() => handleConfirmAction(activeIntent)}
                      disabled={executingAction}
                      className="flex-1 py-2.5 rounded-lg gradient-primary text-white text-xs font-bold shadow-xs flex items-center justify-center gap-1.5 hover:opacity-95 disabled:opacity-50"
                    >
                      {executingAction ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Confirm & Record in Database</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleCancelAction}
                      disabled={executingAction}
                      className="px-4 py-2.5 rounded-lg bg-white border border-surface-300 text-surface-700 text-xs font-semibold hover:bg-surface-100 flex items-center gap-1"
                    >
                      <XCircle className="w-3.5 h-3.5 text-surface-500" />
                      <span>Cancel</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Action Executed Banner */}
              {msg.actionExecuted && (
                <div className="mt-2.5 p-2 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-xs font-bold text-emerald-800">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>{msg.actionResult || 'Database updated successfully!'}</span>
                </div>
              )}
            </div>
            <span className="text-[10px] text-surface-400 px-1">{msg.timestamp}</span>
          </div>
        ))}

        {voiceState === 'understanding' && (
          <div className="flex items-center gap-2 p-3 bg-white rounded-2xl border border-surface-200 max-w-[220px] animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
            <span className="text-xs text-surface-500 font-medium">Checking live Kirana DB...</span>
          </div>
        )}
        <div ref={chatBottomRef} />
      </div>

      {/* Input Query Bar */}
      <div className="flex gap-2">
        <input
          type="text"
          value={manualText}
          onChange={(e) => setManualText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && manualText.trim()) {
              processTranscript(manualText);
              setManualText('');
            }
          }}
          placeholder="Ask or type command (e.g. 'Rice stock entha?', 'Ramesh ki 500 udhar rasi pettu')..."
          className="input-field text-sm flex-1 bg-white"
        />
        <button
          onClick={() => {
            if (manualText.trim()) {
              processTranscript(manualText);
              setManualText('');
            }
          }}
          disabled={voiceState === 'processing' || voiceState === 'understanding'}
          className="px-4 py-2.5 rounded-xl gradient-primary text-white text-sm font-semibold shadow-sm flex items-center gap-1.5 hover:opacity-95 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </div>

      {/* Quick Suggestions Chips */}
      <div className="space-y-1.5 pt-1">
        <p className="text-xs font-bold uppercase text-surface-400 tracking-wider">
          Suggested Commands (Tap to test):
        </p>
        <div className="flex flex-wrap gap-2">
          {quickSuggestions.map((item, idx) => (
            <button
              key={idx}
              onClick={() => processTranscript(item.query)}
              className="px-3 py-2 rounded-xl bg-white border border-surface-200 hover:border-primary-400 hover:bg-primary-50/50 text-xs font-semibold text-surface-700 transition-all text-left flex items-center gap-1.5 shadow-2xs"
            >
              <HelpCircle className="w-3.5 h-3.5 text-primary-500 flex-shrink-0" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
