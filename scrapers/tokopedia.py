import random
from typing import List, Dict, Any
from scrapers.base import BaseScraper
from taxonomy.categories import find_category_path

class TokopediaScraper(BaseScraper):
    source_name: str = "tokopedia"
    source_type: str = "consumer"

    async def search(self, query: str, category_leaf: str) -> List[Dict[str, Any]]:
        """
        Simulates searching on Tokopedia. Returns mock product details matching search.
        """
        path = find_category_path(category_leaf)
        category_path = path if path else ["Consumer Goods", category_leaf]
        
        products = []
        
        # Determine items based on category
        if category_leaf == "Smartphones":
            items = [
                {"title": "Samsung Galaxy S24 Ultra 12GB 256GB", "brand": "Samsung", "base_price": 18000000, "specs": {"ram": "12GB", "storage": "256GB", "screen_size": "6.8 inch", "battery": "5000 mAh"}},
                {"title": "Samsung Galaxy A55 5G 8GB 256GB", "brand": "Samsung", "base_price": 6000000, "specs": {"ram": "8GB", "storage": "256GB", "screen_size": "6.6 inch", "battery": "5000 mAh"}},
                {"title": "Apple iPhone 15 Pro Max 256GB", "brand": "Apple", "base_price": 22000000, "specs": {"ram": "8GB", "storage": "256GB", "screen_size": "6.7 inch", "battery": "4441 mAh"}},
                {"title": "Xiaomi Redmi Note 13 Pro 8GB 256GB", "brand": "Xiaomi", "base_price": 3800000, "specs": {"ram": "8GB", "storage": "256GB", "screen_size": "6.67 inch", "battery": "5000 mAh"}},
            ]
        elif category_leaf == "Pistons":
            items = [
                {"title": "Piston NPR Toyota 2JZ Engine 86mm Standard", "brand": "NPR", "base_price": 2500000, "oem": "13101-46090", "specs": {"bore_diameter": "86mm", "stroke": "86mm", "material": "aluminum", "compression_ratio": "8.5"}},
                {"title": "Piston NPR Mitsubishi L300 Diesel", "brand": "NPR", "base_price": 1800000, "oem": "MD050390", "specs": {"bore_diameter": "91.1mm", "stroke": "95mm", "material": "cast_iron", "compression_ratio": "21.0"}},
                {"title": "Forged Piston Set Mahle Honda K20 K24 87mm", "brand": "Mahle", "base_price": 9500000, "oem": "193048590", "specs": {"bore_diameter": "87mm", "stroke": "99mm", "material": "forged_steel", "compression_ratio": "12.5"}},
            ]
        elif category_leaf == "Laundry Detergent":
            items = [
                {"title": "Rinso Cair Molto Deterjen Cair 1.8 Liter", "brand": "Rinso", "base_price": 45000, "specs": {"form": "liquid", "weight_volume": "1.8L", "scent": "rose"}},
                {"title": "Rinso Bubuk Anti Noda 1.8 kg", "brand": "Rinso", "base_price": 42000, "specs": {"form": "powder", "weight_volume": "1.8kg", "scent": "original"}},
                {"title": "Attack Sensor Matic Deterjen Bubuk 1.2kg", "brand": "Attack", "base_price": 38000, "specs": {"form": "powder", "weight_volume": "1.2kg", "scent": "floral"}},
            ]
        elif category_leaf == "Interior Paint":
            items = [
                {"title": "Dulux Catylac Interior Paint Putih 5 kg", "brand": "Dulux", "base_price": 175000, "specs": {"finish": "matte", "base": "water", "volume": "5L", "color": "white"}},
                {"title": "Nippon Paint Vinilex Cat Tembok Interior 25 kg", "brand": "Nippon Paint", "base_price": 680000, "specs": {"finish": "matte", "base": "water", "volume": "25L", "color": "white"}},
            ]
        else:
            # Fallback random item
            items = [
                {"title": f"Generic Brand {category_leaf} Product", "brand": "Generic", "base_price": 100000, "specs": {}}
            ]

        # Apply search query filter if provided
        if query:
            items = [it for it in items if query.lower() in it["title"].lower() or query.lower() in it["brand"].lower()]

        for i, item in enumerate(items):
            # Convert prices: Tokopedia price is IDR, we also need USD conversion (assume 1 USD = 16,000 IDR)
            price_idr = item["base_price"] * random.uniform(0.95, 1.05)
            price_usd = price_idr / 16000.0
            
            p_data = {
                "source": self.source_name,
                "source_id": f"tokopedia-{category_leaf.lower()}-{i}",
                "source_url": f"https://www.tokopedia.com/p/{category_leaf.lower()}-{i}",
                "title": item["title"],
                "title_en": item["title"],
                "category_path": category_path,
                "category_leaf": category_leaf,
                "brand": item["brand"],
                "oem_part_number": item.get("oem"),
                "product_type": "component" if category_leaf in ["Pistons", "Components"] else "finished_good",
                "specifications": item["specs"],
                "specifications_raw": item["specs"],
                "description": f"Beautiful and premium {item['title']} from our verified merchant.",
                "images": [f"https://picsum.photos/seed/{category_leaf.lower()}/300/300"],
                "seller_name": f"Official {item['brand']} Store",
                "seller_type": "retailer",
                "seller_rating": round(random.uniform(4.5, 4.9), 1),
                "seller_location": "Jakarta, Indonesia",
                "price": price_idr,
                "currency": "IDR",
                "price_usd": price_usd,
                "unit_of_measure": "piece" if category_leaf not in ["Laundry Detergent", "Interior Paint"] else "unit",
                "stock_status": "in_stock"
            }
            products.append(p_data)
            
        return products

    async def get_price(self, source_id: str) -> Dict[str, Any]:
        # Return a simple mock price update
        return {
            "price": random.uniform(10000, 20000000),
            "currency": "IDR",
            "stock_status": "in_stock"
        }
