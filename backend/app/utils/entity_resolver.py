"""DukaanSetu — Kirana Entity Resolution & Terminology Normalization Engine.
Provides robust multilingual resolution for products, customers, suppliers, units, and trade terms
across Telugu, Hindi, English, and colloquial Indian retail phrasing.
Zero random fallbacks: ambiguous or missing entities explicitly trigger clarification.
"""
import re
import difflib
import logging

logger = logging.getLogger(__name__)

# Standard Indian Kirana Synonym & Transliteration Dictionary
KIRANA_PRODUCT_SYNONYMS = {
    # Rice / Grains
    'biyyam': 'Rice',
    'biyyamu': 'Rice',
    'chawal': 'Rice',
    'arisi': 'Rice',
    'tandula': 'Rice',
    'rice': 'Rice',
    'sona masoori': 'Rice',
    'basmati': 'Rice',

    # Wheat / Flour
    'godhuma': 'Wheat',
    'godhumalu': 'Wheat',
    'gehun': 'Wheat',
    'aata': 'Wheat Flour',
    'godhuma pindi': 'Wheat Flour',
    'maida': 'Maida',

    # Sugar / Jaggery
    'chakkera': 'Sugar',
    'chakera': 'Sugar',
    'panchadara': 'Sugar',
    'chini': 'Sugar',
    'shakkar': 'Sugar',
    'sugar': 'Sugar',
    'bellam': 'Jaggery',
    'gud': 'Jaggery',
    'jaggery': 'Jaggery',

    # Oils & Ghee
    'nune': 'Sunflower Oil',
    'tel': 'Sunflower Oil',
    'oil': 'Sunflower Oil',
    'sunflower oil': 'Sunflower Oil',
    'sunflower nune': 'Sunflower Oil',
    'verusenaga nune': 'Groundnut Oil',
    'groundnut oil': 'Groundnut Oil',
    'mustard oil': 'Mustard Oil',
    'sarson tel': 'Mustard Oil',
    'ghee': 'Ghee',
    'neyyi': 'Ghee',

    # Pulses & Dal
    'kandi pappu': 'Toor Dal',
    'kandi': 'Toor Dal',
    'toor dal': 'Toor Dal',
    'tur dal': 'Toor Dal',
    'arhar dal': 'Toor Dal',
    'dal': 'Toor Dal',
    'pesara pappu': 'Moong Dal',
    'moong dal': 'Moong Dal',
    'minapa pappu': 'Urad Dal',
    'urad dal': 'Urad Dal',
    'senaga pappu': 'Chana Dal',
    'chana dal': 'Chana Dal',

    # FMCG & Beverages
    'parle': 'Parle-G Biscuits',
    'parle-g': 'Parle-G Biscuits',
    'parle g': 'Parle-G Biscuits',
    'biscuit': 'Parle-G Biscuits',
    'biscuits': 'Parle-G Biscuits',
    'red label': 'Red Label Tea',
    'tea': 'Red Label Tea',
    'chai': 'Red Label Tea',
    'tea podi': 'Red Label Tea',
    'chaipatti': 'Red Label Tea',
    'coffee': 'Nescafe Coffee',
    'nescafe': 'Nescafe Coffee',
    'coffee podi': 'Nescafe Coffee',
    'milk': 'Amul Milk',
    'paalu': 'Amul Milk',
    'doodh': 'Amul Milk',

    # Telugu script product synonyms
    'రైస్': 'Rice',
    'బియ్యం': 'Rice',
    'బియ్యము': 'Rice',
    'సోనా మసూరి': 'Rice',
    'బాస్మతి': 'Rice',
    'గోధుమ': 'Wheat',
    'గోధుమలు': 'Wheat',
    'గోధుమ పిండి': 'Wheat Flour',
    'మైదా': 'Maida',
    'చక్కెర': 'Sugar',
    'చక్కర': 'Sugar',
    'పంచదార': 'Sugar',
    'షుగర్': 'Sugar',
    'బెల్లం': 'Jaggery',
    'నూనె': 'Sunflower Oil',
    'ఆయిల్': 'Sunflower Oil',
    'సన్‌ఫ్లవర్': 'Sunflower Oil',
    'వేరుశెనగ నూనె': 'Groundnut Oil',
    'నెయ్యి': 'Ghee',
    'కందిపప్పు': 'Toor Dal',
    'కంది పప్పు': 'Toor Dal',
    'పప్పు': 'Toor Dal',
    'పెసరపప్పు': 'Moong Dal',
    'మినప్పప్పు': 'Urad Dal',
    'శనగపప్పు': 'Chana Dal',
    'బిస్కెట్లు': 'Parle-G Biscuits',
    'టీ': 'Red Label Tea',
    'టీ పొడి': 'Red Label Tea',
    'కాఫీ': 'Nescafe Coffee',
    'పాలు': 'Amul Milk',

    # Jewellery Synonyms (Telugu, Hindi, English, Transliteration)
    'gold': '22K Gold Chain',
    'bhangaram': '22K Gold Chain',
    'bangaram': '22K Gold Chain',
    'sona': '22K Gold Chain',
    'gold chain': '22K Gold Chain',
    'chain': '22K Gold Chain',
    'golusu': '22K Gold Chain',
    'bhangaru golusu': '22K Gold Chain',
    'gold bangles': '22K Gold Bangles',
    'bangles': '22K Gold Bangles',
    'gajulu': '22K Gold Bangles',
    'bhangaru gajulu': '22K Gold Bangles',
    'kangan': '22K Gold Bangles',
    'gold ring': '22K Gold Ring',
    'ring': '22K Gold Ring',
    'ungaram': '22K Gold Ring',
    'bhangaru ungaram': '22K Gold Ring',
    'anguthi': '22K Gold Ring',
    'temple haram': '22K Temple Haramu',
    'haram': '22K Temple Haramu',
    'buttalu': '22K Jhumkas / Buttalu',
    'jhumkas': '22K Jhumkas / Buttalu',
    'silver': '92.5 Silver Anklets / Pattilu',
    'vendi': '92.5 Silver Anklets / Pattilu',
    'chandi': '92.5 Silver Anklets / Pattilu',
    'pattilu': '92.5 Silver Anklets / Pattilu',
    'vendi pattilu': '92.5 Silver Anklets / Pattilu',
    'payal': '92.5 Silver Anklets / Pattilu',
    'deepam': 'Silver Kamakshi Pooja Lamp',
    'kamakshi deepam': 'Silver Kamakshi Pooja Lamp',
    'vendi deepam': 'Silver Kamakshi Pooja Lamp',
    'diya': 'Silver Kamakshi Pooja Lamp',
    'silver plate': 'Silver Dinner Plate',
    'vendi kancham': 'Silver Dinner Plate',
    'diamond ring': '18K Diamond Solitaire Ring',
    'vajram': '18K Diamond Solitaire Ring',
    'heera': '18K Diamond Solitaire Ring',
    'gold coin': '24K Pure Gold Coin 999',
    'coin': '24K Pure Gold Coin 999',
    'bhangaru coin': '24K Pure Gold Coin 999',
    'sikka': '24K Pure Gold Coin 999',
    'బంగారం': '22K Gold Chain',
    'గొలుసు': '22K Gold Chain',
    'గాజులు': '22K Gold Bangles',
    'ఉంగరం': '22K Gold Ring',
    'వెండి': '92.5 Silver Anklets / Pattilu',
    'పట్టీలు': '92.5 Silver Anklets / Pattilu',
    'దీపం': 'Silver Kamakshi Pooja Lamp',

    # Flower Synonyms (Telugu, Hindi, English, Transliteration)
    'jasmine': 'Jasmine / Mallepoolu',
    'mallepoolu': 'Jasmine / Mallepoolu',
    'malle': 'Jasmine / Mallepoolu',
    'malli': 'Jasmine / Mallepoolu',
    'mogra': 'Jasmine / Mallepoolu',
    'marigold': 'Yellow Marigold / Banthi',
    'banthi': 'Yellow Marigold / Banthi',
    'banthipoolu': 'Yellow Marigold / Banthi',
    'genda': 'Yellow Marigold / Banthi',
    'rose': 'Red Dutch Roses',
    'roses': 'Red Dutch Roses',
    'gulabi': 'Red Dutch Roses',
    'gulabi poolu': 'Red Dutch Roses',
    'gulab': 'Red Dutch Roses',
    'chrysanthemum': 'Chrysanthemum / Chamanthi',
    'chamanthi': 'Chrysanthemum / Chamanthi',
    'chamanthipoolu': 'Chrysanthemum / Chamanthi',
    'sevanti': 'Chrysanthemum / Chamanthi',
    'crossandra': 'Crossandra / Kanakambaram',
    'kanakambaram': 'Crossandra / Kanakambaram',
    'kanakambaralu': 'Crossandra / Kanakambaram',
    'lotus': 'Pink Lotus / Kamalam',
    'kamalam': 'Pink Lotus / Kamalam',
    'tamara': 'Pink Lotus / Kamalam',
    'tamarapoolu': 'Pink Lotus / Kamalam',
    'kamal': 'Pink Lotus / Kamalam',
    'garland': 'Wedding Rose & Jasmine Garlands',
    'garlands': 'Wedding Rose & Jasmine Garlands',
    'danda': 'Wedding Rose & Jasmine Garlands',
    'dandalu': 'Wedding Rose & Jasmine Garlands',
    'kalyana dandalu': 'Wedding Rose & Jasmine Garlands',
    'maru': 'Fragrant Maru Bundles',
    'maruvamu': 'Fragrant Leaves & Foliage',
    'tulasi': 'Temple Tulasi Garland',
    'tulasi mala': 'Temple Tulasi Garland',
    'మల్లెపూలు': 'Jasmine / Mallepoolu',
    'బంతిపూలు': 'Yellow Marigold / Banthi',
    'గులాబీలు': 'Red Dutch Roses',
    'చామంతి': 'Chrysanthemum / Chamanthi',
    'తామరపూలు': 'Pink Lotus / Kamalam',
    'దండలు': 'Wedding Rose & Jasmine Garlands',

    # Clothing & Textiles
    'kanchi pattu saree': 'Kanchi Pattu Saree',
    'pattu saree': 'Kanchi Pattu Saree',
    'saree': 'Kanchi Pattu Saree',
    'sarees': 'Kanchi Pattu Saree',
    'cheera': 'Kanchi Pattu Saree',
    'cheeralu': 'Kanchi Pattu Saree',
    'చీర': 'Kanchi Pattu Saree',
    'చీరలు': 'Kanchi Pattu Saree',
    'shirt': "Cotton Men's Formal Shirt",
    'shirts': "Cotton Men's Formal Shirt",
    'cotton shirt': "Cotton Men's Formal Shirt",
    'షర్టు': "Cotton Men's Formal Shirt",
    'jeans': "Levi's Denim Jeans 32/34",
    'pants': "Levi's Denim Jeans 32/34",
    'jeans pant': "Levi's Denim Jeans 32/34",
    'జీన్స్': "Levi's Denim Jeans 32/34",
    'kurti': "Women's Cotton Kurti / Dupatta Set",
    'kurta': "Women's Cotton Kurti / Dupatta Set",
    'dhoti': 'Pure Cotton Dhoti & Kanduva',
    'dhavathi': 'Pure Cotton Dhoti & Kanduva',
    'dhovati': 'Pure Cotton Dhoti & Kanduva',
    'ధోవతి': 'Pure Cotton Dhoti & Kanduva',
    'school uniform': 'School Uniform Fabric Set',
    'uniform': 'School Uniform Fabric Set',

    # Pharmacy & Medical
    'dolo': 'Dolo 650mg Tablets',
    'dolo 650': 'Dolo 650mg Tablets',
    'డోలో': 'Dolo 650mg Tablets',
    'paracetamol': 'Dolo 650mg Tablets',
    'crocin': 'Crocin Advance 500mg',
    'క్రోసిన్': 'Crocin Advance 500mg',
    'crocin advance': 'Crocin Advance 500mg',
    'benadryl': 'Benadryl Cough Syrup 100ml',
    'cough syrup': 'Benadryl Cough Syrup 100ml',
    'daggu mandhu': 'Benadryl Cough Syrup 100ml',
    'దగ్గు మందు': 'Benadryl Cough Syrup 100ml',
    'insulin': 'Human Mixtard 30/70 Insulin',
    'ఇన్సులిన్': 'Human Mixtard 30/70 Insulin',
    'ors': 'ORS Electral Powder 21.8g',
    'electral': 'ORS Electral Powder 21.8g',
    'ఓఆర్ఎస్': 'ORS Electral Powder 21.8g',
    'omeprazole': 'Omeprazole 20mg Capsules',
    'gas tablet': 'Omeprazole 20mg Capsules',
    'గ్యాస్ టాబ్లెట్': 'Omeprazole 20mg Capsules',
    'bp monitor': 'Digital BP Monitor',
    'bp machine': 'Digital BP Monitor',
    'బీపీ మిషన్': 'Digital BP Monitor',

    # Bakery & Confectionery
    'black forest': 'Black Forest Cake 1kg',
    'cake': 'Black Forest Cake 1kg',
    'కేక్': 'Black Forest Cake 1kg',
    'bread': 'Fresh Milk Bread 400g',
    'milk bread': 'Fresh Milk Bread 400g',
    'బ్రెడ్': 'Fresh Milk Bread 400g',
    'mysore pak': 'Ghee Mysore Pak',
    'మైసూర్ పాక్': 'Ghee Mysore Pak',
    'kaju katli': 'Kaju Katli',
    'కాజు కట్లి': 'Kaju Katli',
    'puff': 'Egg & Veg Puff',
    'puffs': 'Egg & Veg Puff',
    'పఫ్': 'Egg & Veg Puff',
    'osmania biscuits': 'Osmania Tea Biscuits',
    'ఉస్మానియా బిస్కెట్లు': 'Osmania Tea Biscuits',

    'cream roll': 'Vanilla Fresh Cream Roll',
    'fresh cream roll': 'Vanilla Fresh Cream Roll',
    'క్రీమ్ రోల్': 'Vanilla Fresh Cream Roll',
    'sweet': 'Ghee Mysore Pak',
    'sweets': 'Ghee Mysore Pak',
    'mithai': 'Ghee Mysore Pak',
    'స్వీట్లు': 'Ghee Mysore Pak',

    # Restaurant & Tiffin
    'biryani': 'Special Chicken Dum Biryani',
    'chicken biryani': 'Special Chicken Dum Biryani',
    'బిర్యానీ': 'Special Chicken Dum Biryani',
    'dosa': 'Ghee Masala Dosa',
    'masala dosa': 'Ghee Masala Dosa',
    'దోశ': 'Ghee Masala Dosa',
    'idli': 'Steamed Idli Sambar',
    'idli sambar': 'Steamed Idli Sambar',
    'ఇడ్లీ': 'Steamed Idli Sambar',
    'meals': 'South Indian Thali Meals',
    'thali': 'South Indian Thali Meals',
    'భోజనం': 'South Indian Thali Meals',
    'basmati rice': 'Raw Basmati Rice Bulk 25kg',
    'cooking oil': 'Cooking Sunflower Oil Tin 15L',
    'oil tin': 'Cooking Sunflower Oil Tin 15L',
    'chapathi': 'Chapathi with Mixed Veg Kurma',
    'chapati': 'Chapathi with Mixed Veg Kurma',
    'chapatis': 'Chapathi with Mixed Veg Kurma',
    'చపాతీ': 'Chapathi with Mixed Veg Kurma',
    'parotta': 'Chapathi with Mixed Veg Kurma',
    'roti': 'Chapathi with Mixed Veg Kurma',
    'kurma': 'Chapathi with Mixed Veg Kurma',

    # Tea & Coffee
    'irani chai': 'Special Irani Dum Chai',
    'dum chai': 'Special Irani Dum Chai',
    'చాయ్': 'Special Irani Dum Chai',
    'cutting': 'Special Irani Dum Chai',
    'cutting chai': 'Special Irani Dum Chai',
    'filter coffee': 'South Indian Filter Coffee',
    'ఫిల్టర్ కాఫీ': 'South Indian Filter Coffee',
    'samosa': 'Hot Onion Samosa',
    'సమోసా': 'Hot Onion Samosa',
    'bajji': 'Mirchi Bajji',
    'mirchi bajji': 'Mirchi Bajji',
    'మిర్చి బజ్జీ': 'Mirchi Bajji',
    'buffalo milk': 'Buffalo Milk 1 Litre',
    'గేదె పాలు': 'Buffalo Milk 1 Litre',
    'bun maska': 'Bun Maska',
    'maska bun': 'Bun Maska',
    'bun': 'Bun Maska',
    'బన్': 'Bun Maska',
    'బన్ మస్కా': 'Bun Maska',

    # Hardware & Electrical
    'pvc pipe': 'PVC Pipe 1 inch 10ft',
    'pipe': 'PVC Pipe 1 inch 10ft',
    'పైపు': 'PVC Pipe 1 inch 10ft',
    'copper wire': 'Finolex Copper Wire 2.5 sq mm',
    'wire': 'Finolex Copper Wire 2.5 sq mm',
    'వైరు': 'Finolex Copper Wire 2.5 sq mm',
    'modular switch': 'Anchor Roma Modular Switch 6A',
    'switch': 'Anchor Roma Modular Switch 6A',
    'స్విచ్': 'Anchor Roma Modular Switch 6A',
    'cement': 'UltraTech Cement 50kg',
    'ultratech': 'UltraTech Cement 50kg',
    'సిమెంట్': 'UltraTech Cement 50kg',
    'asian paints': 'Asian Paints Apex White 20L',
    'paint': 'Asian Paints Apex White 20L',
    'పెయింట్': 'Asian Paints Apex White 20L',
    'screws': 'Steel Screws & Rawlplugs Box',
    'స్క్రూలు': 'Steel Screws & Rawlplugs Box',
    'led bulb': '9W LED Bulbs Cool White',
    'led': '9W LED Bulbs Cool White',
    'bulb': '9W LED Bulbs Cool White',
    'bulbs': '9W LED Bulbs Cool White',
    'ఎల్ఈడీ బల్బు': '9W LED Bulbs Cool White',
    'బల్బు': '9W LED Bulbs Cool White',

    # Auto Spares
    'engine oil': 'Castrol Activ 4T 20W-40 1L',
    'castrol': 'Castrol Activ 4T 20W-40 1L',
    'brake shoes': 'Hero Splendor Brake Shoes',
    'brake pad': 'Hero Splendor Brake Shoes',
    'బ్రేక్': 'Hero Splendor Brake Shoes',
    'battery': 'Amaron 12V Bike Battery 4Ah',
    'bike battery': 'Amaron 12V Bike Battery 4Ah',
    'బ్యాటరీ': 'Amaron 12V Bike Battery 4Ah',
    'tyre': 'MRF Nylogrip Tyre 2.75-18',
    'mrf tyre': 'MRF Nylogrip Tyre 2.75-18',
    'టైరు': 'MRF Nylogrip Tyre 2.75-18',
    'clutch cable': 'Clutch Cable for Bajaj Pulsar',
    'spark plug': 'Spark Plug NGK 2-Wheeler',
    'ప్లగ్': 'Spark Plug NGK 2-Wheeler',
    'chain sprocket': 'Rolon Chain Sprocket Kit',
    'sprocket': 'Rolon Chain Sprocket Kit',
    'chain kit': 'Rolon Chain Sprocket Kit',
    'చైన్ కిట్': 'Rolon Chain Sprocket Kit',
    'చైన్ స్ప్రాకెట్': 'Rolon Chain Sprocket Kit',

    # Vegetables & Fruits
    'tomato': 'Fresh Country Tomatoes / Tamata',
    'tomatoes': 'Fresh Country Tomatoes / Tamata',
    'tamata': 'Fresh Country Tomatoes / Tamata',
    'టమాటా': 'Fresh Country Tomatoes / Tamata',
    'onion': 'Onion / Ullipaya',
    'onions': 'Onion / Ullipaya',
    'ullipaya': 'Onion / Ullipaya',
    'ullipayalu': 'Onion / Ullipaya',
    'pyaz': 'Onion / Ullipaya',
    'ఉల్లిపాయలు': 'Onion / Ullipaya',
    'potato': 'Potato / Bangala Dumpa',
    'potatoes': 'Potato / Bangala Dumpa',
    'aloo': 'Potato / Bangala Dumpa',
    'bangala dumpa': 'Potato / Bangala Dumpa',
    'బంగాళాదుంపలు': 'Potato / Bangala Dumpa',
    'green chillies': 'Green Chillies / Pachi Mirchi',
    'chillies': 'Green Chillies / Pachi Mirchi',
    'pachi mirchi': 'Green Chillies / Pachi Mirchi',
    'మిర్చి': 'Green Chillies / Pachi Mirchi',
    'palak': 'Fresh Palak / Spinach',
    'spinach': 'Fresh Palak / Spinach',
    'పాలకూర': 'Fresh Palak / Spinach',
    'banana': 'Yelakki Small Bananas',
    'bananas': 'Yelakki Small Bananas',
    'arati pandlu': 'Yelakki Small Bananas',
    'అరటిపండ్లు': 'Yelakki Small Bananas',
    'apple': 'Kashmir Red Apples',
    'apples': 'Kashmir Red Apples',
    'kashmir apples': 'Kashmir Red Apples',
    'యాపిల్స్': 'Kashmir Red Apples',

    # Electronics & Mobile
    'samsung': 'Samsung Galaxy A15 5G 128GB',
    'mobile': 'Samsung Galaxy A15 5G 128GB',
    'మొబైల్': 'Samsung Galaxy A15 5G 128GB',
    'earbuds': 'boAt Airdopes 141 Bluetooth Earbuds',
    'airdopes': 'boAt Airdopes 141 Bluetooth Earbuds',
    'boat': 'boAt Airdopes 141 Bluetooth Earbuds',
    'ఇయర్ బడ్స్': 'boAt Airdopes 141 Bluetooth Earbuds',
    'charger': 'Fast 20W Type-C Charger Adapter',
    'fast charger': 'Fast 20W Type-C Charger Adapter',
    'ఛార్జర్': 'Fast 20W Type-C Charger Adapter',
    'power bank': '10000mAh Dual USB Power Bank',
    'powerbank': '10000mAh Dual USB Power Bank',
    'పవర్ బ్యాంక్': '10000mAh Dual USB Power Bank',
    'type-c cable': 'Braided 1.5m Type-C Fast Cable',
    'tempered glass': '9D Edge-to-Edge Tempered Glass',
    'screen guard': '9D Edge-to-Edge Tempered Glass',
    'స్క్రీన్ గార్డ్': '9D Edge-to-Edge Tempered Glass',
    'smart watch': 'Noise ColorFit Pulse Smart Watch',
    'smartwatch': 'Noise ColorFit Pulse Smart Watch',
    'watch': 'Noise ColorFit Pulse Smart Watch',
    'స్మార్ట్ వాచ్': 'Noise ColorFit Pulse Smart Watch',

    # Clothing & Textiles Additions
    'handloom saree': 'Handloom Cotton Saree',
    'cotton saree': 'Handloom Cotton Saree',
    'చేనేత చీర': 'Handloom Cotton Saree',

    # Flowers & Pooja Additions
    'pooja camphor': 'Pooja Camphor / Karpuram',
    'camphor': 'Pooja Camphor / Karpuram',
    'karpuram': 'Pooja Camphor / Karpuram',
    'కర్పూరం': 'Pooja Camphor / Karpuram',
    'pooja ghee': 'Cow Ghee for Deepam',
    'deepam ghee': 'Cow Ghee for Deepam',
    'దీపం నెయ్యి': 'Cow Ghee for Deepam',
}

