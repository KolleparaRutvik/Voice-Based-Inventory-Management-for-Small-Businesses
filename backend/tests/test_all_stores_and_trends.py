"""Tests for all 12 retail verticals product coverage, entity resolution,
trend alerts service, and TREND_CHECK voice intent interpretation.
"""
import pytest
from app.routes.auth import STORE_SEED_DATA
from app.utils.local_db import (
    LocalDbClient,
    DEMO_SHOP_ID,
    DEMO_JEWEL_SHOP_ID,
    DEMO_FLOWER_SHOP_ID,
    DEMO_CLOTH_SHOP_ID,
    DEMO_PHARMA_SHOP_ID,
    DEMO_BAKERY_SHOP_ID,
    DEMO_REST_SHOP_ID,
    DEMO_TEA_SHOP_ID,
    DEMO_HARDWARE_SHOP_ID,
    DEMO_AUTO_SHOP_ID,
    DEMO_VEG_SHOP_ID,
    DEMO_ELEC_SHOP_ID,
)
from app.utils.entity_resolver import resolve_product
from app.services.trend_alerts import generate_trend_alerts, get_voice_trend_insights
from app.routes.voice import build_local_interpretation


def test_52_all_12_stores_have_rich_seed_catalog():
    """Verify all 12 store verticals have 7-8 products, suppliers, and customers."""
    expected_stores = [
        'kirana', 'flowers', 'jewellery', 'clothing', 'pharmacy', 'bakery',
        'restaurant', 'teacoffee', 'hardware', 'autoparts', 'vegetables', 'electronics'
    ]
    for stype in expected_stores:
        assert stype in STORE_SEED_DATA, f"Missing store seed data for {stype}"
        data = STORE_SEED_DATA[stype]
        products = data.get('products', [])
        suppliers = data.get('suppliers', [])
        customers = data.get('customers', [])

        assert len(products) >= 7, f"{stype} should have at least 7 products, found {len(products)}"
        assert len(suppliers) >= 2, f"{stype} should have at least 2 suppliers, found {len(suppliers)}"
        assert len(customers) >= 2, f"{stype} should have at least 2 customers, found {len(customers)}"

        for p in products:
            assert 'name' in p and len(p['name']) > 0
            assert 'base_unit' in p and len(p['base_unit']) > 0
            price = p.get('selling_price') or p.get('purchase_price') or p.get('price')
            assert price is not None and price > 0, f"Product {p['name']} missing valid price"
            assert 'minimum_stock' in p and p['minimum_stock'] >= 0


def test_53_local_db_all_demo_stores_seeded():
    """Verify in-memory local DB seeds all 12 store types with full catalogs."""
    shop_ids = [
        DEMO_SHOP_ID, DEMO_JEWEL_SHOP_ID, DEMO_FLOWER_SHOP_ID, DEMO_CLOTH_SHOP_ID,
        DEMO_PHARMA_SHOP_ID, DEMO_BAKERY_SHOP_ID, DEMO_REST_SHOP_ID, DEMO_TEA_SHOP_ID,
        DEMO_HARDWARE_SHOP_ID, DEMO_AUTO_SHOP_ID, DEMO_VEG_SHOP_ID, DEMO_ELEC_SHOP_ID
    ]
    client = LocalDbClient()
    for sid in shop_ids:
        prods = client.table('products').select('*').eq('shop_id', sid).execute().data
        assert len(prods) >= 7, f"Local DB shop {sid} should have >= 7 products, found {len(prods)}"
        
        inv = client.table('inventory').select('*').eq('shop_id', sid).execute().data
        assert len(inv) >= len(prods), f"Inventory missing for some products in shop {sid}"


