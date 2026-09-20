"""Authentication routes."""
import uuid
from flask import Blueprint, request, g
from app.utils import require_auth, success_response, error_response
from app.utils.auth import DEMO_SHOP_MAP
from app.utils.supabase_client import get_supabase

auth_bp = Blueprint('auth', __name__)

# Initial seed templates for all 12 retail shop types
# Initial seed templates for all 12 retail shop types (7-8 products each)
STORE_SEED_DATA = {
    'kirana': {
        'categories': ['Grains & Rice', 'Pulses & Dal', 'Spices & Masala', 'Sugar & Jaggery', 'Oils & Ghee', 'Dairy', 'Beverages', 'Snacks & Biscuits', 'Cleaning & Household', 'Other'],
        'suppliers': [('Srinivas Wholesale Traders', '+91 9876543001'), ('Kishan Dal & Grains Agency', '+91 9876543002'), ('Vijaya Dairy & Oil Depot', '+91 9876543003')],
        'customers': [('Ramesh Kumar (Monthly Ration)', '+91 9848011221', 1250.0), ('Suresh Reddy (Teacher)', '+91 9848011222', 450.0)],
        'products': [
            {'name': 'Rice (Biyyam)', 'local_name': 'Biyyam', 'category': 'Grains & Rice', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 25, 'purchase_price': 1450, 'selling_price': 65, 'minimum_stock': 125, 'recommended_stock': 500, 'reorder_quantity': 250, 'stock': 450},
            {'name': 'Sugar (Chakkera)', 'local_name': 'Chakkera', 'category': 'Sugar & Jaggery', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 50, 'purchase_price': 2100, 'selling_price': 48, 'minimum_stock': 50, 'recommended_stock': 200, 'reorder_quantity': 100, 'stock': 180},
            {'name': 'Sunflower Oil (Nune)', 'local_name': 'Nune', 'category': 'Oils & Ghee', 'base_unit': 'litre', 'purchase_unit': 'litre', 'selling_unit': 'litre', 'conversion_factor': 1, 'purchase_price': 150, 'selling_price': 165, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 30, 'stock': 35},
            {'name': 'Toor Dal (Kandi Pappu)', 'local_name': 'Kandi Pappu', 'category': 'Pulses & Dal', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 25, 'purchase_price': 2750, 'selling_price': 125, 'minimum_stock': 25, 'recommended_stock': 100, 'reorder_quantity': 50, 'stock': 65},
            {'name': 'Wheat Flour / Aata (గోధుమ పిండి)', 'local_name': 'Aata', 'category': 'Grains & Rice', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 10, 'purchase_price': 380, 'selling_price': 45, 'minimum_stock': 20, 'recommended_stock': 80, 'reorder_quantity': 40, 'stock': 60},
            {'name': 'Parle-G Biscuits', 'local_name': 'Parle-G', 'category': 'Snacks & Biscuits', 'base_unit': 'packet', 'purchase_unit': 'carton', 'selling_unit': 'packet', 'conversion_factor': 24, 'purchase_price': 240, 'selling_price': 10, 'minimum_stock': 50, 'recommended_stock': 200, 'reorder_quantity': 96, 'stock': 120},
            {'name': 'Red Label Tea', 'local_name': 'Tea Podi', 'category': 'Beverages', 'base_unit': 'packet', 'purchase_unit': 'box', 'selling_unit': 'packet', 'conversion_factor': 12, 'purchase_price': 1200, 'selling_price': 110, 'minimum_stock': 20, 'recommended_stock': 60, 'reorder_quantity': 36, 'stock': 42},
            {'name': 'Jaggery / Bellam (బెల్లం)', 'local_name': 'Bellam', 'category': 'Sugar & Jaggery', 'base_unit': 'kg', 'purchase_unit': 'kg', 'selling_unit': 'kg', 'conversion_factor': 1, 'purchase_price': 55, 'selling_price': 70, 'minimum_stock': 20, 'recommended_stock': 50, 'reorder_quantity': 25, 'stock': 18},
        ]
    },
    'flowers': {
        'categories': ['Garlands (Dandalu)', 'Loose Flowers (విడి పూలు)', 'Pooja Camphor', 'Agarbatti & Dhoop', 'Pooja Oils & Ghee', 'Pooja Samagri'],
        'suppliers': [('Pushpa Wholesale Flower Mandi', '+91 9876544001'), ('Sri Balaji Pooja Stores', '+91 9876544002'), ('Gudur Jasmine Farmers Guild', '+91 9876544003')],
        'customers': [('Ravi Wedding Decorators', '+91 9440211221', 8500.0), ('Bhadrakali Temple Trust', '+91 9440211222', 4200.0)],
        'products': [
            {'name': 'Marigold Garlands (బంతిపూల దండలు)', 'local_name': 'Banthipula Danda', 'category': 'Garlands (Dandalu)', 'base_unit': 'garland', 'purchase_unit': 'bunch', 'selling_unit': 'garland', 'conversion_factor': 10, 'purchase_price': 400, 'selling_price': 60, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 25, 'stock': 40},
            {'name': 'Jasmine Strings / Mallepoolu (మల్లెపూలు)', 'local_name': 'Mallepoolu', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'mora', 'purchase_unit': 'basket', 'selling_unit': 'mora', 'conversion_factor': 25, 'purchase_price': 1000, 'selling_price': 60, 'minimum_stock': 10, 'recommended_stock': 60, 'reorder_quantity': 20, 'stock': 45},
            {'name': 'Red Dutch Roses (ఎరుపు గులాబీలు)', 'local_name': 'Gulabi Poolu', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'bundle', 'purchase_unit': 'bundle', 'selling_unit': 'stem', 'conversion_factor': 20, 'purchase_price': 180, 'selling_price': 15, 'minimum_stock': 2, 'recommended_stock': 15, 'reorder_quantity': 5, 'stock': 8},
            {'name': 'Chrysanthemum / Chamanthi (చామంతిపూలు)', 'local_name': 'Chamanthi', 'category': 'Loose Flowers (విడి పూలు)', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 10, 'purchase_price': 1200, 'selling_price': 180, 'minimum_stock': 8, 'recommended_stock': 50, 'reorder_quantity': 15, 'stock': 35},
            {'name': 'Pink Lotus / Kamalam (తామరపూలు)', 'local_name': 'Kamalam', 'category': 'Garlands (Dandalu)', 'base_unit': 'piece', 'purchase_unit': 'bundle', 'selling_unit': 'piece', 'conversion_factor': 25, 'purchase_price': 375, 'selling_price': 25, 'minimum_stock': 10, 'recommended_stock': 100, 'reorder_quantity': 30, 'stock': 60},
            {'name': 'Pooja Camphor (కర్పూరం)', 'local_name': 'Karpuram', 'category': 'Pooja Camphor', 'base_unit': 'packet', 'purchase_unit': 'box', 'selling_unit': 'packet', 'conversion_factor': 20, 'purchase_price': 500, 'selling_price': 35, 'minimum_stock': 15, 'recommended_stock': 60, 'reorder_quantity': 30, 'stock': 45},
            {'name': 'Cow Ghee for Deepam (దీపం నెయ్యి)', 'local_name': 'Pooja Ghee', 'category': 'Pooja Oils & Ghee', 'base_unit': 'bottle', 'purchase_unit': 'box', 'selling_unit': 'bottle', 'conversion_factor': 12, 'purchase_price': 1200, 'selling_price': 130, 'minimum_stock': 5, 'recommended_stock': 24, 'reorder_quantity': 12, 'stock': 18},
        ]
    },
    'jewellery': {
        'categories': ['Gold Chains & Necklaces', 'Gold Bangles & Rings', 'Silver Anklets (పట్టీలు)', 'Silver Pooja Articles', 'Diamond Ornaments', 'Coins & Bullion'],
        'suppliers': [('Bombay Bullion Refinery', '+91 9876545001'), ('Hyderabad Silver Palace', '+91 9876545002'), ('Kalyan Bullion Wholesalers', '+91 9848099001')],
        'customers': [('Suresh Goud (Gold Loan / Udhar)', '+91 9848122331', 35000.0), ('Padma Priya (Bridal Advance)', '+91 9848122332', 60000.0)],
        'products': [
            {'name': '22K Gold Chain (916 Hallmarked)', 'local_name': 'Bangaru Chain', 'category': 'Gold Chains & Necklaces', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1, 'purchase_price': 6850, 'selling_price': 7250, 'minimum_stock': 20, 'recommended_stock': 120, 'reorder_quantity': 40, 'stock': 65},
            {'name': '22K Gold Bangles (బంగారు గాజులు)', 'local_name': 'Bhangaru Gajulu', 'category': 'Gold Bangles & Rings', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1, 'purchase_price': 6850, 'selling_price': 7250, 'minimum_stock': 40, 'recommended_stock': 200, 'reorder_quantity': 80, 'stock': 110},
            {'name': '22K Gold Ring (బంగారు ఉంగరం)', 'local_name': 'Bhangaru Ungaram', 'category': 'Gold Bangles & Rings', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1, 'purchase_price': 6850, 'selling_price': 7300, 'minimum_stock': 10, 'recommended_stock': 60, 'reorder_quantity': 20, 'stock': 35},
            {'name': 'Silver Anklets (వెండి పట్టీలు)', 'local_name': 'Vendi Pattilu', 'category': 'Silver Anklets (పట్టీలు)', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1, 'purchase_price': 82, 'selling_price': 95, 'minimum_stock': 100, 'recommended_stock': 800, 'reorder_quantity': 200, 'stock': 450},
            {'name': 'Silver Laxmi Coin (10 grams)', 'local_name': 'Vendi Coin', 'category': 'Coins & Bullion', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 20, 'purchase_price': 16000, 'selling_price': 950, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 20, 'stock': 35},
            {'name': 'Silver Kamakshi Pooja Lamp (దీపం)', 'local_name': 'Vendi Deepam', 'category': 'Silver Pooja Articles', 'base_unit': 'gram', 'purchase_unit': 'gram', 'selling_unit': 'gram', 'conversion_factor': 1, 'purchase_price': 80, 'selling_price': 92, 'minimum_stock': 100, 'recommended_stock': 500, 'reorder_quantity': 150, 'stock': 280},
            {'name': '24K Pure Gold Coin 999 (బంగారు నాణెం)', 'local_name': 'Bhangaru Coin', 'category': 'Coins & Bullion', 'base_unit': 'gram', 'purchase_unit': 'pavan', 'selling_unit': 'gram', 'conversion_factor': 8, 'purchase_price': 60000, 'selling_price': 63200, 'minimum_stock': 16, 'recommended_stock': 100, 'reorder_quantity': 32, 'stock': 48},
        ]
    },
    'clothing': {
        'categories': ['Men Wear', 'Women Sarees', 'Kids Wear', 'Dress Materials', 'Fabrics & Rolls', 'Traditional Wear'],
        'suppliers': [('Surat Textile Mills', '+91 9876546001'), ('Kanchi Silk Weavers', '+91 9876546002'), ('Raymond & Arvind Fabrics Depot', '+91 9848055002')],
        'customers': [('Ravi Teja (Wedding Udhar)', '+91 9848055111', 14500.0), ('Smt. Sujatha (Chit Saree)', '+91 9848055222', 4200.0)],
        'products': [
            {'name': 'Cotton Formal Shirts', 'local_name': 'Cotton Shirt', 'category': 'Men Wear', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 10, 'purchase_price': 4500, 'selling_price': 599, 'minimum_stock': 15, 'recommended_stock': 60, 'reorder_quantity': 30, 'stock': 45},
            {'name': 'Kanchipuram Silk Sarees (పట్టు చీర)', 'local_name': 'Pattu Cheera', 'category': 'Women Sarees', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1, 'purchase_price': 4800, 'selling_price': 6500, 'minimum_stock': 5, 'recommended_stock': 25, 'reorder_quantity': 10, 'stock': 18},
            {'name': 'Denim Jeans (Standard Fit)', 'local_name': 'Jeans Pant', 'category': 'Men Wear', 'base_unit': 'piece', 'purchase_unit': 'set', 'selling_unit': 'piece', 'conversion_factor': 5, 'purchase_price': 3500, 'selling_price': 999, 'minimum_stock': 10, 'recommended_stock': 40, 'reorder_quantity': 20, 'stock': 32},
            {'name': "Women's Cotton Kurti Set (కుర్తీ సెట్)", 'local_name': 'Kurti Set', 'category': 'Women Sarees', 'base_unit': 'set', 'purchase_unit': 'set', 'selling_unit': 'set', 'conversion_factor': 1, 'purchase_price': 620, 'selling_price': 890, 'minimum_stock': 15, 'recommended_stock': 80, 'reorder_quantity': 25, 'stock': 50},
            {'name': 'Pure Cotton Dhoti & Kanduva (ధోవతి)', 'local_name': 'Dhovati Kanduva', 'category': 'Men Wear', 'base_unit': 'set', 'purchase_unit': 'set', 'selling_unit': 'set', 'conversion_factor': 1, 'purchase_price': 310, 'selling_price': 450, 'minimum_stock': 10, 'recommended_stock': 70, 'reorder_quantity': 20, 'stock': 45},
            {'name': 'School Uniform Fabric Set (స్కూల్ యూనిఫామ్)', 'local_name': 'Uniform Fabric', 'category': 'Fabrics & Rolls', 'base_unit': 'meter', 'purchase_unit': 'roll', 'selling_unit': 'meter', 'conversion_factor': 50, 'purchase_price': 11000, 'selling_price': 320, 'minimum_stock': 30, 'recommended_stock': 200, 'reorder_quantity': 80, 'stock': 120},
            {'name': 'Handloom Cotton Saree (చేనేత చీర)', 'local_name': 'Handloom Saree', 'category': 'Women Sarees', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1, 'purchase_price': 950, 'selling_price': 1450, 'minimum_stock': 8, 'recommended_stock': 35, 'reorder_quantity': 15, 'stock': 24},
        ]
    },
    'pharmacy': {
        'categories': ['Tablets & Capsules', 'Syrups & Suspensions', 'Injections & Vials', 'First Aid & Surgical', 'Ayurvedic & OTC', 'Health Devices'],
        'suppliers': [('Apollo Wholesale Pharma', '+91 9876547001'), ('Reddy Labs Distributor', '+91 9876547002'), ('Cipla Regional Stockist', '+91 9876547003')],
        'customers': [('Krishna Murthy (Senior Citizen BP Udhar)', '+91 9848066111', 3250.0), ('Madhavi Latha (Pediatric Tab)', '+91 9848066222', 850.0)],
        'products': [
            {'name': 'Paracetamol 650mg Tablets (Dolo 650)', 'local_name': 'Dolo 650', 'category': 'Tablets & Capsules', 'base_unit': 'strip', 'purchase_unit': 'box', 'selling_unit': 'strip', 'conversion_factor': 15, 'purchase_price': 360, 'selling_price': 32, 'minimum_stock': 25, 'recommended_stock': 150, 'reorder_quantity': 50, 'stock': 120},
            {'name': 'Azithromycin 500mg Tablets (Azee 500)', 'local_name': 'Azee 500', 'category': 'Tablets & Capsules', 'base_unit': 'strip', 'purchase_unit': 'box', 'selling_unit': 'strip', 'conversion_factor': 10, 'purchase_price': 780, 'selling_price': 115, 'minimum_stock': 10, 'recommended_stock': 40, 'reorder_quantity': 20, 'stock': 28},
            {'name': 'Benadryl Cough Syrup 100ml (దగ్గు మందు)', 'local_name': 'Daggu Mandhu', 'category': 'Syrups & Suspensions', 'base_unit': 'bottle', 'purchase_unit': 'box', 'selling_unit': 'bottle', 'conversion_factor': 12, 'purchase_price': 1050, 'selling_price': 115, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 24, 'stock': 35},
            {'name': 'Human Mixtard 30/70 Insulin (ఇన్సులిన్)', 'local_name': 'Insulin Vial', 'category': 'Injections & Vials', 'base_unit': 'vial', 'purchase_unit': 'pack', 'selling_unit': 'vial', 'conversion_factor': 5, 'purchase_price': 780, 'selling_price': 185, 'minimum_stock': 5, 'recommended_stock': 30, 'reorder_quantity': 10, 'stock': 18},
            {'name': 'ORS Electral Powder 21.8g (ఓఆర్ఎస్)', 'local_name': 'ORS Sachet', 'category': 'First Aid & Surgical', 'base_unit': 'sachet', 'purchase_unit': 'box', 'selling_unit': 'sachet', 'conversion_factor': 25, 'purchase_price': 420, 'selling_price': 22, 'minimum_stock': 30, 'recommended_stock': 200, 'reorder_quantity': 80, 'stock': 140},
            {'name': 'Digital BP Monitor (బీపీ మిషన్)', 'local_name': 'BP Monitor', 'category': 'Health Devices', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1, 'purchase_price': 1150, 'selling_price': 1450, 'minimum_stock': 2, 'recommended_stock': 12, 'reorder_quantity': 4, 'stock': 8},
            {'name': 'Crocin Advance 500mg (క్రోసిన్)', 'local_name': 'Crocin', 'category': 'Tablets & Capsules', 'base_unit': 'strip', 'purchase_unit': 'box', 'selling_unit': 'strip', 'conversion_factor': 20, 'purchase_price': 380, 'selling_price': 25, 'minimum_stock': 20, 'recommended_stock': 100, 'reorder_quantity': 40, 'stock': 75},
        ]
    },
    'bakery': {
        'categories': ['Fresh Bread & Buns', 'Celebration Cakes', 'Traditional Sweets', 'Savory Puffs & Samosas', 'Cookies & Biscuits'],
        'suppliers': [('Standard Flour & Yeast Corp', '+91 9876548001'), ('Dairy Fresh Cream Ltd', '+91 9876548002'), ('Vijaya Dairy Milk Supply', '+91 9848077001')],
        'customers': [('Modern High School (Party Order Udhar)', '+91 9848077111', 5200.0), ('Srinivasa Caterers (Sweet Boxes)', '+91 9848077222', 8400.0)],
        'products': [
            {'name': 'Fresh Milk Bread 400g (పాల బ్రెడ్)', 'local_name': 'Milk Bread', 'category': 'Fresh Bread & Buns', 'base_unit': 'packet', 'purchase_unit': 'crate', 'selling_unit': 'packet', 'conversion_factor': 20, 'purchase_price': 600, 'selling_price': 40, 'minimum_stock': 15, 'recommended_stock': 80, 'reorder_quantity': 30, 'stock': 55},
            {'name': 'Black Forest Cake 1kg (బ్లాక్ ఫారెస్ట్ కేక్)', 'local_name': 'Black Forest Cake', 'category': 'Celebration Cakes', 'base_unit': 'kg', 'purchase_unit': 'kg', 'selling_unit': 'kg', 'conversion_factor': 1, 'purchase_price': 380, 'selling_price': 550, 'minimum_stock': 3, 'recommended_stock': 20, 'reorder_quantity': 6, 'stock': 12},
            {'name': 'Ghee Mysore Pak (నెయ్యి మైసూర్ పాక్)', 'local_name': 'Mysore Pak', 'category': 'Traditional Sweets', 'base_unit': 'kg', 'purchase_unit': 'tray', 'selling_unit': 'kg', 'conversion_factor': 5, 'purchase_price': 1750, 'selling_price': 480, 'minimum_stock': 5, 'recommended_stock': 35, 'reorder_quantity': 15, 'stock': 22},
            {'name': 'Kaju Katli (కాజు కట్లి)', 'local_name': 'Kaju Katli', 'category': 'Traditional Sweets', 'base_unit': 'kg', 'purchase_unit': 'tray', 'selling_unit': 'kg', 'conversion_factor': 5, 'purchase_price': 3200, 'selling_price': 850, 'minimum_stock': 4, 'recommended_stock': 25, 'reorder_quantity': 10, 'stock': 15},
            {'name': 'Egg & Veg Hot Puff (పఫ్స్)', 'local_name': 'Puff', 'category': 'Savory Puffs & Samosas', 'base_unit': 'piece', 'purchase_unit': 'tray', 'selling_unit': 'piece', 'conversion_factor': 30, 'purchase_price': 480, 'selling_price': 25, 'minimum_stock': 20, 'recommended_stock': 120, 'reorder_quantity': 50, 'stock': 80},
            {'name': 'Osmania Tea Biscuits (ఉస్మానియా బిస్కెట్లు)', 'local_name': 'Osmania Biscuits', 'category': 'Cookies & Biscuits', 'base_unit': 'box', 'purchase_unit': 'carton', 'selling_unit': 'box', 'conversion_factor': 12, 'purchase_price': 1080, 'selling_price': 120, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 20, 'stock': 38},
            {'name': 'Vanilla Cream Roll (క్రీమ్ రోల్)', 'local_name': 'Cream Roll', 'category': 'Savory Puffs & Samosas', 'base_unit': 'piece', 'purchase_unit': 'tray', 'selling_unit': 'piece', 'conversion_factor': 20, 'purchase_price': 200, 'selling_price': 18, 'minimum_stock': 15, 'recommended_stock': 60, 'reorder_quantity': 30, 'stock': 40},
        ]
    },
    'restaurant': {
        'categories': ['Breakfast Tiffins', 'Meals & Biryani', 'Kitchen Raw Materials', 'Curries & Starters', 'Beverages'],
        'suppliers': [('Rythu Bazar Vegetable Wholesalers', '+91 9848088001'), ('Modern Poultry & Meat Supply', '+91 9848088002'), ('Telangana Wholesale Rice & Oil', '+91 9876549001')],
        'customers': [('Subba Rao (Monthly Mess)', '+91 9848088111', 3200.0), ('Polytechnic Staff Union (Tea & Tiffin)', '+91 9848088222', 4600.0)],
        'products': [
            {'name': 'Special Chicken Dum Biryani (చికెన్ బిర్యానీ)', 'local_name': 'Chicken Biryani', 'category': 'Meals & Biryani', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1, 'purchase_price': 130, 'selling_price': 220, 'minimum_stock': 10, 'recommended_stock': 80, 'reorder_quantity': 25, 'stock': 45},
            {'name': 'Ghee Masala Dosa (మసాలా దోశ)', 'local_name': 'Masala Dosa', 'category': 'Breakfast Tiffins', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1, 'purchase_price': 30, 'selling_price': 60, 'minimum_stock': 20, 'recommended_stock': 120, 'reorder_quantity': 40, 'stock': 90},
            {'name': 'Steamed Idli Sambar (ఇడ్లీ సాంబార్)', 'local_name': 'Idli Sambar', 'category': 'Breakfast Tiffins', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1, 'purchase_price': 18, 'selling_price': 40, 'minimum_stock': 20, 'recommended_stock': 150, 'reorder_quantity': 50, 'stock': 110},
            {'name': 'South Indian Thali Meals (పూర్తి భోజనం)', 'local_name': 'Bhojanam', 'category': 'Meals & Biryani', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1, 'purchase_price': 65, 'selling_price': 110, 'minimum_stock': 15, 'recommended_stock': 90, 'reorder_quantity': 30, 'stock': 65},
            {'name': 'Raw Basmati Rice Bulk 25kg (బిర్యానీ బియ్యం)', 'local_name': 'Basmati Rice Bag', 'category': 'Kitchen Raw Materials', 'base_unit': 'bag', 'purchase_unit': 'bag', 'selling_unit': 'bag', 'conversion_factor': 1, 'purchase_price': 2100, 'selling_price': 2400, 'minimum_stock': 3, 'recommended_stock': 15, 'reorder_quantity': 6, 'stock': 10},
            {'name': 'Cooking Sunflower Oil Tin 15L (వంట నూనె)', 'local_name': 'Oil Tin', 'category': 'Kitchen Raw Materials', 'base_unit': 'can', 'purchase_unit': 'can', 'selling_unit': 'can', 'conversion_factor': 1, 'purchase_price': 1650, 'selling_price': 1850, 'minimum_stock': 2, 'recommended_stock': 10, 'reorder_quantity': 4, 'stock': 7},
            {'name': 'Chapathi with Mixed Veg Kurma (చపాతీ)', 'local_name': 'Chapathi', 'category': 'Breakfast Tiffins', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1, 'purchase_price': 22, 'selling_price': 50, 'minimum_stock': 15, 'recommended_stock': 80, 'reorder_quantity': 30, 'stock': 55},
        ]
    },
    'teacoffee': {
        'categories': ['Hot Beverages', 'Tea Stall Snacks', 'Raw Ingredients', 'Biscuits & Mints', 'Milk & Dairy'],
        'suppliers': [('Niloufer Chai Supply', '+91 9876550001'), ('Sangam Dairy Whole Milk', '+91 9848099001'), ('Brooke Bond & Nescafe Depot', '+91 9848099002')],
        'customers': [('Court Auto Drivers Union (Tea Tab)', '+91 9848099111', 1850.0), ('LIC Office Staff (Daily Refreshment)', '+91 9848099222', 1200.0)],
        'products': [
            {'name': 'Special Irani Dum Chai (ఇరానీ దమ్ చాయ్)', 'local_name': 'Irani Chai', 'category': 'Hot Beverages', 'base_unit': 'cup', 'purchase_unit': 'cup', 'selling_unit': 'cup', 'conversion_factor': 1, 'purchase_price': 6, 'selling_price': 15, 'minimum_stock': 50, 'recommended_stock': 400, 'reorder_quantity': 150, 'stock': 280},
            {'name': 'South Indian Filter Coffee (ఫిల్టర్ కాఫీ)', 'local_name': 'Filter Coffee', 'category': 'Hot Beverages', 'base_unit': 'cup', 'purchase_unit': 'cup', 'selling_unit': 'cup', 'conversion_factor': 1, 'purchase_price': 9, 'selling_price': 20, 'minimum_stock': 25, 'recommended_stock': 200, 'reorder_quantity': 80, 'stock': 140},
            {'name': 'Hot Onion Samosa (ఉల్లి సమోసా)', 'local_name': 'Samosa', 'category': 'Tea Stall Snacks', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1, 'purchase_price': 4.5, 'selling_price': 10, 'minimum_stock': 20, 'recommended_stock': 150, 'reorder_quantity': 50, 'stock': 95},
            {'name': 'Mirchi Bajji (మిర్చి బజ్జీ)', 'local_name': 'Mirchi Bajji', 'category': 'Tea Stall Snacks', 'base_unit': 'plate', 'purchase_unit': 'plate', 'selling_unit': 'plate', 'conversion_factor': 1, 'purchase_price': 14, 'selling_price': 30, 'minimum_stock': 15, 'recommended_stock': 80, 'reorder_quantity': 30, 'stock': 60},
            {'name': 'Buffalo Milk 1 Litre (గేదె పాలు)', 'local_name': 'Paalu', 'category': 'Raw Ingredients', 'base_unit': 'litre', 'purchase_unit': 'can', 'selling_unit': 'litre', 'conversion_factor': 20, 'purchase_price': 1200, 'selling_price': 70, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 25, 'stock': 35},
            {'name': 'Sugar Commercial 50kg (చక్కెర బస్తా)', 'local_name': 'Chakkera Bag', 'category': 'Raw Ingredients', 'base_unit': 'bag', 'purchase_unit': 'bag', 'selling_unit': 'bag', 'conversion_factor': 1, 'purchase_price': 1950, 'selling_price': 2050, 'minimum_stock': 2, 'recommended_stock': 6, 'reorder_quantity': 3, 'stock': 4},
            {'name': 'Bun Maska (బన్ మస్కా)', 'local_name': 'Bun Maska', 'category': 'Tea Stall Snacks', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1, 'purchase_price': 12, 'selling_price': 25, 'minimum_stock': 15, 'recommended_stock': 70, 'reorder_quantity': 25, 'stock': 45},
        ]
    },
    'hardware': {
        'categories': ['Plumbing & Pipes', 'Electrical Wires & Switches', 'Cement & Construction', 'Paints & Primers', 'Hand Tools & Fasteners'],
        'suppliers': [('Finolex Cable Hub', '+91 9876551001'), ('Ashirvad Pipe Dist.', '+91 9876551002'), ('Supreme Pipes Wholesalers', '+91 98480aa001')],
        'customers': [('Koti Plumber (Contractor Udhar)', '+91 98480aa111', 18500.0), ('Satyam Electrician (Running Tab)', '+91 98480aa222', 9200.0)],
        'products': [
            {'name': 'PVC Pipe 1 inch 10ft (పీవీసీ పైపు)', 'local_name': 'PVC Pipe', 'category': 'Plumbing & Pipes', 'base_unit': 'length', 'purchase_unit': 'bundle', 'selling_unit': 'length', 'conversion_factor': 10, 'purchase_price': 1250, 'selling_price': 160, 'minimum_stock': 15, 'recommended_stock': 80, 'reorder_quantity': 30, 'stock': 60},
            {'name': 'Finolex Copper Wire 2.5 sq mm (రాగి వైరు)', 'local_name': 'Copper Wire', 'category': 'Electrical Wires & Switches', 'base_unit': 'roll', 'purchase_unit': 'box', 'selling_unit': 'roll', 'conversion_factor': 4, 'purchase_price': 9800, 'selling_price': 2850, 'minimum_stock': 5, 'recommended_stock': 30, 'reorder_quantity': 10, 'stock': 18},
            {'name': 'Anchor Roma Modular Switch 6A (యాంకర్ స్విచ్)', 'local_name': 'Anchor Switch', 'category': 'Electrical Wires & Switches', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 20, 'purchase_price': 640, 'selling_price': 42, 'minimum_stock': 25, 'recommended_stock': 150, 'reorder_quantity': 50, 'stock': 120},
            {'name': 'UltraTech Cement 50kg (సిమెంట్ బస్తా)', 'local_name': 'Cement Bag', 'category': 'Cement & Construction', 'base_unit': 'bag', 'purchase_unit': 'bag', 'selling_unit': 'bag', 'conversion_factor': 1, 'purchase_price': 345, 'selling_price': 390, 'minimum_stock': 20, 'recommended_stock': 120, 'reorder_quantity': 40, 'stock': 70},
            {'name': 'Asian Paints Apex White 20L (ఏషియన్ పెయింట్)', 'local_name': 'Asian Paint', 'category': 'Paints & Primers', 'base_unit': 'bucket', 'purchase_unit': 'bucket', 'selling_unit': 'bucket', 'conversion_factor': 1, 'purchase_price': 3250, 'selling_price': 3800, 'minimum_stock': 4, 'recommended_stock': 20, 'reorder_quantity': 8, 'stock': 12},
            {'name': 'Steel Screws & Rawlplugs Box (స్క్రూలు)', 'local_name': 'Screws Box', 'category': 'Hand Tools & Fasteners', 'base_unit': 'box', 'purchase_unit': 'carton', 'selling_unit': 'box', 'conversion_factor': 10, 'purchase_price': 1350, 'selling_price': 180, 'minimum_stock': 10, 'recommended_stock': 40, 'reorder_quantity': 15, 'stock': 28},
            {'name': '9W LED Bulbs Cool White (ఎల్ఈడీ బల్బు)', 'local_name': 'LED Bulbs', 'category': 'Electrical Wires & Switches', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 20, 'purchase_price': 1100, 'selling_price': 85, 'minimum_stock': 15, 'recommended_stock': 60, 'reorder_quantity': 25, 'stock': 40},
        ]
    },
    'autoparts': {
        'categories': ['Engine Oils & Lubricants', 'Brake Systems & Pads', 'Ignition & Electricals', 'Transmission & Chains', 'Tyres & Tubes', 'Batteries & Horns', 'Cables & Filters', 'Care & Maintenance'],
        'suppliers': [
            ('Castrol India Lubricants Stockist', '+91 98480bb001'),
            ('Bosch Automotive Parts Wholesale', '+91 98480bb002'),
            ('Hero & TVS Genuine Spares Agency', '+91 98480bb003'),
            ('Exide & Amaron Batteries Hub', '+91 98480bb004')
        ],
        'customers': [
            ('Shiva Mechanic (Shiva Auto Garage Tab)', '+91 98480bb111', 12500.0),
            ('Ramesh Auto Garage (Running Spares Credit)', '+91 98480bb222', 7800.0),
            ('Raju Bike Point (Engine Oil & Pads Tab)', '+91 98480bb333', 3450.0)
        ],
        'products': [
            {'name': 'Castrol Activ 4T 20W-40 1L (ఇంజన్ ఆయిల్)', 'local_name': 'Engine Oil', 'category': 'Engine Oils & Lubricants', 'base_unit': 'bottle', 'purchase_unit': 'box', 'selling_unit': 'bottle', 'conversion_factor': 12, 'purchase_price': 4200, 'selling_price': 420, 'minimum_stock': 12, 'recommended_stock': 70, 'reorder_quantity': 24, 'stock': 45},
            {'name': 'Motul 3000 4T Plus 10W-30 1L (మోటుల్ ఇంజన్ ఆయిల్)', 'local_name': 'Motul Oil', 'category': 'Engine Oils & Lubricants', 'base_unit': 'bottle', 'purchase_unit': 'box', 'selling_unit': 'bottle', 'conversion_factor': 12, 'purchase_price': 4440, 'selling_price': 440, 'minimum_stock': 10, 'recommended_stock': 50, 'reorder_quantity': 20, 'stock': 28},
            {'name': 'Hero Splendor Brake Shoes (బ్రేక్ షూస్)', 'local_name': 'Brake Shoes', 'category': 'Brake Systems & Pads', 'base_unit': 'set', 'purchase_unit': 'box', 'selling_unit': 'set', 'conversion_factor': 10, 'purchase_price': 1800, 'selling_price': 240, 'minimum_stock': 8, 'recommended_stock': 50, 'reorder_quantity': 20, 'stock': 30},
            {'name': 'Front Disc Brake Pads Pulsar / Apache (ఫ్రంట్ డిస్క్ ప్యాడ్లు)', 'local_name': 'Disc Brake Pads', 'category': 'Brake Systems & Pads', 'base_unit': 'set', 'purchase_unit': 'box', 'selling_unit': 'set', 'conversion_factor': 10, 'purchase_price': 2600, 'selling_price': 350, 'minimum_stock': 6, 'recommended_stock': 30, 'reorder_quantity': 12, 'stock': 15},
            {'name': 'Amaron 12V Bike Battery 4Ah (బైక్ బ్యాటరీ)', 'local_name': 'Bike Battery', 'category': 'Batteries & Horns', 'base_unit': 'unit', 'purchase_unit': 'unit', 'selling_unit': 'unit', 'conversion_factor': 1, 'purchase_price': 1180, 'selling_price': 1450, 'minimum_stock': 3, 'recommended_stock': 20, 'reorder_quantity': 6, 'stock': 12},
            {'name': 'MRF Nylogrip Tyre 90/90-12 Activa (ఎంఆర్ఎఫ్ టైరు)', 'local_name': 'MRF Tyre', 'category': 'Tyres & Tubes', 'base_unit': 'piece', 'purchase_unit': 'piece', 'selling_unit': 'piece', 'conversion_factor': 1, 'purchase_price': 1380, 'selling_price': 1650, 'minimum_stock': 4, 'recommended_stock': 25, 'reorder_quantity': 8, 'stock': 16},
            {'name': 'Spark Plug NGK 2-Wheeler (స్పార్క్ ప్లగ్)', 'local_name': 'Spark Plug', 'category': 'Ignition & Electricals', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 10, 'purchase_price': 650, 'selling_price': 95, 'minimum_stock': 15, 'recommended_stock': 100, 'reorder_quantity': 30, 'stock': 60},
            {'name': 'Rolon Chain Sprocket Kit Splendor (చైన్ కిట్)', 'local_name': 'Chain Sprocket', 'category': 'Transmission & Chains', 'base_unit': 'set', 'purchase_unit': 'set', 'selling_unit': 'set', 'conversion_factor': 1, 'purchase_price': 850, 'selling_price': 1150, 'minimum_stock': 3, 'recommended_stock': 15, 'reorder_quantity': 5, 'stock': 9},
            {'name': 'Clutch Cable for Bajaj Pulsar (క్లచ్ కేబుల్)', 'local_name': 'Clutch Cable', 'category': 'Cables & Filters', 'base_unit': 'piece', 'purchase_unit': 'bundle', 'selling_unit': 'piece', 'conversion_factor': 10, 'purchase_price': 850, 'selling_price': 130, 'minimum_stock': 6, 'recommended_stock': 40, 'reorder_quantity': 15, 'stock': 25},
            {'name': 'Roots 12V High-Tone Bike Horn (రూట్స్ బైక్ హారన్)', 'local_name': 'Bike Horn', 'category': 'Batteries & Horns', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 6, 'purchase_price': 1500, 'selling_price': 320, 'minimum_stock': 4, 'recommended_stock': 24, 'reorder_quantity': 8, 'stock': 14},
            {'name': 'Air Filter for Hero Splendor / HF (ఎయిర్ ఫిల్టర్)', 'local_name': 'Air Filter', 'category': 'Cables & Filters', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 10, 'purchase_price': 950, 'selling_price': 140, 'minimum_stock': 8, 'recommended_stock': 40, 'reorder_quantity': 15, 'stock': 22},
            {'name': 'WD-40 / Motul Chain Lube Spray 400ml (చైన్ ల్యూబ్ స్ప్రే)', 'local_name': 'Chain Lube', 'category': 'Care & Maintenance', 'base_unit': 'can', 'purchase_unit': 'box', 'selling_unit': 'can', 'conversion_factor': 12, 'purchase_price': 3240, 'selling_price': 350, 'minimum_stock': 6, 'recommended_stock': 30, 'reorder_quantity': 12, 'stock': 18},
        ]
    },
    'vegetables': {
        'categories': ['Fresh Daily Veggies', 'Onions & Potatoes', 'Leafy Greens', 'Fresh Seasonal Fruits', 'Exotic & Salad Veg'],
        'suppliers': [('Bowenpally Wholesale Sabzi Mandi', '+91 9876553001'), ('Kothapet Fruit Commission', '+91 9876553002'), ('Rythu Bazar Vegetable Guild', '+91 98480cc001')],
        'customers': [('Balaji Fast Food Center (Daily Veggies)', '+91 98480cc111', 3800.0), ('Raghavendra Mess (Vegetables)', '+91 98480cc222', 2400.0)],
        'products': [
            {'name': 'Fresh Country Tomatoes (నాటు టమాటాలు)', 'local_name': 'Tamata', 'category': 'Fresh Daily Veggies', 'base_unit': 'kg', 'purchase_unit': 'crate', 'selling_unit': 'kg', 'conversion_factor': 25, 'purchase_price': 550, 'selling_price': 35, 'minimum_stock': 20, 'recommended_stock': 100, 'reorder_quantity': 40, 'stock': 70},
            {'name': 'Onion / Ullipaya (ఉల్లిపాయలు)', 'local_name': 'Ullipaya', 'category': 'Onions & Potatoes', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 50, 'purchase_price': 1100, 'selling_price': 30, 'minimum_stock': 40, 'recommended_stock': 200, 'reorder_quantity': 80, 'stock': 135},
            {'name': 'Potato / Bangala Dumpa (బంగాళాదుంపలు)', 'local_name': 'Bangala Dumpa', 'category': 'Onions & Potatoes', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 50, 'purchase_price': 1250, 'selling_price': 32, 'minimum_stock': 30, 'recommended_stock': 160, 'reorder_quantity': 70, 'stock': 105},
            {'name': 'Green Chillies / Pachi Mirchi (పచ్చిమిర్చి)', 'local_name': 'Pachi Mirchi', 'category': 'Fresh Daily Veggies', 'base_unit': 'kg', 'purchase_unit': 'bag', 'selling_unit': 'kg', 'conversion_factor': 10, 'purchase_price': 450, 'selling_price': 60, 'minimum_stock': 8, 'recommended_stock': 35, 'reorder_quantity': 15, 'stock': 22},
            {'name': 'Fresh Palak / Spinach (పాలకూర కట్ట)', 'local_name': 'Palakoora', 'category': 'Leafy Greens', 'base_unit': 'bunch', 'purchase_unit': 'bundle', 'selling_unit': 'bunch', 'conversion_factor': 25, 'purchase_price': 225, 'selling_price': 15, 'minimum_stock': 10, 'recommended_stock': 60, 'reorder_quantity': 20, 'stock': 42},
            {'name': 'Yelakki Small Bananas (ఎలక్కి అరటిపండ్లు)', 'local_name': 'Arati Pandlu', 'category': 'Fresh Seasonal Fruits', 'base_unit': 'dozen', 'purchase_unit': 'crate', 'selling_unit': 'dozen', 'conversion_factor': 10, 'purchase_price': 420, 'selling_price': 60, 'minimum_stock': 8, 'recommended_stock': 40, 'reorder_quantity': 15, 'stock': 28},
            {'name': 'Kashmir Red Apples (కాశ్మీర్ యాపిల్స్)', 'local_name': 'Apples', 'category': 'Fresh Seasonal Fruits', 'base_unit': 'kg', 'purchase_unit': 'box', 'selling_unit': 'kg', 'conversion_factor': 18, 'purchase_price': 2160, 'selling_price': 160, 'minimum_stock': 15, 'recommended_stock': 60, 'reorder_quantity': 30, 'stock': 35},
        ]
    },
    'electronics': {
        'categories': ['Smartphones', 'Fast Chargers & Adapters', 'Bluetooth Audio & Sound', 'Powerbanks & Cables', 'Screen Guards & Covers', 'Storage & Memory', 'Smartwatches & Gadgets'],
        'suppliers': [
            ('Redmi & Xiaomi National Distributor', '+91 9876554001'),
            ('boAt Audio Official Distributor', '+91 98480dd002'),
            ('Samsung Mobile Regional Wholesale', '+91 98480dd001'),
            ('SanDisk & Portronics Gadgets Agency', '+91 98480dd003')
        ],
        'customers': [
            ('Kalyan (Engineering Student Tab)', '+91 98480dd111', 1500.0),
            ('Naresh (Samsung Phone EMI Account)', '+91 98480dd222', 9500.0),
            ('Suresh (Display & Tempered Glass Udhar)', '+91 98480dd333', 2800.0)
        ],
        'products': [
            {'name': 'Samsung Galaxy A15 5G 128GB (శాంసంగ్ మొబైల్)', 'local_name': 'Samsung Mobile', 'category': 'Smartphones', 'base_unit': 'unit', 'purchase_unit': 'unit', 'selling_unit': 'unit', 'conversion_factor': 1, 'purchase_price': 13200, 'selling_price': 14999, 'minimum_stock': 2, 'recommended_stock': 12, 'reorder_quantity': 4, 'stock': 8},
            {'name': 'Redmi 13C 5G 128GB (రెడ్‌మి 5G మొబైల్)', 'local_name': 'Redmi Mobile', 'category': 'Smartphones', 'base_unit': 'unit', 'purchase_unit': 'unit', 'selling_unit': 'unit', 'conversion_factor': 1, 'purchase_price': 9800, 'selling_price': 11499, 'minimum_stock': 2, 'recommended_stock': 15, 'reorder_quantity': 5, 'stock': 9},
            {'name': 'boAt Airdopes 141 Bluetooth Earbuds (ఇయర్ బడ్స్)', 'local_name': 'boAt Earbuds', 'category': 'Bluetooth Audio & Sound', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 10, 'purchase_price': 8900, 'selling_price': 1199, 'minimum_stock': 5, 'recommended_stock': 35, 'reorder_quantity': 10, 'stock': 22},
            {'name': 'boAt Rockerz 255 Pro+ Neckband (బ్లూటూత్ నెక్‌బ్యాండ్)', 'local_name': 'boAt Neckband', 'category': 'Bluetooth Audio & Sound', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 10, 'purchase_price': 7800, 'selling_price': 1099, 'minimum_stock': 4, 'recommended_stock': 25, 'reorder_quantity': 8, 'stock': 16},
            {'name': 'Fast 20W Type-C Charger Adapter (టైప్-సి ఛార్జర్)', 'local_name': 'Fast Charger', 'category': 'Fast Chargers & Adapters', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 10, 'purchase_price': 3200, 'selling_price': 499, 'minimum_stock': 10, 'recommended_stock': 60, 'reorder_quantity': 20, 'stock': 40},
            {'name': 'SuperVOOC 33W Fast Charger with Cable (33W ఫాస్ట్ ఛార్జర్)', 'local_name': '33W Charger', 'category': 'Fast Chargers & Adapters', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 10, 'purchase_price': 5200, 'selling_price': 799, 'minimum_stock': 5, 'recommended_stock': 30, 'reorder_quantity': 10, 'stock': 18},
            {'name': '10000mAh Dual USB Power Bank (పవర్ బ్యాంక్)', 'local_name': 'Power Bank', 'category': 'Powerbanks & Cables', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 5, 'purchase_price': 3800, 'selling_price': 999, 'minimum_stock': 3, 'recommended_stock': 25, 'reorder_quantity': 10, 'stock': 15},
            {'name': '20000mAh 22.5W Fast Power Bank (20000mAh పవర్ బ్యాంక్)', 'local_name': '20000mAh Power Bank', 'category': 'Powerbanks & Cables', 'base_unit': 'unit', 'purchase_unit': 'box', 'selling_unit': 'unit', 'conversion_factor': 5, 'purchase_price': 6200, 'selling_price': 1699, 'minimum_stock': 2, 'recommended_stock': 15, 'reorder_quantity': 5, 'stock': 8},
            {'name': 'Braided 1.5m Type-C Fast Cable (యూఎస్బీ కేబుల్)', 'local_name': 'Type-C Cable', 'category': 'Powerbanks & Cables', 'base_unit': 'piece', 'purchase_unit': 'bundle', 'selling_unit': 'piece', 'conversion_factor': 20, 'purchase_price': 2200, 'selling_price': 199, 'minimum_stock': 15, 'recommended_stock': 100, 'reorder_quantity': 30, 'stock': 65},
            {'name': '9D Edge-to-Edge Tempered Glass (స్క్రీన్ గార్డ్)', 'local_name': 'Screen Guard', 'category': 'Screen Guards & Covers', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 25, 'purchase_price': 1250, 'selling_price': 150, 'minimum_stock': 20, 'recommended_stock': 150, 'reorder_quantity': 50, 'stock': 90},
            {'name': 'SanDisk 64GB Ultra MicroSD Card (మెమరీ కార్డు)', 'local_name': 'Memory Card', 'category': 'Storage & Memory', 'base_unit': 'piece', 'purchase_unit': 'pack', 'selling_unit': 'piece', 'conversion_factor': 10, 'purchase_price': 3600, 'selling_price': 499, 'minimum_stock': 5, 'recommended_stock': 30, 'reorder_quantity': 10, 'stock': 18},
            {'name': 'Noise ColorFit Pulse Smart Watch (స్మార్ట్ వాచ్)', 'local_name': 'Smart Watch', 'category': 'Smartwatches & Gadgets', 'base_unit': 'piece', 'purchase_unit': 'box', 'selling_unit': 'piece', 'conversion_factor': 5, 'purchase_price': 6500, 'selling_price': 1799, 'minimum_stock': 3, 'recommended_stock': 15, 'reorder_quantity': 5, 'stock': 8},
        ]
    },
}


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and create their shop + seed data."""
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", "VALIDATION_ERROR")
    
    required = ['email', 'full_name', 'shop_name']
    for field in required:
        if not data.get(field):
            return error_response(f"{field} is required", "VALIDATION_ERROR")
    
    email = data['email'].strip().lower()
    shop_type = data.get('shop_type', 'kirana').strip().lower()
    
    try:
        supabase = get_supabase()
        
        # Check if user already exists
        existing = supabase.table('users').select('*').eq('email', email).limit(1).execute()
        if existing.data and len(existing.data) > 0:
            user_rec = existing.data[0]
            shop_res = supabase.table('shops').select('*').eq('owner_id', user_rec['id']).limit(1).execute()
            shop_rec = shop_res.data[0] if (shop_res.data and len(shop_res.data) > 0) else None
            user_token = f"user-token-{user_rec['id']}"
            return success_response({
                'user': user_rec,
                'shop': shop_rec,
                'token': user_token,
                'session': {'access_token': user_token}
            }, 200)

        # Generate unique IDs
        user_id = str(uuid.uuid4())
        auth_id = str(uuid.uuid4())
        shop_id = str(uuid.uuid4())
        
        # Check if caller passed a valid Supabase Bearer token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            if not token.startswith('demo-') and not token.startswith('user-'):
                try:
                    user_response = supabase.auth.get_user(token)
                    if user_response and user_response.user:
                        auth_id = str(user_response.user.id)
                except Exception:
                    pass

        # Create user profile
        user = supabase.table('users').insert({
            'id': user_id,
            'auth_id': auth_id,
            'email': email,
            'full_name': data['full_name'].strip(),
            'phone': data.get('phone', '').strip(),
            'language': data.get('language', 'te'),
            'is_active': True,
        }).execute()
        
        # Create shop
        shop = supabase.table('shops').insert({
            'id': shop_id,
            'owner_id': user_id,
            'name': data['shop_name'].strip(),
            'type': shop_type,
            'phone': data.get('phone', '').strip(),
            'currency': 'INR',
            'is_active': True,
        }).execute()
        
        # Add user as shop owner
        supabase.table('shop_members').insert({
            'shop_id': shop_id,
            'user_id': user_id,
            'role': 'owner',
        }).execute()
        
        # Seed categories, suppliers, and initial products matching this vertical
        template = STORE_SEED_DATA.get(shop_type, STORE_SEED_DATA['kirana'])
        
        for cat_name in template['categories']:
            supabase.table('categories').insert({
                'shop_id': shop_id,
                'name': cat_name,
            }).execute()
        
        for s_name, s_phone in template['suppliers']:
            supabase.table('suppliers').insert({
                'shop_id': shop_id,
                'name': s_name,
                'phone': s_phone,
            }).execute()

        for c_name, c_phone, c_credit in template.get('customers', []):
            cust_res = supabase.table('customers').insert({
                'shop_id': shop_id,
                'name': c_name,
                'phone': c_phone,
                'total_credit': c_credit,
                'is_active': True,
            }).execute()
            if cust_res.data and c_credit > 0:
                cid = cust_res.data[0]['id']
                supabase.table('borrowings').insert({
                    'shop_id': shop_id,
                    'customer_id': cid,
                    'customer_name': c_name,
                    'status': 'ACTIVE',
                    'total_value': c_credit,
                    'paid_amount': 0.0,
                    'remaining_balance': c_credit,
                    'notes': 'Initial credit balance',
                    'created_by': user_id
                }).execute()
        
        for prod in template['products']:
            stock = prod.get('stock', 20)
            prod_copy = {k: v for k, v in prod.items() if k != 'stock'}
            prod_copy['shop_id'] = shop_id
            inserted_prod = supabase.table('products').insert(prod_copy).execute()
            if inserted_prod.data and len(inserted_prod.data) > 0:
                pid = inserted_prod.data[0]['id']
                supabase.table('inventory').insert({
                    'shop_id': shop_id,
                    'product_id': pid,
                    'current_stock': stock,
                    'stock_unit': prod_copy['base_unit'],
                }).execute()

        session_token = f"user-token-{user_id}"
        user_record = user.data[0] if (user.data and len(user.data) > 0) else {'id': user_id, 'email': email, 'full_name': data['full_name']}
        shop_record = shop.data[0] if (shop.data and len(shop.data) > 0) else {'id': shop_id, 'name': data['shop_name'], 'type': shop_type}

        return success_response({
            'user': user_record,
            'shop': shop_record,
            'token': session_token,
            'session': {'access_token': session_token}
        }, 201)
        
    except Exception as e:
        return error_response(f"Registration failed: {str(e)}", "REGISTRATION_ERROR", 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint with direct database fallback to bypass Supabase email confirmation rate limits."""
    data = request.get_json()
    if not data or not data.get('email'):
        return error_response("Email is required", "VALIDATION_ERROR")
    
    email = data['email'].strip().lower()
    
    try:
        supabase = get_supabase()
        
        # 1. Check if email belongs to a demo store account
        for d_token, d_info in DEMO_SHOP_MAP.items():
            if d_info.get('email') == email:
                u_res = supabase.table('users').select('*').eq('email', email).limit(1).execute()
                s_res = supabase.table('shops').select('*').eq('id', d_info['shop_id']).limit(1).execute()
                u_rec = u_res.data[0] if (u_res.data and len(u_res.data) > 0) else {'id': d_info['auth_id'], 'email': email, 'full_name': 'Store Owner'}
                s_rec = s_res.data[0] if (s_res.data and len(s_res.data) > 0) else {'id': d_info['shop_id'], 'name': 'DukaanSetu Store'}
                return success_response({
                    'user': u_rec,
                    'shop': s_rec,
                    'token': d_token,
                    'session': {
                        'access_token': d_token,
                        'refresh_token': d_token,
                    }
                })

        # 2. Check if user exists in database directly
        profile = supabase.table('users').select('*').eq('email', email).limit(1).execute()
        if profile.data and len(profile.data) > 0:
            user_rec = profile.data[0]
            shop_result = supabase.table('shops').select('*').eq('owner_id', user_rec['id']).eq('is_active', True).limit(1).execute()
            shop_rec = shop_result.data[0] if (shop_result.data and len(shop_result.data) > 0) else None
            user_token = f"user-token-{user_rec['id']}"
            return success_response({
                'user': user_rec,
                'shop': shop_rec,
                'token': user_token,
                'session': {
                    'access_token': user_token,
                    'refresh_token': user_token,
                }
            })
            
        # 3. Try Supabase Auth API
        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": data.get('password', ''),
            })
            if result.user:
                prof = supabase.table('users').select('*').eq('auth_id', str(result.user.id)).limit(1).execute()
                shop = None
                if prof.data and len(prof.data) > 0:
                    shop_res = supabase.table('shops').select('*').eq('owner_id', prof.data[0]['id']).eq('is_active', True).limit(1).execute()
                    if shop_res.data and len(shop_res.data) > 0:
                        shop = shop_res.data[0]
                return success_response({
                    'user': prof.data[0] if (prof.data and len(prof.data) > 0) else None,
                    'shop': shop,
                    'token': result.session.access_token,
                    'session': {
                        'access_token': result.session.access_token,
                        'refresh_token': result.session.refresh_token,
                    }
                })
        except Exception:
            pass
        
        return error_response("Invalid credentials. Please check your email and password.", "AUTH_ERROR", 401)
        
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", "AUTH_ERROR", 500)


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile and shop."""
    return success_response({
        'user': getattr(g, 'user', None),
        'shop': getattr(g, 'shop', None),
    })
