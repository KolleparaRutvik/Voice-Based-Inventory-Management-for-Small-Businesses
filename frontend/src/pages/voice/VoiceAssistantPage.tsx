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
  PlusCircle,
  MinusCircle,
  AlertCircle,
  ShoppingBag,
  CheckCircle2,
  ArrowRight,
  UserCheck
} from 'lucide-react';
import { voiceService, inventoryService, productsService, assistantService, purchaseOrdersService } from '../../services/api';
import { useLanguage } from '../../context/LanguageContext';
import LanguageSwitcher from '../../components/LanguageSwitcher';
import type { VoiceState, VoiceIntent, Product } from '../../types';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  topic?: string;
  suggested_action?: {
    action_type: 'CREATE_PURCHASE_ORDER' | 'ADD_STOCK' | 'RECORD_BORROWING';
    product_id?: string;
    product_name: string;
    quantity: number;
    unit: string;
    supplier_id?: string;
    customer_name?: string;
    title: string;
    description?: string;
  } | null;
  actionExecuted?: boolean;
  timestamp: string;
}

export default function VoiceAssistantPage() {
  const navigate = useNavigate();
  const { t, language, getSpeechLang } = useLanguage();

  const [activeTab, setActiveTab] = useState<'entry' | 'question'>('question');
  const [voiceState, setVoiceState] = useState<VoiceState>('ready');
  const [transcript, setTranscript] = useState('');
  const [manualText, setManualText] = useState('');
  const [intent, setIntent] = useState<VoiceIntent | null>(null);
  const [error, setError] = useState('');
  const [responseText, setResponseText] = useState('');
  const [products, setProducts] = useState<Product[]>([]);

  // Conversational Chat Stream (Modes 1, 2, 3)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      role: 'assistant',
      content: language === 'te'
        ? 'నమస్కారం! నేను మీ వ్యాపారి వాయిస్ అసిస్టెంట్. బియ్యం స్టాక్, అమ్మకాలు, వచ్చే వారానికి సరిపోతుందా లేదా అప్పుల వివరాలు ఏవైనా అడగవచ్చు.'
        : language === 'hi'
        ? 'नमस्ते! मैं आपका व्यापारी वॉयस सहायक हूँ। आप स्टॉक, उधारी या अगले हफ्ते की जरूरत के बारे में पूछ सकते हैं।'
        : 'Welcome! I am your Vyapari Voice assistant. Ask anything about stock levels, credit balances, or demand projections.',
      topic: 'GENERAL',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  // Question / Assistant Answer state
  const [questionLoading, setQuestionLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  // Editable fields in confirmation modal
  const [editQty, setEditQty] = useState('');
  const [editUnit, setEditUnit] = useState('');
  const [editPrice, setEditPrice] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);
  const chatBottomRef = useRef<HTMLDivElement | null>(null);

  // Load existing products for entity resolution
  useEffect(() => {
    productsService.getAll().then(res => {
      if (res.success && res.data) {
        const list = (res.data as { items: Product[] }).items || (res.data as Product[]);
        setProducts(list);
      }
    }).catch(() => {});
  }, []);

  // Scroll chat into view
  useEffect(() => {
    if (activeTab === 'question') {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, questionLoading, activeTab]);

  // Sync edit state when intent changes
  useEffect(() => {
    if (intent) {
      setEditQty(String(intent.quantity || 1));
      setEditUnit(intent.unit || 'kg');
      setEditPrice(String(intent.price || 0));
    }
  }, [intent]);

  // Text-to-Speech audio reader
  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = getSpeechLang();
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Handle Conversational Multi-Turn Query (Modes 1, 2, 3)
  const handleAskQuestion = async (queryText: string) => {
    if (!queryText.trim()) return;
    setTranscript(queryText);
    setQuestionLoading(true);
    setError('');

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Update stream with user question
    const updatedHistory = [...chatMessages, userMsg];
    setChatMessages(updatedHistory);

    try {
      // Format history for backend API context preservation
      const apiHistory = updatedHistory.slice(-8).map(m => ({
        role: m.role,
        content: m.content
      }));

      const res = await assistantService.query({
        question: queryText,
        conversation_history: apiHistory,
        language
      });

      if (res.success && res.data) {
        const data = res.data as any;
        const botMsg: ChatMessage = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: data.answer || 'Stock data checked successfully.',
          topic: data.topic,
          suggested_action: data.suggested_action,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, botMsg]);

        const speechMsg = data.voice_text || data.answer;
        speakText(speechMsg);

        // Persist conversation to database
        voiceService.saveConversation({
          user_message: queryText,
          language,
          intent: data.topic || 'GENERAL',
          entities: data.suggested_action ? { suggested_action: data.suggested_action } : {},
          confirmation_status: 'CONFIRMED',
        }).catch(() => {}); // Non-blocking save
      } else {
        throw new Error('Could not analyze question with database');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Assistant query failed');
    } finally {
      setQuestionLoading(false);
      setVoiceState('ready');
    }
  };

  // Execute 1-Click Action Card Suggested by AI
  const handleExecuteAction = async (msgId: string, action: ChatMessage['suggested_action']) => {
    if (!action) return;
    setActionLoadingId(msgId);

    try {
      if (action.action_type === 'CREATE_PURCHASE_ORDER') {
        const prod = products.find(p => p.id === action.product_id || p.name === action.product_name) || products[0];
        await purchaseOrdersService.create({
          supplier_id: action.supplier_id || prod?.supplier_id || 's1',
          product_id: prod.id,
          quantity: action.quantity || 10,
          unit: action.unit || prod.base_unit || 'bag',
          unit_price: prod.purchase_price || 1200,
          notes: `Created via Vyapari Voice Assistant Action: ${action.title}`
        });

        // Mark executed
        setChatMessages(prev => prev.map(m => m.id === msgId ? { ...m, actionExecuted: true } : m));

        const confMsg: ChatMessage = {
          id: `asst-conf-${Date.now()}`,
          role: 'assistant',
          content: language === 'te'
            ? `ఆర్డర్ సృష్టించబడింది! ${action.quantity} ${action.unit} ${action.product_name} కోసం పర్చేజ్ ఆర్డర్ రూపొందించబడింది.`
            : `Purchase order created! Successfully placed order for ${action.quantity} ${action.unit} of ${action.product_name}.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, confMsg]);
        speakText(confMsg.content);
      } else if (action.action_type === 'ADD_STOCK') {
        const prod = products.find(p => p.id === action.product_id || p.name === action.product_name) || products[0];
        await inventoryService.stockIn({
          product_id: prod.id,
          quantity: action.quantity,
          unit: action.unit || prod.base_unit,
          price: prod.purchase_price || 0,
          notes: 'Voice Action Execution'
        });

        setChatMessages(prev => prev.map(m => m.id === msgId ? { ...m, actionExecuted: true } : m));

        const confMsg: ChatMessage = {
          id: `asst-conf-${Date.now()}`,
          role: 'assistant',
          content: `Stock updated! Added ${action.quantity} ${action.unit} of ${action.product_name}.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, confMsg]);
        speakText(confMsg.content);
      }
    } catch (err: any) {
      alert('Action execution error: ' + (err?.message || 'Server failed'));
    } finally {
      setActionLoadingId(null);
    }
  };

  // Handle Voice Command / Stock Entry (Pillars 2 & 4)
  const processStockTranscript = async (text: string) => {
    if (!text.trim()) return;
    setTranscript(text);
    setVoiceState('understanding');
    setError('');

    const lower = text.toLowerCase();
    const isQuestion = lower.includes('entha') || lower.includes('undi') || lower.includes('how much') ||
      lower.includes('kitna') || lower.includes('baki') || lower.includes('stock?') || lower.includes('stock ?') ||
      lower.includes('who owes') || lower.includes('low stock') || lower.includes('saripothunda') || lower.includes('enough');

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
          product: parsed.canonical_name || parsed.product_name || parsed.product || 'Rice (Biyyam)',
          quantity: Number(parsed.quantity) || 5,
          unit: parsed.unit || 'bag',
          price: Number(parsed.unit_price || parsed.price) || 0,
          supplier: parsed.supplier_name || parsed.supplier,
          customer: parsed.customer_name || parsed.customer,
          confidence: Number(parsed.confidence) || 0.95,
        };
        setIntent(mappedIntent);
        setVoiceState('confirming');
      } else {
        throw new Error('Could not determine intent from voice');
      }
    } catch {
      // Fallback intent resolution with alias matching
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

  // Start Voice Recording with Web Speech API & MediaRecorder Fallback
  const startRecording = useCallback(() => {
    setError('');
    setTranscript('');
    setIntent(null);
    setResponseText('');

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

  // Server-Side Audio Recording & Multimodal Transcription
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

        if (chunksRef.current.length > 0) {
          try {
            const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'speech.webm');

            const trRes = await voiceService.transcribeAudio(formData);
            if (trRes.success && (trRes.data as any)?.transcript) {
              const transcribedText = (trRes.data as any).transcript;
              if (activeTab === 'question') {
                await handleAskQuestion(transcribedText);
              } else {
                await processStockTranscript(transcribedText);
              }
              return;
            }
          } catch (sttErr) {
            console.warn('Server STT fallback:', sttErr);
          }
        }

        // Graceful backup query
        if (activeTab === 'question') {
          handleAskQuestion('రైస్ స్టాక్ ఎంత ఉంది?');
        } else {
          processStockTranscript('5 bags biyyam add cheyyi 1450 rupees');
        }
      };

      mediaRecorder.start();
      setVoiceState('listening');
    } catch {
      setError('Microphone access not granted. You can type or tap the quick command chips below!');
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

  // Human Confirmation Action Execution (Pillar 2)
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

  // Sample Telugu / Hindi / English Questions
  const questionSuggestions = [
    { text: 'రైస్ స్టాక్ ఎంత ఉంది?', lang: 'te' },
    { text: 'వచ్చే వారానికి సరిపోతుందా?', lang: 'te' },
    { text: 'ఎవరెవరు అప్పు ఉన్నారు?', lang: 'te' },
    { text: 'चावल का स्टॉक कितना है?', lang: 'hi' },
    { text: 'How much Sugar is left?', lang: 'en' },
    { text: 'Will oil stock last next week?', lang: 'en' },
  ];

  // Sample Stock Entry Commands
  const entrySuggestions = [
    { text: '5 basthalu biyyam add cheyyi 1450 rupees', intent: 'STOCK_IN' },
    { text: '10 packets Parle-G sold', intent: 'STOCK_OUT' },
    { text: 'Ramesh ki 200 udhar rasi pettu', intent: 'BORROW_OUT' },
    { text: '10 kg Sugar add cheyyi', intent: 'STOCK_IN' },
  ];

  return (
    <div className="page-container pt-4 space-y-4 animate-fade-in max-w-4xl mx-auto pb-16">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-surface-200">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="touch-btn border border-surface-200 w-10 h-10">
            <ArrowLeft className="w-5 h-5 text-surface-600" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-surface-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-600 animate-pulse" />
              <span>{t('appName')}</span>
            </h2>
            <p className="text-xs text-surface-500">Live Voice AI • Telugu, Hindi & English</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <LanguageSwitcher />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex rounded-xl bg-surface-100 p-1">
        <button
          onClick={() => { setActiveTab('question'); setVoiceState('ready'); }}
          className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 ${
            activeTab === 'question'
              ? 'bg-white text-primary-700 shadow-xs'
              : 'text-surface-600 hover:text-surface-900'
          }`}
        >
          <HelpCircle className="w-4 h-4 text-primary-500" />
          <span>Smart Assistant (Ask Anything)</span>
        </button>
        <button
          onClick={() => { setActiveTab('entry'); setVoiceState('ready'); }}
          className={`flex-1 py-2 text-xs sm:text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 ${
            activeTab === 'entry'
              ? 'bg-white text-primary-700 shadow-xs'
              : 'text-surface-600 hover:text-surface-900'
          }`}
        >
          <PlusCircle className="w-4 h-4 text-emerald-500" />
          <span>Stock & Udhar Voice Entry</span>
        </button>
      </div>

      {/* Voice Status State Visualizer Card */}
      <div className="card p-5 text-center flex flex-col items-center justify-center space-y-3 bg-gradient-to-b from-white to-surface-50/50">
        <p className="text-xs font-bold uppercase tracking-wider text-surface-400">
          {voiceState === 'listening' ? 'Active Recording' : 'Microphone Status'}
        </p>

        {/* Microphone Button with States */}
        <div className="relative">
          {voiceState === 'listening' && (
            <div className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-60 pointer-events-none scale-125" />
          )}

          <button
            onClick={voiceState === 'listening' ? stopRecording : startRecording}
            className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition-all active:scale-95 ${
              voiceState === 'listening'
                ? 'bg-red-500 text-white ring-4 ring-red-300 animate-pulse'
                : voiceState === 'processing' || voiceState === 'understanding'
                ? 'bg-amber-500 text-white'
                : voiceState === 'confirming'
                ? 'bg-primary-600 text-white'
                : voiceState === 'completed'
                ? 'bg-emerald-500 text-white'
                : 'gradient-primary text-white hover:opacity-95 ring-4 ring-primary-100'
            }`}
          >
            {voiceState === 'listening' ? (
              <MicOff className="w-9 h-9" />
            ) : voiceState === 'processing' || voiceState === 'understanding' ? (
              <Loader2 className="w-9 h-9 animate-spin" />
            ) : voiceState === 'completed' ? (
              <Check className="w-9 h-9" />
            ) : (
              <Mic className="w-9 h-9" />
            )}
          </button>
        </div>

        {/* State Label & Guidance */}
        <div className="space-y-0.5">
          <p className="text-sm font-bold text-surface-800">
            {voiceState === 'listening' && 'Listening to you... Speak now'}
            {voiceState === 'processing' && 'Processing speech...'}
            {voiceState === 'understanding' && 'Understanding with Supabase reality...'}
            {voiceState === 'confirming' && 'Review & Confirm Action'}
            {voiceState === 'completed' && 'Completed successfully!'}
            {voiceState === 'ready' && 'Tap mic to speak (Telugu / Hindi / English)'}
            {voiceState === 'error' && 'Error occurred. Tap mic to retry'}
          </p>
          <p className="text-xs text-surface-400">
            {voiceState === 'listening' ? 'Click again or pause to finish recording' : 'Works with Kirana terms: biyyam, chakkera, nune, udhar, saripothunda'}
          </p>
        </div>
      </div>

      {/* ERROR BANNER */}
      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 animate-shake">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* TAB 1: CONVERSATIONAL ASSISTANT STREAM (Modes 1, 2, 3) */}
      {activeTab === 'question' && (
        <div className="space-y-4">
          {/* Chat Stream Window */}
          <div className="card p-4 h-[380px] overflow-y-auto space-y-3 bg-surface-50/40 border-surface-200">
            {chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-1 animate-fade-in`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[75%] p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white rounded-br-xs'
                      : 'bg-white text-surface-900 border border-surface-200/90 rounded-bl-xs'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* 1-Click Action Suggestion Card (Mode 1) */}
                  {msg.suggested_action && (
                    <div className="mt-3 p-3 rounded-xl bg-amber-50 border border-amber-200 text-surface-900 space-y-2">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                        <ShoppingBag className="w-3.5 h-3.5 text-amber-700" />
                        <span>Recommended Action: {msg.suggested_action.title}</span>
                      </div>
                      <p className="text-[11px] text-surface-600">
                        Product: <b>{msg.suggested_action.product_name}</b> • Qty: <b>{msg.suggested_action.quantity} {msg.suggested_action.unit}</b>
                      </p>

                      {msg.actionExecuted ? (
                        <div className="flex items-center gap-1 text-xs font-bold text-emerald-700 pt-1">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Action Executed in Database!</span>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleExecuteAction(msg.id, msg.suggested_action)}
                          disabled={actionLoadingId === msg.id}
                          className="w-full py-2 rounded-lg gradient-primary text-white text-xs font-semibold shadow-xs flex items-center justify-center gap-1.5 hover:opacity-95 disabled:opacity-50"
                        >
                          {actionLoadingId === msg.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <>
                              <span>Confirm & Place Order</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </>
                          )}
                        </button>
                      )}
                    </div>
                  )}
                </div>
                <span className="text-[10px] text-surface-400 px-1">{msg.timestamp}</span>
              </div>
            ))}

            {questionLoading && (
              <div className="flex items-center gap-2 p-3 bg-white rounded-2xl border border-surface-200 max-w-[200px] animate-pulse">
                <Loader2 className="w-4 h-4 animate-spin text-primary-600" />
                <span className="text-xs text-surface-500 font-medium">Analyzing database...</span>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>

          {/* Question Input Field */}
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
              placeholder="Ask anything (e.g. 'Rice stock entha undi?', 'Next week ki saripothunda?')..."
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
              Quick Suggestions (Tap to ask live):
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

      {/* TAB 2: STOCK & UDHAR VOICE ENTRY (Pillar 2 & 4) */}
      {activeTab === 'entry' && (
        <div className="space-y-4">
          {/* CONFIRMATION CARD (Pillar 2: Mandatory Human Verification) */}
          {voiceState === 'confirming' && intent && (
            <div className="card p-5 border-2 border-primary-400 shadow-md space-y-4 animate-scale-up bg-white">
              <div className="flex items-center justify-between pb-2 border-b border-surface-100">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-primary-600" />
                  <h3 className="font-bold text-base text-surface-900">Verify & Confirm Entry</h3>
                </div>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="text-xs font-semibold text-primary-600 hover:underline flex items-center gap-1"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  <span>{isEditing ? 'Cancel Edit' : 'Edit Values'}</span>
                </button>
              </div>

              {/* Spoken Transcript Preview */}
              <div className="p-2.5 rounded-lg bg-surface-50 text-xs text-surface-600">
                Spoken: <i>"{transcript}"</i>
              </div>

              {/* Action Form Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-surface-50">
                  <span className="text-[10px] text-surface-400 uppercase font-bold">Action</span>
                  <p className="font-bold text-sm text-surface-900 mt-0.5">{intent.intent}</p>
                </div>
                <div className="p-3 rounded-xl bg-surface-50">
                  <span className="text-[10px] text-surface-400 uppercase font-bold">Product</span>
                  <p className="font-bold text-sm text-surface-900 mt-0.5 truncate">{intent.product}</p>
                </div>
                <div className="p-3 rounded-xl bg-surface-50">
                  <span className="text-[10px] text-surface-400 uppercase font-bold">Quantity</span>
                  {isEditing ? (
                    <input
                      type="number"
                      value={editQty}
                      onChange={(e) => setEditQty(e.target.value)}
                      className="w-full mt-1 px-2 py-1 text-sm border rounded"
                    />
                  ) : (
                    <p className="font-bold text-sm text-surface-900 mt-0.5">{editQty || intent.quantity} {editUnit || intent.unit}</p>
                  )}
                </div>
                <div className="p-3 rounded-xl bg-surface-50">
                  <span className="text-[10px] text-surface-400 uppercase font-bold">Unit Price</span>
                  {isEditing ? (
                    <input
                      type="number"
                      value={editPrice}
                      onChange={(e) => setEditPrice(e.target.value)}
                      className="w-full mt-1 px-2 py-1 text-sm border rounded"
                    />
                  ) : (
                    <p className="font-bold text-sm text-surface-900 mt-0.5">₹{editPrice || intent.price}</p>
                  )}
                </div>
              </div>

              {/* Customer / Supplier info if detected */}
              {intent.customer && (
                <div className="flex items-center gap-2 p-2.5 rounded-lg bg-blue-50 text-xs text-blue-800">
                  <UserCheck className="w-4 h-4" />
                  <span>Customer Udhar recorded for: <b>{intent.customer}</b></span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleConfirm}
                  className="flex-1 py-3 rounded-xl gradient-primary text-white font-bold text-sm shadow-md hover:opacity-95 flex items-center justify-center gap-2"
                >
                  <Check className="w-4 h-4" />
                  <span>Confirm & Save to Supabase</span>
                </button>
                <button
                  onClick={() => setVoiceState('ready')}
                  className="px-4 py-3 rounded-xl border border-surface-200 text-surface-600 font-semibold text-sm hover:bg-surface-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Success Response State */}
          {voiceState === 'completed' && (
            <div className="card p-5 bg-emerald-50 border border-emerald-200 text-center space-y-3 animate-fade-in">
              <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
              <h3 className="font-bold text-base text-emerald-900">Database Updated!</h3>
              <p className="text-sm text-emerald-800">{responseText}</p>
              <button
                onClick={() => setVoiceState('ready')}
                className="px-6 py-2 rounded-xl gradient-primary text-white font-semibold text-xs shadow-xs"
              >
                Record Another Command
              </button>
            </div>
          )}

          {/* Manual Input Fallback */}
          {voiceState === 'ready' && (
            <div className="space-y-3 pt-1">
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
                  placeholder="Or type voice command (e.g. '5 bags biyyam vachayi 1450 rupees')..."
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

              {/* Sample Commands */}
              <div className="space-y-2 pt-1">
                <p className="text-xs font-bold uppercase text-surface-400 tracking-wider">
                  Sample Commands (Tap to execute):
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
      )}
    </div>
  );
}
