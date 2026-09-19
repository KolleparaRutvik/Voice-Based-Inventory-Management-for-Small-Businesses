import React, { createContext, useContext, useState } from 'react';

export type Language = 'en' | 'te' | 'hi';

export interface Translations {
  // App brand & common
  appName: string;
  tagline: string;
  loading: string;
  save: string;
  cancel: string;
  confirm: string;
  delete: string;
  edit: string;
  close: string;
  all: string;
  search: string;
  filter: string;
  actions: string;
  status: string;

  // Navigation
  navDashboard: string;
  navProducts: string;
  navInventory: string;
  navTransactions: string;
  navBorrowings: string;
  navSuppliers: string;
  navOrders: string;
  navAnalytics: string;
  navVoiceAssistant: string;
  navNotifications: string;
  navSettings: string;
  navMore: string;
  logout: string;

  // Dashboard & Metrics
  totalStockValue: string;
  totalProducts: string;
  lowStockItems: string;
  activeBorrowings: string;
  quickActions: string;
  askAssistant: string;
  askPlaceholder: string;
  voiceCommandTitle: string;
  recentTransactions: string;

  // Products & Stock
  addProduct: string;
  productName: string;
  localName: string;
  category: string;
  currentStock: string;
  baseUnit: string;
  purchaseUnit: string;
  sellingUnit: string;
  conversionFactor: string;
  purchasePrice: string;
  sellingPrice: string;
  margin: string;
  minStock: string;
  stockIn: string;
  stockOut: string;
  unitConversion: string;

  // Voice & Assistant
  tapToSpeak: string;
  listening: string;
  processing: string;
  understanding: string;
  pleaseConfirm: string;
  done: string;
  sampleCommands: string;
  voiceTabEntry: string;
  voiceTabQuestions: string;
  askQuestionPrompt: string;
  askSample1: string;
  askSample2: string;
  askSample3: string;
  askSample4: string;
  entrySample1: string;
  entrySample2: string;
  entrySample3: string;

  // Borrowings / Udhar
  customerName: string;
  amountDue: string;
  whatsappReminder: string;
  settlePayment: string;
}