# Unit Normalization Map
UNIT_MAP = {
    'bag': 'bag',
    'bags': 'bag',
    'bastha': 'bag',
    'basthalu': 'bag',
    'borya': 'bag',
    'bori': 'bag',
    'sack': 'bag',
    'sacks': 'bag',
    'kg': 'kg',
    'kgs': 'kg',
    'kilo': 'kg',
    'kilos': 'kg',
    'kilogram': 'kg',
    'kilograms': 'kg',
    'g': 'gram',
    'gram': 'gram',
    'grams': 'gram',
    'gm': 'gram',
    'gms': 'gram',
    'litre': 'litre',
    'litres': 'litre',
    'liter': 'litre',
    'liters': 'litre',
    'l': 'litre',
    'ltr': 'litre',
    'ml': 'ml',
    'packet': 'packet',
    'packets': 'packet',
    'pocket': 'packet',
    'pockets': 'packet',
    'pkt': 'packet',
    'pkts': 'packet',
    'piece': 'piece',
    'pieces': 'piece',
    'pcs': 'piece',
    'pc': 'piece',
    'nagulu': 'piece',
    'box': 'box',
    'boxes': 'box',
    'pette': 'box',
    'pettelu': 'box',
    'carton': 'box',

    # Jewellery Units
    'tola': 'tola',
    'tolas': 'tola',
    'thulam': 'tola',
    'thulalu': 'tola',
    'tulam': 'tola',
    'sovereign': 'pavan',
    'sovereigns': 'pavan',
    'pavan': 'pavan',
    'pavala': 'pavan',
    'carat': 'carat',
    'carats': 'carat',
    'ct': 'carat',
    'mg': 'mg',
    'milligram': 'mg',
    'milligrams': 'mg',

    # Flower Units
    'mora': 'mora',
    'moras': 'mora',
    'moora': 'mora',
    'moorala': 'mora',
    'muralu': 'mora',
    'kattu': 'kattu',
    'kattulu': 'kattu',
    'kattalu': 'kattu',
    'bundle': 'bundle',
    'bundles': 'bundle',
    'mala': 'garland',
    'malalu': 'garland',
    'danda': 'garland',
    'dandalu': 'garland',
    'garland': 'garland',
    'garlands': 'garland',
    'butta': 'basket',
    'buttas': 'basket',
    'buttalu': 'basket',
    'basket': 'basket',
    'baskets': 'basket',
    'stem': 'stem',
    'stems': 'stem',
    'set': 'set',
    'sets': 'set',
    'jatha': 'piece',
    'jathalu': 'piece',
    'cartons': 'box',
    'can': 'can',
    'cans': 'can',
    'dabba': 'can',
    'dabbalu': 'can',
    'tin': 'can',
    'tins': 'can',
    'dozen': 'dozen',
    'dozens': 'dozen',
    'katta': 'bunch',
    'kattalu': 'bunch',
    'bunch': 'bunch',
    'bunches': 'bunch',
    'meter': 'meter',
    'meters': 'meter',
    'metre': 'meter',
    'metres': 'meter',
    'meeterlu': 'meter',
    'roll': 'roll',
    'rolls': 'roll',
    'strip': 'strip',
    'strips': 'strip',
    'tablet': 'strip',
    'tablets': 'strip',
    'vial': 'vial',
    'vials': 'vial',
    'sachet': 'sachet',
    'sachets': 'sachet',
    'bottle': 'bottle',
    'bottles': 'bottle',
    'plate': 'plate',
    'plates': 'plate',
    'portion': 'plate',
    'cup': 'cup',
    'cups': 'cup',
    'length': 'length',
    'lengths': 'length',
    'bucket': 'bucket',
    'buckets': 'bucket',
    'unit': 'unit',
    'units': 'unit',
}

