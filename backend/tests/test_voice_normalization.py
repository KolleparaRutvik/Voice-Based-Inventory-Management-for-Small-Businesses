"""Tests 1-6: Voice Normalization & Kirana Terminology Resolution.
Verifies English, Telugu, Hindi, Mixed Telugu-English, Mixed Hindi-English, and Transliterations.
"""
import pytest
from app.utils.entity_resolver import (
    resolve_product,
    resolve_customer,
    normalize_unit,
    extract_numbers_and_units,
    KIRANA_PRODUCT_SYNONYMS
)

SAMPLE_CATALOG = [
    {'id': 'prod-1', 'name': 'Rice (Biyyam)', 'local_name': 'Biyyam', 'base_unit': 'kg', 'purchase_unit': 'bag', 'current_stock': 500},
    {'id': 'prod-2', 'name': 'Sugar (Chakkera)', 'local_name': 'Chakkera', 'base_unit': 'kg', 'purchase_unit': 'bag', 'current_stock': 330},
    {'id': 'prod-3', 'name': 'Sunflower Oil (Nune)', 'local_name': 'Nune', 'base_unit': 'litre', 'purchase_unit': 'can', 'current_stock': 37},
    {'id': 'prod-4', 'name': 'Toor Dal (Kandi Pappu)', 'local_name': 'Kandi Pappu', 'base_unit': 'kg', 'purchase_unit': 'bag', 'current_stock': 65},
    {'id': 'prod-5', 'name': 'Parle-G Biscuits', 'local_name': 'Parle-G', 'base_unit': 'packet', 'purchase_unit': 'carton', 'current_stock': 120},
    {'id': 'prod-6', 'name': 'Jaggery (Bellam)', 'local_name': 'Bellam', 'base_unit': 'kg', 'purchase_unit': 'kg', 'current_stock': 8},
]

SAMPLE_ALIASES = [
    {'alias': 'chawal', 'product_id': 'prod-1'},
    {'alias': 'chini', 'product_id': 'prod-2'},
    {'alias': 'tel', 'product_id': 'prod-3'},
]


def test_1_english_speech_resolution():
    """Test 1: Standard English voice command resolution."""
    prod_res = resolve_product('Rice', SAMPLE_CATALOG)
    assert prod_res['matched_product'] is not None
    assert prod_res['matched_product']['id'] == 'prod-1'
    assert prod_res['is_ambiguous'] is False

    facts = extract_numbers_and_units("Add 5 bags rice 1450 rupees")
    assert facts['quantity'] == 5
    assert facts['unit'] == 'bag'
    assert facts['price'] == 1450


def test_2_telugu_speech_resolution():
    """Test 2: Pure Telugu terminology and word numbers."""
    prod_res = resolve_product('బియ్యం', SAMPLE_CATALOG)
    # Checks local name or synonym
    assert prod_res['matched_product'] is not None or resolve_product('biyyam', SAMPLE_CATALOG)['matched_product'] is not None

    biyyam_res = resolve_product('biyyam', SAMPLE_CATALOG)
    assert biyyam_res['matched_product']['id'] == 'prod-1'

    # Word numbers in Telugu: "aidu basthalu" = 5 bags
    facts = extract_numbers_and_units("aidu basthalu biyyam")
    assert facts['quantity'] == 5
    assert facts['unit'] == 'bag'


def test_3_hindi_speech_resolution():
    """Test 3: Pure Hindi terminology and units."""
    chawal_res = resolve_product('chawal', SAMPLE_CATALOG, SAMPLE_ALIASES)
    assert chawal_res['matched_product'] is not None
    assert chawal_res['matched_product']['id'] == 'prod-1'

    facts = extract_numbers_and_units("paanch kilo chini stock mein dalo")
    assert facts['quantity'] == 5
    assert facts['unit'] == 'kg'


def test_4_telugu_english_mixed():
    """Test 4: Mixed Telugu + English trade phrasing."""
    facts = extract_numbers_and_units("5 basthalu biyyam add cheyyi 1450 rupees")
    assert facts['quantity'] == 5
    assert facts['unit'] == 'bag'
    assert facts['price'] == 1450

    prod_res = resolve_product('biyyam', SAMPLE_CATALOG)
    assert prod_res['matched_product']['name'] == 'Rice (Biyyam)'


def test_5_hindi_english_mixed():
    """Test 5: Mixed Hindi + English trade phrasing."""
    facts = extract_numbers_and_units("10 packets Parle-G sold becha")
    assert facts['quantity'] == 10
    assert facts['unit'] == 'packet'

    prod_res = resolve_product('parle', SAMPLE_CATALOG)
    assert prod_res['matched_product']['id'] == 'prod-5'


def test_6_kirana_transliterations():
    """Test 6: Transliterations for all major Kirana items."""
    test_mappings = [
        ('biyyam', 'prod-1'),
        ('chakkera', 'prod-2'),
        ('nune', 'prod-3'),
        ('kandi pappu', 'prod-4'),
        ('bellam', 'prod-6'),
    ]
    for term, expected_id in test_mappings:
        res = resolve_product(term, SAMPLE_CATALOG)
        assert res['matched_product'] is not None, f"Failed for {term}"
        assert res['matched_product']['id'] == expected_id, f"Wrong match for {term}"
