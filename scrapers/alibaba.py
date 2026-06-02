import random
from typing import List, Dict, Any
from scrapers.base import BaseScraper
from taxonomy.categories import find_category_path

class AlibabaScraper(BaseScraper):
    source_name: str = "alibaba"
    source_type: str = "b2b"

    async def search(self, query: str, category_leaf: str) -> List[Dict[str, Any]]:
        """
        Simulates searching on Alibaba. Returns mock products with tiered pricing and MOQs in USD.
        """
        path = find_category_path(category_leaf)
        category_path = path if path else ["Industrial", category_leaf]
        
        products = []
        
        # Define B2B supplier listings
        if category_leaf == "Pistons":
            items = [
                {
                    "title": "High Quality Engine Piston for Toyota 2JZ 13101-46090",
                    "brand": "NPR",
                    "base_price_usd": 12.0,
                    "oem": "13101-46090",
                    "specs": {"bore_diameter": "86mm", "stroke": "86mm", "material": "aluminum", "compression_ratio": "8.5"},
                    "moq": 100,
                    "tiers": [{"qty": 100, "price": 12.0}, {"qty": 500, "price": 10.5}, {"qty": 2000, "price": 9.0}]
                },
                {
                    "title": "Factory Price Cast Iron Diesel Piston for Mitsubishi L300 Engine MD050390",
                    "brand": "NPR",
                    "base_price_usd": 8.5,
                    "oem": "MD050390",
                    "specs": {"bore_diameter": "91.1mm", "stroke": "95mm", "material": "cast_iron", "compression_ratio": "21.0"},
                    "moq": 200,
                    "tiers": [{"qty": 200, "price": 8.5}, {"qty": 1000, "price": 7.5}, {"qty": 5000, "price": 6.8}]
                },
                {
                    "title": "Custom Forged Racing Pistons Set for Honda K20 K24 87mm Bore Size",
                    "brand": "Mahle",
                    "base_price_usd": 45.0,
                    "oem": "193048590",
                    "specs": {"bore_diameter": "87mm", "stroke": "99mm", "material": "forged_steel", "compression_ratio": "12.5"},
                    "moq": 50,
                    "tiers": [{"qty": 50, "price": 45.0}, {"qty": 200, "price": 41.0}, {"qty": 1000, "price": 37.5}]
                }
            ]
        elif category_leaf == "Smartphones":
            items = [
                {
                    "title": "Wholesale Samsung Galaxy S24 Ultra 5G Smart Phone 12GB+256GB Unlocked",
                    "brand": "Samsung",
                    "base_price_usd": 750.0,
                    "specs": {"ram": "12GB", "storage": "256GB", "screen_size": "6.8 inch", "battery": "5000 mAh"},
                    "moq": 10,
                    "tiers": [{"qty": 10, "price": 750.0}, {"qty": 50, "price": 710.0}, {"qty": 200, "price": 680.0}]
                },
                {
                    "title": "Cheap Android Smartphone 8GB 256GB Factory Unlocked OEM Phone",
                    "brand": "OEM",
                    "base_price_usd": 95.0,
                    "specs": {"ram": "8GB", "storage": "256GB", "screen_size": "6.6 inch", "battery": "5000 mAh"},
                    "moq": 100,
                    "tiers": [{"qty": 100, "price": 95.0}, {"qty": 500, "price": 88.0}, {"qty": 2000, "price": 80.0}]
                }
            ]
        elif category_leaf == "Tempered Glass":
            items = [
                {
                    "title": "Factory Direct Sale 10mm Clear Flat Tempered Glass Sheet for Building Glass Door",
                    "brand": "Asahi",
                    "base_price_usd": 15.0, # price per m² or piece
                    "specs": {"thickness": "10mm", "width": "1200mm", "height": "2400mm", "tint": "clear"},
                    "moq": 50,
                    "tiers": [{"qty": 50, "price": 15.0}, {"qty": 200, "price": 13.5}, {"qty": 1000, "price": 11.5}]
                }
            ]
        elif category_leaf == "Steel Sheet":
            items = [
                {
                    "title": "Cold Rolled 304 Stainless Steel Sheet Plate 2mm Thickness Mill Finish",
                    "brand": "Generic",
                    "base_price_usd": 2.2, # price per kg
                    "specs": {"grade": "304", "thickness": "2mm", "width": "1220mm", "length": "2440mm", "surface_finish": "mill"},
                    "moq": 1000, # 1000 kg (1 ton)
                    "tiers": [{"qty": 1000, "price": 2.2}, {"qty": 5000, "price": 2.0}, {"qty": 20000, "price": 1.8}]
                }
            ]
        else:
            items = [
                {
                    "title": f"Industrial Grade {category_leaf} Manufacturer Supply",
                    "brand": "Generic",
                    "base_price_usd": 5.0,
                    "specs": {},
                    "moq": 100,
                    "tiers": [{"qty": 100, "price": 5.0}]
                }
            ]

        if query:
            items = [it for it in items if query.lower() in it["title"].lower() or query.lower() in it["brand"].lower()]

        for i, item in enumerate(items):
            # Price fluctuates slightly
            price_usd = item["base_price_usd"] * random.uniform(0.96, 1.04)
            # Adjust tiers
            adjusted_tiers = []
            for t in item["tiers"]:
                adjusted_tiers.append({
                    "qty": t["qty"],
                    "price": round(t["price"] * (price_usd / item["base_price_usd"]), 2)
                })

            p_data = {
                "source": self.source_name,
                "source_id": f"alibaba-{category_leaf.lower()}-{i}",
                "source_url": f"https://www.alibaba.com/product-detail/{category_leaf.lower()}-{i}.html",
                "title": item["title"],
                "title_en": item["title"],
                "category_path": category_path,
                "category_leaf": category_leaf,
                "brand": item["brand"],
                "oem_part_number": item.get("oem"),
                "product_type": "raw_material" if category_leaf in ["Steel Sheet", "Metals"] else ("component" if category_leaf in ["Pistons", "Tempered Glass"] else "finished_good"),
                "specifications": item["specs"],
                "specifications_raw": item["specs"],
                "description": f"Professional supplier of industrial {item['title']}. We support custom OEM processing, certification support, and global shipping.",
                "images": [f"https://picsum.photos/seed/{category_leaf.lower()}-alibaba/300/300"],
                "seller_name": f"Henan {item['brand'] if item['brand'] != 'Generic' else 'Industrial'} Manufacturing Co., Ltd.",
                "seller_type": "manufacturer",
                "seller_rating": round(random.uniform(4.2, 4.8), 1),
                "seller_location": "Henan, China",
                "price": price_usd,
                "currency": "USD",
                "price_usd": price_usd,
                "min_order_qty": item["moq"],
                "price_tiers": adjusted_tiers,
                "unit_of_measure": "piece" if category_leaf != "Steel Sheet" else "kg",
                "stock_status": "in_stock"
            }
            products.append(p_data)
            
        return products

    async def get_price(self, source_id: str) -> Dict[str, Any]:
        return {
            "price": random.uniform(1.0, 1000.0),
            "currency": "USD",
            "stock_status": "in_stock"
        }