# Telugu & Hindi Word Numbers
WORD_NUMBERS = {
    # Telugu
    'oka': 1, 'okati': 1, 'voka': 1,
    'rendu': 2, 'iravai': 20,
    'moodu': 3, 'muppai': 30,
    'naalugu': 4, 'nalugu': 4, 'nalabhai': 40,
    'aidu': 5, 'ayidu': 5, 'yaabhai': 50, 'yabhai': 50,
    'aaru': 6, 'aravai': 60,
    'eedu': 7, 'yedu': 7, 'debbhai': 70,
    'enimidi': 8, 'yenimidi': 8, 'enabhai': 80,
    'thommidi': 9, 'thombhai': 90,
    'padi': 10, 'padhi': 10,
    'vanda': 100, 'vandha': 100,
    'veyyi': 1000, 'veye': 1000,

    # Hindi
    'ek': 1,
    'do': 2,
    'teen': 3,
    'chaar': 4, 'char': 4,
    'paanch': 5, 'panch': 5,
    'chhah': 6, 'che': 6,
    'saat': 7,
    'aath': 8,
    'nau': 9,
    'das': 10,
    'gyaarah': 11, 'baarah': 12, 'terah': 13, 'chaudah': 14, 'pandrah': 15,
    'bees': 20, 'tees': 30, 'chaalis': 40, 'pachaas': 50,
    'sau': 100, 'hazaar': 1000,
}


