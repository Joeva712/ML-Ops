import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import structlog
from config.settings import settings

logger = structlog.get_logger(__name__)

import httpx

class SupabaseRESTClient:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    def table(self, name: str):
        return SupabaseTable(self.url, name, self.headers)

class SupabaseTable:
    def __init__(self, base_url: str, table_name: str, headers: dict):
        self.url = f"{base_url}/rest/v1/{table_name}"
        self.headers = headers

    def select(self, columns: str = "*"):
        return SupabaseQuery(self.url, self.headers, "GET", params={"select": columns})

    def insert(self, data: dict):
        headers = self.headers.copy()
        headers["Prefer"] = "return=representation"
        res = httpx.post(self.url, json=data, headers=headers)
        res.raise_for_status()
        return SupabaseResponse(res.json())

    def update(self, data: dict):
        return SupabaseQuery(self.url, self.headers, "PATCH", json_data=data)

class SupabaseQuery:
    def __init__(self, url: str, headers: dict, method: str, params: dict = None, json_data: dict = None):
        self.url = url
        self.headers = headers.copy()
        self.method = method
        self.params = params or {}
        self.json_data = json_data or {}

    def eq(self, field: str, value: Any):
        self.params[field] = f"eq.{value}"
        return self

    def execute(self):
        if self.method == "GET":
            res = httpx.get(self.url, params=self.params, headers=self.headers)
        elif self.method == "PATCH":
            self.headers["Prefer"] = "return=representation"
            res = httpx.patch(self.url, json=self.json_data, params=self.params, headers=self.headers)
        res.raise_for_status()
        return SupabaseResponse(res.json())

class SupabaseResponse:
    def __init__(self, data):
        self.data = data

# Supabase Client Initialization
supabase_client = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        supabase_client = SupabaseRESTClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Custom Supabase REST client initialized successfully")
    except Exception as e:
        logger.warning("Failed to initialize Supabase REST. Falling back to SQLite.", error=str(e))
else:
    logger.info("Supabase URL or Key missing. Using local SQLite database as fallback.")


# Local SQLite Database Fallback
SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "price_intelligence.db")

def init_sqlite_db():
    """Initializes SQLite tables corresponding to the Supabase schemas for local fallback/testing."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        source TEXT,
        source_id TEXT,
        source_url TEXT,
        title TEXT,
        title_en TEXT,
        category_path TEXT,
        category_leaf TEXT,
        brand TEXT,
        oem_part_number TEXT,
        product_type TEXT,
        specifications TEXT,
        specifications_raw TEXT,
        description TEXT,
        images TEXT,
        seller_name TEXT,
        seller_type TEXT,
        seller_rating REAL,
        seller_location TEXT,
        created_at TEXT,
        updated_at TEXT,
        UNIQUE(source, source_id)
    )
    """)
    
    # Price records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT,
        source TEXT,
        price REAL,
        currency TEXT,
        price_usd REAL,
        price_per_unit REAL,
        unit_of_measure TEXT,
        min_order_qty INTEGER,
        price_tiers TEXT,
        shipping_cost REAL,
        discount_pct REAL,
        is_promo INTEGER,
        stock_status TEXT,
        recorded_at TEXT,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    
    # Supplier Intake Submissions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS supplier_submissions (
        id TEXT PRIMARY KEY,
        company_name TEXT,
        contact_email TEXT,
        country TEXT,
        category TEXT,
        product_name TEXT,
        specifications TEXT,
        unit_price REAL,
        currency TEXT,
        moq INTEGER,
        lead_time_days INTEGER,
        tiered_pricing TEXT,
        certifications TEXT,
        images TEXT,
        notes TEXT,
        status TEXT,
        submitted_at TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info("SQLite database tables initialized", path=SQLITE_DB_PATH)

# Initialize on import
init_sqlite_db()

