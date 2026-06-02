import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.settings import settings
from config.logging import configure_logging
import structlog

# Set up logging
configure_logging()
logger = structlog.get_logger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="Price Intelligence API",
    description="MLOps Price checking & Fair price estimation endpoints",
    version="1.0.0"
)

# Add CORS Middleware (Allow Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import Routers
from api.routers import predictions, products, intake

app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(intake.router, prefix="/api/v1", tags=["OEM Intake"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "sqlite_fallback_active" if not settings.SUPABASE_KEY else "supabase_active"}

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the MLOps Price Intelligence API",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