def normalize_unit(unit_str):
    """Normalize raw spoken unit to canonical unit string."""
    if not unit_str:
        return 'unit'
    cleaned = unit_str.lower().strip()
    return UNIT_MAP.get(cleaned, cleaned)


def extract_numbers_and_units(text):
    """Extract numeric quantity, price, and unit from text in Telugu, Hindi, or English."""
    cleaned = text.lower()
    qty = None
    price = None
    unit = None

    # Check for direct digit patterns: "5 bags", "10 kg", "1450 rupees", "₹500"
    # Price detection
    price_match = re.search(r'(?:₹|rs\.?|rupees?|roopayalu?|rupaye?)\s*(\d+(?:\.\d+)?)', cleaned)
    if not price_match:
        price_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:₹|rs\.?|rupees?|roopayalu?|rupaye?)', cleaned)
    if price_match:
        try:
            price = float(price_match.group(1))
        except ValueError:
            pass

    # Unit and Quantity detection
    for raw_u, std_u in UNIT_MAP.items():
        pattern = rf'(\d+(?:\.\d+)?)\s*{raw_u}\b'
        match = re.search(pattern, cleaned)
        if match:
            try:
                qty = float(match.group(1))
                unit = std_u
                break
            except ValueError:
                pass

    # Word numbers if no digit quantity found
    if qty is None:
        tokens = cleaned.split()
        for i, tok in enumerate(tokens):
            if tok in WORD_NUMBERS:
                qty = float(WORD_NUMBERS[tok])
                if i + 1 < len(tokens):
                    next_tok = tokens[i + 1]
                    if next_tok in UNIT_MAP:
                        unit = UNIT_MAP[next_tok]
                break

    # If quantity still not found, check any first standalone integer that isn't the price
    if qty is None:
        num_matches = re.findall(r'\b\d+(?:\.\d+)?\b', cleaned)
        for n in num_matches:
            val = float(n)
            if price is not None and val == price:
                continue
            qty = val
            break

    return {'quantity': qty, 'unit': unit, 'price': price}