# DB Helper Functions
def upsert_product(product: Dict[str, Any]) -> str:
    """Upserts a product into either Supabase or SQLite."""
    product_id = product.get("id") or str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat()
    
    if supabase_client:
        try:
            # Prepare payload for Supabase
            payload = {
                "source": product.get("source"),
                "source_id": product.get("source_id"),
                "source_url": product.get("source_url"),
                "title": product.get("title"),
                "title_en": product.get("title_en"),
                "category_path": ",".join(product.get("category_path", [])),
                "category_leaf": product.get("category_leaf"),
                "brand": product.get("brand"),
                "oem_part_number": product.get("oem_part_number"),
                "product_type": product.get("product_type", "finished_good"),
                "specifications": product.get("specifications", {}),
                "specifications_raw": product.get("specifications_raw", {}),
                "description": product.get("description"),
                "images": product.get("images", []),
                "seller_name": product.get("seller_name"),
                "seller_type": product.get("seller_type"),
                "seller_rating": product.get("seller_rating"),
                "seller_location": product.get("seller_location"),
                "updated_at": now_str
            }
            
            # Check if product already exists
            res = supabase_client.table("products").select("id").eq("source", product["source"]).eq("source_id", product["source_id"]).execute()
            if res.data:
                product_id = res.data[0]["id"]
                supabase_client.table("products").update(payload).eq("id", product_id).execute()
            else:
                payload["id"] = product_id
                payload["created_at"] = now_str
                supabase_client.table("products").insert(payload).execute()
            
            return product_id
        except Exception as e:
            logger.error("Supabase upsert product failed, retrying on SQLite", error=str(e))
            
    # SQLite fallback
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    import json
    
    # Check duplicate
    cursor.execute("SELECT id FROM products WHERE source = ? AND source_id = ?", (product["source"], product["source_id"]))
    row = cursor.fetchone()
    
    specs_json = json.dumps(product.get("specifications", {}))
    specs_raw_json = json.dumps(product.get("specifications_raw", {}))
    images_json = json.dumps(product.get("images", []))
    cat_path_str = ",".join(product.get("category_path", []))
    
    if row:
        product_id = row[0]
        cursor.execute("""
        UPDATE products SET
            source_url = ?, title = ?, title_en = ?, category_path = ?, category_leaf = ?,
            brand = ?, oem_part_number = ?, product_type = ?, specifications = ?, specifications_raw = ?,
            description = ?, images = ?, seller_name = ?, seller_type = ?, seller_rating = ?,
            seller_location = ?, updated_at = ?
        WHERE id = ?
        """, (
            product.get("source_url"), product.get("title"), product.get("title_en"), cat_path_str, product.get("category_leaf"),
            product.get("brand"), product.get("oem_part_number"), product.get("product_type", "finished_good"), specs_json, specs_raw_json,
            product.get("description"), images_json, product.get("seller_name"), product.get("seller_type"), product.get("seller_rating"),
            product.get("seller_location"), now_str, product_id
        ))
    else:
        cursor.execute("""
        INSERT INTO products (
            id, source, source_id, source_url, title, title_en, category_path, category_leaf,
            brand, oem_part_number, product_type, specifications, specifications_raw, description,
            images, seller_name, seller_type, seller_rating, seller_location, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id, product["source"], product["source_id"], product.get("source_url"), product.get("title"), product.get("title_en"),
            cat_path_str, product.get("category_leaf"), product.get("brand"), product.get("oem_part_number"),
            product.get("product_type", "finished_good"), specs_json, specs_raw_json, product.get("description"),
            images_json, product.get("seller_name"), product.get("seller_type"), product.get("seller_rating"),
            product.get("seller_location"), now_str, now_str
        ))
    conn.commit()
    conn.close()
    return product_id

def insert_price_record(record: Dict[str, Any]) -> None:
    """Inserts a price observation into the database."""
    now_str = datetime.utcnow().isoformat()
    
    if supabase_client:
        try:
            payload = {
                "product_id": record["product_id"],
                "source": record["source"],
                "price": float(record["price"]),
                "currency": record["currency"],
                "price_usd": float(record["price_usd"]),
                "price_per_unit": float(record["price_per_unit"]) if record.get("price_per_unit") else None,
                "unit_of_measure": record.get("unit_of_measure"),
                "min_order_qty": record.get("min_order_qty"),
                "price_tiers": record.get("price_tiers", []),
                "shipping_cost": float(record["shipping_cost"]) if record.get("shipping_cost") else None,
                "discount_pct": float(record["discount_pct"]) if record.get("discount_pct") else None,
                "is_promo": record.get("is_promo", False),
                "stock_status": record.get("stock_status", "in_stock"),
                "recorded_at": now_str
            }
            supabase_client.table("price_records").insert(payload).execute()
            return
        except Exception as e:
            logger.error("Supabase insert price failed, falling back to SQLite", error=str(e))
            
    # SQLite
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    import json
    cursor.execute("""
    INSERT INTO price_records (
        product_id, source, price, currency, price_usd, price_per_unit, unit_of_measure,
        min_order_qty, price_tiers, shipping_cost, discount_pct, is_promo, stock_status, recorded_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["product_id"], record["source"], float(record["price"]), record["currency"], float(record["price_usd"]),
        float(record["price_per_unit"]) if record.get("price_per_unit") else None, record.get("unit_of_measure"),
        record.get("min_order_qty"), json.dumps(record.get("price_tiers", [])),
        float(record["shipping_cost"]) if record.get("shipping_cost") else None,
        float(record["discount_pct"]) if record.get("discount_pct") else None,
        1 if record.get("is_promo") else 0, record.get("stock_status", "in_stock"), now_str
    ))
    conn.commit()
    conn.close()

