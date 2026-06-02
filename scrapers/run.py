import asyncio
import structlog
from datetime import datetime
from scrapers.tokopedia import TokopediaScraper
from scrapers.shopee import ShopeeScraper
from scrapers.alibaba import AlibabaScraper
from taxonomy.input_corrector import InputCorrector
from db import supabase_client

# Setup logging
logger = structlog.get_logger(__name__)

async def run_scraping():
    logger.info("Starting Scraper Data Ingestion Pipeline")
    
    # Instantiate scrapers
    scrapers = [
        TokopediaScraper(),
        ShopeeScraper(),
        AlibabaScraper()
    ]
    
    # Categories to scrape
    categories = ["Smartphones", "Pistons", "Laundry Detergent", "Interior Paint", "Tempered Glass", "Steel Sheet"]
    
    total_products = 0
    total_prices = 0
    
    for category in categories:
        logger.info("Scraping category", category=category)
        
        for scraper in scrapers:
            logger.info("Executing search on platform", platform=scraper.source_name, category=category)
            try:
                # Run search
                raw_products = await scraper.search(query="", category_leaf=category)
                logger.info("Scrape search completed", platform=scraper.source_name, count=len(raw_products))
                
                for rp in raw_products:
                    # Clean and validate input through Input Corrector
                    corrector_res = InputCorrector.correct_input(rp)
                    corrected_product = corrector_res["corrected_request"]
                    
                    # Log corrections for visibility
                    if "corrections" in corrector_res:
                        logger.info("Input corrected", 
                                    original_title=rp["title"], 
                                    corrections_count=len(corrector_res["corrections"]))
                    
                    # Prepare product record for db
                    db_product = {
                        "source": rp["source"],
                        "source_id": rp["source_id"],
                        "source_url": rp["source_url"],
                        "title": corrected_product["title"],
                        "title_en": rp.get("title_en"),
                        "category_path": corrected_product["category_path"],
                        "category_leaf": category,
                        "brand": corrected_product["brand"],
                        "oem_part_number": corrected_product["oem_part_number"],
                        "product_type": rp["product_type"],
                        "specifications": corrected_product["specifications"],
                        "specifications_raw": rp["specifications_raw"],
                        "description": rp.get("description"),
                        "images": rp.get("images", []),
                        "seller_name": rp.get("seller_name"),
                        "seller_type": rp.get("seller_type"),
                        "seller_rating": rp.get("seller_rating"),
                        "seller_location": rp.get("seller_location")
                    }
                    
                    # Save to DB
                    prod_id = supabase_client.upsert_product(db_product)
                    total_products += 1
                    
                    # Prepare price record
                    db_price = {
                        "product_id": prod_id,
                        "source": rp["source"],
                        "price": rp["price"],
                        "currency": rp["currency"],
                        "price_usd": rp["price_usd"],
                        "price_per_unit": rp.get("price_per_unit") or rp["price_usd"], # default unit price to price_usd
                        "unit_of_measure": rp.get("unit_of_measure"),
                        "min_order_qty": rp.get("min_order_qty", 1),
                        "price_tiers": rp.get("price_tiers", []),
                        "shipping_cost": rp.get("shipping_cost"),
                        "discount_pct": rp.get("discount_pct"),
                        "is_promo": rp.get("is_promo", False),
                        "stock_status": rp.get("stock_status", "in_stock")
                    }
                    
                    supabase_client.insert_price_record(db_price)
                    total_prices += 1
                    
            except Exception as e:
                logger.error("Error scraping platform", platform=scraper.source_name, category=category, error=str(e))
                
    logger.info("Scraper pipeline execution finished", products_upserted=total_products, prices_inserted=total_prices)

if __name__ == "__main__":
    asyncio.run(run_scraping())