def resolve_product(product_query, catalog_products, alias_records=None):
    """Resolve product query against current shop catalog with alias, local_name, and fuzzy matching.
    Returns dict:
      {
        'matched_product': product or None,
        'confidence': float,
        'ambiguous_candidates': [list of product names if ambiguous],
        'is_ambiguous': bool
      }
    NEVER defaults to catalog_products[0].
    """
    if not product_query or not catalog_products:
        return {'matched_product': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}

    query = product_query.lower().strip()

    # 1. Check Product Aliases table first (highest priority local mapping)
    if alias_records:
        for a in alias_records:
            alias_txt = a.get('alias', '').lower().strip()
            if alias_txt == query or (len(query) >= 3 and (alias_txt in query or query in alias_txt)):
                pid = a.get('product_id')
                prod = next((p for p in catalog_products if p['id'] == pid), None)
                if prod:
                    return {'matched_product': prod, 'confidence': 0.98, 'ambiguous_candidates': [], 'is_ambiguous': False}

    # 2. Exact and Substring Match against Product Names & Local Names
    exact_matches = []
    for p in catalog_products:
        pname = p['name'].lower()
        plocal = (p.get('local_name') or '').lower()
        ptelugu = (p.get('telugu_name') or '').lower()
        if query == pname or (plocal and query == plocal) or (ptelugu and query == ptelugu):
            return {'matched_product': p, 'confidence': 1.0, 'ambiguous_candidates': [], 'is_ambiguous': False}
        if (len(query) >= 3 and query in pname) or (plocal and len(query) >= 3 and query in plocal) or (ptelugu and len(query) >= 3 and query in ptelugu):
            exact_matches.append(p)

    if len(exact_matches) == 1:
        return {'matched_product': exact_matches[0], 'confidence': 0.95, 'ambiguous_candidates': [], 'is_ambiguous': False}
    elif len(exact_matches) > 1:
        return {
            'matched_product': None,
            'confidence': 0.5,
            'ambiguous_candidates': [p['name'] for p in exact_matches],
            'is_ambiguous': True
        }

    # 3. Check Built-in Kirana Synonyms & Transliterations
    synonym_target = KIRANA_PRODUCT_SYNONYMS.get(query)
    if not synonym_target:
        for term, target in KIRANA_PRODUCT_SYNONYMS.items():
            if term in query:
                synonym_target = target
                break

    if synonym_target:
        syn_matches = []
        synt = synonym_target.lower()
        for p in catalog_products:
            pname = p['name'].lower()
            plocal = (p.get('local_name') or '').lower()
            ptelugu = (p.get('telugu_name') or '').lower()
            if (synt in pname or pname in synt) or (plocal and (synt in plocal or plocal in synt)) or (ptelugu and (synt in ptelugu or ptelugu in synt)):
                syn_matches.append(p)
        if len(syn_matches) == 1:
            return {'matched_product': syn_matches[0], 'confidence': 0.95, 'ambiguous_candidates': [], 'is_ambiguous': False}
        elif len(syn_matches) > 1:
            return {
                'matched_product': None,
                'confidence': 0.5,
                'ambiguous_candidates': [p['name'] for p in syn_matches],
                'is_ambiguous': True
            }

    # 4. Fuzzy Matching with difflib
    scored_candidates = []
    for p in catalog_products:
        pname = p['name'].lower()
        plocal = (p.get('local_name') or '').lower()
        ratio_name = difflib.SequenceMatcher(None, query, pname).ratio()
        ratio_local = difflib.SequenceMatcher(None, query, plocal).ratio() if plocal else 0.0
        best_ratio = max(ratio_name, ratio_local)

        # Word-level token match bonus
        for word in pname.split():
            w_clean = re.sub(r'[^a-zA-Z0-9]', '', word.lower())
            if w_clean and (query == w_clean or difflib.SequenceMatcher(None, query, w_clean).ratio() > 0.82):
                best_ratio = max(best_ratio, 0.88)

        if best_ratio >= 0.60:
            scored_candidates.append((best_ratio, p))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    if not scored_candidates:
        return {'matched_product': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}

    top_score, top_prod = scored_candidates[0]

    # Check for close competitors (ambiguity)
    if len(scored_candidates) > 1:
        second_score, second_prod = scored_candidates[1]
        if (top_score - second_score) < 0.10 and second_score >= 0.70:
            return {
                'matched_product': None,
                'confidence': top_score,
                'ambiguous_candidates': [top_prod['name'], second_prod['name']],
                'is_ambiguous': True
            }

    if top_score >= 0.70:
        return {'matched_product': top_prod, 'confidence': round(top_score, 2), 'ambiguous_candidates': [], 'is_ambiguous': False}

    return {'matched_product': None, 'confidence': round(top_score, 2), 'ambiguous_candidates': [], 'is_ambiguous': False}