def get_latest_prices(category: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Gets the latest products and their most recent price details."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    import json
    
    sql = """
    SELECT p.*, pr.price, pr.currency, pr.price_usd, pr.price_per_unit, pr.unit_of_measure, 
           pr.min_order_qty, pr.price_tiers, pr.stock_status, pr.recorded_at
    FROM products p
    LEFT JOIN (
        SELECT * FROM price_records 
        GROUP BY product_id 
        HAVING max(recorded_at)
    ) pr ON p.id = pr.product_id
    WHERE 1=1
    """
    params = []
    
    if category:
        sql += " AND p.category_leaf = ?"
        params.append(category)
        
    if query:
        sql += " AND (p.title LIKE ? OR p.brand LIKE ? OR p.oem_part_number LIKE ?)"
        q_wildcard = f"%{query}%"
        params.extend([q_wildcard, q_wildcard, q_wildcard])
        
    sql += " ORDER BY pr.recorded_at DESC"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        d = dict(r)
        d["category_path"] = d["category_path"].split(",") if d["category_path"] else []
        d["specifications"] = json.loads(d["specifications"]) if d["specifications"] else {}
        d["specifications_raw"] = json.loads(d["specifications_raw"]) if d["specifications_raw"] else {}
        d["images"] = json.loads(d["images"]) if d["images"] else []
        d["price_tiers"] = json.loads(d["price_tiers"]) if d.get("price_tiers") else []
        results.append(d)
        
    conn.close()
    return results

def get_price_history(product_id: str) -> List[Dict[str, Any]]:
    """Fetches the time-series price logs for a product."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT price, currency, price_usd, recorded_at, source
    FROM price_records
    WHERE product_id = ?
    ORDER BY recorded_at ASC
    """, (product_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_intake_submission(submission: Dict[str, Any]) -> str:
    """Saves a supplier intake form submission."""
    sub_id = submission.get("id") or str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat()
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    import json
    
    cursor.execute("""
    INSERT INTO supplier_submissions (
        id, company_name, contact_email, country, category, product_name, specifications,
        unit_price, currency, moq, lead_time_days, tiered_pricing, certifications, images, notes, status, submitted_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sub_id, submission["company_name"], submission["contact_email"], submission["country"],
        submission["category"], submission["product_name"], json.dumps(submission.get("specifications", {})),
        float(submission["unit_price"]), submission["currency"], submission.get("moq", 1),
        submission.get("lead_time_days", 7), json.dumps(submission.get("tiered_pricing", [])),
        json.dumps(submission.get("certifications", [])), json.dumps(submission.get("images", [])),
        submission.get("notes", ""), submission.get("status", "pending"), now_str
    ))
    conn.commit()
    conn.close()
    return sub_id

def get_intake_submissions() -> List[Dict[str, Any]]:
    """Fetches all supplier intake submissions."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    import json
    
    cursor.execute("SELECT * FROM supplier_submissions ORDER BY submitted_at DESC")
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        d = dict(r)
        d["specifications"] = json.loads(d["specifications"]) if d["specifications"] else {}
        d["tiered_pricing"] = json.loads(d["tiered_pricing"]) if d["tiered_pricing"] else []
        d["certifications"] = json.loads(d["certifications"]) if d["certifications"] else []
        d["images"] = json.loads(d["images"]) if d["images"] else []
        results.append(d)
        
    conn.close()
    return results
