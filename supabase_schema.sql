-- Supabase Initial Database Schema
-- Copy and paste this script into your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query) and click Run.

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    title_en TEXT,
    category_path TEXT NOT NULL,
    category_leaf TEXT NOT NULL,
    brand TEXT,
    oem_part_number TEXT,
    product_type TEXT DEFAULT 'finished_good',
    specifications JSONB DEFAULT '{}'::jsonb,
    specifications_raw JSONB DEFAULT '{}'::jsonb,
    description TEXT,
    images TEXT[] DEFAULT '{}'::text[],
    seller_name TEXT,
    seller_type TEXT DEFAULT 'distributor',
    seller_rating REAL,
    seller_location TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT products_source_source_id_key UNIQUE (source, source_id)
);

-- 2. Price Records Table
CREATE TABLE IF NOT EXISTS price_records (
    id BIGSERIAL PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    price NUMERIC(15,2) NOT NULL,
    currency TEXT NOT NULL,
    price_usd NUMERIC(15,2) NOT NULL,
    price_per_unit NUMERIC(15,4),
    unit_of_measure TEXT,
    min_order_qty INTEGER DEFAULT 1,
    price_tiers JSONB DEFAULT '[]'::jsonb,
    shipping_cost NUMERIC(10,2),
    discount_pct REAL,
    is_promo BOOLEAN DEFAULT FALSE,
    stock_status TEXT DEFAULT 'in_stock',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Supplier Intake Submissions Table
CREATE TABLE IF NOT EXISTS supplier_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    country TEXT NOT NULL,
    category TEXT NOT NULL,
    product_name TEXT NOT NULL,
    specifications JSONB DEFAULT '{}'::jsonb,
    unit_price NUMERIC(15,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    moq INTEGER DEFAULT 1,
    lead_time_days INTEGER DEFAULT 7,
    tiered_pricing JSONB DEFAULT '[]'::jsonb,
    certifications TEXT[] DEFAULT '{}'::text[],
    images TEXT[] DEFAULT '{}'::text[],
    notes TEXT,
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_products_category_leaf ON products(category_leaf);
CREATE INDEX IF NOT EXISTS idx_products_oem_part ON products(oem_part_number) WHERE oem_part_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_price_records_product_time ON price_records(product_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_records_price_usd ON price_records(price_usd);
CREATE INDEX IF NOT EXISTS idx_supplier_submissions_email ON supplier_submissions(contact_email);