def resolve_customer(customer_query, customers_list):
    """Resolve customer name against shop's registered customers with phonetic, transliteration, and fuzzy matching.
    Returns:
      {
        'matched_customer': customer dict or None,
        'confidence': float,
        'ambiguous_candidates': [list of names],
        'is_ambiguous': bool
      }
    NEVER creates or assumes customer if ambiguous or unknown.
    """
    if not customer_query or not customers_list:
        return {'matched_customer': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}

    query = customer_query.lower().strip()
    query_clean = re.sub(r'[^a-z0-9]', '', query)

    # 1. Exact and normalized match
    for c in customers_list:
        cname = c['name'].lower().strip()
        primary_name = cname.split('(')[0].strip()
        cname_clean = re.sub(r'[^a-z0-9]', '', primary_name)
        if query == cname or query == primary_name or query_clean == cname_clean:
            return {'matched_customer': c, 'confidence': 1.0, 'ambiguous_candidates': [], 'is_ambiguous': False, 'is_new_customer': False}

    # 2. Token match against primary customer name (excluding notes in parentheses)
    matching_subs = []
    for c in customers_list:
        cname = c['name'].lower()
        primary_name = cname.split('(')[0].strip()
        primary_tokens = re.findall(r'\w+', primary_name)
        if query == primary_name or any(query == w for w in primary_tokens):
            matching_subs.append(c)

    if len(matching_subs) == 1:
        return {'matched_customer': matching_subs[0], 'confidence': 0.95, 'ambiguous_candidates': [], 'is_ambiguous': False, 'is_new_customer': False}
    elif len(matching_subs) > 1:
        return {
            'matched_customer': None,
            'confidence': 0.5,
            'ambiguous_candidates': [c['name'] for c in matching_subs],
            'is_ambiguous': True,
            'is_new_customer': False,
            'extracted_name': customer_query.strip().title()
        }

    # 3. Fuzzy matching with disambiguation check
    scored = []
    for c in customers_list:
        cname = c['name'].lower()
        primary_name = cname.split('(')[0].strip()
        first_token = primary_name.split()[0] if primary_name.split() else primary_name
        r1 = difflib.SequenceMatcher(None, query, primary_name).ratio()
        r2 = difflib.SequenceMatcher(None, query, first_token).ratio()
        score = max(r1, r2)
        if score >= 0.55:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return {
            'matched_customer': None,
            'confidence': 0.0,
            'ambiguous_candidates': [],
            'is_ambiguous': False,
            'is_new_customer': True,
            'extracted_name': customer_query.strip().title()
        }

    top_score, top_cust = scored[0]

    if len(scored) > 1:
        second_score, second_cust = scored[1]
        # If two distinct customers have close similarity scores (e.g. Ruthwik vs Prudhvi)
        if (top_score - second_score) < 0.15 and second_score >= 0.65:
            return {
                'matched_customer': None,
                'confidence': top_score,
                'ambiguous_candidates': [top_cust['name'], second_cust['name']],
                'is_ambiguous': True,
                'is_new_customer': False,
                'extracted_name': customer_query.strip().title()
            }

    if top_score >= 0.75:
        return {'matched_customer': top_cust, 'confidence': round(top_score, 2), 'ambiguous_candidates': [], 'is_ambiguous': False, 'is_new_customer': False}

    return {
        'matched_customer': None,
        'confidence': round(top_score, 2),
        'ambiguous_candidates': [],
        'is_ambiguous': False,
        'is_new_customer': True,
        'extracted_name': customer_query.strip().title()
    }


