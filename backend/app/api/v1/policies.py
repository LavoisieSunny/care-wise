from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Body
from app.schemas.policy import PolicyDetails, PolicyListResponse, PolicyUploadResponse
from app.services.policy_service import policy_service
from app.core.audit_log import record_event

router = APIRouter()

@router.get("/policies", response_model=PolicyListResponse, tags=["Policies"])
async def list_policies():
    """Get all loaded insurance policies (sample and user uploaded)."""
    policies = policy_service.list_policies()
    return PolicyListResponse(policies=policies, count=len(policies))

@router.get("/policies/{policy_id}", response_model=PolicyDetails, tags=["Policies"])
async def get_policy(policy_id: str):
    """Get full parsed details of a specific insurance policy."""
    policy = policy_service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.post("/policies/upload", response_model=PolicyUploadResponse, tags=["Policies"])
async def upload_policy_pdf(file: UploadFile = File(...), mode: str = Query("quick", pattern="^(quick|ai)$")):
    """Upload an insurance policy document (PDF) to perform fast OCR text and heuristic extraction."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF policy documents are currently supported.")
    
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        response = policy_service.parse_pdf(content, file.filename, mode=mode)
        record_event(
            action="policy.upload",
            target_type="policy",
            target_id=response.policy.id if response.policy else None,
            detail={"filename": file.filename, "mode": mode, "size_bytes": len(content)},
        )
        return response
    except Exception as e:
        record_event(
            action="policy.upload",
            target_type="policy",
            outcome="failure",
            detail={"filename": file.filename, "error": str(e)},
        )
        raise HTTPException(status_code=500, detail=f"Failed to extract policy text: {str(e)}")

@router.post("/policies/upload/deep", response_model=PolicyUploadResponse, tags=["Policies"])
async def upload_policy_deep(upload_id: str = Query(...)):
    """Run deep AI LLM semantic extraction on previously uploaded document using cached page texts."""
    try:
        response = policy_service.parse_pdf_deep(upload_id)
        record_event(
            action="policy.deep_extract",
            target_type="policy",
            target_id=upload_id,
            detail={"mode": "ai_deep_extraction"},
        )
        return response
    except ValueError as ve:
        record_event(action="policy.deep_extract", target_type="policy", target_id=upload_id,
                      outcome="failure", detail={"error": str(ve)})
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        record_event(action="policy.deep_extract", target_type="policy", target_id=upload_id,
                      outcome="failure", detail={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed AI deep extraction: {str(e)}")