def test_54_entity_resolver_across_all_store_types():
    """Test entity resolution works for distinctive products in diverse store types."""
    # Bakery
    bakery_prods = [
        {'id': 'b1', 'name': 'Milk Bread (400g)', 'telugu_name': 'మిల్క్ బ్రెడ్'},
        {'id': 'b2', 'name': 'Kaju Katli (కాజూ కట్లీ)', 'telugu_name': 'కాజూ కట్లీ'},
        {'id': 'b3', 'name': 'Cream Roll', 'telugu_name': 'క్రీమ్ రోల్'}
    ]
    r_b1 = resolve_product('bread', bakery_prods)
    assert r_b1['matched_product'] is not None and r_b1['matched_product']['id'] == 'b1'
    r_b2 = resolve_product('కాజూ కట్లీ', bakery_prods)
    assert r_b2['matched_product'] is not None and r_b2['matched_product']['id'] == 'b2'
    r_b3 = resolve_product('cream roll', bakery_prods)
    assert r_b3['matched_product'] is not None and r_b3['matched_product']['id'] == 'b3'

    # Restaurant
    rest_prods = [
        {'id': 'r1', 'name': 'Chicken Dum Biryani', 'telugu_name': 'చికెన్ దమ్ బిర్యానీ'},
        {'id': 'r2', 'name': 'Idli Sambar (4 pcs)', 'telugu_name': 'ఇడ్లీ సాంబార్'},
        {'id': 'r3', 'name': 'Masala Dosa', 'telugu_name': 'మసాలా దోశ'}
    ]
    r_r1 = resolve_product('biryani', rest_prods)
    assert r_r1['matched_product'] is not None and r_r1['matched_product']['id'] == 'r1'
    r_r2 = resolve_product('idli', rest_prods)
    assert r_r2['matched_product'] is not None and r_r2['matched_product']['id'] == 'r2'
    r_r3 = resolve_product('దోశ', rest_prods)
    assert r_r3['matched_product'] is not None and r_r3['matched_product']['id'] == 'r3'

    # Hardware
    hw_prods = [
        {'id': 'h1', 'name': '9W LED Bulbs', 'telugu_name': '9W ఎల్‌ఈడీ బల్బులు'},
        {'id': 'h2', 'name': 'PVC Pipe 1-inch (20ft)', 'telugu_name': 'పీవీసీ పైపు 1 అంగుళం'},
        {'id': 'h3', 'name': '2.5 sq mm Copper Wire Roll', 'telugu_name': 'కాపర్ వైర్ రోల్'}
    ]
    r_h1 = resolve_product('led bulbs', hw_prods)
    assert r_h1['matched_product'] is not None and r_h1['matched_product']['id'] == 'h1'
    r_h2 = resolve_product('pvc pipe', hw_prods)
    assert r_h2['matched_product'] is not None and r_h2['matched_product']['id'] == 'h2'
    r_h3 = resolve_product('copper wire', hw_prods)
    assert r_h3['matched_product'] is not None and r_h3['matched_product']['id'] == 'h3'

    # Auto Parts
    auto_prods = [
        {'id': 'a1', 'name': '4T 10W-30 Engine Oil (1 Litre)', 'telugu_name': '4T 10W-30 ఇంజిన్ ఆయిల్'},
        {'id': 'a2', 'name': 'Two-Wheeler Spark Plug', 'telugu_name': 'స్పార్క్ ప్లగ్'},
        {'id': 'a3', 'name': 'Front Disc Brake Pads', 'telugu_name': 'ఫ్రంట్ బ్రేక్ ప్యాడ్లు'}
    ]
    r_a1 = resolve_product('engine oil', auto_prods)
    assert r_a1['matched_product'] is not None and r_a1['matched_product']['id'] == 'a1'
    r_a2 = resolve_product('spark plug', auto_prods)
    assert r_a2['matched_product'] is not None and r_a2['matched_product']['id'] == 'a2'
    r_a3 = resolve_product('brake pads', auto_prods)
    assert r_a3['matched_product'] is not None and r_a3['matched_product']['id'] == 'a3'

    # Electronics
    elec_prods = [
        {'id': 'e1', 'name': '20W Type-C Fast Charger', 'telugu_name': '20W టైప్-సి ఫాస్ట్ ఛార్జర్'},
        {'id': 'e2', 'name': 'Bluetooth Wireless Earbuds', 'telugu_name': 'బ్లూటూత్ ఇయర్‌బడ్స్'},
        {'id': 'e3', 'name': 'Redmi 13C 5G (128GB)', 'telugu_name': 'రెడ్‌మి 13C 5G'}
    ]
    r_e1 = resolve_product('type c charger', elec_prods)
    assert r_e1['matched_product'] is not None and r_e1['matched_product']['id'] == 'e1'
    r_e2 = resolve_product('earbuds', elec_prods)
    assert r_e2['matched_product'] is not None and r_e2['matched_product']['id'] == 'e2'
    r_e3 = resolve_product('redmi', elec_prods)
    assert r_e3['matched_product'] is not None and r_e3['matched_product']['id'] == 'e3'


def test_55_trend_alerts_service():
    """Verify trend_alerts service analyzes demo shop inventory and returns alerts."""
    shop_id = DEMO_SHOP_ID
    alerts = generate_trend_alerts(shop_id)
    assert isinstance(alerts, list)
    for alert in alerts:
        assert 'type' in alert
        assert 'title' in alert
        assert 'message' in alert


def test_56_voice_trend_insights():
    """Verify spoken & written voice insights generation in Telugu, Hindi, and English."""
    shop_id = DEMO_SHOP_ID
    insights_en = get_voice_trend_insights(shop_id, 'en')
    assert 'voice_text' in insights_en
    assert 'answer' in insights_en
    assert len(insights_en['voice_text']) > 0

    insights_te = get_voice_trend_insights(shop_id, 'te')
    assert 'voice_text' in insights_te
    assert len(insights_te['voice_text']) > 0

    insights_hi = get_voice_trend_insights(shop_id, 'hi')
    assert 'voice_text' in insights_hi
    assert len(insights_hi['voice_text']) > 0


def test_57_voice_trend_intent_interpretation():
    """Verify TREND_CHECK intent is recognized by local rule-based voice interpreter."""
    products = [{'id': 'p1', 'name': 'Sona Masoori Rice'}]
    customers = [{'id': 'c1', 'name': 'Ramesh Kumar'}]
    facts = {}

    # English phrases
    r1 = build_local_interpretation("Which items are selling fast and trending?", products, customers, facts)
    assert r1.get('intent') == 'TREND_CHECK'

    r2 = build_local_interpretation("show me fast moving products", products, customers, facts)
    assert r2.get('intent') == 'TREND_CHECK'

    # Telugu phrases
    r3 = build_local_interpretation("ఏ వస్తువులు ఎక్కువగా అమ్ముడవుతున్నాయి?", products, customers, facts)
    assert r3.get('intent') == 'TREND_CHECK'

    r4 = build_local_interpretation("షాప్ ట్రెండ్ ఎలా ఉంది?", products, customers, facts)
    assert r4.get('intent') == 'TREND_CHECK'

    # Hindi phrases
    r5 = build_local_interpretation("kaun se items fast sell ho rahe hain", products, customers, facts)
    assert r5.get('intent') == 'TREND_CHECK'
