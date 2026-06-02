import random
from typing import List, Dict, Any
from scrapers.base import BaseScraper
from taxonomy.categories import find_category_path

class ShopeeScraper(BaseScraper):
    source_name: str = "shopee"
    source_type: str = "consumer"

    async def search(self, query: str, category_leaf: str) -> List[Dict[str, Any]]:
        """
        Simulates searching on Shopee. Returns mock products matching category.
        """
        path = find_category_path(category_leaf)
        category_path = path if path else ["Consumer Goods", category_leaf]
        
        products = []
        
        if category_leaf == "Smartphones":
            items = [
                {"title": "Samsung Galaxy S24 Ultra Dual SIM 256GB", "brand": "Samsung", "base_price": 18200000, "specs": {"ram": "12GB", "storage": "256GB", "screen_size": "6.8 inch", "battery": "5000 mAh"}},
                {"title": "Samsung Galaxy A55 5G RAM 8GB ROM 256GB", "brand": "Samsung", "base_price": 5950000, "specs": {"ram": "8GB", "storage": "256GB", "screen_size": "6.6 inch", "battery": "5000 mAh"}},
                {"title": "Apple iPhone 15 Pro Max Garansi Resmi 256GB", "brand": "Apple", "base_price": 22400000, "specs": {"ram": "8GB", "storage": "256GB", "screen_size": "6.7 inch", "battery": "4441 mAh"}},
            ]
        elif category_leaf == "Pistons":
            items = [
                {"title": "Piston NPR Toyota 2JZ Engine 86mm Standard Set", "brand": "NPR", "base_price": 2450000, "oem": "13101-46090", "specs": {"bore_diameter": "86mm", "stroke": "86mm", "material": "aluminum", "compression_ratio": "8.5"}},
                {"title": "Piston Assy Mitsubishi L300 Diesel NPR Japan", "brand": "NPR", "base_price": 1850000, "oem": "MD050390", "specs": {"bore_diameter": "91.1mm", "stroke": "95mm", "material": "cast_iron", "compression_ratio": "21.0"}},
            ]
        elif category_leaf == "Laundry Detergent":
            items = [
                {"title": "Rinso Liquid Deterjen Cair Molto Rose 1800mL", "brand": "Rinso", "base_price": 44000, "specs": {"form": "liquid", "weight_volume": "1.8L", "scent": "rose"}},
                {"title": "Rinso Deterjen Bubuk Anti Noda 1.8kg", "brand": "Rinso", "base_price": 41500, "specs": {"form": "powder", "weight_volume": "1.8kg", "scent": "original"}},
            ]
        elif category_leaf == "Interior Paint":
            items = [
                {"title": "Dulux Catylac Interior Paint 5kg Warna Putih", "brand": "Dulux", "base_price": 172000, "specs": {"finish": "matte", "base": "water", "volume": "5L", "color": "white"}},
                {"title": "Nippon Paint Vinilex Interior Wall Paint 25kg White", "brand": "Nippon Paint", "base_price": 675000, "specs": {"finish": "matte", "base": "water", "volume": "25L", "color": "white"}},
            ]
        else:
            items = [
                {"title": f"Shopee Generic Brand {category_leaf}", "brand": "Generic", "base_price": 95000, "specs": {}}
            ]

        if query:
            items = [it for it in items if query.lower() in it["title"].lower() or query.lower() in it["brand"].lower()]

        for i, item in enumerate(items):
            price_idr = item["base_price"] * random.uniform(0.94, 1.04)
            price_usd = price_idr / 16000.0
            
            p_data = {
                "source": self.source_name,
                "source_id": f"shopee-{category_leaf.lower()}-{i}",
                "source_url": f"https://shopee.co.id/product/{category_leaf.lower()}-{i}",
                "title": item["title"],
                "title_en": item["title"],
                "category_path": category_path,
                "category_leaf": category_leaf,
                "brand": item["brand"],
                "oem_part_number": item.get("oem"),
                "product_type": "component" if category_leaf in ["Pistons", "Components"] else "finished_good",
                "specifications": item["specs"],
                "specifications_raw": item["specs"],
                "description": f"Grab this high-quality {item['title']} on Shopee now with discount codes.",
                "images": [f"https://picsum.photos/seed/{category_leaf.lower()}-shopee/300/300"],
                "seller_name": f"{item['brand']} Official Shop",
                "seller_type": "retailer",
                "seller_rating": round(random.uniform(4.6, 4.9), 1),
                "seller_location": "Surabaya, Indonesia",
                "price": price_idr,
                "currency": "IDR",
                "price_usd": price_usd,
                "unit_of_measure": "piece" if category_leaf not in ["Laundry Detergent", "Interior Paint"] else "unit",
                "stock_status": "in_stock"
            }
            products.append(p_data)
            
        return products

    async def get_price(self, source_id: str) -> Dict[str, Any]:
        return {
            "price": random.uniform(10000, 25000000),
            "currency": "IDR",
            "stock_status": "in_stock"
        }