def extract_customer_from_loan_phrase(transcript):
    """Extract customer name from varied loan, credit, or udhar phrasing across English, Telugu, and Hindi."""
    if not transcript:
        return None
    t = transcript.strip()
    patterns = [
        # Clear / settle loan: "Clear loan of Ramesh" / "Clear Ramesh loan"
        r'clear\s+(?:the\s+)?(?:loan|udhar|debt|appu)\s+(?:of|for)\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)',
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+(?:loan|udhar|debt|appu)\s+(?:clear|settle|raddhu|maaf)',
        # "one person Rahul took a loan of 500" / "person Kiran has taken a loan"
        r'(?:one\s+)?person\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+(?:has\s+taken|took|borrowed)',
        # "Kiran has taken a loan of 500" / "Raju took a loan of 1000"
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+(?:has\s+taken|took)\s+(?:a\s+)?(?:loan|udhar|credit|debt|appu|karz)',
        # "Sita borrowed 300" / "Sita borrowed 500 loan"
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+borrowed\b',
        # "Loan of 500 to Mahesh" / "Give loan of 500 to Mahesh"
        r'(?:loan|udhar|credit|appu|karz)\s+(?:of\s+[\d,\.]+\s+)?(?:to|for)\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)',
        # "Add loan for Mahesh" / "Record loan for Mahesh"
        r'(?:add|record|create|give)\s+(?:a\s+)?(?:loan|udhar|credit|debt)\s+(?:of\s+[\d,\.]+\s+)?(?:to|for)\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)',
        # "Mahesh took 500 loan"
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+took\s+[\d,\.]+\s+(?:loan|udhar|appu|karz)\b',
        # Telugu: "రమేష్ అప్పు తీసుకున్నాడు" / "Ramesh appu theesukunnadu" / "Ramesh loan theesukunnadu"
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+(?:appu|loan|udhar)\s+(?:theesukunnadu|tesukunnadu|teeskunnadu|తీసుకున్నాడు)',
        # Hindi: "Ramesh ne 500 loan liya" / "Ramesh karz liya"
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+ne\s+(?:[\d,\.]+\s+)?(?:loan|udhar|karz)\s+liya',
        # Suffix matching: "Ramesh ki 500 udhar" / "Ramesh ko 500" / "Ramesh గారికి"
        r'\b([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)\s+(?:ki|ko|gaari|gari|nu|to|గారికి|గారి|కు|కి|ను|కో)\b',
        # "Add customer Ramesh"
        r'(?:add|create|new)\s+customer\s+([A-Za-z\u0c00-\u0c7f\u0900-\u097f]+)'
    ]
    stopwords = {
        'a', 'an', 'the', 'one', 'person', 'customer', 'new', 'item', 'loan', 'udhar', 'credit',
        'debt', 'cash', 'money', 'stock', 'today', 'yesterday', 'please', 'add', 'give', 'take',
        'took', 'clear', 'settle', 'forgive', 'delete', 'remove', 'check', 'show', 'view'
    }
    for p in patterns:
        m = re.search(p, t, re.IGNORECASE)
        if m:
            cand = m.group(1).strip()
            if cand.lower() not in stopwords and len(cand) >= 2:
                return cand.title()
    return None