const translations: Record<Language, Translations> = {
  en: {
    appName: 'Vyapari Voice',
    tagline: 'Voice-First Kirana Inventory & Business Assistant',
    loading: 'Loading...',
    save: 'Save',
    cancel: 'Cancel',
    confirm: 'Confirm Action',
    delete: 'Delete',
    edit: 'Edit',
    close: 'Close',
    all: 'All',
    search: 'Search products...',
    filter: 'Filter',
    actions: 'Actions',
    status: 'Status',

    navDashboard: 'Dashboard',
    navProducts: 'Products',
    navInventory: 'Inventory',
    navTransactions: 'Transactions',
    navBorrowings: 'Borrowings (Udhar)',
    navSuppliers: 'Suppliers',
    navOrders: 'Purchase Orders',
    navAnalytics: 'Analytics',
    navVoiceAssistant: 'Voice Assistant',
    navNotifications: 'Notifications',
    navSettings: 'Settings',
    navMore: 'More',
    logout: 'Logout',

    totalStockValue: 'Total Stock Value',
    totalProducts: 'Total Products',
    lowStockItems: 'Low Stock Items',
    activeBorrowings: 'Pending Udhar',
    quickActions: 'Quick Actions',
    askAssistant: 'Ask Vyapari AI',
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Rice stock entha undi?")...',
    voiceCommandTitle: 'Voice Command',
    recentTransactions: 'Recent Transactions',

    addProduct: 'Add Product',
    productName: 'Product Name',
    localName: 'Regional Name',
    category: 'Category',
    currentStock: 'Current Stock',
    baseUnit: 'Base Unit',
    purchaseUnit: 'Purchase Unit',
    sellingUnit: 'Selling Unit',
    conversionFactor: 'Conversion Factor',
    purchasePrice: 'Purchase Price',
    sellingPrice: 'Selling Price',
    margin: 'Margin',
    minStock: 'Minimum Stock',
    stockIn: 'Stock In (+)',
    stockOut: 'Stock Out (-)',
    unitConversion: 'Unit Conversion',

    tapToSpeak: 'Tap to Speak',
    listening: 'Listening to your voice...',
    processing: 'Processing audio...',
    understanding: 'AI Analyzing with Database...',
    pleaseConfirm: 'Please Confirm Action',
    done: 'Completed Successfully!',
    sampleCommands: 'Quick Voice Commands',
    voiceTabEntry: 'Voice Stock Entry',
    voiceTabQuestions: 'Stock Questions & AI',
    askQuestionPrompt: 'Ask any question about your stock, udhar or prices',
    askSample1: 'How much rice is left in stock?',
    askSample2: 'How much sunflower oil is available?',
    askSample3: 'How much does Ramesh owe in Udhar?',
    askSample4: 'Which items are low in stock?',
    entrySample1: 'Added 5 bags of Rice at 1450 rupees',
    entrySample2: 'Sold 2 litres of Sunflower Oil for cash',
    entrySample3: 'Given 500 rupees Udhar to Ramesh',

    customerName: 'Customer Name',
    amountDue: 'Amount Due',
    whatsappReminder: 'WhatsApp Reminder',
    settlePayment: 'Settle Payment',
  },

  te: {
    appName: 'వ్యాపారి వాయిస్',
    tagline: 'వాయిస్-ఆధారిత కిరాణా ఇన్వెంటరీ & బిజినెస్ అసిస్టెంట్',
    loading: 'లోడ్ అవుతోంది...',
    save: 'సేవ్ చేయండి',
    cancel: 'రద్దు',
    confirm: 'నిర్ధారించండి',
    delete: 'తొలగించు',
    edit: 'సవరించు',
    close: 'మూసివేయి',
    all: 'అన్నీ',
    search: 'వస్తువులను వెతకండి...',
    filter: 'ఫిల్టర్',
    actions: 'చర్యలు',
    status: 'స్థితి',

    navDashboard: 'డ్యాష్‌బోర్డ్',
    navProducts: 'వస్తువులు (Products)',
    navInventory: 'స్టాక్ ఇన్వెంటరీ',
    navTransactions: 'లావాదేవీలు',
    navBorrowings: 'బాకీలు (ఉధార్)',
    navSuppliers: 'సరఫరాదారులు',
    navOrders: 'కొనుగోలు ఆర్డర్లు',
    navAnalytics: 'వ్యాపార విశ్లేషణ',
    navVoiceAssistant: 'వాయిస్ అసిస్టెంట్',
    navNotifications: 'నోటిఫికేషన్లు',
    navSettings: 'సెట్టింగ్‌లు',
    navMore: 'మరిన్ని',
    logout: 'లాగ్ అవుట్',

    totalStockValue: 'మొత్తం స్టాక్ విలువ',
    totalProducts: 'మొత్తం వస్తువులు',
    lowStockItems: 'తక్కువ స్టాక్ ఉన్నవి',
    activeBorrowings: 'కస్టమర్ బాకీలు (ఉధార్)',
    quickActions: 'త్వరిత చర్యలు',
    askAssistant: 'వ్యాపారి AI ని అడగండి',
    askPlaceholder: 'తెలుగు లేదా ఇంగ్లీషులో అడగండి (ఉదా: "రైస్ స్టాక్ ఎంత ఉంది?")...',
    voiceCommandTitle: 'వాయిస్ కమాండ్',
    recentTransactions: 'ఇటీవలి లావాదేవీలు',

    addProduct: 'కొత్త వస్తువు జోడించు',
    productName: 'వస్తువు పేరు',
    localName: 'తెలుగు పేరు (Local Name)',
    category: 'వర్గం (Category)',
    currentStock: 'ప్రస్తుత స్టాక్',
    baseUnit: 'ప్రాథమిక యూనిట్ (కేజీ/లీటర్)',
    purchaseUnit: 'కొనుగోలు యూనిట్ (బస్తా/డబ్బా)',
    sellingUnit: 'విక్రయ యూనిట్ (కేజీ/లీటర్)',
    conversionFactor: 'యూనిట్ మార్పిడి (1 బస్తా = కేజీలు)',
    purchasePrice: 'కొనుగోలు ధర',
    sellingPrice: 'అమ్మకపు ధర',
    margin: 'లాభం మార్జిన్',
    minStock: 'కనిష్ట స్టాక్ పరిమితి',
    stockIn: 'స్టాక్ ఇన్ (+ కొనుగోలు)',
    stockOut: 'స్టాక్ అవుట్ (- అమ్మకం)',
    unitConversion: 'యూనిట్ మార్పిడి లెక్క',

    tapToSpeak: 'మాట్లాడటానికి నొక్కండి',
    listening: 'వింటున్నాము... మాట్లాడండి',
    processing: 'ప్రాసెస్ చేస్తున్నాము...',
    understanding: 'డేటాబేస్ నుండి AI విశ్లేషిస్తోంది...',
    pleaseConfirm: 'దయచేసి వివరాలను పరిశీలించి నిర్ధారించండి',
    done: 'విజయవంతంగా పూర్తయింది!',
    sampleCommands: 'ఉదాహరణ వాయిస్ ఆదేశాలు',
    voiceTabEntry: 'వాయిస్ స్టాక్ ఎంట్రీ',
    voiceTabQuestions: 'స్టాక్ ప్రశ్నలు & AI సమాధానం',
    askQuestionPrompt: 'మీ దుకాణంలోని స్టాక్, ఉధార్ బాకీల గురించి ఏదైనా అడగండి',
    askSample1: 'రైస్ స్టాక్ ఎంత ఉంది?',
    askSample2: 'నూనె స్టాక్ ఎంత మిగిలింది?',
    askSample3: 'రమేష్ ఎంత బాకీ ఉన్నాడు?',
    askSample4: 'ఏ వస్తువులు తక్కువ స్టాక్ ఉన్నాయి?',
    entrySample1: '5 బస్తాల బియ్యం కొన్నాం 1450 రూపాయలు',
    entrySample2: '2 లీటర్ల సన్‌ఫ్లవర్ నూనె అమ్మాము',
    entrySample3: 'రమేష్ కి 500 రూపాయలు ఉధార్ ఇచ్చాం',

    customerName: 'కస్టమర్ పేరు',
    amountDue: 'బాకీ మొత్తం',
    whatsappReminder: 'వాట్సాప్ రిమైండర్',
    settlePayment: 'బాకీ చెల్లించండి',
  },

  hi: {
    appName: 'व्यापारी वॉइस',
    tagline: 'वॉइस-आधारित किराना इन्वेंटरी व बिजनेस सहायक',
    loading: 'लोड हो रहा है...',
    save: 'सुरक्षित करें',
    cancel: 'रद्द करें',
    confirm: 'पुष्टि करें',
    delete: 'हटाएं',
    edit: 'संपादित करें',
    close: 'बंद करें',
    all: 'सभी',
    search: 'सामान खोजें...',
    filter: 'फ़िल्टर',
    actions: 'कार्रवाई',
    status: 'स्थिति',

    navDashboard: 'डैशबोर्ड',
    navProducts: 'उत्पाद (Products)',
    navInventory: 'स्टॉक इन्वेंटरी',
    navTransactions: 'लेन-देन',
    navBorrowings: 'उधार खाता',
    navSuppliers: 'आपूर्तिकर्ता',
    navOrders: 'खरीद ऑर्डर',
    navAnalytics: 'व्यापार विश्लेषण',
    navVoiceAssistant: 'वॉइस असिस्टेंट',
    navNotifications: 'सूचनाएं',
    navSettings: 'सेटिंग्स',
    navMore: 'और भी',
    logout: 'लॉग आउट',

    totalStockValue: 'कुल स्टॉक मूल्य',
    totalProducts: 'कुल उत्पाद',
    lowStockItems: 'कम स्टॉक वाले आइटम',
    activeBorrowings: 'कुल बकाया उधार',
    quickActions: 'त्वरित कार्य',
    askAssistant: 'व्यापारी AI से पूछें',
    askPlaceholder: 'हिंदी या अंग्रेजी में पूछें (जैसे "चावल का स्टॉक कितना है?")...',
    voiceCommandTitle: 'वॉइस कमांड',
    recentTransactions: 'हाल के लेन-देन',

    addProduct: 'नया सामान जोड़ें',
    productName: 'उत्पाद नाम',
    localName: 'स्थानीय नाम',
    category: 'श्रेणी (Category)',
    currentStock: 'मौजूदा स्टॉक',
    baseUnit: 'आधार इकाई (किलो/लीटर)',
    purchaseUnit: 'खरीद इकाई (बोरी/पेटी)',
    sellingUnit: 'बिक्री इकाई (किलो/लीटर)',
    conversionFactor: 'इकाई परिवर्तन (1 बोरी = किलो)',
    purchasePrice: 'खरीद मूल्य',
    sellingPrice: 'बिक्री मूल्य',
    margin: 'मुनाफा मार्जिन',
    minStock: 'न्यूनतम स्टॉक सीमा',
    stockIn: 'स्टॉक इन (+ खरीद)',
    stockOut: 'स्टॉक आउट (- बिक्री)',
    unitConversion: 'इकाई रूपांतरण',

    tapToSpeak: 'बोलने के लिए दबाएं',
    listening: 'सुन रहे हैं... बोलिए',
    processing: 'प्रोसेस हो रहा है...',
    understanding: 'डेटाबेस से AI विश्लेषण कर रहा है...',
    pleaseConfirm: 'कृपया पुष्टि करें',
    done: 'सफलतापूर्वक दर्ज किया गया!',
    sampleCommands: 'त्वरित वॉइस आदेश',
    voiceTabEntry: 'वॉइस स्टॉक एंट्री',
    voiceTabQuestions: 'स्टॉक सवाल व AI उत्तर',
    askQuestionPrompt: 'स्टॉक, उधार व कीमतों के बारे में कोई भी सवाल पूछें',
    askSample1: 'चावल का स्टॉक कितना है?',
    askSample2: 'सूर्यमुखी तेल कितना बचा है?',
    askSample3: 'रमेश पर कितना उधार बाकी है?',
    askSample4: 'कौन से सामान कम स्टॉक में हैं?',
    entrySample1: '5 बोरी चावल आया 1450 रुपये',
    entrySample2: '2 लीटर तेल नकद में बेचा',
    entrySample3: 'रमेश को 500 रुपये उधार दिया',

    customerName: 'ग्राहक का नाम',
    amountDue: 'बकाया राशि',
    whatsappReminder: 'व्हाट्सएप रिमाइंडर',
    settlePayment: 'उधार चुकता करें',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: keyof Translations) => string;
  getSpeechLang: () => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('vyapari_lang');
    return (saved === 'te' || saved === 'hi' || saved === 'en') ? saved : 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('vyapari_lang', lang);
  };

  const t = (key: keyof Translations): string => {
    return translations[language]?.[key] || translations.en[key] || String(key);
  };

  const getSpeechLang = (): string => {
    if (language === 'te') return 'te-IN';
    if (language === 'hi') return 'hi-IN';
    return 'en-IN';
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, getSpeechLang }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
