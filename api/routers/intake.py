from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr
from db import supabase_client

router = APIRouter()

class IntakeSubmissionRequest(BaseModel):
    company_name: str
    contact_email: EmailStr
    country: str
    category: str
    product_name: str
    specifications: Dict[str, Any] = {}
    unit_price: float
    currency: str = "USD"
    moq: int = 1
    lead_time_days: int = 7
    tiered_pricing: List[Dict[str, Any]] = []
    certifications: List[str] = []
    images: List[str] = []
    notes: Optional[str] = ""

@router.post("/intake/submit")
async def submit_intake(request: IntakeSubmissionRequest):
    try:
        sub_id = supabase_client.save_intake_submission(request.dict())
        return {
            "status": "success",
            "message": "Intake form submitted successfully for admin review",
            "submission_id": sub_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit intake: {str(e)}")

@router.get("/intake/submissions")
async def get_intake_submissions():
    submissions = supabase_client.get_intake_submissions()
    return {"data": submissions, "count": len(submissions)}