def extract_phone_number(transcript):
    """Extract a 10-digit Indian phone number if spoken in the query."""
    if not transcript:
        return None
    m = re.search(r'(?:\+?91[\-\s]?)?([6-9]\d{9})\b', transcript)
    if m:
        return m.group(1)
    digits = re.findall(r'\b\d\b', transcript)
    if len(digits) == 10 and digits[0] in '6789':
        return ''.join(digits)
    return None


def resolve_supplier(supplier_query, suppliers_list):
    """Resolve supplier name against shop's registered suppliers."""
    if not supplier_query or not suppliers_list:
        return {'matched_supplier': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}

    query = supplier_query.lower().strip()
    for s in suppliers_list:
        if query in s['name'].lower():
            return {'matched_supplier': s, 'confidence': 0.95, 'ambiguous_candidates': [], 'is_ambiguous': False}

    scored = []
    for s in suppliers_list:
        score = difflib.SequenceMatcher(None, query, s['name'].lower()).ratio()
        if score >= 0.60:
            scored.append((score, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    if scored and scored[0][0] >= 0.70:
        return {'matched_supplier': scored[0][1], 'confidence': round(scored[0][0], 2), 'ambiguous_candidates': [], 'is_ambiguous': False}

    return {'matched_supplier': None, 'confidence': 0.0, 'ambiguous_candidates': [], 'is_ambiguous': False}
