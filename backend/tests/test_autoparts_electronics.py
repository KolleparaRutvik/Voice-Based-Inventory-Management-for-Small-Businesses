"""Tests for Auto Parts & Spares and Electronics & Mobiles retail verticals.
Verifies 12-product rich catalog depth, 4 suppliers, 3 borrowers, multilingual entity resolution,
units (kit, pair, bottle, can), vertical seasonal demand intelligence (Ayudha Pooja & Diwali surge),
and voice assistant command interpretations.
"""
import pytest
from app.routes.auth import STORE_SEED_DATA
from app.utils.local_db import (
    LocalDbClient,
    DEMO_AUTO_SHOP_ID,
    DEMO_ELEC_SHOP_ID,
)
from app.utils.entity_resolver import resolve_product, normalize_unit, extract_numbers_and_units
from app.services.festival_service import analyze_festival_demand
from app.routes.voice import build_local_interpretation


def test_autoparts_and_electronics_have_12_products_and_rich_entities():
    """Verify Auto Parts & Electronics have full 12-product catalogs, 4 suppliers, 3 borrowers."""
    # 1. Auto Parts
    auto_data = STORE_SEED_DATA['autoparts']
    assert len(auto_data['products']) == 12, f"Auto Parts must have 12 products, found {len(auto_data['products'])}"
    assert len(auto_data['suppliers']) >= 4, f"Auto Parts must have 4 suppliers, found {len(auto_data['suppliers'])}"
    assert len(auto_data['customers']) >= 3, f"Auto Parts must have 3 borrowers/mechanics, found {len(auto_data['customers'])}"

    # 2. Electronics
    elec_data = STORE_SEED_DATA['electronics']
    assert len(elec_data['products']) == 12, f"Electronics must have 12 products, found {len(elec_data['products'])}"
    assert len(elec_data['suppliers']) >= 4, f"Electronics must have 4 suppliers, found {len(elec_data['suppliers'])}"
    assert len(elec_data['customers']) >= 3, f"Electronics must have 3 borrowers/customers, found {len(elec_data['customers'])}"


def test_local_db_seeded_with_full_autoparts_and_electronics_data():
    """Verify in-memory local DB seeds full 12 products, inventory, suppliers, and borrowings."""
    client = LocalDbClient()

    # Auto Parts
    auto_prods = client.table('products').select('*').eq('shop_id', DEMO_AUTO_SHOP_ID).execute().data
    auto_inv = client.table('inventory').select('*').eq('shop_id', DEMO_AUTO_SHOP_ID).execute().data
    auto_supp = client.table('suppliers').select('*').eq('shop_id', DEMO_AUTO_SHOP_ID).execute().data
    auto_borr = client.table('borrowings').select('*').eq('shop_id', DEMO_AUTO_SHOP_ID).execute().data

    assert len(auto_prods) == 12
    assert len(auto_inv) == 12
    assert len(auto_supp) >= 4
    assert len(auto_borr) >= 3

    # Electronics
    elec_prods = client.table('products').select('*').eq('shop_id', DEMO_ELEC_SHOP_ID).execute().data
    elec_inv = client.table('inventory').select('*').eq('shop_id', DEMO_ELEC_SHOP_ID).execute().data
    elec_supp = client.table('suppliers').select('*').eq('shop_id', DEMO_ELEC_SHOP_ID).execute().data
    elec_borr = client.table('borrowings').select('*').eq('shop_id', DEMO_ELEC_SHOP_ID).execute().data

    assert len(elec_prods) == 12
    assert len(elec_inv) == 12
    assert len(elec_supp) >= 4
    assert len(elec_borr) >= 3


def test_autoparts_multilingual_entity_resolution():
    """Test resolution of automotive terms across English, Telugu, and brand names."""
    client = LocalDbClient()
    auto_prods = client.table('products').select('*').eq('shop_id', DEMO_AUTO_SHOP_ID).execute().data

    cases = [
        ('Castrol 4T oil', 'Castrol Activ 4T 20W-40 1L'),
        ('Motul oil', 'Motul 3000 4T Plus 10W-30 1L'),
        ('Splendor brake shoes', 'Hero Splendor Brake Shoes'),
        ('Pulsar disc pads', 'Front Disc Brake Pads Pulsar / Apache'),
        ('Amaron battery', 'Amaron 12V Bike Battery 4Ah'),
        ('MRF tyre', 'MRF Nylogrip Tyre 90/90-12 Activa'),
        ('NGK spark plug', 'Spark Plug NGK 2-Wheeler'),
        ('Rolon chain sprocket', 'Rolon Chain Sprocket Kit Splendor'),
        ('Pulsar clutch cable', 'Clutch Cable for Bajaj Pulsar'),
        ('Roots horn', 'Roots 12V High-Tone Bike Horn'),
        ('Hero air filter', 'Air Filter for Hero Splendor / HF'),
        ('Chain lube spray', 'WD-40 / Motul Chain Lube Spray 400ml'),
        ('మోబిల్', 'Castrol Activ 4T 20W-40 1L'),
        ('బ్యాటరీ', 'Amaron 12V Bike Battery 4Ah'),
        ('టైరు', 'MRF Nylogrip Tyre 90/90-12 Activa'),
    ]

    for query, expected_name in cases:
        res = resolve_product(query, auto_prods)
        assert res['matched_product'] is not None, f"Failed to resolve Auto Parts query '{query}'"
        assert expected_name in res['matched_product']['name'], f"Expected {expected_name} in {res['matched_product']['name']}"


