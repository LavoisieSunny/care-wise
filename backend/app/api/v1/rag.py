from fastapi import APIRouter
from app.schemas.rag import RAGQueryRequest, GroundedAnswerResponse
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/rag/query", response_model=GroundedAnswerResponse, tags=["RAG Assistant"])
async def query_policy_rag(req: RAGQueryRequest):
    """Ask questions about the caregiver's policy and receive answers strictly grounded with page and clause citations."""
    return rag_service.answer_query(
        policy_id=req.policy_id,
        query=req.query,
        hospital_name=req.hospital_name,
        procedure_name=req.procedure_name
    )
