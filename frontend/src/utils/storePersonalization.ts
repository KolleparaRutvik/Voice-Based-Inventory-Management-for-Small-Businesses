// DukaanSetu — Store Personalization Config for All 12 Retail Verticals

export interface StorePersona {
  id: string;
  name: string;
  emoji: string;
  defaultShopName: string;
  voiceExample: {
    te: string;
    hi: string;
    en: string;
  };
  askPlaceholder: string;
  assistantGreeting: {
    te: string;
    hi: string;
    en: string;
  };
  assistantDbChecking: string;
  manualInputPlaceholder: string;
  suggestions: Array<{ label: string; query: string }>;
}

export const STORE_PERSONAS: Record<string, StorePersona> = {
  kirana: {
    id: 'kirana',
    name: 'Kirana & Grocery',
    emoji: '🛒',
    defaultShopName: 'Sri Lakshmi Kirana Store',
    voiceExample: {
      te: '"5 బస్తాల బియ్యం కొన్నాం 1450 రూపాయలు" లేదా "రైస్ స్టాక్ ఎంత ఉంది?"',
      hi: '"5 बोरी चावल आया 1450 रुपये" या "चावल का स्टॉक कितना है?"',
      en: '"5 bags biyyam add cheyyi" or "How much rice stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Rice stock entha undi?", "Ramesh ki 500 udhar rayi")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ కిరాణా వాయిస్ అసిస్టెంట్. బియ్యం, నూనె, పప్పుల స్టాక్, పండుగ సరుకులు లేదా ఉధార్ వివరాలు ఏదైనా అడగవచ్చు లేదా వాయిస్ తో రికార్డ్ చేయవచ్చు.',
      hi: 'नमस्ते! मैं आपका किराना वॉयस सहायक हूँ। आप चावल, तेल, दाल का स्टॉक, बिक्री या उधारी आसानी से बोलकर रिकॉर्ड कर सकते हैं।',
      en: 'Welcome to Sri Lakshmi Kirana! Ask about rice, oil, pulses stock, festival demand, or record customer udhar with your voice.',
    },
    assistantDbChecking: 'Checking live Kirana DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Rice stock entha?', 'Ramesh ki 500 udhar rasi pettu')...",
    suggestions: [
      { label: '🔥 Trending & fast-moving items?', query: 'Which items are selling fast and trending?' },
      { label: '⚠️ Low stock alert check', query: 'What items have low stock alerts?' },
      { label: 'రైస్ స్టాక్ ఎంత ఉంది?', query: 'రైస్ స్టాక్ ఎంత ఉంది?' },
      { label: 'Add 5 bags Sona Masoori Rice', query: 'Add 5 bags Sona Masoori Rice' },
      { label: 'దసరా పండుగకి ఏ సరుకులు కావాలి?', query: 'దసరా పండుగకి ఏ సరుకులు కావాలి?' },
      { label: 'Ramesh ki 500 udhar rasi pettu', query: 'Ramesh ki 500 udhar rasi pettu' },
      { label: 'How much loan does Ramesh have?', query: 'How much loan does Ramesh have?' },
      { label: 'Clear loan of Ramesh', query: 'Clear loan of Ramesh' },
      { label: 'Sugar stock check cheyyi', query: 'Sugar stock check cheyyi' },
      { label: 'Check festival demand', query: 'Check festival demand' },
    ],
  },

  flowers: {
    id: 'flowers',
    name: 'Flower & Pooja Shop',
    emoji: '🌸',
    defaultShopName: 'Sri Pushpa Pooja Store',
    voiceExample: {
      te: '"20 బంతిపూల దండలు కొన్నాం" లేదా "మల్లెపూలు, కర్పూరం స్టాక్ ఎంత ఉంది?"',
      hi: '"20 गेंदा फूल माला आया" या "कपूर और अगरबत्ती का स्टॉक कितना है?"',
      en: '"Add 20 marigold garlands" or "How much camphor & agarbatti stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Banthipulu stock entha?", "Pooja camphor entha undi?")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ పూల & పూజా సామాగ్రి వాయిస్ అసిస్టెంట్. బంతిపూలు, మల్లెపూలు, కర్పూరం, అగర్‌బత్తీల స్టాక్ మరియు పండుగ ఆర్డర్లు వాయిస్ తో నిర్వహించండి.',
      hi: 'नमस्ते! मैं आपका फूल व पूजा दुकान वॉयस सहायक हूँ। गेंदा, चमेली माला, कपूर, अगरबत्ती का स्टॉक और त्योहारों के ऑर्डर बोलकर प्रबंधित करें।',
      en: 'Welcome to Flower & Pooja Store! Check fresh garland stock, festival pooja demand, camphor, or record customer flower bookings.',
    },
    assistantDbChecking: 'Checking live Flower & Pooja DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Banthipulu stock entha?', 'Anitha ki 350 pooja items udhar rayi')...",
    suggestions: [
      { label: '🔥 Trending flowers & festival spike?', query: 'Which flowers are trending and in high demand?' },
      { label: '⚠️ బంతిపూల & కర్పూరం లో స్టాక్ అలర్ట్', query: 'What flower and pooja items are low stock?' },
      { label: 'బంతిపూల దండలు (Marigold) స్టాక్ ఎంత ఉంది?', query: 'బంతిపూల దండలు స్టాక్ ఎంత ఉంది?' },
      { label: 'Add 25 Marigold Garlands', query: 'Add 25 Marigold Garlands' },
      { label: 'Check Diwali pooja flower demand', query: 'Check Diwali pooja flower demand' },
      { label: 'Anitha ki 350 pooja items udhar rayi', query: 'Anitha ki 350 pooja items udhar rayi' },
      { label: 'కర్పూరం & అగర్‌బత్తీలు స్టాక్ సరిపోతుందా?', query: 'కర్పూరం అగర్‌బత్తీలు స్టాక్ సరిపోతుందా?' },
      { label: 'How much loan does Anitha have?', query: 'How much loan does Anitha have?' },
      { label: 'Jasmine Strings (మల్లెపూలు) stock entha?', query: 'Jasmine Strings stock entha?' },
      { label: 'Clear loan of Anitha', query: 'Clear loan of Anitha' },
    ],
  },

  jewellery: {
    id: 'jewellery',
    name: 'Jewellery Shop',
    emoji: '💎',
    defaultShopName: 'Sri Swarna Jewellers',
    voiceExample: {
      te: '"5 గ్రాముల గోల్డ్ చైన్ అమ్మాం" లేదా "సిల్వర్ పట్టీలు స్టాక్ ఎంత ఉంది?"',
      hi: '"5 ग्राम सोने की चैन बेची" या "चांदी की पायल का स्टॉक कितना है?"',
      en: '"Sold 5 grams gold chain" or "How much silver anklets stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Gold chain stock entha?", "Silver coins stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ జ్యువెలరీ వాయిస్ అసిస్టెంట్. బంగారం, వెండి ఆభరణాల స్టాక్, ధన్‌తేరస్ / పెళ్లిళ్ల డిమాండ్ లేదా కస్టమర్ అడ్వాన్స్/బకాయిలు వాయిస్ తో తనిఖీ చేయండి.',
      hi: 'नमस्ते! मैं आपका आभूषण वॉयस सहायक हूँ। सोना, चांदी के जेवर, धनतेरस व शादी की मांग और ग्राहक उधार हिसाब आसानी से बोलकर देखें।',
      en: 'Welcome to Jewellery Store! Track gold & silver ornaments, weight in grams/tolas, Dhanteras demand, or manage customer credit accounts.',
    },
    assistantDbChecking: 'Checking live Jewellery DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Gold chain stock entha?', 'Rajesh ki 25000 gold advance udhar rayi')...",
    suggestions: [
      { label: '🔥 Trending jewellery & gold items?', query: 'Which jewellery items are trending and selling fast?' },
      { label: '⚠️ Ornaments low stock check', query: 'What jewellery items have low stock?' },
      { label: '22K Gold Chain stock entha undi?', query: '22K Gold Chain stock entha undi?' },
      { label: 'Add 5 Silver Anklets (వెండి పట్టీలు)', query: 'Add 5 Silver Anklets' },
      { label: 'Check Dhanteras & Akshaya Tritiya gold demand', query: 'Check Dhanteras and Akshaya Tritiya gold demand' },
      { label: 'Rajesh ki 25000 gold advance udhar rayi', query: 'Rajesh ki 25000 gold advance udhar rayi' },
      { label: 'Silver Coins 10g stock entha?', query: 'Silver Coins 10g stock entha?' },
      { label: 'How much loan does Rajesh have?', query: 'How much loan does Rajesh have?' },
      { label: 'Diamond Nose Pin stock check cheyyi', query: 'Diamond Nose Pin stock check cheyyi' },
      { label: 'Clear loan of Rajesh', query: 'Clear loan of Rajesh' },
    ],
  },

  clothing: {
    id: 'clothing',
    name: 'Clothing & Textiles',
    emoji: '👕',
    defaultShopName: 'Sri Raghavendra Cloth Emporium',
    voiceExample: {
      te: '"10 కాటన్ షర్టులు అమ్మాం" లేదా "కాంచీపురం పట్టు చీరలు స్టాక్ ఎంత ఉంది?"',
      hi: '"10 कॉटन शर्ट बेची" या "सिल्क साड़ियों का स्टॉक कितना है?"',
      en: '"Sold 10 cotton shirts" or "How much silk sarees stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Cotton shirts stock entha?", "Silk sarees stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ క్లాతింగ్ & టెక్స్‌టైల్స్ వాయిస్ అసిస్టెంట్. చీరలు, షర్టులు, డ్రెస్ మెటీరియల్స్ స్టాక్, సైజులు, పెళ్లిళ్ల సీజన్ డిమాండ్ వాయిస్ తో నిర్వహించండి.',
      hi: 'नमस्ते! मैं आपका कपड़ा दुकान वॉयस सहायक हूँ। शर्ट, साड़ी, पैंट और शादी के सीजन की मांग आसानी से बोलकर चेक करें।',
      en: 'Welcome to Cloth Emporium! Track shirts, sarees, jeans, fabric meters, festive wedding season demand, and customer tailoring ledgers.',
    },
    assistantDbChecking: 'Checking live Clothing & Textiles DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Cotton shirts stock entha?', 'Suresh ki 1800 cloth udhar rayi')...",
    suggestions: [
      { label: '🔥 Trending festive clothing styles?', query: 'Which clothing items are selling fast and trending?' },
      { label: '⚠️ Sarees & shirts low stock check', query: 'What clothes have low stock?' },
      { label: 'Cotton Shirts stock entha undi?', query: 'Cotton Shirts stock entha undi?' },
      { label: 'Add 15 Kanchipuram Silk Sarees', query: 'Add 15 Kanchipuram Silk Sarees' },
      { label: 'Wedding season shirts sarees demand check cheyyi', query: 'Wedding season shirts sarees demand check cheyyi' },
      { label: 'Suresh ki 1800 cloth udhar rasi pettu', query: 'Suresh ki 1800 cloth udhar rasi pettu' },
      { label: 'Denim Jeans 32 size stock entha?', query: 'Denim Jeans 32 size stock entha?' },
      { label: 'How much loan does Suresh have?', query: 'How much loan does Suresh have?' },
      { label: 'Suiting fabric rolls stock check cheyyi', query: 'Suiting fabric rolls stock check cheyyi' },
      { label: 'Clear loan of Suresh', query: 'Clear loan of Suresh' },
    ],
  },

  pharmacy: {
    id: 'pharmacy',
    name: 'Pharmacy / Medical',
    emoji: '💊',
    defaultShopName: 'Sri Durga Medical & General Stores',
    voiceExample: {
      te: '"10 స్ట్రిప్పుల పారాసిటమాల్ అమ్మాం" లేదా "ఆజిత్రోమైసిన్ స్టాక్ ఎంత ఉంది?"',
      hi: '"10 स्ट्रिप पैरासिटामोल बिका" या "कफ सिरप का स्टॉक कितना है?"',
      en: '"Sold 10 strips Paracetamol" or "How much Cough Syrup stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Paracetamol stock entha?", "Cough syrup stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ మెడికల్ & ఫార్మసీ వాయిస్ అసిస్టెంట్. టాబ్లెట్లు, సిరప్‌లు, ఇంజెక్షన్ల స్టాక్, ఎక్స్‌పైరీ హెచ్చరికలు లేదా కస్టమర్ మందుల ఖాతా వాయిస్ తో రికార్డ్ చేయండి.',
      hi: 'नमस्ते! मैं आपका मेडिकल स्टोर वॉयस सहायक हूँ। दवाइयों की स्ट्रिप्स, सिरप, स्टॉक और उधारी हिसाब आसानी से बोलकर ट्रैक करें।',
      en: 'Welcome to Medical & Pharmacy Store! Track tablet strips, syrups, vials, seasonal illness demand, and patient medicine ledgers.',
    },
    assistantDbChecking: 'Checking live Medical & Pharmacy DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Paracetamol stock entha?', 'Venkatesh ki 650 medicine udhar rayi')...",
    suggestions: [
      { label: '🔥 Fast-moving seasonal medicines?', query: 'Which medicines are selling fast and trending?' },
      { label: '⚠️ Low stock tablet & syrup alert', query: 'What medicines are low stock?' },
      { label: 'Paracetamol 650mg strips stock entha undi?', query: 'Paracetamol 650mg strips stock entha undi?' },
      { label: 'Add 20 strips Azithromycin 500mg', query: 'Add 20 strips Azithromycin 500mg' },
      { label: 'Check monsoon fever medicines demand', query: 'Check monsoon fever medicines demand' },
      { label: 'Venkatesh ki 650 medicine udhar rayi', query: 'Venkatesh ki 650 medicine udhar rayi' },
      { label: 'Cough Syrup 100ml bottles stock entha?', query: 'Cough Syrup 100ml bottles stock entha?' },
      { label: 'How much loan does Venkatesh have?', query: 'How much loan does Venkatesh have?' },
      { label: 'Vitamin C tablets stock check cheyyi', query: 'Vitamin C tablets stock check cheyyi' },
      { label: 'Clear loan of Venkatesh', query: 'Clear loan of Venkatesh' },
    ],
  },

  bakery: {
    id: 'bakery',
    name: 'Bakery & Sweet Shop',
    emoji: '🍞',
    defaultShopName: 'Sri Sai Sweet Home & Bakery',
    voiceExample: {
      te: '"5 కేజీల కాజూ కట్లీ కొన్నాం" లేదా "మిల్క్ బ్రెడ్ స్టాక్ ఎంత ఉంది?"',
      hi: '"5 किलो काजू कतली आया" या "मिल्क ब्रेड का स्टॉक कितना है?"',
      en: '"Add 5 kg Kaju Katli" or "How much Milk Bread stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Bread stock entha?", "Cakes stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ బేకరీ & స్వీట్స్ వాయిస్ అసిస్టెంట్. బ్రెడ్, కేకులు, మిఠాయిలు, పఫ్స్ తాజా స్టాక్ మరియు పండుగ స్వీట్ ఆర్డర్లు వాయిస్ తో ట్రాక్ చేయండి.',
      hi: 'नमस्ते! मैं आपका बेकरी व मिठाई वॉयस सहायक हूँ। केक, ब्रेड, काजू कतली, समोसे का फ्रेश स्टॉक और पार्टी ऑर्डर बोलकर चेक करें।',
      en: 'Welcome to Sweet Home & Bakery! Check daily fresh bread loaves, celebration cakes, traditional sweets, and festive bulk orders.',
    },
    assistantDbChecking: 'Checking live Bakery & Sweets DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Milk Bread stock entha?', 'Ravi ki 450 cake udhar rayi')...",
    suggestions: [
      { label: '🔥 Fast-moving bakery & snack items?', query: 'Which bakery items are trending and selling fast?' },
      { label: '⚠️ Fresh bread & puffs low stock check', query: 'What bakery items have low stock?' },
      { label: 'Milk Bread loaves stock entha undi?', query: 'Milk Bread loaves stock entha undi?' },
      { label: 'Add 10 kg Kaju Katli (కాజూ కట్లీ)', query: 'Add 10 kg Kaju Katli' },
      { label: 'Black Forest Cake stock check cheyyi', query: 'Black Forest Cake stock check cheyyi' },
      { label: 'Ravi ki 450 birthday cake udhar rayi', query: 'Ravi ki 450 birthday cake udhar rayi' },
      { label: 'Veg Puffs evening fresh stock సరిపోతుందా?', query: 'Veg Puffs evening fresh stock సరిపోతుందా?' },
      { label: 'How much loan does Ravi have?', query: 'How much loan does Ravi have?' },
      { label: 'Gulab Jamun kg stock entha?', query: 'Gulab Jamun kg stock entha?' },
      { label: 'Clear loan of Ravi', query: 'Clear loan of Ravi' },
    ],
  },

  restaurant: {
    id: 'restaurant',
    name: 'Restaurant / Tiffin',
    emoji: '🍽️',
    defaultShopName: 'Sri Annapurna Tiffin & Meals',
    voiceExample: {
      te: '"50 ఇడ్లీ ప్లేట్లు అమ్మాం" లేదా "చికెన్ బిర్యానీ రైస్ స్టాక్ ఎంత ఉంది?"',
      hi: '"50 प्लेट इडली बिका" या "बिरयानी और राशन का स्टॉक कितना है?"',
      en: '"Sold 50 plates Idli" or "How much Biryani & grocery stock left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Biryani plates stock entha?", "Idli batter stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ రెస్టారెంట్ & టిఫిన్ సెంటర్ వాయిస్ అసిస్టెంట్. టిఫిన్ ప్లేట్లు, బిర్యానీ భాగాలు, కిచెన్ సరుకులు మరియు కస్టమర్ నెలవారీ మెస్ ఖాతాలు వాయిస్ తో నిర్వహించండి.',
      hi: 'नमस्ते! मैं आपका भोजनालय व टिफिन वॉयस सहायक हूँ। इडली, डोसा, थाली और किचन सामान का स्टॉक बोलकर ट्रैक करें।',
      en: 'Welcome to Tiffin & Meals! Monitor daily breakfast plates, lunch thali, biryani orders, kitchen ingredients, and monthly mess udhar.',
    },
    assistantDbChecking: 'Checking live Restaurant & Kitchen DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Idli plates stock entha?', 'Mahesh Mess ki 1200 meals udhar rayi')...",
    suggestions: [
      { label: '🔥 High demand tiffin & meal dishes?', query: 'Which dishes are selling fast and high demand?' },
      { label: '⚠️ Kitchen ingredients low stock check', query: 'What kitchen items are low stock?' },
      { label: 'Idli Sambar plates stock entha undi?', query: 'Idli Sambar plates stock entha undi?' },
      { label: 'Add 25 plates Chicken Dum Biryani', query: 'Add 25 plates Chicken Dum Biryani' },
      { label: 'Check dinner rush ingredients stock', query: 'Check dinner rush ingredients stock' },
      { label: 'Mahesh Mess ki 1200 monthly meals udhar rayi', query: 'Mahesh Mess ki 1200 monthly meals udhar rayi' },
      { label: 'Masala Dosa batter stock సరిపోతుందా?', query: 'Masala Dosa batter stock సరిపోతుందా?' },
      { label: 'How much loan does Mahesh Mess have?', query: 'How much loan does Mahesh Mess have?' },
      { label: 'Basmati rice for biryani stock entha?', query: 'Basmati rice for biryani stock entha?' },
      { label: 'Clear loan of Mahesh Mess', query: 'Clear loan of Mahesh Mess' },
    ],
  },

  teacoffee: {
    id: 'teacoffee',
    name: 'Tea & Coffee Stall',
    emoji: '☕',
    defaultShopName: 'Sri Balaji Irani Tea & Coffee Point',
    voiceExample: {
      te: '"50 కప్పుల ఇరానీ చాయ్ అమ్మాం" లేదా "పాలు, టీ పొడి స్టాక్ ఎంత ఉంది?"',
      hi: '"50 कप ईरानी चाय बिका" या "दूध और चाय पत्ती का स्टॉक कितना है?"',
      en: '"Sold 50 cups Irani Chai" or "How much milk & tea powder left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Tea powder stock entha?", "Milk packets stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ టీ & కాఫీ పాయింట్ వాయిస్ అసిస్టెంట్. ఇరానీ చాయ్, ఫిల్టర్ కాఫీ, ఉస్మానియా బిస్కెట్లు, పాల ప్యాకెట్ల స్టాక్ మరియు రోజువారీ కస్టమర్ల టీ ఖాతా రికార్డ్ చేయండి.',
      hi: 'नमस्ते! मैं आपका चाय व कॉफ़ी स्टॉल वॉयस सहायक हूँ। स्पेशल चाय, कॉफ़ी, बिस्कुट और दूध का स्टॉक बोलकर तुरंत चेक करें।',
      en: 'Welcome to Irani Tea & Coffee Point! Check milk packets, tea powder, Osmania biscuits, and maintain daily customer tea tallies.',
    },
    assistantDbChecking: 'Checking live Tea & Coffee DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Special Irani Chai count?', 'Auto Raju ki 120 tea udhar rayi')...",
    suggestions: [
      { label: '🔥 Rush hour tea & snacks trend?', query: 'Which tea and snacks are selling fast?' },
      { label: '⚠️ Milk & tea powder stock check', query: 'Is milk and tea powder stock low?' },
      { label: 'Special Irani Chai cups count entha?', query: 'Special Irani Chai cups count entha?' },
      { label: 'Add 20 packets Full Cream Milk', query: 'Add 20 packets Full Cream Milk' },
      { label: 'Osmania Biscuits stock check cheyyi', query: 'Osmania Biscuits stock check cheyyi' },
      { label: 'Auto Raju ki 120 tea biscuits udhar rayi', query: 'Auto Raju ki 120 tea biscuits udhar rayi' },
      { label: 'Evening rush ki tea powder సరిపోతుందా?', query: 'Evening rush ki tea powder సరిపోతుందా?' },
      { label: 'How much loan does Auto Raju have?', query: 'How much loan does Auto Raju have?' },
      { label: 'Filter Coffee decoction stock entha?', query: 'Filter Coffee decoction stock entha?' },
      { label: 'Clear loan of Auto Raju', query: 'Clear loan of Auto Raju' },
    ],
  },

  hardware: {
    id: 'hardware',
    name: 'Hardware & Electrical',
    emoji: '🔧',
    defaultShopName: 'Sri Hanuman Hardware & Electricals',
    voiceExample: {
      te: '"10 LED బల్బులు అమ్మాం" లేదా "కాపర్ వైర్, PVC పైపుల స్టాక్ ఎంత ఉంది?"',
      hi: '"10 एलईडी बल्ब बिका" या "कॉपर वायर और पीवीसी पाइप का स्टॉक कितना है?"',
      en: '"Sold 10 LED bulbs" or "How much copper wire & PVC pipes left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "LED bulbs stock entha?", "Copper wire stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ హార్డ్‌వేర్ & ఎలక్ట్రికల్స్ వాయిస్ అసిస్టెంట్. వైరింగ్, స్విచ్‌లు, PVC పైపులు, సిమెంట్, టూల్స్ స్టాక్ మరియు ప్లంబర్/ఎలక్ట్రీషియన్ ఉధార్ వాయిస్ తో ట్రాక్ చేయండి.',
      hi: 'नमस्ते! मैं आपका हार्डवेयर व इलेक्ट्रिकल्स वॉयस सहायक हूँ। तार, स्विच, पाइप, सीमेंट और इलेक्ट्रीशियन उधार हिसाब आसानी से ट्रैक करें।',
      en: 'Welcome to Hardware & Electricals! Track wire bundles, LED lights, plumbing PVC pipes, switches, and contractor udhar accounts.',
    },
    assistantDbChecking: 'Checking live Hardware & Electrical DB...',
    manualInputPlaceholder: "Ask or type command (e.g. '9W LED Bulbs stock entha?', 'Plumber Srinivas ki 3500 udhar rayi')...",
    suggestions: [
      { label: '🔥 Fast-moving electrical & pipes?', query: 'Which hardware items are selling fast and trending?' },
      { label: '⚠️ LED bulbs & wire low stock check', query: 'What hardware items have low stock?' },
      { label: '9W LED Bulbs stock entha undi?', query: '9W LED Bulbs stock entha undi?' },
      { label: 'Add 10 rolls 2.5mm Copper Wire', query: 'Add 10 rolls 2.5mm Copper Wire' },
      { label: 'PVC Pipes 1-inch stock check cheyyi', query: 'PVC Pipes 1-inch stock check cheyyi' },
      { label: 'Plumber Srinivas ki 3500 pipes fittings udhar rayi', query: 'Plumber Srinivas ki 3500 pipes fittings udhar rayi' },
      { label: 'Modular Switches 6A stock entha?', query: 'Modular Switches 6A stock entha?' },
      { label: 'How much loan does Plumber Srinivas have?', query: 'How much loan does Plumber Srinivas have?' },
      { label: 'Asian Paints White 20L stock check cheyyi', query: 'Asian Paints White 20L stock check cheyyi' },
      { label: 'Clear loan of Plumber Srinivas', query: 'Clear loan of Plumber Srinivas' },
    ],
  },

  autoparts: {
    id: 'autoparts',
    name: 'Auto Parts & Spares',
    emoji: '🛠️',
    defaultShopName: 'Sri Ganesh Auto Spares & Accessories',
    voiceExample: {
      te: '"5 డబ్బాల ఇంజిన్ ఆయిల్ అమ్మాం" లేదా "బ్రేక్ ప్యాడ్స్, స్పార్క్ ప్లగ్స్ స్టాక్ ఎంత ఉంది?"',
      hi: '"5 बोतल इंजन ऑयल बिका" या "ब्रेक पैड और स्पार्क प्लग का स्टॉक कितना है?"',
      en: '"Sold 5 cans engine oil" or "How much brake pads & spark plugs left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Engine oil stock entha?", "Brake pads stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ ఆటో స్పేర్స్ & యాక్సెసరీస్ వాయిస్ అసిస్టెంట్. ఇంజిన్ ఆయిల్, బ్రేక్ ప్యాడ్లు, స్పార్క్ ప్లగ్‌లు, బ్యాటరీలు మరియు మెకానిక్ ఉధార్ వాయిస్ తో నిర్వహించండి.',
      hi: 'नमस्ते! मैं आपका ऑटो पार्ट्स वॉयस सहायक हूँ। इंजन ऑयल, ब्रेक पैड, प्लग और मैकेनिक उधारी हिसाब आसानी से बोलकर देखें।',
      en: 'Welcome to Auto Spares! Manage 2-wheeler and 4-wheeler parts, engine oils, brake pads, filters, and garage mechanic credit ledgers.',
    },
    assistantDbChecking: 'Checking live Auto Spares DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Engine oil stock entha?', 'Mechanic Shiva ki 1850 spares udhar rayi')...",
    suggestions: [
      { label: '🔥 High demand engine oils & spares?', query: 'Which auto parts are trending and selling fast?' },
      { label: '⚠️ Brake pads & oil low stock check', query: 'What auto spares are low stock?' },
      { label: '4T 10W-30 Engine Oil bottles stock entha undi?', query: '4T 10W-30 Engine Oil bottles stock entha undi?' },
      { label: 'Add 10 sets Front Disc Brake Pads', query: 'Add 10 sets Front Disc Brake Pads' },
      { label: 'Spark Plugs stock check cheyyi', query: 'Spark Plugs stock check cheyyi' },
      { label: 'Mechanic Shiva ki 1850 spares udhar rayi', query: 'Mechanic Shiva ki 1850 spares udhar rayi' },
      { label: 'Exide Two-Wheeler Battery stock entha?', query: 'Exide Two-Wheeler Battery stock entha?' },
      { label: 'How much loan does Mechanic Shiva have?', query: 'How much loan does Mechanic Shiva have?' },
      { label: 'Drive Chain Sprocket kit stock check cheyyi', query: 'Drive Chain Sprocket kit stock check cheyyi' },
      { label: 'Clear loan of Mechanic Shiva', query: 'Clear loan of Mechanic Shiva' },
    ],
  },

  vegetables: {
    id: 'vegetables',
    name: 'Vegetable & Fruit Market',
    emoji: '🥬',
    defaultShopName: 'Sri Lakshmi Fresh Veg & Fruits',
    voiceExample: {
      te: '"50 కేజీల టమాటాలు కొన్నాం" లేదా "ఉల్లిపాయలు, బంగాళాదుంపలు స్టాక్ ఎంత ఉంది?"',
      hi: '"50 किलो टमाटर आया" या "प्याज और आलू का स्टॉक कितना है?"',
      en: '"Add 50 kg tomatoes" or "How much onions & potatoes left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Tomato stock entha?", "Onions stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ కూరగాయలు & పండ్ల మార్కెట్ వాయిస్ అసిస్టెంట్. టమాటాలు, ఉల్లిపాయలు, ఆపిల్స్ తాజా నిల్వలు మరియు హోటల్/కస్టమర్ల రోజువారీ బకాయిలు వాయిస్ తో రికార్డ్ చేయండి.',
      hi: 'नमस्ते! मैं आपका सब्जी व फल मंडी वॉयस सहायक हूँ। टमाटर, प्याज, आलू, सेब का ताजा स्टॉक और मंडी भाव बोलकर रिकॉर्ड करें।',
      en: 'Welcome to Fresh Veg & Fruits Market! Monitor perishable crate weights, daily wholesale arrivals, tomato/onion stocks, and hotel credit accounts.',
    },
    assistantDbChecking: 'Checking live Veg & Fruits DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Tomatoes stock entha?', 'Mess Narayana ki 450 veg udhar rayi')...",
    suggestions: [
      { label: '🔥 Fast-moving daily vegetables?', query: 'Which vegetables are selling fast and trending?' },
      { label: '⚠️ Perishable low stock & reorder alert', query: 'What vegetables are low stock?' },
      { label: 'Hybrid Tomatoes (టమాటాలు) stock entha undi?', query: 'Hybrid Tomatoes stock entha undi?' },
      { label: 'Add 50 kg Onions (ఉల్లిపాయలు)', query: 'Add 50 kg Onions' },
      { label: 'Kashmir Apples crates stock check cheyyi', query: 'Kashmir Apples crates stock check cheyyi' },
      { label: 'Mess Narayana ki 450 veg items udhar rayi', query: 'Mess Narayana ki 450 veg items udhar rayi' },
      { label: 'Fresh Coriander bunches stock సరిపోతుందా?', query: 'Fresh Coriander bunches stock సరిపోతుందా?' },
      { label: 'How much loan does Mess Narayana have?', query: 'How much loan does Mess Narayana have?' },
      { label: 'Potatoes (బంగాళాదుంపలు) stock entha?', query: 'Potatoes stock entha?' },
      { label: 'Clear loan of Mess Narayana', query: 'Clear loan of Mess Narayana' },
    ],
  },

  electronics: {
    id: 'electronics',
    name: 'Electronics & Mobiles',
    emoji: '📱',
    defaultShopName: 'Sri Tech Zone Mobiles & Electronics',
    voiceExample: {
      te: '"3 రెడ్‌మి మొబైల్స్ అమ్మాం" లేదా "టైప్-సి ఛార్జర్లు, ఇయర్‌బడ్స్ స్టాక్ ఎంత ఉంది?"',
      hi: '"3 रेडमी मोबाइल बिका" या "टाइप-सी चार्जर और ईयरबड्स का स्टॉक कितना है?"',
      en: '"Sold 3 Redmi mobiles" or "How much Type-C chargers & earbuds left?"',
    },
    askPlaceholder: 'Ask in Telugu, Hindi or English (e.g. "Mobile chargers stock entha?", "Earbuds stock")...',
    assistantGreeting: {
      te: 'నమస్కారం! నేను మీ మొబైల్స్ & ఎలక్ట్రానిక్స్ వాయిస్ అసిస్టెంట్. స్మార్ట్‌ఫోన్లు, ఫాస్ట్ ఛార్జర్లు, ఇయర్‌బడ్స్, టెంపర్డ్ గ్లాస్ స్టాక్ మరియు ఈఎంఐ/ఉధార్ లెడ్జర్ వాయిస్ తో రికార్డ్ చేయండి.',
      hi: 'नमस्ते! मैं आपका इलेक्ट्रॉनिक्स व मोबाइल स्टोर वॉयस सहायक हूँ। स्मार्टफोन, चार्जर, ईयरफोन का स्टॉक और ग्राहक ईएमआई/उधारी आसानी से बोलें।',
      en: 'Welcome to Mobiles & Electronics! Track smartphones, fast chargers, Bluetooth earbuds, mobile accessories, warranty items, and customer credit.',
    },
    assistantDbChecking: 'Checking live Electronics DB...',
    manualInputPlaceholder: "Ask or type command (e.g. 'Redmi 5G stock entha?', 'Kalyan ki 1500 charger udhar rayi')...",
    suggestions: [
      { label: '🔥 Trending smartphones & fast chargers?', query: 'Which mobile accessories and phones are selling fast?' },
      { label: '⚠️ Low stock earbuds & chargers check', query: 'What electronics items have low stock?' },
      { label: 'Redmi 13C 5G mobiles stock entha undi?', query: 'Redmi 13C 5G mobiles stock entha undi?' },
      { label: 'Add 10 units 20W Type-C Fast Chargers', query: 'Add 10 units 20W Type-C Fast Chargers' },
      { label: 'Bluetooth Wireless Earbuds stock check cheyyi', query: 'Bluetooth Wireless Earbuds stock check cheyyi' },
      { label: 'Kalyan ki 1500 charger tempered glass udhar rayi', query: 'Kalyan ki 1500 charger tempered glass udhar rayi' },
      { label: 'Boat BassHeads earphones stock entha?', query: 'Boat BassHeads earphones stock entha?' },
      { label: 'How much loan does Kalyan have?', query: 'How much loan does Kalyan have?' },
      { label: 'Tempered Glass 11D stock check cheyyi', query: 'Tempered Glass 11D stock check cheyyi' },
      { label: 'Clear loan of Kalyan', query: 'Clear loan of Kalyan' },
    ],
  },
};

/**
 * Retrieve the active persona given a store type slug or fallback to kirana
 */
export function getStorePersona(storeType?: string | null): StorePersona {
  if (!storeType) {
    const saved = localStorage.getItem('dukaansetu_store_type');
    if (saved && STORE_PERSONAS[saved]) {
      return STORE_PERSONAS[saved];
    }
    return STORE_PERSONAS.kirana;
  }
  const normalized = storeType.toLowerCase().trim();
  return STORE_PERSONAS[normalized] || STORE_PERSONAS.kirana;
}
