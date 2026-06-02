import asyncio
import structlog
from scrapers.run import run_scraping
from ml.matching.train import train_matching_model
from ml.pricing.train import train_pricing_model
from db import supabase_client

logger = structlog.get_logger(__name__)

async def run_quality_check():
    """Runs a data quality verification check on products and price records."""
    logger.info("Starting Data Quality checks")
    products = supabase_client.get_latest_prices()
    
    anomalies = 0
    missing_specs = 0
    
    for p in products:
        # Check price anomaly: price <= 0
        if p.get("price") is not None and p["price"] <= 0:
            anomalies += 1
            logger.warning("Data anomaly: Product price is zero or negative", title=p["title"], price=p["price"])
            
        # Check specifications completeness
        if not p.get("specifications"):
            missing_specs += 1
            
    logger.info("Data Quality check complete", 
                total_products=len(products), 
                anomalies_found=anomalies, 
                missing_specs_count=missing_specs)

async def run_retrain():
    """Retrains the model based on newly ingested database records."""
    logger.info("Starting automated model retraining pipeline")
    products = supabase_client.get_latest_prices()
    
    # 1. Train Pricing Model
    for leaf in ["Smartphones", "Pistons", "Laundry Detergent"]:
        category_products = [p for p in products if p.get("category_leaf") == leaf]
        prices = [float(p["price_usd"]) for p in category_products if p.get("price_usd") is not None]
        if prices:
            train_pricing_model(prices, leaf)
            
    # 2. Train Product Matching Model (mock training sample pair list)
    if len(products) >= 2:
        # Construct positive and negative training pairs
        pairs = []
        # Positive pair (same leaf and brand)
        p1 = products[0]
        p2 = next((p for p in products[1:] if p["category_leaf"] == p1["category_leaf"]), None)
        if p2:
            pairs.append((p1, p2, 1))
            
        # Negative pair (different leaf)
        n2 = next((p for p in products[1:] if p["category_leaf"] != p1["category_leaf"]), None)
        if n2:
            pairs.append((p1, n2, 0))
            
        if pairs:
            train_matching_model(pairs)
            
    logger.info("Automated model retraining completed successfully")

async def main():
    # Execute a full scrape and retraining run
    await run_scraping()
    await run_quality_check()
    await run_retrain()

if __name__ == "__main__":
    asyncio.run(main())