def test_electronics_multilingual_entity_resolution():
    """Test resolution of electronic terms across English, Telugu, and model names."""
    client = LocalDbClient()
    elec_prods = client.table('products').select('*').eq('shop_id', DEMO_ELEC_SHOP_ID).execute().data

    cases = [
        ('Samsung 5G phone', 'Samsung Galaxy A15 5G 128GB'),
        ('Redmi 13C 5G', 'Redmi 13C 5G 128GB'),
        ('boAt airdopes', 'boAt Airdopes 141 Bluetooth Earbuds'),
        ('boAt rockerz neckband', 'boAt Rockerz 255 Pro+ Neckband'),
        ('20W fast charger', 'Fast 20W Type-C Charger Adapter'),
        ('33W soniccharge', 'SuperVOOC 33W Fast Charger with Cable'),
        ('10000mah power bank', '10000mAh Dual USB Power Bank'),
        ('Ambrane 20000 power bank', '20000mAh 22.5W Fast Power Bank'),
        ('Type C cable', 'Braided 1.5m Type-C Fast Cable'),
        ('9D tempered glass', '9D Edge-to-Edge Tempered Glass'),
        ('SanDisk 64GB memory card', 'SanDisk 64GB Ultra MicroSD Card'),
        ('Noise smart watch', 'Noise ColorFit Pulse Smart Watch'),
        ('శామ్‌సంగ్ మొబైల్', 'Samsung Galaxy A15 5G 128GB'),
        ('ఇయర్ బడ్స్', 'boAt Airdopes 141 Bluetooth Earbuds'),
        ('స్క్రీన్ గార్డ్', '9D Edge-to-Edge Tempered Glass'),
    ]

    for query, expected_name in cases:
        res = resolve_product(query, elec_prods)
        assert res['matched_product'] is not None, f"Failed to resolve Electronics query '{query}'"
        assert expected_name in res['matched_product']['name'], f"Expected {expected_name} in {res['matched_product']['name']}"


def test_automotive_and_electronics_units():
    """Verify specific retail units normalize correctly."""
    assert normalize_unit('kit') == 'kit'
    assert normalize_unit('kits') == 'kit'
    assert normalize_unit('pair') == 'pair'
    assert normalize_unit('pairs') == 'pair'
    assert normalize_unit('bottle') == 'bottle'
    assert normalize_unit('can') == 'can'
    assert normalize_unit('piece') == 'piece'
    assert normalize_unit('set') == 'set'


def test_autoparts_seasonal_festival_demand():
    """Verify seasonal surge analysis tailored to Auto Parts for Ayudha Pooja / Dussehra."""
    res = analyze_festival_demand(
        shop_id=DEMO_AUTO_SHOP_ID,
        festival_name='Navratri / Dussehra',
        reference_date='2026-09-21'
    )
    assert res['festival'] is not None
    assert 'Navratri / Dussehra' in res['festival']['event']
    recs = res['recommendations']
    assert len(recs) > 0, "Expected recommendations for Auto Parts during Ayudha Pooja"

    # Check key automotive surge items are present in recommendations
    rec_item_names = [r['item_name'] for r in recs]
    assert any('Engine Oil' in name for name in rec_item_names), "Engine oil must have surge target during Ayudha Pooja"
    assert any('Brake Shoes' in name or 'Brake' in name for name in rec_item_names), "Brake parts must have surge target"


def test_electronics_seasonal_festival_demand():
    """Verify seasonal surge analysis tailored to Electronics for Diwali / Dhanteras."""
    res = analyze_festival_demand(
        shop_id=DEMO_ELEC_SHOP_ID,
        festival_name='Diwali / Dhanteras',
        reference_date='2026-09-21'
    )
    assert res['festival'] is not None
    assert 'Diwali' in res['festival']['event']
    recs = res['recommendations']
    assert len(recs) > 0, "Expected recommendations for Electronics during Diwali"

    rec_item_names = [r['item_name'] for r in recs]
    assert any('5G Smartphone' in name for name in rec_item_names), "5G Smartphone must have surge target during Diwali"
    assert any('Earbuds' in name or 'Audio' in name or 'boAt' in name for name in rec_item_names), "Audio earbuds must have surge target"
    assert any('Smart Watch' in name for name in rec_item_names), "Smart watch must have surge target"


def test_voice_commands_autoparts_and_electronics():
    """Verify local voice interpretation for auto parts and electronics commands."""
    # 1. Auto Parts: Stock check
    f1 = extract_numbers_and_units("Castrol engine oil entha undi?")
    res_stock = build_local_interpretation("Castrol engine oil entha undi?", None, None, f1)
    assert res_stock['intent'] == 'STOCK_CHECK'

    # 2. Electronics: Udhar loan recording
    f2 = extract_numbers_and_units("Kalyan ki 1500 charger udhar rayi")
    res_udhar = build_local_interpretation("Kalyan ki 1500 charger udhar rayi", None, None, f2)
    assert res_udhar['intent'] in ('UDHAR_LOAN', 'BORROW_OUT')
    assert res_udhar['amount'] == 1500.0 or res_udhar['amount'] == 1500

    # 3. Auto Parts: Stock in
    f3 = extract_numbers_and_units("10 bottles castrol engine oil vachayi")
    res_in = build_local_interpretation("10 bottles castrol engine oil vachayi", None, None, f3)
    assert res_in['intent'] == 'STOCK_IN'
    assert res_in['quantity'] == 10.0

    # 4. Electronics: Stock out / sale
    f4 = extract_numbers_and_units("2 redmi mobiles ammamu")
    res_out = build_local_interpretation("2 redmi mobiles ammamu", None, None, f4)
    assert res_out['intent'] == 'STOCK_OUT'
    assert res_out['quantity'] == 2.0

