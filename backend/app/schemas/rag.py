from typing import List, Optional
from pydantic import BaseModel
from .policy import ClauseCitation

class RAGQueryRequest(BaseModel):
    policy_id: str
    query: str
    hospital_name: Optional[str] = None
    procedure_name: Optional[str] = None

class GroundedAnswerResponse(BaseModel):
    query: str
    answer: str
    confidence: float
    citations: List[ClauseCitation]
    grounded_clauses: List[str]
    suggested_actions: List[str]
    policy_name: str
