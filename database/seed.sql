-- ============================================================
-- DUKAANSETU — Seed Data
-- Run AFTER schema.sql
-- ============================================================

-- NOTE: In production, users are created via Supabase Auth.
-- This seed data is for development/demo purposes.
-- You must first create a user via Supabase Auth, then use that auth_id here.

-- For demo: replace 'DEMO_AUTH_ID' with actual Supabase Auth user UUID after registration.

-- ============================================================
-- DEMO USER (placeholder — will be created via auth flow)
-- ============================================================
-- INSERT INTO users (id, auth_id, email, full_name, phone, language) VALUES
-- ('11111111-1111-1111-1111-111111111111', 'DEMO_AUTH_ID', 'demo@dukaansetu.com', 'Srinivas Kumar', '+91 9876543210', 'te');

-- ============================================================
-- DEMO SHOP (placeholder — will be created via registration)
-- ============================================================
-- INSERT INTO shops (id, owner_id, name, type, phone, address, city, state) VALUES
-- ('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Sri Lakshmi Kirana Store', 'kirana', '+91 9876543210', 'Main Road, Warangal', 'Warangal', 'Telangana');

-- ============================================================
-- GLOBAL UNIT CONVERSIONS (inserted per shop after creation)
-- These will be auto-created when a shop is registered
-- ============================================================

-- For reference, default conversion rules:
-- 1 bag (rice) = 25 kg
-- 1 bag (sugar) = 50 kg  
-- 1 quintal = 100 kg
-- 1 kg = 1000 gram
-- 1 litre = 1000 ml
-- 1 dozen = 12 pieces
-- 1 carton (biscuits) = 24 packets
-- 1 box = 12 pieces

-- ============================================================
-- DEFAULT CATEGORIES (created per shop)
-- ============================================================
-- These categories are inserted automatically during shop creation:
-- Grains & Rice
-- Pulses & Dal
-- Spices & Masala
-- Sugar & Jaggery
-- Oils & Ghee
-- Dairy
-- Beverages
-- Snacks & Biscuits
-- Cleaning & Household
-- Personal Care
-- Other

-- ============================================================
-- SAMPLE PRODUCTS (for demo — use shop_id from actual registration)
-- ============================================================
-- Products will include:
-- 1. Rice (Biyyam) — base: kg, purchase: bag (25kg), sell: kg
-- 2. Wheat (Godhumalu) — base: kg, purchase: bag (50kg), sell: kg
-- 3. Sugar (Chakkera) — base: kg, purchase: bag (50kg), sell: kg
-- 4. Sunflower Oil (Nune) — base: litre, purchase: can (15L), sell: litre
-- 5. Jaggery (Bellam) — base: kg, purchase: kg, sell: kg
-- 6. Toor Dal (Kandi Pappu) — base: kg, purchase: bag (25kg), sell: kg
-- 7. Parle-G Biscuits — base: packet, purchase: carton (24), sell: packet
-- 8. Amul Milk — base: packet, purchase: crate, sell: packet
-- 9. Red Label Tea — base: packet, purchase: box, sell: packet
-- 10. Nescafe Coffee — base: packet, purchase: box, sell: packet

-- ============================================================
-- SAMPLE SUPPLIERS (for demo)
-- ============================================================
-- 1. ABC Traders — Grains, Dal
-- 2. Srinivas Wholesale — Sugar, Oil, Jaggery
-- 3. Lakshmi Distributors — Biscuits, Tea, Coffee, FMCG

-- ============================================================
-- NOTE: Actual seed data is created programmatically via the 
-- Flask backend during the first shop registration.
-- See backend/app/services/seed_service.py
-- ============================================================
