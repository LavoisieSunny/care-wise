from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.policy import PolicyDetails, PolicyListResponse, PolicyUploadResponse
from app.services.policy_service import policy_service

router = APIRouter()

@router.get("/policies", response_model=PolicyListResponse, tags=["Policies"])
async def list_policies():
    """List all available pre-loaded and ingested insurance policies."""
    policies = policy_service.list_policies()
    return PolicyListResponse(policies=policies)

@router.get("/policies/{policy_id}", response_model=PolicyDetails, tags=["Policies"])
async def get_policy(policy_id: str):
    """Get complete extracted details and grounded citations for a specific policy."""
    policy = policy_service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.post("/policies/upload", response_model=PolicyUploadResponse, tags=["Policies"])
async def upload_policy_pdf(file: UploadFile = File(...)):
    """Upload an insurance policy document (PDF) to perform AI extraction and grounded citation indexing."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF policy documents are currently supported.")
    
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        response = policy_service.parse_pdf(content, file.filename)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract policy text: {str(e)}")
